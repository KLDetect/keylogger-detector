#!/bin/bash

# =============================== 
# Step1: Find keyboard file paths
# ===============================

# Output file path
kbd_output_file="kbd_file_paths.txt"

# Function to follow symbolic links recursively
follow_symlinks() {
  local filepath=$1

  if [[ -L $filepath ]]; then
    local resolved_path=$(readlink -f "$filepath")
    echo "$resolved_path" >> "$kbd_output_file"
    follow_symlinks "$resolved_path"
  fi
}

# Traverse files in /dev/input/by-path
echo -n > "$kbd_output_file"
find /dev/input/by-path -type l -name '*kbd*' -print0 | while IFS= read -r -d '' filepath; do
  #echo "$filepath" >> "$kbd_output_file"
  follow_symlinks "$filepath"
done

echo "Keyboard file paths written to $kbd_output_file"

# ===============================
# Step2: Find pids using keyboard event files
# ===============================

# Use found kbd file paths to find corresponding pids
pids_input_file="$kbd_output_file"
pids_output_file="pids.txt"

echo -n > "$pids_output_file"

declare -a pids_array

# Get pids of processes using the keyboard and put in array
while IFS= read -r pathname; do
    pids=$(fuser "$pathname")
    # add pids to array
    for pid in $pids; do
      pids_array+=("$pid")
    done
done < "$pids_input_file"

# sort and remove duplicates
sorted_pids=$(printf '%s\n' "${pids_array[@]}" | sort -nu)

# write unique and sorted pids to file, separated by newlines
printf '%s\n' "${sorted_pids[@]}" > "$pids_output_file"

echo "Pids written to $pids_output_file"

# ===============================
# Step3: Find processes/program names using pids
# ===============================
exe_input_file="$pids_output_file"
exe_output_file="suspicous_exes.txt"

# Clear output file
echo -n > "$exe_output_file"

