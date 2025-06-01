import argparse
import pathlib
import eyed3

def set_titles_from_filenames(directory_path: str):
    """
    Scans a directory for MP3 files and sets their title metadata
    to their filename (without the .mp3 extension).

    Args:
        directory_path: The path to the directory to scan.
    """
    source_dir = pathlib.Path(directory_path)
    if not source_dir.is_dir():
        print(f"Error: '{directory_path}' is not a valid directory.")
        return

    print(f"Scanning for MP3 files in '{source_dir.resolve()}'...")
    mp3_files_found = 0
    mp3_files_updated = 0

    for file_path in source_dir.rglob("*.mp3"):
        mp3_files_found += 1
        try:
            audiofile = eyed3.load(file_path)
            if audiofile is None or audiofile.tag is None:
                # Attempt to initialize a tag if it doesn't exist
                if audiofile is None: # Should not happen if rglob found it
                    print(f"Warning: Could not load MP3 file: {file_path}")
                    continue
                audiofile.initTag(version=eyed3.id3.ID3_V2_3) # Or ID3_V2_4
                if audiofile.tag is None: # If still None, then skip
                    print(f"Warning: Could not initialize or load tag for: {file_path}")
                    continue
            
            # Get filename without extension
            new_title = file_path.stem
            
            # Set the title
            audiofile.tag.title = new_title
            audiofile.tag.save(version=eyed3.id3.ID3_V2_3, encoding='utf-8') # Explicitly save as v2.3
            print(f"Updated title for '{file_path.name}' to '{new_title}'")
            mp3_files_updated += 1

        except Exception as e:
            print(f"Error processing file {file_path.name}: {e}")

    print(f"\n--- Summary ---")
    print(f"Total MP3 files found: {mp3_files_found}")
    print(f"MP3 files updated: {mp3_files_updated}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Set MP3 title metadata from filenames (without .mp3 extension)."
    )
    parser.add_argument(
        "directory",
        type=str,
        help="The directory containing MP3 files to process.",
    )
    args = parser.parse_args()

    set_titles_from_filenames(args.directory) 