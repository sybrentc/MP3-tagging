import os
import sys
import subprocess

def set_album_art(mp3_path, art_path):
    if not os.path.exists(mp3_path):
        print(f"Error: MP3 file {mp3_path} does not exist")
        return False
    
    if not os.path.exists(art_path):
        print(f"Error: Album art file {art_path} does not exist")
        return False

    try:
        # Step 1: Remove all existing images using eyeD3 CLI
        print(f"Attempting to remove all images from: {mp3_path}")
        remove_command = ["eyeD3", "--remove-all-images", mp3_path]
        remove_result = subprocess.run(remove_command, capture_output=True, text=True, check=False)

        if remove_result.returncode == 0:
            print(f"Successfully removed images from {mp3_path} (or no images to remove).")
        else:
            # eyeD3 might return non-0 if no images were found, which is not an error for our purpose.
            # We'll print the output for debugging but proceed.
            print(f"eyeD3 --remove-all-images for {mp3_path} finished with code {remove_result.returncode}.")
            if remove_result.stdout:
                print(f"  stdout: {remove_result.stdout.strip()}")
            if remove_result.stderr:
                print(f"  stderr: {remove_result.stderr.strip()}")
            # We can choose to continue even if removal wasn't 'successful' in eyeD3's eyes, 
            # as long as adding the new image works.

        # Step 2: Add the new album art using eyeD3 CLI
        print(f"Attempting to add image {art_path} to: {mp3_path}")
        # Ensure art_path is absolute for the command, or accessible from CWD
        # If art_path is just 'cool.jpg', it assumes it's in the CWD where eyeD3 runs.
        add_command = ["eyeD3", "--add-image", f"{art_path}:FRONT_COVER", mp3_path]
        add_result = subprocess.run(add_command, capture_output=True, text=True, check=False)

        if add_result.returncode == 0:
            print(f"Successfully set album art for {mp3_path} using {art_path}")
            return True
        else:
            print(f"Error setting album art for {mp3_path} using eyeD3 --add-image.")
            print(f"  Return Code: {add_result.returncode}")
            if add_result.stdout:
                print(f"  stdout: {add_result.stdout.strip()}")
            if add_result.stderr:
                print(f"  stderr: {add_result.stderr.strip()}")
            return False

    except Exception as e:
        print(f"An unexpected error occurred while processing {mp3_path}: {str(e)}")
        return False

def process_directory(directory_path, art_path):
    if not os.path.exists(directory_path):
        print(f"Error: Directory {directory_path} does not exist")
        return

    # Make art_path absolute if it's not already, to be safe for subprocess calls
    # or ensure it's handled correctly relative to the script's execution CWD.
    # For 'cool.jpg' in project root, and script run from project root, it's usually fine.
    abs_art_path = os.path.abspath(art_path)
    if not os.path.exists(abs_art_path):
        print(f"Error: Album art file {abs_art_path} (absolute) does not exist. Original path: {art_path}")
        # Fallback to using art_path as is, in case it's found relative to CWD by eyeD3
        # but this is less robust.
        abs_art_path = art_path 
        print(f"Proceeding with art_path as: {abs_art_path}")

    success_count = 0
    fail_count = 0

    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith('.mp3'):
                mp3_file_path = os.path.join(root, file)
                if set_album_art(mp3_file_path, abs_art_path):
                    success_count += 1
                else:
                    fail_count += 1
    
    print(f"\nProcessing complete:")
    print(f"Successfully processed: {success_count} files")
    print(f"Failed to process: {fail_count} files")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python set_album_art.py <directory_path> <album_art_path>")
        sys.exit(1)
    
    directory_to_process = sys.argv[1]
    album_art_image_path = sys.argv[2]
    process_directory(directory_to_process, album_art_image_path) 