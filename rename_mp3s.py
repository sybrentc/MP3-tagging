#!/usr/bin/env python3

import os
import eyed3
import argparse
from pathlib import Path
import re

def sanitize_filename(filename):
    """
    Sanitize the filename by removing or replacing invalid characters.
    """
    # Replace invalid characters with underscores
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip('. ')
    return sanitized

def rename_mp3s(directory: str):
    """
    Renames MP3 files in the given directory using their ID3 metadata.
    Format: [album artist] - [title].mp3
    
    Args:
        directory: Directory containing MP3 files to rename
    """
    dir_path = Path(directory)
    
    if not dir_path.is_dir():
        print(f"Error: Directory not found: {directory}")
        return
    
    print(f"Scanning MP3 files in: {dir_path}\n")
    
    total_files = 0
    renamed_files = 0
    skipped_files = 0
    
    for mp3_file in dir_path.glob("*.mp3"):
        total_files += 1
        try:
            audiofile = eyed3.load(mp3_file)
            if audiofile is None or audiofile.tag is None:
                print(f"Skipped {mp3_file.name}: No ID3 tag found")
                skipped_files += 1
                continue
            
            if not audiofile.tag.album_artist or not audiofile.tag.title:
                print(f"Skipped {mp3_file.name}: Missing album artist or title metadata")
                skipped_files += 1
                continue
            
            # Create new filename
            album_artist = sanitize_filename(audiofile.tag.album_artist)
            title = sanitize_filename(audiofile.tag.title)
            new_name = f"{album_artist} - {title}.mp3"
            
            # Skip if the filename is already in the correct format
            if mp3_file.name == new_name:
                print(f"Skipped {mp3_file.name}: Already in correct format")
                skipped_files += 1
                continue
            
            # Create new path
            new_path = mp3_file.parent / new_name
            
            # Check if a file with the new name already exists
            if new_path.exists():
                print(f"Skipped {mp3_file.name}: A file with the new name already exists")
                skipped_files += 1
                continue
            
            # Rename the file
            mp3_file.rename(new_path)
            print(f"Renamed: {mp3_file.name} -> {new_name}")
            renamed_files += 1
            
        except Exception as e:
            print(f"Error processing {mp3_file.name}: {str(e)}")
            skipped_files += 1
    
    print(f"\n--- Summary ---")
    print(f"Total MP3 files scanned: {total_files}")
    print(f"Files renamed: {renamed_files}")
    print(f"Files skipped: {skipped_files}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Rename MP3 files using their ID3 metadata.')
    parser.add_argument('directory', help='Directory containing MP3 files to rename')
    args = parser.parse_args()
    
    rename_mp3s(args.directory) 