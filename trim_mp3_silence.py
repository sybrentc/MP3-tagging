import os
import subprocess
import re
import shutil
import sys
import argparse

# MUSIC_ROOT_DIR = "/Users/stencate/Desktop/Music/Fatboy Slim/" # This line should be removed or ensured it's commented.
SILENCE_THRESHOLD_DB = "-50dB"  # dB level to consider as silence
MIN_SILENCE_DETECT_DURATION = "1" # seconds (string for ffmpeg's -d option)
MIN_SILENCE_DURATION_TO_TRIM = 0.5 # seconds (actual length of silence to qualify for trimming)
END_OF_TRACK_TOLERANCE = 0.2 # seconds (how close silence_end must be to track_duration to be "at the end")
                               # Increased slightly from 0.1 to be a bit more inclusive.

def run_command(command_parts):
    """Runs a command and returns its stdout, stderr, and return code."""
    try:
        process = subprocess.Popen(command_parts, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        stdout, stderr = process.communicate(timeout=120) # 2 min timeout for ffmpeg processes
        return stdout, stderr, process.returncode
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
        print(f"  COMMAND TIMEOUT: {' '.join(command_parts)}")
        return stdout, stderr, -1 # Indicate timeout
    except Exception as e:
        print(f"  COMMAND FAILED: {' '.join(command_parts)} - Error: {e}")
        return "", str(e), -2 # Indicate other execution error


def check_mp3val(filepath):
    """Checks MP3 integrity using mp3val. Returns True if OK, False if errors."""
    print(f"  Running mp3val check...")
    # -nb: No backup file, -f: try to fix (if simple issues)
    # We're mostly interested in error detection here.
    # If mp3val fixes something benignly, that's fine.
    # If it reports persistent errors, we should not proceed.
    stdout, stderr, returncode = run_command(["mp3val", filepath])

    if returncode != 0:
        print(f"  mp3val command failed for {filepath}. Return code: {returncode}")
        if stderr: print(f"  mp3val stderr: {stderr.strip()}")
        return False

    # mp3val primarily outputs to stdout
    if "ERROR" in stdout:
        print(f"  mp3val found ERRORS for {filepath}:\n{stdout.strip()}")
        return False
    if "WARNING" in stdout and not "FIXED" in stdout : # Warnings without fixes might be problematic
        print(f"  mp3val found WARNINGS for {filepath}:\n{stdout.strip()}")
        # Decide if warnings should halt process. For now, let's be cautious.
        # return False
    if "FIXED" in stdout:
         print(f"  mp3val fixed issues for {filepath}.")
    print(f"  mp3val OK: {filepath}")
    return True

def check_ffmpeg_decode(filepath):
    """Checks for ffmpeg decoding errors. Returns True if OK, False if errors."""
    print(f"  Running ffmpeg decode check...")
    # We are interested in any output to stderr from `ffmpeg -v error`
    _stdout, stderr, returncode = run_command(
        ["ffmpeg", "-v", "error", "-i", filepath, "-f", "null", "-"]
    )
    if returncode != 0 or stderr.strip(): # ffmpeg -v error sends errors to stderr
        print(f"  ffmpeg decode error for {filepath}. Return code: {returncode}")
        if stderr.strip(): print(f"  ffmpeg stderr:\n{stderr.strip()}")
        return False
    print(f"  ffmpeg decode OK: {filepath}")
    return True

def get_silence_at_end_info(filepath):
    """
    Detects silence at the end of a track.
    Returns a dictionary with silence details if found and qualifying, else None.
    """
    print(f"  Detecting silence for {filepath}...")
    cmd = [
        "ffmpeg", "-i", filepath,
        "-af", f"silencedetect=n={SILENCE_THRESHOLD_DB}:d={MIN_SILENCE_DETECT_DURATION}",
        "-f", "null", "-"
    ]
    _stdout, stderr, returncode = run_command(cmd)

    if returncode != 0 and not ("partial file" in stderr.lower() and "Consider increasing probe size" in stderr):
         # Sometimes ffmpeg finishes with return code 1 on success for -f null if it encounters EOF early,
         # but still processes fully for silencedetect. Only fail if stderr indicates a real issue
         # or returncode is non-zero without a clear silencedetect output.
         # A common case is if ffmpeg finishes processing and "conversion stopped" appears.
         # We need to see if silence was actually detected.
         pass # Continue to parse stderr even if returncode is 1, as silencedetect info might be there.


    track_duration_s = None
    duration_match = re.search(r"Duration: (\d{2}):(\d{2}):(\d{2})\.(\d{2,3})", stderr)
    if duration_match:
        h, m, s, ms_str = duration_match.groups()
        ms = int(ms_str.ljust(3, '0')) # Pad to 3 digits for ms if needed
        track_duration_s = int(h) * 3600 + int(m) * 60 + int(s) + ms / 1000.0
    
    if track_duration_s is None:
        print(f"  Could not determine track duration for {filepath}. stderr: {stderr[:500]}")
        return None

    detected_silences = []
    current_start = None
    for line in stderr.splitlines():
        start_match = re.search(r"\[silencedetect .*\] silence_start: ([\d\.]+)", line)
        if start_match:
            current_start = float(start_match.group(1))
        
        end_match = re.search(r"\[silencedetect .*\] silence_end: ([\d\.]+) \| silence_duration: ([\d\.]+)", line)
        if end_match and current_start is not None:
            s_end = float(end_match.group(1))
            s_duration = float(end_match.group(2))
            detected_silences.append({"start": current_start, "end": s_end, "duration": s_duration})
            current_start = None # Reset for the next potential silence block

    if not detected_silences:
        print(f"  No silence blocks detected by ffmpeg for {filepath}")
        return None

    qualifying_silence_at_end = None
    for silence in detected_silences:
        # Check if the silence block ends very close to the track's end
        # and the silence duration is significant enough to trim
        if (track_duration_s - silence["end"]) < END_OF_TRACK_TOLERANCE and \
           silence["duration"] >= MIN_SILENCE_DURATION_TO_TRIM:
            # If multiple such blocks, pick the one that ends latest (closest to track end)
            if qualifying_silence_at_end is None or silence["end"] > qualifying_silence_at_end["end"]:
                qualifying_silence_at_end = silence
    
    if qualifying_silence_at_end:
        print(f"  Found qualifying silence at end: start={qualifying_silence_at_end['start']:.2f}s, "
              f"end={qualifying_silence_at_end['end']:.2f}s, duration={qualifying_silence_at_end['duration']:.2f}s. "
              f"Track duration: {track_duration_s:.2f}s")
        return qualifying_silence_at_end
    else:
        print(f"  No silence at the end met trimming criteria for {filepath}")
        return None


def trim_silence_and_replace(filepath):
    """Trims silence from the end of the file and replaces the original."""
    print(f"  Attempting to trim silence from {filepath}...")
    temp_filepath = filepath + ".trimmed_temp.mp3"
    
    # Using -map_metadata 0 to copy all metadata from input to output
    # Using -id3v2_version 3 to ensure broader compatibility for ID3 tags.
    # Using -q:a 0 for LAME encoder's highest quality VBR.
    cmd = [
        "ffmpeg", "-i", filepath,
        "-af", f"areverse,silenceremove=start_periods=1:start_threshold={SILENCE_THRESHOLD_DB},areverse",
        "-c:a", "libmp3lame", # Explicitly use libmp3lame
        "-q:a", "0",
        "-map_metadata", "0",
        "-id3v2_version", "3", 
        "-y", # Overwrite temp_filepath if it exists
        temp_filepath
    ]
    
    _stdout, stderr, returncode = run_command(cmd)

    if returncode != 0:
        print(f"  ERROR: ffmpeg trimming failed for {filepath}. Return code: {returncode}")
        if stderr: print(f"  ffmpeg stderr:\n{stderr.strip()}")
        if os.path.exists(temp_filepath):
            try: os.remove(temp_filepath)
            except OSError: pass
        return False

    if not os.path.exists(temp_filepath) or os.path.getsize(temp_filepath) == 0:
        print(f"  ERROR: Trimmed file {temp_filepath} not created or is empty.")
        if stderr: print(f"  ffmpeg stderr during trimming:\n{stderr.strip()}")
        if os.path.exists(temp_filepath):
            try: os.remove(temp_filepath)
            except OSError: pass
        return False

    try:
        shutil.move(temp_filepath, filepath)
        print(f"  Successfully trimmed and replaced {filepath}")
        return True
    except Exception as e:
        print(f"  ERROR: Failed to replace {filepath} with {temp_filepath}. Error: {e}")
        if os.path.exists(temp_filepath): # Attempt to clean up temp file
             try: os.remove(temp_filepath)
             except OSError: pass
        return False

def process_music_library(root_dir):
    """Processes all MP3 files in the given root directory."""
    print(f"Starting processing for directory: {root_dir}")
    processed_files = 0
    trimmed_files = 0
    error_files = 0

    for subdir, _dirs, files in os.walk(root_dir):
        for filename in files:
            if filename.lower().endswith(".mp3") and not filename.lower().endswith(".trimmed_temp.mp3"):
                filepath = os.path.join(subdir, filename)
                print(f"\n>>> Processing file: {filepath}")
                processed_files += 1
                
                is_corrupt_or_decode_error = False
                if not check_mp3val(filepath):
                    print(f"  Skipping {filepath} due to mp3val issues.")
                    is_corrupt_or_decode_error = True
                
                if not is_corrupt_or_decode_error and not check_ffmpeg_decode(filepath):
                    print(f"  Skipping {filepath} due to ffmpeg decode issues.")
                    is_corrupt_or_decode_error = True

                if is_corrupt_or_decode_error:
                    error_files +=1
                    continue # Skip to next file

                silence_info = get_silence_at_end_info(filepath)
                if silence_info:
                    if trim_silence_and_replace(filepath):
                        trimmed_files += 1
                    else:
                        error_files += 1 # Count as error if trim fails
                else:
                    print(f"  No qualifying silence to trim for {filepath}.")
    
    print(f"\n--- Processing Summary ---")
    print(f"Total MP3 files processed: {processed_files}")
    print(f"Files trimmed: {trimmed_files}")
    print(f"Files skipped or failed due to errors/trim failure: {error_files}")
    print(f"------------------------")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process MP3 files to check for errors and trim trailing silence.")
    parser.add_argument("music_directory", help="The root directory of the music library to process.")
    parser.add_argument("-y", "--yes", action="store_true", help="Automatically confirm and proceed without interactive prompt.")
    args = parser.parse_args()

    # Ensure the provided path is absolute, as os.walk might behave unexpectedly with relative paths
    # if the script is called from a different directory than the target.
    music_root_to_process = os.path.abspath(args.music_directory)

    if not os.path.isdir(music_root_to_process):
        print(f"ERROR: The specified music directory does not exist or is not a directory: {music_root_to_process}")
        sys.exit(1)

    print("IMPORTANT: This script will attempt to overwrite MP3 files if trimming is applied.")
    print(f"Ensure you have THOROUGHLY BACKED UP your music folder: {music_root_to_process}")
    
    if args.yes or not sys.stdin.isatty():
        print(f"'-y' flag detected or non-interactive mode. Proceeding automatically for directory: {music_root_to_process}")
        process_music_library(music_root_to_process)
    else:
        confirm = input(f"Type 'YES' (all caps) to proceed for directory '{music_root_to_process}': ")
        if confirm == "YES":
            process_music_library(music_root_to_process)
        else:
            print("Operation cancelled by user.") 