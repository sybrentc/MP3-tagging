#!/usr/bin/env python3
import os
import unicodedata
import argparse
from pathlib import Path

def normalize_filenames_to_nfc(root_dir):
    """
    Scans a directory recursively and renames files/directories
    from NFD (or other forms) to Unicode Normalization Form C (NFC).
    Renames are done from the deepest items upwards.
    """
    path_obj = Path(root_dir)
    if not path_obj.is_dir():
        print(f"Error: '{root_dir}' is not a valid directory.")
        return

    print(f"Normalizing filenames in '{path_obj.resolve()}' to NFC...")
    changes_made = 0
    errors = 0

    for current_root, dirnames, filenames in os.walk(path_obj, topdown=False):
        # Normalize filenames first
        for filename in filenames:
            try:
                original_full_path = Path(current_root) / filename
                normalized_filename = unicodedata.normalize('NFC', filename)
                if filename != normalized_filename:
                    new_full_path = Path(current_root) / normalized_filename
                    if new_full_path.exists():
                        print(f"  SKIPPING (target exists): '{original_full_path}' -> '{new_full_path}'")
                        errors +=1
                        continue
                    original_full_path.rename(new_full_path)
                    print(f"  RENAMED FILE: '{original_full_path}' -> '{new_full_path}'")
                    changes_made += 1
            except Exception as e:
                print(f"  ERROR renaming file '{original_full_path}': {e}")
                errors += 1

        # Normalize directory names last (as we are walking bottom-up)
        for dirname in dirnames:
            try:
                original_full_path = Path(current_root) / dirname
                normalized_dirname = unicodedata.normalize('NFC', dirname)
                if dirname != normalized_dirname:
                    new_full_path = Path(current_root) / normalized_dirname
                    if new_full_path.exists():
                        # This case should be less common for dirs if files inside are handled,
                        # but good to check.
                        print(f"  SKIPPING DIR (target exists): '{original_full_path}' -> '{new_full_path}'")
                        errors +=1
                        continue
                    original_full_path.rename(new_full_path)
                    print(f"  RENAMED DIR : '{original_full_path}' -> '{new_full_path}'")
                    changes_made += 1
            except Exception as e:
                print(f"  ERROR renaming directory '{original_full_path}': {e}")
                errors += 1
                
    print("--------------------------------------------------------")
    if changes_made == 0 and errors == 0:
        print("All filenames and directory names were already in NFC. No changes made.")
    else:
        print(f"Normalization complete. {changes_made} items renamed. {errors} errors/skipped.")
    print("--------------------------------------------------------")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Normalize filenames in a directory to Unicode NFC."
    )
    parser.add_argument(
        "directory",
        type=str,
        help="The root directory to scan and normalize.",
    )
    args = parser.parse_args()

    print("IMPORTANT: This script will RENAME files and directories.")
    print(f"Ensure you have a backup of '{Path(args.directory).resolve()}' before proceeding.")
    confirm = input("Are you sure you want to continue? (yes/no): ")

    if confirm.lower() == 'yes':
        normalize_filenames_to_nfc(args.directory)
    else:
        print("Normalization cancelled by user.") 