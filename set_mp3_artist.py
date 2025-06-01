import argparse
import pathlib
import eyed3

def set_artist_for_mp3s(directory_path: str, artist_name: str):
    """
    Scans a directory for MP3 files and sets their artist metadata.

    Args:
        directory_path: The path to the directory to scan.
        artist_name: The name to set as the artist for the MP3 files.
    """
    source_dir = pathlib.Path(directory_path)
    if not source_dir.is_dir():
        print(f"Error: '{directory_path}' is not a valid directory.")
        return

    print(f"Scanning for MP3 files in '{source_dir.resolve()}' to set artist to '{artist_name}'...")
    mp3_files_found = 0
    mp3_files_updated = 0

    for file_path in source_dir.rglob("*.mp3"):
        mp3_files_found += 1
        try:
            audiofile = eyed3.load(file_path)
            if audiofile is None:
                print(f"Warning: Could not load MP3 file: {file_path}")
                continue
            
            if audiofile.tag is None:
                audiofile.initTag(version=eyed3.id3.ID3_V2_3)
                if audiofile.tag is None:
                    print(f"Warning: Could not initialize or load tag for: {file_path}")
                    continue
            
            audiofile.tag.artist = artist_name
            audiofile.tag.save(version=eyed3.id3.ID3_V2_3, encoding='utf-8')
            print(f"Updated artist for '{file_path.name}' to '{artist_name}'")
            mp3_files_updated += 1

        except Exception as e:
            print(f"Error processing file {file_path.name}: {e}")

    print(f"\n--- Summary ---")
    print(f"Total MP3 files found: {mp3_files_found}")
    print(f"MP3 files updated with artist '{artist_name}': {mp3_files_updated}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Set MP3 artist metadata for all files in a directory."
    )
    parser.add_argument(
        "directory",
        type=str,
        help="The directory containing MP3 files to process.",
    )
    parser.add_argument(
        "artist_name",
        type=str,
        help="The artist name to set for the MP3 files.",
    )
    args = parser.parse_args()

    set_artist_for_mp3s(args.directory, args.artist_name) 