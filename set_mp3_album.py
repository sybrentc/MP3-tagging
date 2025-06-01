import argparse
import pathlib
import eyed3

def set_album_for_mp3s(directory_path: str, album_name: str):
    """
    Scans a directory for MP3 files and sets their album metadata.

    Args:
        directory_path: The path to the directory to scan.
        album_name: The name to set as the album for the MP3 files.
    """
    source_dir = pathlib.Path(directory_path)
    if not source_dir.is_dir():
        print(f"Error: '{directory_path}' is not a valid directory.")
        return

    print(f"Scanning for MP3 files in '{source_dir.resolve()}' to set album to '{album_name}'...")
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
            
            audiofile.tag.album = album_name
            audiofile.tag.save(version=eyed3.id3.ID3_V2_3, encoding='utf-8')
            print(f"Updated album for '{file_path.name}' to '{album_name}'")
            mp3_files_updated += 1

        except Exception as e:
            print(f"Error processing file {file_path.name}: {e}")

    print(f"\n--- Summary ---")
    print(f"Total MP3 files found: {mp3_files_found}")
    print(f"MP3 files updated with album '{album_name}': {mp3_files_updated}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Set MP3 album metadata for all files in a directory."
    )
    parser.add_argument(
        "directory",
        type=str,
        help="The directory containing MP3 files to process.",
    )
    parser.add_argument(
        "album_name",
        type=str,
        help="The album name to set for the MP3 files.",
    )
    args = parser.parse_args()

    set_album_for_mp3s(args.directory, args.album_name) 