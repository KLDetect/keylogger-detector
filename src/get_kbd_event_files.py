import os

# Output file path
kbd_output_file = "kbd_file_paths.txt"

# Function to follow symbolic links recursively
def follow_symlinks(filepath):
    if os.path.islink(filepath):
        resolved_path = os.path.realpath(filepath)
        with open(kbd_output_file, "a") as f:
            f.write(resolved_path + "\n")
        follow_symlinks(resolved_path)

# Traverse files in /dev/input/by-path
with open(kbd_output_file, "w") as f:
    f.write("")
for root, dirs, files in os.walk("/dev/input/by-path"):
    for filename in files:
        if "kbd" in filename:
            filepath = os.path.join(root, filename)
            follow_symlinks(filepath)

print("Keyboard file paths written to", kbd_output_file)

