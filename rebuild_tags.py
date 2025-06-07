import argparse
import os
import subprocess
import tempfile
import shutil
import json
from multiprocessing import Pool, cpu_count
from functools import partial

# Centralized, case-insensitive blacklist of metadata keys from ffprobe's output.
# These are the tags we want to check for and remove.
BLACKLISTED_TAG_KEYS = {'itunsmpb', 'itunnorm', 'itunpgap', 'itunes_cddb_1', 'itunes_cddb_tracknumber'}

def process_file(file_path, root_folder):
    """
    This is the main worker function that will be run in parallel.
    It takes a single file path, checks it, and sanitises it if needed.
    """
    # Print a relative path for cleaner output
    relative_path = os.path.relpath(file_path, root_folder)
    print(f"Processing: {relative_path}")

    if check_for_offending_tags(file_path, relative_path):
        sanitise_file(file_path, relative_path)
    else:
        print(f"  - File is clean. Skipping {relative_path}.")

def check_for_offending_tags(file_path, relative_path):
    """
    Uses ffprobe to quickly check if an MP3 file contains any of the
    blacklisted metadata tags.
    """
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', file_path],
            check=True, capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        if 'tags' in data.get('format', {}):
            for key in data['format']['tags']:
                if key.lower() in BLACKLISTED_TAG_KEYS:
                    print(f"  - Found offending tag '{key}' in {relative_path}. Needs sanitisation.")
                    return True
        # If we get here, no offending tags were found
        return False
    except Exception as e:
        print(f"  - Warning: Could not probe {relative_path} for tags: {e}")
        # Assume it's clean if we can't probe it, to be safe.
        return False

def sanitise_file(original_path, relative_path):
    """
    Sanitises a single MP3 file by re-encoding it to strip all embedded data,
    then reapplying a clean, filtered set of metadata.
    """
    print(f"  - Sanitising {relative_path}...")

    # 1. Extract all metadata with ffprobe
    metadata_args = []
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', original_path],
            check=True, capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        if 'tags' in data.get('format', {}):
            for key, value in data['format']['tags'].items():
                if key.lower() not in BLACKLISTED_TAG_KEYS:
                    metadata_args.extend(['-metadata', f'{key}={value}'])
            print(f"    - Preserving {len(metadata_args) // 2} metadata tags for {relative_path}.")
    except Exception as e:
        print(f"    - Warning: Could not extract metadata for {relative_path}: {e}")
        # We can still proceed to strip the file, it will just have no metadata.

    # 2. Re-encode the file using ffmpeg, applying the filtered metadata
    temp_fd, temp_path = tempfile.mkstemp(suffix='.mp3')
    os.close(temp_fd)
    try:
        command = [
            'ffmpeg', '-i', original_path,
            '-c:a', 'libmp3lame',  # Re-encode to guarantee a clean audio stream
            '-q:a', '2',             # VBR quality (0=highest, 9=lowest), a good compromise
            '-map_metadata', '-1',   # Strip all metadata from the source
            '-y'
        ]
        command.extend(metadata_args)  # Add back the preserved metadata
        command.append(temp_path)
        
        subprocess.run(command, check=True, capture_output=True, text=True)
        
        shutil.move(temp_path, original_path)
        print(f"    - Successfully sanitised {relative_path}.")
        return True

    except subprocess.CalledProcessError as e:
        print(f"    - Error during ffmpeg sanitisation: {e.stderr}")
    except Exception as e:
        print(f"    - An unexpected error occurred: {e}")
    
    # Cleanup on failure
    if os.path.exists(temp_path):
        os.remove(temp_path)
    return False

def main():
    """
    Main function to set up argument parsing, find files, and
    kick off the parallel processing.
    """
    parser = argparse.ArgumentParser(
        description='Conditionally and in parallel rebuilds MP3s using ffmpeg if they contain blacklisted tags.'
    )
    parser.add_argument('folder_path', type=str, help='The folder of MP3s to process.')
    args = parser.parse_args()

    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        print("Error: This script requires both 'ffmpeg' and 'ffprobe'.")
        print("Please install them and ensure they are in your PATH.")
        return

    if not os.path.isdir(args.folder_path):
        print(f"Error: Directory not found at '{args.folder_path}'")
        return

    # 1. Find all MP3 files first
    mp3_files = []
    for root, _, files in os.walk(args.folder_path):
        for filename in files:
            if filename.lower().endswith('.mp3'):
                mp3_files.append(os.path.join(root, filename))

    if not mp3_files:
        print("No MP3 files found in the specified directory.")
        return
    
    print(f"Found {len(mp3_files)} MP3 file(s). Starting parallel processing...")

    # 2. Use a process pool to run the checks and conversions in parallel
    # We use cpu_count() to automatically use all available cores.
    num_processes = cpu_count()
    print(f"Using {num_processes} processes.")
    
    # We use partial to "pre-fill" the root_folder argument of process_file,
    # since the pool iterator only passes a single argument (the file path).
    worker_func = partial(process_file, root_folder=args.folder_path)
    
    with Pool(processes=num_processes) as pool:
        # map will distribute the mp3_files list among the worker processes
        # and block until all are complete.
        pool.map(worker_func, sorted(mp3_files))
        
    print("\nProcessing complete.")


if __name__ == '__main__':
    main() 