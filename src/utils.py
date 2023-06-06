import os # for path operations, getuid, kill
import subprocess # for executing shell commands
import signal # for sending signals to processes
import sys # for exit

def check_root():
    """
    Check if script is run as root(sudo).

    Raises:
        SystemExit: If not run as root.
    """
    if os.getuid() != 0:
        print("[-] Please run as root.")
        sys.exit(1)

def check_packages():
    """
    Check if all required packages are installed.

    Raises:
        SystemExit: If any packges is missing.
    """
    packages = ['fuser', 'which']
    missing_packages = []

    for package in packages:
        if subprocess.call(['which', package]) != 0:
            missing_packages.append(package)
    if len(missing_packages) > 0:
        print("[-] Missing packages: {}".format(', '.join(missing_packages)))
        sys.exit(1)

def get_keyboard_device_files(names):
    """
    Get paths corresponding to keyboard device files by searching /dev/input/by-path.
    Uses get_real_path() to resolve symlinks.

    Args:
        names (list): List of strings to use for searching. e.g.['kbd']

    Returns:
       str: Path to keyboard device file.

    """
    keyboard_device_files = []
    for root, dirs, files in os.walk('/dev/input/by-path'):
        for file in files:
            if any(name in file for name in names):
                keyboard_device_files.append(get_real_path(os.path.join(root, file)))
    return keyboard_device_files

def get_real_path(path):
    """
    Resolve a path of a file.
    Args:
        path (str): Path to a file. Possibly a symlink.
    
    Returns:
        str: The resolved (real) path.
    """
    if os.path.islink(path):
        return os.path.realpath(path)
    else:
        return path

def get_pids_using_file(path):
    """
    Get all process IDs using a file. (Essentially a wrapper for fuser.)

    Args:
        path (str): Path to a file. Usually /dev/input/eventX.

    Returns:
        list: List of process IDs.

    Raises:
        SystemExit: If fuser fails to run.
    """
    try:
        pids = subprocess.check_output(['fuser', path]).decode('utf-8').split()
    except subprocess.CalledProcessError:
        print("[-] Error: fuser failed to run on", path)
        sys.exit(1)
    return pids

def get_process_name(pid):
    """
    Get the name of a process.

    Args:
        pid (int): Process ID.

    Returns:
        str: Name of the process.
    """
    with open('/proc/{}/comm'.format(pid)) as f:
        return f.read().strip()

def kill_processes(pids):
    """
    Kill processes.

    Args:
        pids (list): List of process IDs.
    """

    for pid in pids:
        try:
            os.kill(int(pid), signal.SIGKILL)
        except ProcessLookupError:
            print("[-] Process {} not found.".format(pid))

