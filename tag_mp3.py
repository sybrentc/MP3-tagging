import argparse
import eyed3
from pathlib import Path

def tag_mp3(file_path: str, artist: str = None, album: str = None, title: str = None):
    """
    Sets metadata for a single MP3 file.

    Args:
        file_path: Path to the MP3 file
        artist: Artist name to set (optional)
        album: Album name to set (optional)
        title: Title to set (optional)
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
            audiofile.initTag()

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

        # Save changes
        audiofile.tag.save()
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
    args = parser.parse_args()

    tag_mp3(args.file_path, args.artist, args.album, args.title) 