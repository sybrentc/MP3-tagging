import argparse
import os
import subprocess
import tempfile
import shutil
import json

# Centralized, case-insensitive blacklist of metadata keys from ffprobe's output.
# These are the tags we want to check for and remove.
BLACKLISTED_TAG_KEYS = {'itunsmpb', 'itunnorm', 'itunpgap', 'itunes_cddb_1', 'itunes_cddb_tracknumber'}

def check_for_offending_tags(file_path):
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
                    print(f"  - Found offending tag: '{key}'. File needs sanitisation.")
                    return True
        # If we get here, no offending tags were found
        return False
    except Exception as e:
        print(f"  - Warning: Could not probe file {os.path.basename(file_path)} for tags: {e}")
        # Assume it's clean if we can't probe it, to be safe.
        return False

def sanitise_file(original_path):
    """
    Sanitises a single MP3 file by re-encoding it to strip all embedded data,
    then reapplying a clean, filtered set of metadata.
    """
    print(f"  - Sanitising {os.path.basename(original_path)}...")

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
            print(f"    - Preserving {len(metadata_args) // 2} metadata tags.")
    except Exception as e:
        print(f"    - Warning: Could not extract metadata for {os.path.basename(original_path)}: {e}")
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
        print(f"    - Successfully sanitised {os.path.basename(original_path)}.")
        return True

    except subprocess.CalledProcessError as e:
        print(f"    - Error during ffmpeg sanitisation: {e.stderr}")
    except Exception as e:
        print(f"    - An unexpected error occurred: {e}")
    
    # Cleanup on failure
    if os.path.exists(temp_path):
        os.remove(temp_path)
    return False

def process_directory(folder_path):
    """
    Recursively scans a directory for MP3 files, checks for offending tags,
    and sanitises them only if needed.
    """
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        print("Error: This script requires both 'ffmpeg' and 'ffprobe'.")
        print("Please install them and ensure they are in your PATH.")
        return

    for root, _, files in os.walk(folder_path):
        for filename in sorted(files):
            if not filename.lower().endswith('.mp3'):
                continue

            file_path = os.path.join(root, filename)
            print(f"Processing: {filename}")

            if check_for_offending_tags(file_path):
                sanitise_file(file_path)
            else:
                print("  - File is clean. Skipping.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Conditionally rebuilds MP3 files using ffmpeg if they contain blacklisted tags.'
    )
    parser.add_argument('folder_path', type=str, help='The folder of MP3s to process.')
    args = parser.parse_args()
    if os.path.isdir(args.folder_path):
        process_directory(args.folder_path)
    else:
        print(f"Error: Directory not found at '{args.folder_path}'") 