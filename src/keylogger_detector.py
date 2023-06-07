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
    kill_processes,
    kill_process
    )

# Global variables/CLI options

auto_kill_option = False
verbose_option = False
safe_option = False
add_white_list_option = False
add_black_list_option = False
debug_option = False

# Functions
def debug(option, to_print):
    if option:
        print('[Debug]', to_print)

def print_help():
    print('Usage: python3 keylogger_detector.py [OPTIONS]')
    print('Options:')
    print('  -h, --help\t\t\tPrint this help message')
    print('  -v, --verbose\t\t\tVerbose mode. Informative information will be displayed duting execution')
    print('  -a, --auto-kill\t\tAutomatically kill blacklisted processes')
    print('  -s, --safe\t\t\tSafe mode. Asked to confirm before killing a process')
    print('  -w, --add-white-list\t\t\tActivate prompt to add program names to the whitelist') #For some reason this line gets messed up in display 
    print('  -b, --add-black-list\t\t\tAutomatically add program names chosen to kill to the blacklist')
    print('  -d, --debug\t\t\tDebug mode. Print debug statements')

def set_input_options():
    """
    Set input options based on command line arguments

    Invalid arguments are ignored

    Raises:
        SystemExit: If -h or --help is passed as an argument, the help message is printed and the program exits
    """

    global auto_kill_option, verbose_option, safe_option, add_white_list_option
    global debug_option, add_black_list_option
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            print(arg)
            if arg == '-h' or arg == '--help':
                print_help()
                sys.exit(0)
            elif arg == '-v' or arg == '--verbose':
                verbose_option = True
            elif arg == '-a' or arg == '--auto-kill':
                auto_kill_option = True
            elif arg == '-s' or arg == '--safe':
                safe_option = True
            elif arg == '-w' or arg == '--add-white-list' :
                add_white_list_option = True
            elif arg == '-b' or arg == '--add-black-list':
                add_black_list_option = True
            elif arg == '-d' or arg == '--debug':
                debug_option = True
   

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
    print('Do you want to kill {}? (y/n)'.format(process_name))
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
    debug(True, str(sys.argv)) # Set manually to debug if args are being read
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

    debug(debug_option, 'Whitelist option: ' + str(add_white_list_option))
    debug(debug_option, 'Vebose option: ' + str(verbose_option))
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
        pids += get_pids_using_file(device_file)
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
        name_pid_dict.setdefault(name, []).append(pid) 
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
                        kill_processes(name_pid_dict[name])
                else:
                    kill_processes(name_pid_dict[name])
                if verbose_option:
                    print('[Verbose] Process auto-killed:', name)

    ############################
    # 6. Identify suspicious processes, i.e. those not whitelisted
    ############################
    suspicious_processes = []
    for name in process_names:
        if name not in white_listed_programs and not in auto_kill_programs:
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
    
    if safe_option:
        print('[Safe] You are in safe mode. In safe mode you will be asked to confirm each kill.')
        print('[Safe] Please be aware that killing an important process may cause your system to crash.')

    print('Please enter the names of the processes to kill, separated by a space.')
    print('To not kill any just hit enter.')

    to_kill = input().split()
    if len(to_kill) == 0:
        print('[+] No processes to kill.')

    if verbose_option:
        print('[Verbose] Processes to kill:', to_kill)

    # If the safe_option is set, prompt the user to confirm each kill
    if safe_option:
        for name in to_kill:
            for pid in name_pid_dict[name]:
                if confirm_kill_procces(name):
                    debug(debug_option, 'Killing process: ' + name)
                    debug(debug_option, 'type(id): ' + str(type(pid)))
                    kill_process(id)
                    if verbose_option:
                        print('[Verbose] Process killed:', name)
    else:
        for name in to_kill:
            for pid in name_pid_dict[name]:
                debug(debug_option, 'Killing process: ' + name)
                debug(debug_option, 'type(id): ' + str(type(pid)))
                kill_process(pid)
                if verbose_option:
                    print('[Verbose] Process killed:', name)
                    

    ############################
    # 8. Update whitelist and/or blacklist if options set
    ############################
    debug(debug_option, 'Whitelist option:' + str(add_white_list_option))
    if add_white_list_option:
        print('Please type the names of any process to whitelist, separated by a spcace.')
        to_whitelist = input().split()
        if len(to_whitelist) == 0 and verbose_option:
            print('[Verbose] No processes chosen to whitelist.')
        else: 
            white_listed_programs += to_whitelist
            if verbose_option:
                print('[Verbose] Newly whitelisted programs: ', to_whitelist)

    to_kill = list(set(to_kill))

    if add_black_list_option:
        auto_kill_programs.extend(to_kill)
        if verbose_option:
            print('[Verbose] Newly blacklisted programs: ', to_kill)

    ###########################
    # 9. Cleanup
    ###########################
    auto_kill_programs = list(set(auto_kill_programs))
    config['auto_kill_programs'] = auto_kill_programs
    white_listed_programs = list(set(white_listed_programs))
    config['white_listed_programs'] = white_listed_programs
    kbd_names = list(set(kbd_names))
    config['kbd_names'] = kbd_names
    save_config(config)
    if verbose_option:
        print('[Verbose] Config file saved')
    
    print('[+] Program completed. Exiting.')

if __name__ == '__main__':
    detect_keyloggers()






        

