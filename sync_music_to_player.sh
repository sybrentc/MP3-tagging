#!/bin/bash

# Script to synchronize Music folder to MP3 player

SOURCE_DIR="/Users/stencate/Desktop/Music/"
DEST_DIR="/Volumes/AGP-M2/Music/"

# Ensure SOURCE_DIR ends with a slash for rsync to copy contents correctly
[[ "$SOURCE_DIR" != */ ]] && SOURCE_DIR="${SOURCE_DIR}/"

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Source directory $SOURCE_DIR does not exist."
    exit 1
fi

# Check if destination directory exists
if [ ! -d "$DEST_DIR" ]; then
    echo "Error: Destination directory $DEST_DIR does not exist."
    echo "Please ensure your MP3 player is connected and mounted."
    exit 1
fi

echo "Starting DRY RUN music synchronization VERIFICATION from $SOURCE_DIR to $DEST_DIR..."
echo "Using rsync flags: -av -n --delete --progress --iconv=UTF-8-MAC,UTF-8 --modify-window=2 --size-only --no-perms --omit-dir-times --no-whole-file"
echo "Caffeinate will be used to prevent sleep during the sync."
echo "NO CHANGES WILL BE MADE."


echo "Ensure you have backups if necessary (though no changes will be made)."
echo "You have 5 seconds to cancel (Ctrl+C)..."
sleep 5

# -a: archive mode (implies -rlptgoD, but we override some with --no-perms etc.)
# -v: verbose
# -n: DRY RUN - show what would be done, but don't actually do it.
# --delete: delete extraneous files from dest dirs
# --progress: show progress per file
# --iconv=UTF-8-MAC,UTF-8: convert filenames from macOS specific UTF-8 to standard UTF-8 for destination
# --modify-window=2: tolerate timestamp differences up to 2 seconds (good for FAT32)
# --size-only: only compare file sizes, ignore timestamps (robust for problematic FAT32 mtimes)
# --no-perms: skip preserving permissions (good for FAT32)
# --omit-dir-times: Don't preserve directory modification times (good for FAT32)
# --no-whole-file: Use rsync's delta-transfer algorithm (efficient for updates)
# caffeinate -i: prevent idle sleep during rsync

caffeinate -i rsync -av -n --delete --progress --iconv=UTF-8-MAC,UTF-8 --modify-window=2 --size-only --no-perms --omit-dir-times --no-whole-file "$SOURCE_DIR" "$DEST_DIR"

SYNC_STATUS=$?

if [ $SYNC_STATUS -eq 0 ]; then
    echo "Dry run verification completed successfully."
else
    echo "Error: Dry run verification failed with rsync exit code $SYNC_STATUS."
fi

exit $SYNC_STATUS 