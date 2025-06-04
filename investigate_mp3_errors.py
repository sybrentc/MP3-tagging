import os
import subprocess
import re
import sys
import argparse
from datetime import datetime

LOG_FILENAME = "mp3_error_report.log"

def run_command(command_parts):
    """Runs a command and returns its stdout, stderr, and return code."""
    try:
        process = subprocess.Popen(command_parts, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        # Increased timeout for potentially problematic files
        stdout, stderr = process.communicate(timeout=180) 
        return stdout, stderr, process.returncode
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
        # Ensure stdout and stderr are strings even after timeout
        stdout_str = stdout if isinstance(stdout, str) else (stdout.decode('utf-8', errors='replace') if stdout else "")
        stderr_str = stderr if isinstance(stderr, str) else (stderr.decode('utf-8', errors='replace') if stderr else "")
        print(f"  COMMAND TIMEOUT: {' '.join(command_parts)}")
        return stdout_str, f"COMMAND TIMEOUT: {' '.join(command_parts)}\n{stderr_str}", -1 
    except Exception as e:
        print(f"  COMMAND FAILED: {' '.join(command_parts)} - Error: {e}")
        return "", f"COMMAND FAILED: {' '.join(command_parts)} - Error: {e}", -2


def check_mp3val_for_report(filepath):
    """
    Checks MP3 integrity using mp3val.
    Returns a string with error details if errors are found, else None.
    """
    print(f"  Checking {filepath} with mp3val...")
    stdout, stderr, returncode = run_command(["mp3val", filepath])
    
    error_output = []
    if returncode != 0:
        error_output.append(f"mp3val command failed with return code {returncode}.")
    if stderr.strip():
        error_output.append(f"mp3val stderr:\n{stderr.strip()}")
    if "ERROR" in stdout:
        error_output.append(f"mp3val stdout reported ERRORs:\n{stdout.strip()}")
    elif "WARNING" in stdout and not "FIXED" in stdout: # Non-fixed warnings might be of interest
        error_output.append(f"mp3val stdout reported WARNINGs (not fixed):\n{stdout.strip()}")
    
    if error_output:
        return f"--- mp3val Errors for {os.path.basename(filepath)} ---\n" + "\n".join(error_output)
    
    print(f"  mp3val OK: {filepath}")
    return None

def check_ffmpeg_decode_for_report(filepath):
    """
    Checks for ffmpeg decoding errors.
    Returns a string with error details if errors are found, else None.
    """
    print(f"  Checking {filepath} with ffmpeg (decode)...")
    _stdout, stderr, returncode = run_command(
        ["ffmpeg", "-v", "error", "-i", filepath, "-f", "null", "-"]
    )
    
    # ffmpeg -v error sends errors to stderr. A non-zero return code also indicates an issue.
    if returncode != 0 or stderr.strip():
        error_details = f"--- ffmpeg Decode Errors for {os.path.basename(filepath)} ---\n"
        if returncode != 0:
            error_details += f"ffmpeg command exited with return code {returncode}.\n"
        if stderr.strip():
            error_details += f"ffmpeg stderr:\n{stderr.strip()}\n"
        return error_details
        
    print(f"  ffmpeg decode OK: {filepath}")
    return None

def investigate_mp3_files(root_dir, log_file_path):
    """
    Investigates MP3 files for errors using mp3val and ffmpeg decode check,
    logging any errors found.
    """
    print(f"Starting investigation for directory: {root_dir}")
    print(f"Errors will be logged to: {log_file_path}")
    
    files_processed = 0
    files_with_errors = 0
    
    with open(log_file_path, "w", encoding="utf-8") as log_f:
        log_f.write(f"MP3 Error Investigation Report - Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_f.write(f"Scanning directory: {root_dir}\n\n")

        for subdir, _dirs, files in os.walk(root_dir):
            for filename in files:
                if filename.lower().endswith(".mp3"):
                    filepath = os.path.join(subdir, filename)
                    print(f"\n>>> Investigating file: {filepath}")
                    files_processed += 1
                    has_errors_for_this_file = False
                    
                    mp3val_error = check_mp3val_for_report(filepath)
                    if mp3val_error:
                        print(f"  ERROR (mp3val): {filepath}")
                        log_f.write(f"File: {filepath}\n")
                        log_f.write(f"{mp3val_error}\n\n")
                        has_errors_for_this_file = True
                        
                    ffmpeg_error = check_ffmpeg_decode_for_report(filepath)
                    if ffmpeg_error:
                        # Avoid duplicate "File:" line if mp3val also erred
                        if not has_errors_for_this_file:
                             log_f.write(f"File: {filepath}\n")
                        print(f"  ERROR (ffmpeg decode): {filepath}")
                        log_f.write(f"{ffmpeg_error}\n\n")
                        has_errors_for_this_file = True
                    
                    if has_errors_for_this_file:
                        files_with_errors += 1
                        
    summary = (
        f"\n--- Investigation Summary ---\n"
        f"Total MP3 files investigated: {files_processed}\n"
        f"Total files with errors logged: {files_with_errors}\n"
        f"Error report saved to: {log_file_path}\n"
        f"-----------------------------"
    )
    print(summary)
    with open(log_file_path, "a", encoding="utf-8") as log_f: # Append summary
        log_f.write(summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Investigate MP3 files for corruption and decode errors.")
    parser.add_argument("music_directory", help="The root directory of the music library to investigate.")
    args = parser.parse_args()

    music_root_to_investigate = os.path.abspath(args.music_directory)

    if not os.path.isdir(music_root_to_investigate):
        print(f"ERROR: The specified music directory does not exist or is not a directory: {music_root_to_investigate}")
        sys.exit(1)
        
    # Determine log file path relative to the script's location or workspace root
    # For simplicity, let's assume script is run from workspace root or its location is known
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_file_path = os.path.join(script_dir, LOG_FILENAME)


    print(f"Starting MP3 error investigation for: {music_root_to_investigate}")
    print(f"A detailed report will be saved to '{log_file_path}'.")
    
    investigate_mp3_files(music_root_to_investigate, log_file_path) 