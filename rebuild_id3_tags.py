import argparse
import pathlib
import eyed3
import shutil # For potential backup later, not used yet

def rebuild_tags_for_mp3(file_path: pathlib.Path, target_album: str, target_album_artist: str):
    """
    Reads essential tags, removes all tags, and reapplies them with a new album and album artist.
    """
    print(f"Processing: {file_path.name}")
    preserved_tags = {
        "title": None,
        "artist": None,
        "track_num": None, # Tuple (number, total)
        "year": None,      # Integer year
        "genre_name": None,
        "images": [],      # List of tuples (type, data, mime_type, description)
        "comments": [],    # List of tuples (description, text, lang)
        "composer": None,
        "disc_num": None   # Tuple (number, total)
    }

    try:
        audiofile = eyed3.load(file_path)
        if audiofile and audiofile.tag:
            tag = audiofile.tag
            preserved_tags["title"] = tag.title
            preserved_tags["artist"] = tag.artist
            preserved_tags["track_num"] = tag.track_num # (track, total_tracks)
            
            best_date = tag.getBestDate()
            if best_date and best_date.year:
                preserved_tags["year"] = best_date.year
            
            if tag.genre:
                preserved_tags["genre_name"] = tag.genre.name
            
            for img in tag.images:
                preserved_tags["images"].append((img.picture_type, img.image_data, img.mime_type, img.description))
            
            for comment in tag.comments:
                preserved_tags["comments"].append((comment.description, comment.text, comment.lang))

            preserved_tags["composer"] = tag.composer
            preserved_tags["disc_num"] = tag.disc_num # (disc, total_discs)
            
            print(f"  Preserved: Title='{preserved_tags['title']}', Artist='{preserved_tags['artist']}'")

    except Exception as e:
        print(f"  Warning: Could not fully read existing tags from {file_path.name}: {e}")

    # Remove all existing tags
    try:
        print(f"  Removing existing tags from {file_path.name}...")
        eyed3.id3.Tag.remove(file_path, version=eyed3.id3.ID3_V1)
        eyed3.id3.Tag.remove(file_path, version=eyed3.id3.ID3_V2)
        print(f"  Existing tags removed.")
    except Exception as e:
        print(f"  Warning: Error removing tags from {file_path.name}: {e}. Proceeding to re-tag.")

    # Reload the audio file (it should have no tag or a fresh one)
    # and initialize a new tag
    audiofile_to_process = None
    try:
        audiofile_to_process = eyed3.load(file_path)
    except Exception as load_exception:
        print(f"  Warning: eyed3.load() raised an exception for {file_path.name} after tag removal: {load_exception}")
        audiofile_to_process = None

    if audiofile_to_process is None:
        print(f"  eyed3.load() failed for {file_path.name} after tag removal. Attempting direct AudioFile instantiation...")
        try:
            # Attempt to create an AudioFile object directly
            # The path needs to be a string for eyed3.core.AudioFile constructor
            audiofile_for_direct_init = eyed3.core.AudioFile(str(file_path))
            
            # audiofile_for_direct_init.path = file_path # Might be needed if save relies on it, but tag.save() is used.

            print(f"  Initializing new tag directly for {file_path.name}...")
            if not audiofile_for_direct_init.initTag(version=eyed3.id3.ID3_V2_4):
                if not audiofile_for_direct_init.initTag(version=eyed3.id3.ID3_V2_3):
                    print(f"  Error: Could not initialize a new tag directly for {file_path.name}. Skipping.")
                    return False
            # If initTag succeeded, audiofile_for_direct_init.tag should now exist.
            audiofile_to_process = audiofile_for_direct_init # Use this object going forward
            print(f"  New tag directly initialized (v{audiofile_to_process.tag.version[0]}.{audiofile_to_process.tag.version[1]}).")
        except Exception as direct_init_e:
            print(f"  Error: Direct AudioFile instantiation or initTag failed for {file_path.name}: {direct_init_e}. Skipping.")
            return False

    # Ensure we have a valid audiofile object to work with
    if audiofile_to_process is None:
        print(f"  Error: Failed to obtain a valid audiofile object for {file_path.name} after all attempts. Skipping.")
        return False
    
    # Make sure the audiofile object is consistently named 'audiofile' for the rest of the script
    audiofile = audiofile_to_process

    # Initialize tag if it doesn't exist on the (potentially newly loaded/created) audiofile object
    if not audiofile.tag:
        print(f"  Initializing new tag for {file_path.name} (tag object missing on loaded audiofile)...")
        if not audiofile.initTag(version=eyed3.id3.ID3_V2_4):
            if not audiofile.initTag(version=eyed3.id3.ID3_V2_3):
                print(f"  Error: Could not initialize a new tag for {file_path.name}. Skipping.")
                return False
        print(f"  New tag initialized (v{audiofile.tag.version[0]}.{audiofile.tag.version[1]}).")
    else:
        # This case means audiofile.load() worked and a tag was present, or direct init worked.
        print(f"  Tag already present after load/re-init (v{audiofile.tag.version[0]}.{audiofile.tag.version[1]}). Proceeding to set fields.")

    # Set the new album and album artist
    audiofile.tag.album = target_album
    audiofile.tag.album_artist = target_album_artist

    # Re-apply preserved tags
    if preserved_tags["title"] is not None:
        audiofile.tag.title = preserved_tags["title"]
    if preserved_tags["artist"] is not None:
        audiofile.tag.artist = preserved_tags["artist"]
    if preserved_tags["track_num"] is not None:
        track_val = preserved_tags["track_num"]
        try:
            # Attempt to treat as CountAndTotalTuple (duck typing)
            if track_val.total is None:
                audiofile.tag.track_num = track_val.count
            else:
                audiofile.tag.track_num = (track_val.count, track_val.total)
        except AttributeError:
            # If .count or .total don't exist, assume it's already in a valid format (int or tuple)
            audiofile.tag.track_num = track_val
    
    if preserved_tags["year"] is not None:
        # eyed3 handles setting date from year; TDRC is preferred for v2.4
        # For simplicity, we're setting it via release_date which should pick appropriate frame.
        try:
            audiofile.tag.release_date = preserved_tags["year"]
        except Exception as e_date:
            print(f"    Warning: Could not set year {preserved_tags['year']}: {e_date}")


    if preserved_tags["genre_name"] is not None:
        try:
            audiofile.tag.genre = preserved_tags["genre_name"]
        except Exception as e_genre:
             print(f"    Warning: Could not set genre '{preserved_tags['genre_name']}': {e_genre}")


    for pic_type, pic_data, mime_type, desc in preserved_tags["images"]:
        if pic_data: # Ensure there's actual image data
            audiofile.tag.images.set(pic_type, pic_data, mime_type, description=desc)
    
    for desc, text, lang in preserved_tags["comments"]:
         audiofile.tag.comments.set(text, description=desc, lang=lang)

    if preserved_tags["composer"] is not None:
        audiofile.tag.composer = preserved_tags["composer"]
    if preserved_tags["disc_num"] is not None:
        disc_val = preserved_tags["disc_num"]
        try:
            # Attempt to treat as CountAndTotalTuple (duck typing)
            if disc_val.total is None:
                audiofile.tag.disc_num = disc_val.count
            else:
                audiofile.tag.disc_num = (disc_val.count, disc_val.total)
        except AttributeError:
            # If .count or .total don't exist, assume it's already in a valid format (int or tuple)
            audiofile.tag.disc_num = disc_val
    
    # Save the tag
    # Prefer ID3v2.4, fallback to v2.3
    print(f"  Saving changes to {file_path.name}...")
    saved_successfully = False
    try:
        audiofile.tag.save(version=eyed3.id3.ID3_V2_4, encoding='utf-8')
        saved_successfully = True
        print(f"    Saved with ID3v2.4.")
    except Exception as e_v24:
        print(f"    Could not save with ID3v2.4: {e_v24}. Trying ID3v2.3...")
        try:
            audiofile.tag.save(version=eyed3.id3.ID3_V2_3, encoding='utf-8')
            saved_successfully = True
            print(f"    Saved with ID3v2.3.")
        except Exception as e_v23:
            print(f"    Error: Could not save {file_path.name} with ID3v2.3 either: {e_v23}")
    
    if saved_successfully:
        print(f"  Successfully rebuilt tags for {file_path.name}")
        return True
    else:
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Rebuilds ID3 tags for MP3 files in a directory. Preserves common tags, sets a new album and album artist."
    )
    parser.add_argument(
        "directory",
        type=str,
        help="The directory containing MP3 files to process.",
    )
    parser.add_argument(
        "album_name",
        type=str,
        help="The new album name to set for all MP3 files.",
    )
    parser.add_argument(
        "album_artist_name",
        type=str,
        help="The new album artist name to set for all MP3 files.",
    )
    args = parser.parse_args()

    source_dir = pathlib.Path(args.directory)
    if not source_dir.is_dir():
        print(f"Error: '{args.directory}' is not a valid directory.")
        return

    print(f"Scanning for MP3 files in '{source_dir.resolve()}' to rebuild tags...")
    mp3_files_found = 0
    mp3_files_rebuilt_successfully = 0
    failed_file_names = [] # Added list to store names of failed files

    for file_path in source_dir.rglob("*.mp3"):
        mp3_files_found += 1
        if rebuild_tags_for_mp3(file_path, args.album_name, args.album_artist_name):
            mp3_files_rebuilt_successfully += 1
        else:
            failed_file_names.append(file_path.name) # Add failed file name to the list
    
    print("\\n--- Rebuild Summary ---")
    print(f"Total MP3 files found: {mp3_files_found}")
    print(f"MP3 files successfully rebuilt: {mp3_files_rebuilt_successfully}")
    
    if failed_file_names:
        print(f"MP3 files that failed to process ({len(failed_file_names)}):")
        for name in failed_file_names:
            print(f"  - {name}")
    else:
        if mp3_files_found > 0 and mp3_files_found == mp3_files_rebuilt_successfully:
             print("All MP3 files processed successfully!")
        elif mp3_files_found == 0:
            print("No MP3 files found in the specified directory.")


if __name__ == "__main__":
    main() 