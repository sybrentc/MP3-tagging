import os
import subprocess
import sys
import argparse

def find_mp3s_without_album(music_folder):
    """
    Finds all MP3 files in the given folder and its subfolders
    that do not have an album ID3 tag.

    Args:
        music_folder (str): The path to the music folder.
    """
    music_folder = os.path.abspath(os.path.expanduser(music_folder))

    if not os.path.isdir(music_folder):
        print(f"Error: Directory not found: {music_folder}", file=sys.stderr)
        sys.exit(1)

    for root, _, files in os.walk(music_folder):
        for file in files:
            if file.lower().endswith(".mp3"):
                filepath = os.path.join(root, file)
                try:
                    result = subprocess.run(
                        ["eyeD3", "--no-color", filepath],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    output = result.stdout
                    is_album_missing = True
                    for line_num, line in enumerate(output.splitlines()):
                        if line.startswith("album:"): # Changed from artist:
                            album_value_part = line.split("album:", 1)[1] # Changed from artist:
                            stripped_album_value = album_value_part.strip()
                            
                            if stripped_album_value and stripped_album_value != "None":
                                is_album_missing = False
                                break 
                    
                    if is_album_missing:
                        print(filepath)

                except subprocess.CalledProcessError as e:
                    # If eyeD3 exits with an error, but the error indicates no tag was found,
                    # we consider the album missing.
                    if "No ID3 v1.x/v2.x tag found!" in e.stdout or "Tag read failed" in e.stdout:
                         print(filepath) 
                    else:
                        # For other eyeD3 errors, print them to stderr.
                        print(f"Error processing {filepath} with eyeD3: {e.stderr or e.stdout}", file=sys.stderr)
                except FileNotFoundError:
                    print("Error: eyeD3 command not found. Please ensure it's installed and in your PATH.", file=sys.stderr)
                    sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find MP3 files without an album ID3 tag.") # Changed description
    parser.add_argument(
        "music_folder",
        nargs="?", 
        default="~/Desktop/Music/", 
        help="The path to the music folder to scan. Defaults to ~/Desktop/Music/"
    )
    args = parser.parse_args()
    music_directory = os.path.expanduser(args.music_folder)
    find_mp3s_without_album(music_directory) # Changed function call 