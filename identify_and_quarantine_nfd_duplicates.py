#!/usr/bin/env python3
import os
import unicodedata
import argparse
from pathlib import Path
import shutil

def identify_and_quarantine_nfd_duplicates(root_dir_str, quarantine_dir_str):
    root_dir = Path(root_dir_str)
    quarantine_dir = Path(quarantine_dir_str)

    if not root_dir.is_dir():
        print(f"Error: Source directory '{root_dir}' not found.")
        return

    try:
        quarantine_dir.mkdir(parents=True, exist_ok=True)
        print(f"Quarantine directory is: {quarantine_dir.resolve()}")
    except Exception as e:
        print(f"Error creating quarantine directory '{quarantine_dir}': {e}")
        return

    print(f"Scanning '{root_dir.resolve()}' for NFD duplicates (NFC version also exists)...")
    nfd_duplicates_found = 0
    moved_to_quarantine = 0
    errors = 0

    items_to_process = []
    for current_root, dirnames, filenames in os.walk(root_dir, topdown=False):
        for name in filenames + dirnames:
            items_to_process.append(Path(current_root) / name)
    
    # Sort by depth (deepest first) to handle files before their parent dirs if both are NFD
    # and ensure directories are processed after their contents.
    # For NFD duplicate check, processing order is less critical than for renaming all to NFC,
    # but good practice for complex file operations.
    items_to_process.sort(key=lambda p: len(p.parts), reverse=True)

    identified_nfd_paths = []

    for item_path in items_to_process:
        item_name = item_path.name
        parent_dir = item_path.parent

        normalized_nfc_name = unicodedata.normalize('NFC', item_name)
        
        # Is the item itself NFD (or some other non-NFC form)?
        if item_name != normalized_nfc_name:
            # This item (item_path) is NFD.
            # Does its NFC equivalent also exist in the same directory?
            nfc_equivalent_path = parent_dir / normalized_nfc_name
            if nfc_equivalent_path.exists() and item_path != nfc_equivalent_path:
                # We found an NFD file/dir (item_path) AND its NFC twin (nfc_equivalent_path) exists.
                # item_path is the NFD duplicate.
                print(f"  NFD DUPLICATE: '{item_path}' (NFC twin: '{normalized_nfc_name}')")
                identified_nfd_paths.append(item_path)
                nfd_duplicates_found += 1
    
    if not identified_nfd_paths:
        print("No NFD files/dirs found that have an existing NFC twin in the same location.")
        shutil.rmdir(quarantine_dir) # Remove empty quarantine dir
        print("Removed empty quarantine directory.")
        return

    print(f"\nFound {nfd_duplicates_found} NFD file(s)/dir(s) that have an existing NFC twin.")
    confirm = input("Move these identified NFD duplicates to the quarantine directory? (yes/no): ")

    if confirm.lower() == 'yes':
        print(f"Moving NFD duplicates to '{quarantine_dir}'...")
        for nfd_path in identified_nfd_paths:
            try:
                # Create corresponding subdirectory structure in quarantine_dir
                relative_path = nfd_path.relative_to(root_dir)
                quarantine_item_path = quarantine_dir / relative_path
                quarantine_item_parent_dir = quarantine_item_path.parent
                quarantine_item_parent_dir.mkdir(parents=True, exist_ok=True)
                
                shutil.move(str(nfd_path), str(quarantine_item_path))
                print(f"  MOVED: '{nfd_path}' -> '{quarantine_item_path}'")
                moved_to_quarantine += 1
            except Exception as e:
                print(f"  ERROR moving '{nfd_path}': {e}")
                errors += 1
        print(f"Finished. Moved {moved_to_quarantine} NFD items to quarantine. {errors} errors.")
    else:
        print("Quarantine action cancelled by user. No files were moved.")
        shutil.rmdir(quarantine_dir) # Remove empty quarantine dir
        print("Removed empty quarantine directory.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Identifies NFD filenames that have an NFC twin in the same directory and quarantines the NFD versions."
    )
    parser.add_argument(
        "directory",
        type=str,
        help="The root directory to scan."
    )
    parser.add_argument(
        "--quarantine_dir",
        type=str,
        default="./NFD_Duplicates_Quarantine", # Default to a subfolder in CWD
        help="The directory to move NFD duplicates to."
    )
    args = parser.parse_args()

    print("IMPORTANT: This script will identify NFD files/dirs that have an NFC twin.")
    print("If confirmed, it will MOVE the NFD versions to a quarantine folder.")
    print(f"Source directory: '{Path(args.directory).resolve()}'")
    print(f"Quarantine directory will be: '{Path(args.quarantine_dir).resolve()}'")
    
    confirm_script = input("Are you sure you want to scan and potentially quarantine files? (yes/no): ")
    if confirm_script.lower() == 'yes':
        identify_and_quarantine_nfd_duplicates(args.directory, args.quarantine_dir)
    else:
        print("Script cancelled by user.") 