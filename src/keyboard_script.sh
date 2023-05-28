#!/bin/bash

# Output file path
output_file="keyboard_files.txt"

# Find keyboard device files
keyboard_files=()
while IFS= read -r -d '' file; do
  if [[ $file == *"kbd"* || $file == *"keyboard"* ]]; then
    keyboard_files+=("$file")
  fi
done < <(find /dev/input -type c -name 'event*')

# Write keyboard files to output file
echo "Keyboard Device Files" > "$output_file"
echo "======================" >> "$output_file"

if [[ ${#keyboard_files[@]} -eq 0 ]]; then
  echo "No keyboard device files found." >> "$output_file"
else
  for file in "${keyboard_files[@]}"; do
    echo "$file" >> "$output_file"
  done
fi

echo "Keyboard files written to $output_file"

