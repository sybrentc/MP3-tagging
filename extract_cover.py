import os
import sys
import subprocess
import eyed3
from pathlib import Path

def extract_cover(mp3_path):
    """
    Extracts cover art from an MP3 file and saves it with a filename based on artist and album.
    
    Args:
        mp3_path: Path to the MP3 file
    """
    if not os.path.exists(mp3_path):
        print(f"Error: File '{mp3_path}' does not exist")
        return False
        
    if not mp3_path.lower().endswith('.mp3'):
        print(f"Error: '{mp3_path}' is not an MP3 file")
        return False
    
    try:
        # Get artist and album from metadata
        audiofile = eyed3.load(mp3_path)
        if audiofile is None or audiofile.tag is None:
            print(f"Error: Could not load metadata from {mp3_path}")
            return False
            
        artist = audiofile.tag.artist or "Unknown"
        album = audiofile.tag.album or "Unknown"
        
        # Create filename from artist and album
        filename = f"{artist}-{album}.jpg"
        # Replace invalid filename characters
        filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.'))
        filename = filename.replace(' ', '_')
        
        # Get the current directory for saving the cover
        current_dir = os.getcwd()
        output_path = os.path.join(current_dir, filename)
        
        # Run ffmpeg command
        cmd = ['ffmpeg', '-i', mp3_path, '-an', '-vcodec', 'copy', output_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Successfully extracted cover art to {output_path}")
            return True
        else:
            print(f"Error extracting cover art: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_cover.py <mp3_file_path>")
        sys.exit(1)
    
    mp3_path = sys.argv[1]
    success = extract_cover(mp3_path)
    sys.exit(0 if success else 1) 