#!/usr/bin/env python3

import os
import sys
import eyed3
from pathlib import Path
import re

def sanitize_filename(filename):
    # Remove or replace characters that might cause issues in filenames
    # Keep spaces and basic punctuation, remove other special characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    return sanitized.strip()

def prefix_artist_to_filename(directory):
    # Convert directory to Path object
    dir_path = Path(directory)
    
    # Check if directory exists
    if not dir_path.exists():
        print(f"Error: Directory '{directory}' does not exist")
        return
    
    # Get all MP3 files in the directory
    mp3_files = list(dir_path.glob('*.mp3'))
    
    if not mp3_files:
        print(f"No MP3 files found in '{directory}'")
        return
    
    renamed_count = 0
    skipped_count = 0
    
    for mp3_file in mp3_files:
        try:
            # Load the audio file
            audiofile = eyed3.load(mp3_file)
            
            if audiofile is None or audiofile.tag is None:
                print(f"Skipping {mp3_file.name}: No ID3 tags found")
                skipped_count += 1
                continue
            
            # Get artist name
            artist = audiofile.tag.artist
            
            if not artist:
                print(f"Skipping {mp3_file.name}: No artist tag found")
                skipped_count += 1
                continue
            
            # Sanitize artist name
            artist = sanitize_filename(artist)
            
            # Create new filename
            new_name = f"{artist} - {mp3_file.name}"
            new_path = mp3_file.parent / new_name
            
            # Check if file with new name already exists
            if new_path.exists():
                print(f"Skipping {mp3_file.name}: File already exists with new name")
                skipped_count += 1
                continue
            
            # Rename the file
            mp3_file.rename(new_path)
            print(f"Renamed: {mp3_file.name} -> {new_name}")
            renamed_count += 1
                
        except Exception as e:
            print(f"Error processing {mp3_file.name}: {str(e)}")
            skipped_count += 1
    
    print(f"\nSummary:")
    print(f"Files renamed: {renamed_count}")
    print(f"Files skipped: {skipped_count}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python prefix_artist_to_filename.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    prefix_artist_to_filename(directory) 