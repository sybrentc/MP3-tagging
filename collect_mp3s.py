import argparse
import pathlib
import shutil

def collect_mp3s(source_folder_path: str, destination_folder_path: str):
    """
    Recursively finds all MP3 files in the source folder and moves them
    to the destination folder. Handles filename conflicts by appending a number.
    """
    source_dir = pathlib.Path(source_folder_path).resolve()
    dest_dir = pathlib.Path(destination_folder_path).resolve()

    if not source_dir.is_dir():
        print(f"Error: Source folder '{source_dir}' does not exist or is not a directory.")
        return

    # Create destination folder if it doesn't exist
    dest_dir.mkdir(parents=True, exist_ok=True)
    print(f"Ensured destination folder exists: '{dest_dir}'")

    mp3_files_found = 0
    mp3_files_moved = 0
    files_skipped_already_exists = 0 # Though we will rename

    print(f"Scanning for MP3 files in '{source_dir}'...")

    for mp3_file_path in source_dir.rglob("*.mp3"):
        mp3_files_found += 1
        original_file_name = mp3_file_path.name
        destination_file_path = dest_dir / original_file_name
        
        # Handle potential filename conflicts
        counter = 1
        while destination_file_path.exists():
            # If it's the exact same file (same path), we can skip it.
            # This check is more relevant if copying, but good for robustness.
            try:
                if destination_file_path.samefile(mp3_file_path):
                    print(f"Skipping '{mp3_file_path.name}' as it is the same file already in destination.")
                    files_skipped_already_exists +=1
                    # Break inner while, continue outer for loop
                    break 
            except FileNotFoundError:
                # This can happen if destination_file_path exists but mp3_file_path was moved/deleted by another process
                pass

            new_name = f"{mp3_file_path.stem} ({counter}){mp3_file_path.suffix}"
            destination_file_path = dest_dir / new_name
            counter += 1
        else: # This 'else' belongs to the 'while' loop: executed if the loop finished normally (no break)
            try:
                shutil.move(str(mp3_file_path), str(destination_file_path))
                print(f"Moved '{mp3_file_path.name}' to '{destination_file_path.name}' in '{dest_dir.name}'")
                mp3_files_moved += 1
            except Exception as e:
                print(f"Error moving file {mp3_file_path.name}: {e}")
            continue # Continue to next file in the rglob loop

        # If we broke from the while loop because samefile() was true
        if files_skipped_already_exists > 0 and mp3_files_moved + files_skipped_already_exists == mp3_files_found :
             pass # This logic is a bit complex, mainly to ensure the counts are right if we skip.

    print(f"\n--- Collection Summary ---")
    print(f"Total MP3 files found in source: {mp3_files_found}")
    print(f"MP3 files successfully moved: {mp3_files_moved}")
    if files_skipped_already_exists > 0:
         print(f"MP3 files skipped (already existed and identical): {files_skipped_already_exists}")
    if mp3_files_found > mp3_files_moved + files_skipped_already_exists:
        print(f"MP3 files failed to move: {mp3_files_found - mp3_files_moved - files_skipped_already_exists}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Collects all MP3 files recursively from a source folder and moves them to a destination folder."
    )
    parser.add_argument(
        "source_directory",
        type=str,
        help="The source directory to scan for MP3 files.",
    )
    parser.add_argument(
        "destination_directory",
        type=str,
        help="The destination directory to move MP3 files to.",
    )
    args = parser.parse_args()

    collect_mp3s(args.source_directory, args.destination_directory) 