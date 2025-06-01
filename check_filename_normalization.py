#!/usr/bin/env python3
import os
import unicodedata
import argparse
from pathlib import Path

def check_normalization(root_dir):
    """
    Scans a directory recursively and reports files/directories whose names
    are not in Unicode Normalization Form C (NFC).
    """
    path_obj = Path(root_dir)
    if not path_obj.is_dir():
        print(f"Error: '{root_dir}' is not a valid directory.")
        return

    print(f"Scanning '{path_obj.resolve()}' for filenames not in NFC (Dry Run)...")
    print("Files/directories that would be renamed (NFD -> NFC):")
    print("--------------------------------------------------------")

    potential_changes = 0

    for current_root, dirnames, filenames in os.walk(path_obj, topdown=True):
        # Check directory names first
        for i, dirname in enumerate(dirnames):
            normalized_dirname = unicodedata.normalize('NFC', dirname)
            if dirname != normalized_dirname:
                original_full_path = Path(current_root) / dirname
                # Simulating what the new path component would be
                print(f"  DIR : '{original_full_path}' -> '{Path(current_root) / normalized_dirname}'")
                potential_changes += 1
                # To ensure os.walk continues with the *original* names during dry run,
                # we don't modify dirnames[i] here.
        
        # Check file names
        for filename in filenames:
            normalized_filename = unicodedata.normalize('NFC', filename)
            if filename != normalized_filename:
                original_full_path = Path(current_root) / filename
                print(f"  FILE: '{original_full_path}' -> '{Path(current_root) / normalized_filename}'")
                potential_changes += 1

    if potential_changes == 0:
        print("\nAll filenames and directory names are already in NFC.")
    else:
        print(f"\nFound {potential_changes} potential changes.")
    print("--------------------------------------------------------")
    print("This was a dry run. No files were actually renamed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check for filenames not in NFC and show potential renames (Dry Run)."
    )
    parser.add_argument(
        "directory",
        type=str,
        help="The root directory to scan.",
    )
    args = parser.parse_args()
    check_normalization(args.directory) 