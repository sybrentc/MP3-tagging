#!/usr/bin/env python3
import os
import unicodedata
from pathlib import Path
import argparse

def analyze_paths(target_nfc_filename, source_parent_dir_str, dest_parent_dir_str):
    source_parent = Path(source_parent_dir_str)
    dest_parent = Path(dest_parent_dir_str)

    print(f"\n--- Analyzing for: '{target_nfc_filename}' ---")

    # Analyze Source
    print(f"\n[SOURCE]: {source_parent}")
    if not source_parent.is_dir():
        print(f"  Error: Source directory not found: {source_parent}")
    else:
        found_on_source = False
        for item_name in os.listdir(source_parent):
            item_path = source_parent / item_name
            # Check if it's a file or dir based on whether target_nfc_filename has an extension
            is_dir_target = not Path(target_nfc_filename).suffix
            
            if is_dir_target and not item_path.is_dir():
                continue
            if not is_dir_target and not item_path.is_file():
                continue

            normalized_item_name = unicodedata.normalize('NFC', item_name)
            if normalized_item_name == target_nfc_filename:
                is_nfc = (item_name == normalized_item_name)
                print(f"  FOUND: '{item_name}' (Is NFC: {is_nfc})")
                found_on_source = True
        if not found_on_source:
            print(f"  No items found that normalize to '{target_nfc_filename}'")

    # Analyze Destination
    print(f"\n[DESTINATION]: {dest_parent}")
    if not dest_parent.is_dir():
        print(f"  Error: Destination directory not found: {dest_parent}")
    else:
        found_on_dest = False
        for item_name in os.listdir(dest_parent):
            item_path = dest_parent / item_name
            is_dir_target = not Path(target_nfc_filename).suffix

            if is_dir_target and not item_path.is_dir():
                continue
            if not is_dir_target and not item_path.is_file():
                continue
            
            normalized_item_name = unicodedata.normalize('NFC', item_name)
            if normalized_item_name == target_nfc_filename:
                is_nfc = (item_name == normalized_item_name)
                print(f"  FOUND: '{item_name}' (Is NFC: {is_nfc})")
                found_on_dest = True
        if not found_on_dest:
            print(f"  No items found that normalize to '{target_nfc_filename}'")

if __name__ == "__main__":
    # Example File Analysis
    analyze_paths(
        target_nfc_filename="Frédéric Chopin - Waltz No. 1 in E-flat major, Op. 18.mp3",
        source_parent_dir_str="/Users/stencate/Desktop/Music/Loose Tracks/",
        dest_parent_dir_str="/Volumes/AGP-M2/Music/Loose Tracks/"
    )

    # Example Directory Analysis
    analyze_paths(
        target_nfc_filename="Chopin; Maria João Pires, Royal Philharmonic Orchestra, André Previn",
        source_parent_dir_str="/Users/stencate/Desktop/Music/",
        dest_parent_dir_str="/Volumes/AGP-M2/Music/"
    )

    # Example Erik Satie file that rsync was deleting from destination
    analyze_paths(
        target_nfc_filename="01. Manière de Commencement.mp3", # This is NFC
        source_parent_dir_str="/Users/stencate/Desktop/Music/Erik Satie/Trois Morceaux en Forme de Poire/",
        dest_parent_dir_str="/Volumes/AGP-M2/Music/Erik Satie/Trois Morceaux en Forme de Poire/"
    )
    
    # Example Japanese filename that rsync was deleting
    analyze_paths(
        target_nfc_filename="崖の上のポニョ Ponyo on the Cliff by the Sea - 海上自衛隊横須賀音楽隊.mp3", # NFC of the Ponyo file
        source_parent_dir_str="/Users/stencate/Desktop/Music/Loose Tracks/",
        dest_parent_dir_str="/Volumes/AGP-M2/Music/Loose Tracks/"
    ) 