import subprocess
import time
import multiprocessing
import os

global Smell

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
			

#TODO Get Return-value from start_stap()			
def start_stap():
	print("Starting Sniffer")
	output = subprocess.Popen(['stap','funcall_trace.stp'],universal_newlines=True)
	if output.stdout != "":
		output.terminate()
		print("fishy")
		Smell = "fishy"
	else:
		output.terminate()
		print("nothing fishy")
		Smell = "not fishy"
	print(Smell + " smell")



	
	
	
	
def load_mod(module):
	result = subprocess.run(['sudo','insmod', module],capture_output = True, text = True)
	if result.returncode == 0:
		print(f"Loaded module: {module}")
		time.sleep(5)
	else:
		print(f"Failed to Loaded module: {module}")
		print(result.stderr)
	
	
def find_file(filename):
    result = []
    for root, dirs, files in os.walk("/"):
        if filename in files:
            file_path = os.path.join(root, filename)
            result.append(file_path)
    result_out = result[0]
    result_out = ''.join(result_out)
    return result_out
	
def getpath(sus_modules):
	for i in range(len(sus_modules)):
		sus_modules[i] = find_file(sus_modules[i] + ".ko")
	return sus_modules
	
def detect_logger(module):
	p1 = multiprocessing.Process(target=start_stap)
	p1.start()
	p2 = multiprocessing.Process(target=load_mod(module))
	p2.start()

	p1.join()
	p2.join()




#==============================================================================================================
#
#Work
#
#==============================================================================================================

whitelist = get_whitelist("whitelist.txt")

lsmod_output = list_modules("lsmod");

sus_modules = compare_mods(whitelist, lsmod_output)

sus_modules = tidy_up(sus_modules)
print(sus_modules)

sus_modules = unload_mod(sus_modules)
time.sleep(1)
print("waited")

sus_modules = getpath(sus_modules)
print(sus_modules)
if len(sus_modules) == 0:
	exit()
suspects = []
for module in range(len(sus_modules)):
	suspects.append(detect_logger(sus_modules[module]))
	
print(suspects)




