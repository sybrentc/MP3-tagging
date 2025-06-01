import os
import sys
from pydub import AudioSegment

def convert_wav_to_mp3(input_path):
    # Check if input is a file or directory
    if os.path.isfile(input_path):
        if input_path.lower().endswith('.wav'):
            convert_single_file(input_path)
        else:
            print(f"Error: {input_path} is not a WAV file")
    elif os.path.isdir(input_path):
        convert_directory(input_path)
    else:
        print(f"Error: {input_path} is not a valid file or directory")

def convert_single_file(wav_path):
    try:
        # Load the WAV file
        audio = AudioSegment.from_wav(wav_path)
        
        # Create MP3 path (replace .wav with .mp3)
        mp3_path = wav_path[:-4] + '.mp3'
        
        # Export as MP3
        audio.export(mp3_path, format='mp3', bitrate='192k')
        print(f"Converted {wav_path} to {mp3_path}")
    except Exception as e:
        print(f"Error converting {wav_path}: {str(e)}")

def convert_directory(directory):
    # Walk through directory
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.wav'):
                wav_path = os.path.join(root, file)
                convert_single_file(wav_path)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python convert_wav_to_mp3.py <wav_file_or_directory>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    convert_wav_to_mp3(input_path) 