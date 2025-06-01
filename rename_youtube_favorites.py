#!/usr/bin/env python3

import os
import sys
import eyed3
from pathlib import Path

def sanitize_filename(filename):
    # Replace invalid filename characters with underscores
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def rename_youtube_favorites(directory):
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
            
            # Check if album is "Youtube Favourites"
            if audiofile.tag.album and audiofile.tag.album == "Youtube Favourites":
                if audiofile.tag.title:
                    # Create new filename from title
                    new_name = sanitize_filename(audiofile.tag.title) + '.mp3'
                    new_path = mp3_file.parent / new_name
                    
                    # Skip if filename would be the same
                    if new_path == mp3_file:
                        print(f"Skipping {mp3_file.name}: Already correctly named")
                        skipped_count += 1
                        continue
                    
                    # Rename the file
                    try:
                        mp3_file.rename(new_path)
                        print(f"Renamed: {mp3_file.name} -> {new_name}")
                        renamed_count += 1
                    except Exception as e:
                        print(f"Error renaming {mp3_file.name}: {str(e)}")
                        skipped_count += 1
                else:
                    print(f"Skipping {mp3_file.name}: No title tag found")
                    skipped_count += 1
            else:
                print(f"Skipping {mp3_file.name}: Not a Youtube Favourites file")
                skipped_count += 1
                
        except Exception as e:
            print(f"Error processing {mp3_file.name}: {str(e)}")
            skipped_count += 1
    
    print(f"\nSummary:")
    print(f"Files renamed: {renamed_count}")
    print(f"Files skipped: {skipped_count}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 rename_youtube_favorites.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    rename_youtube_favorites(directory) 