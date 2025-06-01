#!/usr/bin/env python3

import os
import shutil
import eyed3
import argparse
from pathlib import Path

def move_complete_metadata_files(source_dir: str, dest_dir: str):
    """
    Moves MP3 files with complete metadata (title, artist, and album) to a destination directory.
    
    Args:
        source_dir: Source directory containing MP3 files
        dest_dir: Destination directory for files with complete metadata
    """
    source_path = Path(source_dir)
    dest_path = Path(dest_dir)
    
    if not source_path.is_dir():
        print(f"Error: Source directory not found: {source_dir}")
        return
        
    # Create destination directory if it doesn't exist
    dest_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Scanning MP3 files in: {source_path}")
    print(f"Moving files with complete metadata to: {dest_path}\n")
    
    total_files = 0
    moved_files = 0
    
    for mp3_file in source_path.rglob("*.mp3"):
        total_files += 1
        try:
            audiofile = eyed3.load(mp3_file)
            if audiofile is None or audiofile.tag is None:
                continue
                
            # Check if all required metadata is present and not empty
            if (audiofile.tag.title and 
                audiofile.tag.artist and 
                audiofile.tag.album):
                
                # Create destination path
                dest_file = dest_path / mp3_file.name
                
                # Move the file
                shutil.move(str(mp3_file), str(dest_file))
                print(f"Moved: {mp3_file.name}")
                print(f"  Title: {audiofile.tag.title}")
                print(f"  Artist: {audiofile.tag.artist}")
                print(f"  Album: {audiofile.tag.album}\n")
                moved_files += 1
                
        except Exception as e:
            print(f"Error processing {mp3_file.name}: {str(e)}")
    
    print(f"\n--- Summary ---")
    print(f"Total MP3 files scanned: {total_files}")
    print(f"Files moved: {moved_files}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Move MP3 files with complete metadata to a destination folder.')
    parser.add_argument('source', help='Source directory containing MP3 files')
    parser.add_argument('destination', help='Destination directory for files with complete metadata')
    args = parser.parse_args()
    
    move_complete_metadata_files(args.source, args.destination) 