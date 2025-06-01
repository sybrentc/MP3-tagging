import eyed3
import os
import sys
import eyed3.id3 # Import for specifying ID3 version

def update_mp3_disc_tags(directory_path, album_title, disc_num, total_discs):
    if not os.path.isdir(directory_path):
        print(f"Error: Directory '{directory_path}' not found.")
        return

    print(f"Processing directory: {directory_path}")
    print(f"  Album Title: '{album_title}'")
    print(f"  Disc Number: {disc_num} of {total_discs}")

    processed_count = 0
    error_count = 0

    for root, _, files in os.walk(directory_path):
        for filename in files:
            if filename.lower().endswith('.mp3'):
                mp3_path = os.path.join(root, filename)
                try:
                    audiofile = eyed3.load(mp3_path)
                    if audiofile is None:
                        print(f"Could not load (None returned): {mp3_path}")
                        error_count += 1
                        continue
                    
                    if audiofile.tag is None:
                        audiofile.initTag()
                        print(f"Initialized new tag for: {mp3_path}")

                    audiofile.tag.album = album_title
                    audiofile.tag.disc_num = (disc_num, total_discs)
                    
                    # Explicitly save as ID3 v2.3
                    audiofile.tag.save(version=eyed3.id3.ID3_V2_3)
                    # print(f"Successfully updated tags for: {mp3_path}")
                    processed_count += 1

                except Exception as e:
                    print(f"Error processing {mp3_path}: {str(e)}")
                    error_count += 1
    
    print(f"Finished processing {directory_path}.")
    print(f"  Successfully updated: {processed_count} files")
    print(f"  Errors: {error_count} files")
    print("-" * 30)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python set_disc_tags.py <directory_path> <album_title> <disc_num> <total_discs>")
        print("Example: python set_disc_tags.py \"/path/to/cd1\" \"My Album\" 1 2")
        sys.exit(1)

    dir_path = sys.argv[1]
    album = sys.argv[2]
    try:
        current_disc_num = int(sys.argv[3])
        num_total_discs = int(sys.argv[4])
    except ValueError:
        print("Error: Disc number and total discs must be integers.")
        sys.exit(1)

    update_mp3_disc_tags(dir_path, album, current_disc_num, num_total_discs) 