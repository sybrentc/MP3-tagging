#!/usr/bin/env python3

import os
import sys
import eyed3
from eyed3.id3 import Tag

def set_track_numbers(directory):
    """
    Set track numbers and total tracks for all MP3 files in the directory.
    Track numbers are extracted from the first two digits of the filename.
    """
    # Get all MP3 files and sort them
    mp3_files = [f for f in os.listdir(directory) if f.lower().endswith('.mp3')]
    mp3_files.sort()
    
    if not mp3_files:
        print(f"No MP3 files found in {directory}")
        return
    
    total_tracks = len(mp3_files)
    print(f"Found {total_tracks} MP3 files")
    
    # Process each file
    for filename in mp3_files:
        filepath = os.path.join(directory, filename)
        
        # Extract track number from filename (first two digits)
        try:
            track_num = int(filename[:2])
        except ValueError:
            print(f"Warning: Could not extract track number from {filename}, skipping...")
            continue
        
        # Load the audio file
        audiofile = eyed3.load(filepath)
        if not audiofile:
            print(f"Warning: Could not load {filename}, skipping...")
            continue
        
        # Initialize tag if it doesn't exist
        if not audiofile.tag:
            audiofile.tag = Tag()
        
        # Set track number and total tracks
        audiofile.tag.track_num = (track_num, total_tracks)
        
        # Save changes
        try:
            audiofile.tag.save()
            print(f"Updated track number for {filename}: {track_num}/{total_tracks}")
        except Exception as e:
            print(f"Error saving {filename}: {str(e)}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python set_track_numbers.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory")
        sys.exit(1)
    
    set_track_numbers(directory)

if __name__ == "__main__":
    main() 