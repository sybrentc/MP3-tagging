import os
import eyed3
import sys
from pathlib import Path

def set_album_artist(directory, album_artist):
    """
    Sets the album artist tag for all MP3 files in the specified directory.
    Ensures ID3 v2.4 is used for compatibility.
    
    Args:
        directory: The directory containing MP3 files
        album_artist: The album artist to set
    """
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist")
        return

    print(f"Scanning for MP3 files in '{directory}' to set album artist to '{album_artist}'...")
    mp3_files_found = 0
    mp3_files_updated = 0
    mp3_files_failed = 0

    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.mp3'):
                full_path = os.path.join(root, file)
                mp3_files_found += 1
                
                try:
                    audiofile = eyed3.load(full_path)
                    if audiofile is None:
                        audiofile = eyed3.File(full_path)
                        audiofile.initTag()
                    
                    # Ensure we're using ID3 v2.4
                    if audiofile.tag is None:
                        audiofile.initTag()
                    audiofile.tag.version = (2, 4, 0)  # Set to ID3 v2.4
                    
                    audiofile.tag.album_artist = album_artist
                    audiofile.tag.save(version=(2, 4, 0), encoding='utf-8')  # Explicitly save as v2.4 and utf-8
                    print(f"Updated album artist for '{file}' to '{album_artist}'")
                    mp3_files_updated += 1
                except Exception as e:
                    print(f"Error processing {file}: {e}")
                    mp3_files_failed += 1

    print(f"\n--- Summary ---")
    print(f"Total MP3 files found: {mp3_files_found}")
    print(f"MP3 files updated with album artist '{album_artist}': {mp3_files_updated}")
    if mp3_files_failed > 0:
        print(f"MP3 files that failed to update: {mp3_files_failed}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python set_mp3_album_artist.py <directory_path> <album_artist>")
        sys.exit(1)
    
    directory = sys.argv[1]
    album_artist = sys.argv[2]
    set_album_artist(directory, album_artist) 