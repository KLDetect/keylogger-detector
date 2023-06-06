#!/usr/bin/env python3

import sys
from config import CONFIG_FILE, load_config, save_config
from utils import (
    check_root,
    check_packages,
    get_keyboard_device_files,
    get_real_path,
    get_pids_using_file,
    get_process_name,
    kill_processes
    )

# Global variables

auto_kill_option = False
verbose_option = False
safe_option = False

# Functions

def print_help():
    print('Usage: python3 keylogger_detector.py [OPTIONS]')
    print('Options:')
    print('  -h, --help\t\t\tPrint this help message')
    print('  -v, --verbose\t\t\tVerbose mode. Will cause additional information to be printed during execution')
    print('  -a, --auto-kill\t\tAutomatically kill blacklisted processes')
    print('  -s, --safe\t\t\tSafe mode. Asked to confirm before killing a process')

def set_input_options():
    """
    Set input options based on command line arguments

    Invalid arguments are ignored

    Raises:
        SystemExit: If -h or --help is passed as an argument, the help message is printed and the program exits
    """

    global auto_kill_option, verbose_option, safe_option
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg == '-h' or arg == '--help':
                print_help()
                sys.exit(0)
            elif arg == '-v' or arg == '--verbose':
                verbose_option = True
            elif arg == '-a' or arg == '--auto-kill':
                auto_kill_option = True
            elif arg == '-s' or arg == '--safe':
                safe_option = True
   

def confirm_kill_procces(process_name, times=0):
    """
    Prompt the user to confirm to kill a process.
    Should be used only in safe mode.

    Args:
        process_name (str): Name of the process to kill
        times (int) : Number of times prompt has been displayed but neither y nor n where given. Defaults to 0. 
                      Use to limit promt attempts.

    Returns:
        bool: True if user confirms the kill, False otherwise.

    Raises:
        SystemExit: If the user has given invalid input more than 5 times, the program exits.
    """
    if times > 5:
        print('Too many invalid inputs. Exiting.')
        sys.exit(1)
    if times > 0:
        print('Invalid input. Please enter y or n.')
    print(f'Do you want to kill {process_name}? (y/n)')
    answer = input()
    if answer == 'y':
        return True
    elif answer == 'n':
        return False
    else:
        return confirm_kill_procces(process_name, times+1)

def detect_keyloggers():
    """
    Detect (userland) keylogger processes based on which processes have a keyboard file open (/dev/input/event*)

    The main function of the program.
    Will attempt to detect keyloggers based on the config file, command line arguments and user input.
    Here the control flow and logic of the program are defined.
    """

    ############################
    # 1. Setup and initialization
    ############################   
    global auto_kill_option, verbose_option, safe_option
    global CONFIG_FILE
    set_input_options()
    if verbose_option:
        print('[Verbose] Input options set')

    check_root()
    if verbose_option:
        print('[Verbose] Root access checked')
    
    check_packages()
    if verbose_option:
        print('[Verbose] Packages checked')

    config = load_config()
    if verbose_option: 
        print('[Verbose] Config file loaded')
    
    white_listed_programs = config['white_listed_programs']
    auto_kill_programs = config['auto_kill_programs']
    kbd_names = config['kbd_names']
    if verbose_option:
        print('[Verbose] Config file parsed')

    ############################
    # 2. Get device files mapped to keyboard
    ############################
    keyboard_device_files = get_keyboard_device_files(kbd_names)
    if verbose_option:
        print('[Verbose] Keyboard device files found:', keyboard_device_files)

    ############################
    # 3. Get pids using keyboard device files
    ############################
    pids = []
    for device_file in keyboard_device_files:
        pids.append(get_pids_using_file(device_file))
    pids = sorted(list(set(pids)))
    if verbose_option:
        print('[Verbose] Process IDs using keyboard device files:', pids)

    ############################
    # 4. Get process names using pids
    ############################
    process_names = []
    name_pid_dict = {}
    for pid in pids:
        name = get_process_name(pid)
        process_names.append(name)
        name_pid_dict[name].add(pid)
    process_names = sorted(list(set(process_names)))
    if verbose_option:
        print('[Verbose] Process names using keyboard device files:', process_names)

    ############################
    # 5.If auto_kill option is set, kill auto-killable processes
    ############################
    if auto_kill_option:
        for name in process_names:
            if name in auto_kill_programs:
                if verbose_option:
                    print('[Verbose] Auto-killable process found:', name)
                if safe_option:
                    if confirm_kill_procces(name):
                        kill_process(name_pid_dict[name])
                else:
                    kill_process(name_pid_dict[name])

    ############################
    # 6. Identify suspicious processes, i.e. those not whitelisted
    ############################
    suspicious_processes = []
    for name in process_names:
        if name not in white_listed_programs:
            suspicious_processes.append(name)
    if verbose_option:
        print('[Verbose] Suspicious processes found:', suspicious_processes)
        print('[Verbose] Suspicious processes not killed:', [name for name in suspicious_processes if name not in auto_kill_programs])
        print('[Verbose] Suspicious processes killed:', [name for name in suspicious_processes if name in auto_kill_programs])


    ############################
    # 6.1 If no suspicious processes are found, exit
    ############################
    if len(suspicious_processes) == 0:
        print("[+] No suspicious processes found")
        sys.exit(0)

    ############################
    # 7. Prompt user to chose which processes (not covered by auto kill if set) to kill
    ############################
    print('[-]The following suspicious processes were found:')
    for name in suspicious_processes:
        print(f'\t{name}')
    print('Please enter the names of the processes to kill, separated by a space.')
    print('To not kill any just hit enter.')
    if safe_option:
        print('[Info] You are in safe mode. In safe mode you will be asked to confirm each kill.')
    else:
        print('[Info] Please be aware that killing an important process may cause your system to crash.')

    to_kill = input().split()
    if len(to_kill) == 0:
        print('[+] No processes killed.')
        sys.exit(0)

    if verbose_option:
        print('[Verbose] Processes to kill:', to_kill)
    if safe_option:
        for name in to_kill:
            for pid in name_pid_dict[name]:
                if confirm_kill_procces(name):
                    kill_process(id)
                    if verbose_option:
                        print('[Verbose] Process killed:', name)
    else:
        for name in to_kill:
            for pid in name_pid_dict[name]:
                kill_process(id)
                if verbose_option:
                    print('[Verbose] Process killed:', name)
                    

    to_kill = list(set(to_kill))
    auto_kill_programs = list(set(auto_kill_programs))
    auto_kill_programs.extend(to_kill)
    config['auto_kill_programs'] = auto_kill_programs
    white_listed_programs = list(set(white_listed_programs))
    config['white_listed_programs'] = white_listed_programs
    kbd_names = list(set(kbd_names))
    config['kbd_names'] = kbd_names
    save_config(config, CONFIG_FILE)
    if verbose_option:
        print('[Verbose] Config file saved')

if __name__ == '__main__':
    detect_keyloggers()






        

