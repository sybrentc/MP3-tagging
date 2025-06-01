import os
import unicodedata
import shutil

def simplify_normalize_filenames_to_nfc(target_dir_abs):
    """
    Scans the specified directory and renames files/directories from non-NFC
    to NFC normalization form. 
    
    This script will:
    1. Iterate through all files and directories.
    2. For each item, check if its name is already NFC.
    3. If not, it attempts to rename the item to its NFC equivalent.
    This version does NOT check for existing NFC conflicts or perform deletions/backups.
    It relies on os.rename() to succeed if the NFD->NFC change is trivial (e.g. on APFS)
    or fail if a distinct file with the NFC name already exists.
    """
    print(f"Starting simplified NFC normalization for directory: {target_dir_abs}")
    if not os.path.isdir(target_dir_abs):
        print(f"Error: Directory not found: {target_dir_abs}")
        return 0, 0, 0

    renamed_count = 0
    processed_items = 0
    error_count = 0
    skipped_already_nfc = 0

    # Walk directory from bottom up to handle renaming of contents before their parent directories
    for root, dirs, files in os.walk(target_dir_abs, topdown=False):
        current_items_to_process = []
        # Add files for current directory
        for name in files:
            current_items_to_process.append({'name': name, 'type': 'file', 'path': os.path.join(root, name)})
        # Add directories for current directory (will be processed after their contents due to topdown=False)
        for name in dirs:
            current_items_to_process.append({'name': name, 'type': 'dir', 'path': os.path.join(root, name)})

        for item_info in current_items_to_process:
            processed_items += 1
            original_name = item_info['name']
            original_path = item_info['path']
            item_type = item_info['type']

            # Ensure path still exists (it might have been part of a renamed parent dir)
            if not os.path.exists(original_path) and not os.path.lexists(original_path):
                # print(f"  Skipping {original_path}, no longer exists (possibly due to parent dir rename).")
                continue

            try:
                nfc_name = unicodedata.normalize('NFC', original_name)
            except Exception as e:
                print(f"  Error normalizing name for '{original_path}': {e}. Skipping.")
                error_count += 1
                continue

            if original_name == nfc_name:
                skipped_already_nfc += 1
                continue

            nfc_path = os.path.join(root, nfc_name)

            log_prefix = "  [Non-NFC File]" if item_type == 'file' else "  [Non-NFC Dir]"
            print(f"{log_prefix} Original: '{original_path}'")
            print(f"    Target NFC Name: '{nfc_name}' (potential path: '{nfc_path}')")

            try:
                # Simple rename attempt
                # If original_path and nfc_path refer to the same file on APFS (just different unicode string forms),
                # os.rename should just update the name metadata to NFC.
                # If nfc_path is a genuinely different, existing file, os.rename will likely raise an OSError.
                if original_path == nfc_path: # Should not be strictly necessary if original_name != nfc_name
                    print(f"    Skipping rename: Original and NFC paths are identical strings: '{original_path}'. (Effectively already NFC)")
                    skipped_already_nfc +=1
                else:
                    os.rename(original_path, nfc_path)
                    renamed_count += 1
                    print(f"    Action: Renamed '{original_path}' to '{nfc_path}'.")
            except OSError as e:
                print(f"    Error renaming '{original_path}' to '{nfc_path}': {e}")
                print(f"             This can happen if a *distinct* file/directory already exists at '{nfc_path}'.")
                error_count += 1
            except Exception as e:
                print(f"    Unexpected error processing '{original_path}': {e}")
                error_count += 1

    print(f"Simplified normalization complete for {target_dir_abs}.")
    print(f"Total items encountered (files/dirs): {processed_items}")
    print(f"Items already NFC (skipped): {skipped_already_nfc}")
    print(f"Items renamed to NFC form: {renamed_count}")
    print(f"Errors encountered during rename attempts: {error_count}")
    return renamed_count, error_count, skipped_already_nfc

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python normalize_filenames_in_place.py <target_directory_path>")
        music_dir_default = os.path.expanduser("~/Desktop/Music")
        print(f"No directory provided. If run, would default to: {music_dir_default}")
        print("Please specify the absolute path to your music directory.")
        sys.exit(1)

    target_directory = sys.argv[1]
    
    if not os.path.isabs(target_directory):
        print(f"Error: Please provide an absolute path. '{target_directory}' is not absolute.")
        sys.exit(1)
        
    if not os.path.isdir(target_directory):
         print(f"Error: Target directory '{target_directory}' not found or not a directory.")
         sys.exit(1)
    
    print(f"Running SIMPLIFIED normalization on: {target_directory}")
    print("This script will attempt to rename non-NFC filenames to NFC in place.")
    print("It does NOT delete files or handle conflicts with pre-existing distinct NFC files beyond reporting an error.")
    print("ENSURE YOU HAVE A RELIABLE BACKUP.")
    
    try:
        confirm = raw_input("Are you sure you want to continue? (yes/no): ") # Python 2
    except NameError: 
        confirm = input("Are you sure you want to continue? (yes/no): ") # Python 3

    if confirm.lower() == 'yes':
        simplify_normalize_filenames_to_nfc(target_directory)
    else:
        print("Operation cancelled by user.") 