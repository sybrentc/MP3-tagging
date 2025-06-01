import argparse
import pathlib
import eyed3

def verify_metadata(directory_path: str, expected_album: str, expected_album_artist: str):
    """
    Verifies the album and album artist tags for all MP3 files in a directory.
    """
    source_dir = pathlib.Path(directory_path)
    if not source_dir.is_dir():
        print(f"Error: '{directory_path}' is not a valid directory.")
        return

    print(f"Verifying metadata in '{source_dir.resolve()}'...")
    print(f"Expected Album: '{expected_album}'")
    print(f"Expected Album Artist: '{expected_album_artist}'")
    print("-" * 30)

    mp3_files_found = 0
    correctly_tagged_files = 0
    mismatched_files = []

    for file_path in source_dir.rglob("*.mp3"):
        mp3_files_found += 1
        try:
            audiofile = eyed3.load(file_path)
            if audiofile is None or audiofile.tag is None:
                mismatched_files.append((file_path.name, "Could not load or tag not found"))
                continue

            album_correct = audiofile.tag.album == expected_album
            album_artist_correct = audiofile.tag.album_artist == expected_album_artist

            if album_correct and album_artist_correct:
                correctly_tagged_files += 1
            else:
                details = []
                if not album_correct:
                    details.append(f"Album: '{audiofile.tag.album}' (Expected: '{expected_album}')")
                if not album_artist_correct:
                    details.append(f"Album Artist: '{audiofile.tag.album_artist}' (Expected: '{expected_album_artist}')")
                mismatched_files.append((file_path.name, "; ".join(details)))

        except Exception as e:
            mismatched_files.append((file_path.name, f"Error processing file: {e}"))

    print("\n--- Verification Summary ---")
    print(f"Total MP3 files found: {mp3_files_found}")
    print(f"Files with correct Album AND Album Artist: {correctly_tagged_files}")
    
    incorrect_files_count = mp3_files_found - correctly_tagged_files
    print(f"Files with incorrect or missing metadata: {incorrect_files_count}")

    if mismatched_files:
        print("\nMismatched or problematic files:")
        for name, reason in mismatched_files:
            print(f"  - {name}: {reason}")
    elif mp3_files_found > 0:
        print("\nAll MP3 files have the correct Album and Album Artist set.")
    elif mp3_files_found == 0:
        print("\nNo MP3 files found to verify.")


def main():
    parser = argparse.ArgumentParser(
        description="Verifies Album and Album Artist ID3 tags for MP3 files in a directory."
    )
    parser.add_argument(
        "directory",
        type=str,
        help="The directory containing MP3 files to verify.",
    )
    parser.add_argument(
        "album_name",
        type=str,
        help="The expected album name.",
    )
    parser.add_argument(
        "album_artist_name",
        type=str,
        help="The expected album artist name.",
    )
    args = parser.parse_args()

    verify_metadata(args.directory, args.album_name, args.album_artist_name)

if __name__ == "__main__":
    main() 