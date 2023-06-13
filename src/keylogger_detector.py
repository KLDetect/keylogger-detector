#!/usr/bin/env python3
import subprocess
import time
import os
import sys
from config import CONFIG_FILE, load_config, save_config
from utils import (
    check_platform,
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
kernel_detection_option = False


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
    print('  -w, --add-white-list\t\tActivate prompt to add program names to the whitelist') #For some reason this line gets messed up in display 
    print('  -b, --add-black-list\t\tAutomatically add program names chosen to kill to the blacklist')
    print('  -d, --debug\t\t\tDebug mode. Print debug statements')
    print(' -k, --kernel-detection\t\tRun the kernel keylogger detector, too. CURRENTLY NOT IMPLEMENTED TO DIRECTLY RUN KERNEL DETECTOR.')

def set_input_options():
    """
    Set input options based on command line arguments

    Invalid arguments are ignored

    Raises:
        SystemExit: If -h or --help is passed as an argument, the help message is printed and the program exits
    """

    global auto_kill_option, verbose_option, safe_option, add_white_list_option
    global debug_option, add_black_list_option, kernel_detection_option
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
            elif arg == '-k' or arg == '--kernel-detection':
                kernel_detection_option = True
   

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


def detect_kernel(module):
        """
        Start the systemtap-script.
        load and unload modules twice.
        load module when finished.
        
        Args:
            module(str): Path + name of the module being tested
        
        Returns:
            String: Path + name of the module that is logging keystrokes  
        """        
        if verbose_option:
            print('[Verbose] Started kernel keylogger detection')
        process = subprocess.Popen(['stap','funcall_trace.stp', '-T', '10'], stdout=subprocess.PIPE, text=True)


        for i in range(2):
            subprocess.Popen(['sudo','insmod', module])
            time.sleep(1)
            print(".", end="")
            subprocess.Popen(['sudo','rmmod', module])
            time.sleep(1)
        subprocess.Popen(['sudo','insmod', module])
        print(".")
        out = process.communicate()[0]
        if verbose_option:
            print('[Verbose] Started kernel keylogger detection')

        print(out)
        if out == "[-]":
       	    return module
        print("FAILED")
        return 0
		
def getpath(sus_modules):
	"""
	Gets the path of a list of modules being tested
	calls "find_file()" function
	
	Args:
	    List[module(str)] List of all modules being tested
	    
	Returns:
	    List[modules(str)]List of the Path of all modules being tested
	"""
	for i in range(len(sus_modules)):
		sus_modules[i] = find_file(sus_modules[i] + ".ko")
	return sus_modules
		
def find_file(filename):
    """
    Searches for a file begining at root
    
    Args:
        filename(str) The filename one is looking for
        
    Returns:
        result_out(str) 'The Path_to_Module/Module_name'
    """
    result = []
    for root, dirs, files in os.walk("/"):
        if filename in files:
            file_path = os.path.join(root, filename)
            result.append(file_path)
    result_out = result
    result_out = ''.join(result_out)
    return result_out

def unload_mod(modules):
	"""
	Unloads modules.
	
	Args:
	    module(str) the module that needs to be unloaded. Has to be Path_to_Module/Module_name
	"""
	tmp = []
	for module in modules:
		result = subprocess.run(['sudo','rmmod', module],capture_output = True, text = True)
		if result.returncode == 0:
			if verbose_option:
				print(f"[Verbose] Unloaded module: {module}")
		else:
			if verbose_option:
				print(f"[Verbose] Failed to unloaded module: {module}")
				print("[Verbose] " + result.stderr)
			tmp.append(module)
	result_out = compare_mods(tmp, modules)
	if verbose_option:
		print("[Verbose] ", end="")
		print(result_out)
	return result_out
		
		
def tidy_up(entries):
	"""
	Takes a txt file and removes everything except the first word of a line
	
	Args:
	    File(.txt) in this usecase a whitelist.txt
	    
	Returns:
	    clean_entries(List[str]) List of only the first wrod from each line
	"""
	cleaned_entries = []
	for entry in entries:
		modules = entry.split()
		if modules:
			first_mod = modules[0]
			cleaned_entries.append(first_mod)
	return cleaned_entries
		
def compare_mods(A, B):
	"""
	Does set-suptraction to.
	
	Args:
	    A(list[str]) List of elements one wants to ignore 
	    B(list[str]) List of elements that one wants without all elements in A
	    
	Returns:
	    result(list[str] List of elements that are in B but not in A
	"""
	setA = set(A)
	setB = set(B)
	
	result = setB - setA
	
	return list(result)


def get_whitelist(file_path):
	"""
	reads a text-file
	
	Args:
	    file_path(str) Path to file one wants to read
	    
	Returns:
	    lines(list[str]) List of each line from a file
	"""
	try:
		with open(file_path, 'r') as file:
			lines = file.read().splitlines()
			return lines
	except IOError:
		print(f'Error: Failed to load whitelist{file_path}')
			
def list_modules(command):
	"""
	Calls a command in terminal
	
	Args:
	    command(str) the command one wants to execute
	    
	Returns:
	    result(list[std]) List of each line the command has as an output.
	"""

	result = subprocess.run(command, shell = True, capture_output=True, text=True)
	
	if result.returncode == 0:
		return result.stdout.strip().split('\n')
	else:
		print(f"Failed with error:{result.stderr}")
		return[]



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
    check_platform()

    global auto_kill_option, verbose_option, safe_option, add_white_list_option, kernel_detection_option, debug_option
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
        if (name not in white_listed_programs and name not in auto_kill_programs) or (name in auto_kill_programs and not auto_kill_option):
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
        if not kernel_detection_option:
            exit(0)

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
    
    


   
    debug(debug_option, 'Kernel detection option: ' + str(kernel_detection_option))
    
    ###########################
    # 10. If kernel_detection_option is set, run kernel detection
    ###########################
    
    
    if kernel_detection_option:
        whitelist = get_whitelist("whitelist.txt")
        lsmod_output = list_modules("lsmod")
        sus_modules = compare_mods(whitelist, lsmod_output)
        sus_modules = tidy_up(sus_modules)
        sus_modules = unload_mod(sus_modules)
        time.sleep(1)
        sus_modules = getpath(sus_modules)
        suspects = []
        if verbose_option:
            print("[Verbose] ", end="")
            print(sus_modules)
        if len(sus_modules) == 0 and verbose_option:
            print("[Verbose] Nothing to do")
		    
        for module in sus_modules:
            if module == '': #if modules have an empty path, they are in root
        	    break
            suspects.append(detect_kernel(module))
            time.sleep(1)

        print("Following modules are logging your keystrokes: ")
        for i in range(len(suspects)):
            print( f"[{i}] {suspects[i]}")
        print("Enter the number of the module you want to remove: ")
        user_input = input().split()
        to_remove = []
        for j in user_input:
            to_remove = suspects[int(j)]
            subprocess.Popen(['sudo','rmmod', to_remove])
        if len(to_remove) < 1:
            print(f"Removed {to_remove}")
        
    print('[+] Program completed. Exiting.')		
		
    
    



if __name__ == '__main__':
    detect_keyloggers()
    





        

