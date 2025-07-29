#!/bin/bash

# Check input
if [ -z "$1" ]; then
    echo "Usage: $0 <input_directory>"
    exit 1
fi

INPUT_DIR="$1"
OUTPUT_DIR="${INPUT_DIR%/}/converted"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Process all .wav and .mp3 files in the input directory
for file in "$INPUT_DIR"/*.{wav,mp3}; do
    # Skip if no matching file
    [ -e "$file" ] || continue

    # Get filename without extension
    filename=$(basename "$file")
    base_name="${filename%.*}"

    # Output path
    output_file="$OUTPUT_DIR/${base_name}.wav"

    # Convert or resample
    if [[ "$file" == *.mp3 ]]; then
        echo "Converting MP3 → WAV (16k): $file → $output_file"
        ffmpeg -y -i "$file" -ar 16000 -ac 1 "$output_file"
    elif [[ "$file" == *.wav ]]; then
        echo "Resampling WAV to 16k: $file → $output_file"
        ffmpeg -y -i "$file" -ar 16000 -ac 1 "$output_file"
    fi
done

echo "✅ All files processed. Output saved in: $OUTPUT_DIR"
