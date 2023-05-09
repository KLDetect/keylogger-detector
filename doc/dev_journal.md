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
2. 