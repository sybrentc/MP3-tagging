import os
import subprocess
import sys
import argparse

def find_mp3s_without_title(music_folder):
    """
    Finds all MP3 files in the given folder and its subfolders
    that do not have a title ID3 tag.

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
                    is_title_missing = True
                    for line_num, line in enumerate(output.splitlines()):
                        if line.startswith("title:"):
                            title_value_part = line.split("title:", 1)[1]
                            stripped_title_value = title_value_part.strip()
                            
                            if stripped_title_value and stripped_title_value != "None":
                                is_title_missing = False
                                break 
                    
                    if is_title_missing:
                        print(filepath)

                except subprocess.CalledProcessError as e:
                    if "No ID3 v1.x/v2.x tag found!" in e.stdout or "Tag read failed" in e.stdout:
                         print(filepath) 
                    else:
                        print(f"Error processing {filepath} with eyeD3: {e.stderr or e.stdout}", file=sys.stderr)
                except FileNotFoundError:
                    print("Error: eyeD3 command not found. Please ensure it's installed and in your PATH.", file=sys.stderr)
                    sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find MP3 files without a title ID3 tag.")
    parser.add_argument(
        "music_folder",
        nargs="?", 
        default="~/Desktop/Music/", 
        help="The path to the music folder to scan. Defaults to ~/Desktop/Music/"
    )
    args = parser.parse_args()
    music_directory = os.path.expanduser(args.music_folder)
    find_mp3s_without_title(music_directory) 