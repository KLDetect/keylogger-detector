import subprocess
import time
import multiprocessing

import threading

import os
import sys
from io import TextIOWrapper, BytesIO

pipe1, pipe2 = multiprocessing.Pipe()

#==============================================================================================================
#
#Functions
#
#==============================================================================================================
def list_modules(command):
	result = subprocess.run(command, shell = True, capture_output=True, text=True)
	
	if result.returncode == 0:
		return result.stdout.strip().split('\n')
	else:
		print(f"Failed with error:{result.stderr}")
		return[]

def get_whitelist(file_path):
	try:
		with open(file_path, 'r') as file:
			lines = file.read().splitlines()
			return lines
	except IOError:
		print(f'Error: Failed to load whitelist{file_path}')
		
def compare_mods(A, B):
	setA = set(A)
	setB = set(B)
	
	result = setB - setA
	
	return list(result)
	
def tidy_up(entries):
	cleaned_entries = []
	for entry in entries:
		modules = entry.split()
		if modules:
			first_mod = modules[0]
			cleaned_entries.append(first_mod)
	return cleaned_entries
			
def unload_mod(modules):
	tmp = []
	for module in modules:
		result = subprocess.run(['sudo','rmmod', module],capture_output = True, text = True)
		if result.returncode == 0:
			print(f"Unloaded module: {module}")
		else:
			print(f"Failed to unloaded module: {module}")
			tmp.append(module)
			print(result.stderr)
	result_out = compare_mods(tmp, modules)
	print(result_out)
	return result_out
			




def stap_start():
	print("starting sniffing")
	process = subprocess.Popen(['stap','funcall_trace.stp', '-T', '15'], flush = True)
	process.wait()
	print("ended sniffing")

	
def load_mod(module):
	print(module)
	for i in range(2):
		subprocess.Popen(['sudo','insmod', module])
		time.sleep(1)
		subprocess.Popen(['sudo','rmmod', module])
		time.sleep(1)
	subprocess.Popen(['sudo', 'insmod', module])
	
	
def find_file(filename):
    result = []
    for root, dirs, files in os.walk("/"):
        if filename in files:
            file_path = os.path.join(root, filename)
            result.append(file_path)
    result_out = result
    result_out = ''.join(result_out)
    return result_out
	
def getpath(sus_modules):
	for i in range(len(sus_modules)):
		sus_modules[i] = find_file(sus_modules[i] + ".ko")
	return sus_modules
	
def detect_logger(module):

	
	
	print("starting sniffing")
	process = subprocess.Popen(['stap','funcall_trace.stp', '-T', '10'], stdout=subprocess.PIPE, text=True)


	for i in range(2):
		subprocess.Popen(['sudo','insmod', module])
		time.sleep(1)
		print("-")
		subprocess.Popen(['sudo','rmmod', module])
		time.sleep(1)
	subprocess.Popen(['sudo','insmod', module])
	print("-")
	out = process.communicate()[0]

	


	print("ended sniffing")

	print(out)
	if out == "[-]":
		return module
	print("FAILED")
	return 0



#==============================================================================================================
#
#Work
#
#==============================================================================================================

def run_kernel_detection():
	whitelist = get_whitelist("whitelist.txt")

	lsmod_output = list_modules("lsmod");

	sus_modules = compare_mods(whitelist, lsmod_output)

	sus_modules = tidy_up(sus_modules)

	sus_modules = unload_mod(sus_modules)
	time.sleep(1)

	sus_modules = getpath(sus_modules)
	print(sus_modules)
	if len(sus_modules) == 0:
		print("nothing to do")
		print("ALL CLEAN")
		
	
	
	suspects = []
	for module in sus_modules:
		suspects.append(detect_logger(module))
		time.sleep(1)



	print("Following modules are logging your keystrokes: ")
	for i in range(len(suspects)):
		print( f"[{i}] {suspects[i]}")
	print("Enter the number of the module you want to remove: ")
	user_input = input().split()
	for j in user_input:
		to_remove = suspects[int(j)]
		subprocess.Popen(['sudo','rmmod', to_remove])
		print(f"Removed {to_remove}")
	print("Finished")
	
	






