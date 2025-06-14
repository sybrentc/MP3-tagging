import os
import subprocess
import sys
from pathlib import Path

def convert_umx_to_mp3(input_dir):
    # Find all UMX files in the input directory
    umx_files = list(Path(input_dir).glob('*.umx'))
    print(f"Found {len(umx_files)} UMX files to convert")
    
    successful_conversions = 0
    failed_conversions = 0
    
    for umx_file in umx_files:
        wav_file = umx_file.with_suffix('.wav')
        mp3_file = umx_file.with_suffix('.mp3')
        
        # Step 1: Convert UMX to WAV using openmpt123
        print(f"Converting {umx_file.name} to WAV...")
        openmpt_cmd = [
            'openmpt123',
            '--render',
            '--output-type', 'wav',
            '--output', str(wav_file),
            '--force',
            str(umx_file)
        ]
        
        try:
            subprocess.run(openmpt_cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"Error converting to WAV: {e.stderr}")
            failed_conversions += 1
            continue
        
        # Step 2: Convert WAV to MP3 using ffmpeg
        print(f"Converting {wav_file.name} to MP3...")
        ffmpeg_cmd = [
            'ffmpeg',
            '-i', str(wav_file),
            '-codec:a', 'libmp3lame',
            '-qscale:a', '2',
            str(mp3_file)
        ]
        
        try:
            subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True)
            # Clean up the temporary WAV file
            os.remove(wav_file)
            successful_conversions += 1
        except subprocess.CalledProcessError as e:
            print(f"Error converting to MP3: {e.stderr}")
            failed_conversions += 1
            # Clean up the temporary WAV file even if MP3 conversion failed
            if os.path.exists(wav_file):
                os.remove(wav_file)
    
    print(f"\nConversion complete:")
    print(f"Successfully converted: {successful_conversions} files")
    print(f"Failed to convert: {failed_conversions} files")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python convert_umx_to_mp3.py <input_directory>")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    convert_umx_to_mp3(input_dir) 