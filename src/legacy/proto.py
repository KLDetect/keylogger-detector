import os
import subprocess

# ===============================
# Step1: Find keyboard file paths
# ===============================

# Output file path
kbd_output_file = "kbd_file_paths.txt"

# Function to follow symbolic links recursively
def follow_symlinks(filepath):
    if os.path.islink(filepath):
        resolved_path = os.path.realpath(filepath)
        with open(kbd_output_file, "a") as output_file:
            output_file.write(resolved_path + "\n")
            follow_symlinks(resolved_path)

# Traverse files in /dev/input/by-path
with open(kbd_output_file, "w") as output_file:
    for root, dirs, files in os.walk("/dev/input/by-path"):
        for file in files:
            if "kbd" in file:
                filepath = os.path.join(root, file)
                output_file.write(filepath + "\n")
                follow_symlinks(filepath)

print("Keyboard file paths written to", kbd_output_file)

# ===============================
# Step2: Find pids using keyboard event files
# ===============================

# Use found kbd file paths to find corresponding pids
pids_input_file = kbd_output_file
pids_output_file = "pids.txt"

pids_array = []

# Get pids of processes using the keyboard and put in array
with open(pids_input_file, "r") as input_file:
    for pathname in input_file:
        pathname = pathname.strip()
        pids = subprocess.check_output(["fuser", pathname]).decode().split()
        pids_array.extend(pids)

# Sort and remove duplicates
sorted_pids = sorted(set(pids_array))
print()
print("The following pids where found:" + str(sorted_pids) + "\n")

# Write unique and sorted pids to file, separated by newlines
with open(pids_output_file, "w") as output_file:
    output_file.write("\n".join(sorted_pids) + "\n")
print("Pids written to", pids_output_file)

# ===============================
# Step3: Find processes/program names using pids
# ===============================
exe_input_file = pids_output_file
exe_output_file = "suspicious_exes.txt"

# Clear output file
with open(exe_output_file, "w") as output_file:
    output_file.write("")
exe_pid_dict = {}

for pid in sorted_pids:
    #Get name of executable from PID using process status file
    status_file_path = "/proc/" + pid + "/status"
    with open(status_file_path, "r") as status_file:
        for line in status_file:
            # See cat /proc/{pid}/status | grep "Name:"
            if line.startswith("Name:"):
                exe_name = line.split(":")[1].strip()
                exe_pid_dict[exe_name] = pid            
print("The following executables where found:" + str(exe_pid_dict) + "\n")
