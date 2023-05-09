# Project Journal
## Tuesday, 09.05.2023
### Sebastian Lenzlinger
Add some structure to the project directory. 

The following keyloggers seem promising: [keylogger](https://github.com/arunpn123/keylogger) by arunpn123, which is a keylogger for Linux systems written in C. At this point my understanding is that it is a kernel level keylogger. This is what it says in the Readme. [simple-key-logger](https://github.com/gsingh93/simple-key-logger/tree/master) by gsingh93 is a userspace keylogger. It is also written in C.

Suggested steps of our kernel module:
1. Search the /dev/input/ directory and figrue out which devices correspond to the keyboard.
2. Check who is reading from that file.
3. Somehow figure out what reading is malicious and which not (?!).

Possible flow if it is clearly a user program:
1. On Start, search Keyboard file as above.
2. Start monitoring who has it open.
3. Prompt user to type (randomly)  between 5 - 30 (arbitrary at this point, just to have it limited) characters on the keyboard.
4. Trace where the input is sent.
5. List the processes using it and the files that logged it.

For either path this cannot be the final functionality. It is unclear what is and isn't feasible at this point.
#### Open Questions:
1. What is the main difference between a user space keylogger (operating as root) and a keyloger which initself is a kernel module? What are the essential differences, and is ti really feasible to implement a kernel module that detects malicious kernel activity? Would't we loose usefull abstractions like /dev/ipnut/event* etc. which make it easier to track where I/O goes?
2. What datastructures would a kernel keylogger even use, if it is not storeing the info in user space  ( a log file say). Furthermore, how would it send the info via network? How would we be able to uncover such a datastructure and make it available to a system admin. 
3. How would a kernel keylogger send smth over the network, without any user space component being able to see that (aka not even an admin)?
4. What artifacts besides kernel logs does a kernel module produce. Are any visible in userspace?
5. Would it be possible to expose kernel datastructures to userface without comprimising security?
6. Maybe the app/module is only to be run once as a scan, then one removes the malicous software component, and then returns the OS to a safe state without leakage to user space...
7. Do this questions assume the right underlying model of the linux kernel?
...? more certainly ...
#### TODOs:
1. Install both keyloggers in a VM and see how their functionality works, and how we would detect them  using system programs. This especially applies to the user space keylogger.
2. Really need to figure out where the effect of kernel module would be seen. If its just logging to a logfile then it's basically as good as a user space program and a system admin could find it. 