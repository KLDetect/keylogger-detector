#!/bin/bash

# Output file path
output_file="keyboard_info.txt"

# Step 1: Find keyboard device files
keyboard_files=()
while IFS= read -r -d '' file; do
  if [[ $file == *"kbd"* || $file == *"keyboard"* ]]; then
    keyboard_files+=("$file")
  fi
done < <(find /dev/input/by-path -type l -name 'event*')

# Step 2: Check processes with open keyboard files
echo "Keyboard Information" > "$output_file"
echo "=====================" >> "$output_file"

for keyboard_file in "${keyboard_files[@]}"; do
  echo "Keyboard device file: $keyboard_file" >> "$output_file"

  event_file=$(readlink -f "$keyboard_file")
  echo "Event file: $event_file" >> "$output_file"

  pids=$(fuser -v "$event_file" 2>/dev/null | awk -F'[: ]+' 'NR>1{print $2}')
  echo "PIDs with file open: $pids" >> "$output_file"

  # Step 3: Check corresponding programs
  echo "Corresponding Programs" >> "$output_file"
  echo "---------------------" >> "$output_file"

  for pid in $pids; do
    program=$(readlink -f "/proc/$pid/exe")
    echo "PID $pid corresponds to program: $program" >> "$output_file"
  done

  echo >> "$output_file"
done

echo "Keyboard information written to $output_file"

