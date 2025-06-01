#!/usr/bin/env python3

import os
import sys
import eyed3
from pathlib import Path
import shutil

def organize_mp3s(source_dir, target_dir, artist_name):
    """
    Organize MP3 files by moving files from a specific artist to a target directory.
    
    Args:
        source_dir (str): Source directory containing MP3 files
        target_dir (str): Target directory to move files to
        artist_name (str): Name of the artist to look for
    """
    # Create target directory if it doesn't exist
    os.makedirs(target_dir, exist_ok=True)
    
    # Convert to Path objects for better path handling
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    
    # Counter for moved files
    moved_count = 0
    
    # Walk through the source directory
    for mp3_file in source_path.rglob("*.mp3"):
        try:
            # Load the audio file
            audiofile = eyed3.load(mp3_file)
            
            if audiofile is None:
                print(f"Could not load {mp3_file}")
                continue
                
            # Get the artist name
            if audiofile.tag and audiofile.tag.artist:
                file_artist = audiofile.tag.artist
                
                # Check if this is the artist we're looking for
                if file_artist.lower() == artist_name.lower():
                    # Create the target file path
                    target_file = target_path / mp3_file.name
                    
                    # Move the file
                    print(f"Moving {mp3_file} to {target_file}")
                    shutil.move(str(mp3_file), str(target_file))
                    moved_count += 1
                    
        except Exception as e:
            print(f"Error processing {mp3_file}: {str(e)}")
    
    print(f"\nMoved {moved_count} files to {target_dir}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python organize_mp3s.py <source_directory> <target_directory> <artist_name>")
        sys.exit(1)
        
    source_dir = sys.argv[1]
    target_dir = sys.argv[2]
    artist_name = sys.argv[3]
    
    organize_mp3s(source_dir, target_dir, artist_name) 