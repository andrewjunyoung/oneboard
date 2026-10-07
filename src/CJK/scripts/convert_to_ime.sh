#!/bin/bash

# Convert dictionary.csv to Google Japanese IME format
# Usage: ./convert_to_ime.sh

input_file="dictionary.csv"
output_file="ime_dictionary.txt"

# Check if input file exists
if [ ! -f "$input_file" ]; then
    echo "Error: $input_file not found"
    exit 1
fi

# Remove header row and convert format
# Format: <input>\t<character>\t名詞
tail -n +2 "$input_file" | while IFS=',' read -r stroke_sequence character encoding; do
    echo -e "${encoding}\t${character}\t名詞"
done > "$output_file"

echo "Conversion complete. Output saved to $output_file"