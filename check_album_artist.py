import os
import eyed3
import sys
from pathlib import Path

def check_album_artists(directory):
    mp3_files = []
    files_with_album_artist = []
    
    # Walk through directory
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.mp3'):
                full_path = os.path.join(root, file)
                mp3_files.append(full_path)
                
                # Load the audio file
                audiofile = eyed3.load(full_path)
                if audiofile and audiofile.tag:
                    if audiofile.tag.album_artist:
                        files_with_album_artist.append((full_path, audiofile.tag.album_artist))
    
    # Print results
    print(f"\nTotal MP3 files found: {len(mp3_files)}")
    print(f"Files with album artist tag: {len(files_with_album_artist)}")
    print("\nFiles with album artist tag:")
    for path, artist in files_with_album_artist:
        print(f"{os.path.basename(path)}: {artist}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_album_artist.py <directory_path>")
        sys.exit(1)
    
    directory = sys.argv[1]
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist")
        sys.exit(1)
        
    check_album_artists(directory) 