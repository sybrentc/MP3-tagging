import os
import unicodedata
import shutil

def sanitize_name(name):
    original_name = name
    # Replace dashes
    name = name.replace('\u2014', '-')  # em-dash
    name = name.replace('\u2013', '-')  # en-dash
    
    # Replace smart quotes
    name = name.replace('\u2018', "'")  # left single quote
    name = name.replace('\u2019', "'")  # right single quote
    name = name.replace('\u201c', '"')  # left double quote
    name = name.replace('\u201d', '"')  # right double quote
    
    # Normalize to NFC after replacements
    if name != original_name:
        name = unicodedata.normalize('NFC', name)
        return name
    # If no character replacement occurred, return the original name.
    # NFC normalization should have been handled by prior scripts in that case.
    return original_name

def sanitize_filenames_in_directory(directory_path):
    renamed_count = 0
    for root, dirs, files in os.walk(directory_path, topdown=False):
        # Sanitize file names
        for name in files:
            original_full_path = os.path.join(root, name)
            sanitized_name_part = sanitize_name(name)
            
            if sanitized_name_part != name:
                new_full_path = os.path.join(root, sanitized_name_part)
                
                # Check for conflicts before renaming
                if os.path.exists(new_full_path):
                    print(f"SKIPPING rename: Target '{new_full_path}' already exists. Original: '{original_full_path}'")
                    continue
                
                try:
                    os.rename(original_full_path, new_full_path)
                    print(f"Renamed FILE: '{original_full_path}' to '{new_full_path}'")
                    renamed_count += 1
                except OSError as e:
                    print(f"Error renaming file '{original_full_path}' to '{new_full_path}': {e}")

        # Sanitize directory names
        for name in dirs:
            original_full_path = os.path.join(root, name)
            sanitized_name_part = sanitize_name(name)

            if sanitized_name_part != name:
                new_full_path = os.path.join(root, sanitized_name_part)

                if os.path.exists(new_full_path):
                    print(f"SKIPPING rename: Target '{new_full_path}' already exists. Original: '{original_full_path}'")
                    continue

                try:
                    os.rename(original_full_path, new_full_path)
                    print(f"Renamed DIR:  '{original_full_path}' to '{new_full_path}'")
                    renamed_count += 1
                except OSError as e:
                    print(f"Error renaming directory '{original_full_path}' to '{new_full_path}': {e}")
    
    print(f"\nSanitization complete. {renamed_count} items renamed.")

if __name__ == '__main__':
    music_folder = '/Users/stencate/Desktop/Music/'
    print(f"Starting filename sanitization for directory: {music_folder}")
    print("This will rename files and directories in place.")
    print("Characters to be replaced:")
    print("  Em-dash (—), En-dash (–)  -> Hyphen (-)")
    print("  Left/Right Single Quotes (‘ ’) -> Apostrophe (')")
    print("  Left/Right Double Quotes (“ ”) -> Quotation Mark (\")")
    print("All names will be NFC normalized after changes.")
    # You can add a confirmation step here if you like:
    # input("Press Enter to continue or Ctrl+C to abort...")
    sanitize_filenames_in_directory(music_folder) 