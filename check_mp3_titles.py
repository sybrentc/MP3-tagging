#!/usr/bin/env python3

import os
import sys
import subprocess
from pathlib import Path

def show_mp3_metadata(music_directory):
    """
    Shows all ID3 metadata for MP3 files in a directory.

    Args:
        music_directory (str): The directory containing MP3 files.
    """
    music_path = Path(music_directory)
    if not music_path.is_dir():
        print(f"Error: Directory not found: {music_directory}")
        return

    total_files = 0

    print(f"Scanning MP3 files in: {music_path}\n")

    for mp3_file_path in music_path.rglob("*.mp3"):
        total_files += 1
        print(f"\n=== {mp3_file_path.name} ===")
        try:
            # Run eyeD3 command and capture output
            result = subprocess.run(['eyeD3', str(mp3_file_path)], 
                                 capture_output=True, 
                                 text=True)
            print(result.stdout)
            if result.stderr:
                print("Errors/Warnings:", result.stderr)
        except Exception as e:
            print(f"Error processing {mp3_file_path.name}: {str(e)}")

    print(f"\n--- Summary ---")
    print(f"Total MP3 files processed: {total_files}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_mp3_titles.py <music_directory>")
        sys.exit(1)

    directory_to_scan = sys.argv[1]
    show_mp3_metadata(directory_to_scan) 