# KLDetect
KLDetect is a keylogger detector for the Linux Desktop.
It can detect processes reading from ```/dev/input/event*``` devices and kernel modules registered to listen to keyboard events.

# Dependencies
[Python](https://www.python.org/downloads/)
[SystemTap](https://sourceware.org/systemtap/wiki)

# Setup
Download or clone this repository:
```
git clone https://github.com/sebaschi/keylogger-detector.git
```

Run a keylogger. KLDetect has been tested and shown to work on the following keylogger.

User progams:

* [simple-key-logger](https://github.com/gsingh93/simple-key-logger/tree/master)
* [logkeys](https://github.com/kernc/logkeys)
* [keylog](https://github.com/SCOTPAUL/keylog)
Kernel Module:

* [spy](https://github.com/jarun/spy)

# Developers
Copyright 2023 [Michel Romancuk](https://github.com/SoulKindred), [Sebastian Lenzlinger](https://github.com/sebaschi)





This project is Part of a Univeristy project at the [Operating Systems](https://dmi.unibas.ch/de/studium/computer-science-informatik/lehrangebot-fs23/vorlesung-operating-systems-1/) lecture at the University of Basel, Switzerland.
 A project journal can be found [here](https://github.com/sebaschi/keylogger-detector/blob/main/doc/dev_journal.md).
