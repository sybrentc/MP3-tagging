import argparse
import eyed3
from pathlib import Path

def tag_mp3(file_path: str, artist: str = None, album: str = None, title: str = None, track_num_val: int = None, track_total_val: int = None):
    """
    Sets metadata for a single MP3 file.

    Args:
        file_path: Path to the MP3 file
        artist: Artist name to set (optional)
        album: Album name to set (optional)
        title: Title to set (optional)
        track_num_val: Track number to set (optional)
        track_total_val: Total number of tracks to set (optional)
    """
    file_path = Path(file_path)
    if not file_path.is_file():
        print(f"Error: '{file_path}' is not a valid file.")
        return

    if not file_path.suffix.lower() == '.mp3':
        print(f"Error: '{file_path}' is not an MP3 file.")
        return

    try:
        audiofile = eyed3.load(file_path)
        if audiofile is None:
            print(f"Error: Could not load '{file_path}' as an MP3 file.")
            return

        # Initialize tag if it doesn't exist
        if audiofile.tag is None:
            # Attempt to initialize with a version that supports track numbers well, e.g., v2.4
            audiofile.initTag(version=eyed3.id3.ID3_V2_4)
            if audiofile.tag is None: # If still None, then something is wrong
                print(f"Error: Could not initialize tag for '{file_path}'.")
                return


        # Set metadata if provided
        if artist is not None:
            audiofile.tag.artist = artist
            print(f"Set artist to: {artist}")
        
        if album is not None:
            audiofile.tag.album = album
            print(f"Set album to: {album}")
        
        if title is not None:
            audiofile.tag.title = title
            print(f"Set title to: {title}")

        if track_num_val is not None or track_total_val is not None:
            current_track_num, current_track_total = audiofile.tag.track_num if audiofile.tag.track_num else (None, None)
            
            new_track_num = track_num_val if track_num_val is not None else current_track_num
            new_track_total = track_total_val if track_total_val is not None else current_track_total

            if new_track_num is not None: # We need at least a track number to set it
                audiofile.tag.track_num = (new_track_num, new_track_total)
                print(f"Set track to: {new_track_num}{f'/{new_track_total}' if new_track_total is not None else ''}")
            elif track_total_val is not None: # Only total is provided, but no current track number exists - less ideal
                 # This case might be ambiguous if no track number is set.
                 # For now, if only total is given and no current track number, we won't set it
                 # to avoid (None, total) which can be problematic.
                 # Or, we could decide to default track_num to 0 or 1 if new_track_num is None.
                 # For simplicity, we'll require a track_num if setting track_num field.
                 # However, if track_num_val was None, but track_total_val was provided, AND a current_track_num exists:
                 if current_track_num is not None:
                    audiofile.tag.track_num = (current_track_num, new_track_total)
                    print(f"Updated track total for track {current_track_num} to: {new_track_total}")
                 else:
                    print(f"Warning: Track total provided ({track_total_val}) but no track number to associate it with. Not setting track info.")


        # Save changes
        # Ensure saving with a version that supports the tags well, e.g. v2.4
        audiofile.tag.save(version=eyed3.id3.ID3_V2_4)
        print(f"\nSuccessfully updated metadata for: {file_path.name}")

    except Exception as e:
        print(f"Error processing {file_path.name}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Set metadata for a single MP3 file."
    )
    parser.add_argument(
        "file_path",
        type=str,
        help="Path to the MP3 file to tag."
    )
    parser.add_argument(
        "--artist",
        type=str,
        help="Artist name to set."
    )
    parser.add_argument(
        "--album",
        type=str,
        help="Album name to set."
    )
    parser.add_argument(
        "--title",
        type=str,
        help="Title to set."
    )
    parser.add_argument(
        "--track",
        type=int,
        help="Track number to set."
    )
    parser.add_argument(
        "--track-total",
        type=int,
        help="Total number of tracks in the album to set."
    )
    args = parser.parse_args()

    tag_mp3(args.file_path, args.artist, args.album, args.title, args.track, args.track_total) 