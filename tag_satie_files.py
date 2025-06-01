#!/usr/bin/env python3

import os
import sys
import eyed3
from pathlib import Path

def tag_satie_files(directory):
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
    
    tagged_count = 0
    skipped_count = 0
    
    for mp3_file in mp3_files:
        try:
            # Only process Erik Satie files
            if not mp3_file.name.startswith("Erik Satie"):
                continue
                
            # Load the audio file
            audiofile = eyed3.load(mp3_file)
            
            if audiofile is None:
                print(f"Skipping {mp3_file.name}: Could not load file")
                skipped_count += 1
                continue
            
            # Create new tag if none exists
            if audiofile.tag is None:
                audiofile.tag = eyed3.id3.Tag()
                audiofile.tag.version = (2, 3, 0)  # Use ID3 v2.3
            
            # Set artist
            audiofile.tag.artist = "Erik Satie"
            
            # Set album
            audiofile.tag.album = "Trois Morceaux en Forme de Poire"
            
            # Extract title from filename
            # Format: "Erik Satie - Trois Morceaux en Forme de Poire - [title].mp3"
            title = mp3_file.stem.split(" - ")[-1]
            audiofile.tag.title = title
            
            # Save the tag
            audiofile.tag.save(version=(2, 3, 0))  # Force ID3 v2.3
            print(f"Tagged: {mp3_file.name}")
            tagged_count += 1
                
        except Exception as e:
            print(f"Error processing {mp3_file.name}: {str(e)}")
            skipped_count += 1
    
    print(f"\nSummary:")
    print(f"Files tagged: {tagged_count}")
    print(f"Files skipped: {skipped_count}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python tag_satie_files.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    tag_satie_files(directory) 