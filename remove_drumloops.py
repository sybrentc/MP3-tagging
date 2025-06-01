#!/usr/bin/env python3

import os
import sys
import eyed3
from pathlib import Path

def remove_drumloops(directory):
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
    
    removed_count = 0
    skipped_count = 0
    
    for mp3_file in mp3_files:
        try:
            # Load the audio file
            audiofile = eyed3.load(mp3_file)
            
            if audiofile is None or audiofile.tag is None:
                print(f"Skipping {mp3_file.name}: No ID3 tags found")
                skipped_count += 1
                continue
            
            # Check if album is 'Drumloops'
            if audiofile.tag.album and audiofile.tag.album == "Drumloops":
                try:
                    mp3_file.unlink()  # Delete the file
                    print(f"Removed: {mp3_file.name}")
                    removed_count += 1
                except Exception as e:
                    print(f"Error removing {mp3_file.name}: {str(e)}")
                    skipped_count += 1
            else:
                print(f"Skipping {mp3_file.name}: Not a Drumloops file")
                skipped_count += 1
                
        except Exception as e:
            print(f"Error processing {mp3_file.name}: {str(e)}")
            skipped_count += 1
    
    print(f"\nSummary:")
    print(f"Files removed: {removed_count}")
    print(f"Files skipped: {skipped_count}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python remove_drumloops.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    remove_drumloops(directory) 