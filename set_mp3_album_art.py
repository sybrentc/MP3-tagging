import argparse
import pathlib
import eyed3
import os

def set_album_art(directory_path: str, image_path: str):
    """
    Sets the album art for all MP3 files in the specified directory.
    """
    # Convert paths to Path objects
    directory = pathlib.Path(directory_path)
    image_file = pathlib.Path(image_path)
    
    # Check if directory exists
    if not directory.exists() or not directory.is_dir():
        print(f"Error: Directory '{directory}' does not exist or is not a directory")
        return
    
    # Check if image file exists
    if not image_file.exists() or not image_file.is_file():
        print(f"Error: Image file '{image_file}' does not exist or is not a file")
        return
    
    # Read the image data
    with open(image_file, 'rb') as img_file:
        image_data = img_file.read()
    
    # Get all MP3 files in the directory
    mp3_files = list(directory.glob('*.mp3'))
    total_files = len(mp3_files)
    updated_files = 0
    
    print(f"Scanning for MP3 files in '{directory}' to set album art from '{image_file}'...")
    
    # Process each MP3 file
    for mp3_file in mp3_files:
        try:
            # Load the audio file
            audiofile = eyed3.load(mp3_file)
            if audiofile is None:
                print(f"Error: Could not load {mp3_file.name}")
                continue
            
            # Initialize tag if it doesn't exist
            if audiofile.tag is None:
                audiofile.initTag()
            
            # Remove existing album art
            while len(audiofile.tag.images) > 0:
                audiofile.tag.images.remove(audiofile.tag.images[0].description)
            
            # Add new album art
            audiofile.tag.images.set(3, image_data, 'image/jpeg')
            
            # Save changes
            audiofile.tag.save()
            updated_files += 1
            
        except Exception as e:
            print(f"Error processing file {mp3_file.name}: {str(e)}")
    
    # Print summary
    print("\n--- Summary ---")
    print(f"Total MP3 files found: {total_files}")
    print(f"MP3 files updated with album art: {updated_files}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Set album art for MP3 files in a directory')
    parser.add_argument('directory', help='Directory containing MP3 files')
    parser.add_argument('image', help='Path to the album art image file')
    
    args = parser.parse_args()
    set_album_art(args.directory, args.image) 