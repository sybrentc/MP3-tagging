# Post-Ripping Workflow

1.  Rip CD using Apple Music, exporting as MP3.
2.  Process the ripped MP3s through MusicBrainz Picard for accurate metadata tagging.
3.  Run the `trim_mp3_silence.py` script on the album folder to remove any trailing silence from the tracks.
4.  Synchronize the updated music library with an external drive using the following command in the terminal:
    ```bash
    rsync -avh --delete ~/Desktop/Music/ /Volumes/T9/Music/
    ``` 