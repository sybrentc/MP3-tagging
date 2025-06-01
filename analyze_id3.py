#!/usr/bin/env python3

import eyed3
import os
import sys
import hashlib

def analyze_mp3(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist")
        return

    audiofile = eyed3.load(file_path)
    if audiofile is None:
        print(f"Error: Could not load {file_path}")
        return

    print(f"\nAnalyzing: {file_path}")
    print("-" * 50)

    # Basic tag information
    if audiofile.tag:
        print("\nBasic Tag Information:")
        print(f"Artist: {audiofile.tag.artist}")
        print(f"Album: {audiofile.tag.album}")
        print(f"Title: {audiofile.tag.title}")
        print(f"Album Artist: {audiofile.tag.album_artist}")
        if audiofile.tag.track_num:
            print(f"Track: {audiofile.tag.track_num[0]}/{audiofile.tag.track_num[1]}")
        
        # Detailed album art information
        print("\nAlbum Art Information:")
        if audiofile.tag.images:
            for i, img in enumerate(audiofile.tag.images):
                print(f"\nImage {i+1}:")
                print(f"Description: {img.description}")
                print(f"Picture Type: {img.picture_type}")
                print(f"MIME Type: {img.mime_type}")
                print(f"Size: {len(img.image_data)} bytes")
                # Calculate hash of image data
                img_hash = hashlib.md5(img.image_data).digest()
                print(f"Image Data Hash: {int.from_bytes(img_hash, byteorder='big', signed=True)}")
        else:
            print("No album art found")
    else:
        print("No ID3 tags found")

    # File information
    print("\nFile Information:")
    print(f"Size: {os.path.getsize(file_path)} bytes")
    print(f"Duration: {audiofile.info.time_secs:.2f} seconds")
    print(f"Bit Rate: ~{audiofile.info.bit_rate[1] // 1000} kb/s")

def analyze_directory(directory_path):
    if not os.path.exists(directory_path):
        print(f"Error: Directory {directory_path} does not exist")
        return
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith('.mp3'):
                analyze_mp3(os.path.join(root, file))

def main():
    if len(sys.argv) != 2:
        print("Usage: python analyze_id3.py <mp3_file_path_or_directory>")
        sys.exit(1)
    
    path = sys.argv[1]
    if os.path.isfile(path):
        analyze_mp3(path)
    elif os.path.isdir(path):
        analyze_directory(path)
    else:
        print(f"Error: {path} is not a valid file or directory")
        sys.exit(1)

if __name__ == "__main__":
    main() 