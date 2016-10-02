#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# The MIT License (MIT)
# Copyright (c) 2015 icydoge (icydoge@gmail.com)
# For full license details, see LICENSE.
#
# Langwith.setup: setup script, calling pip to install modules required.

import pip
from os import name

def print_separator():
    print("-------------------------------------")

def pip_install(packages):
    for package in packages:
        print("Langwith: installing dependency package " + str(package) + "...")
        pip.main(['install', package])
        print_separator()

generic_dependencies = ['gevent', 'greenlet', 'pyopenssl', 'ndg-httpsclient', 'pyasn1', 'urllib3', 'requests']

# Example
if __name__ == '__main__':

    print("Langwith: Set up initiating...")
    print_separator()

    if name == "nt":
        print("Langwith: We seems to be on Windows, installing ported curses for command line graphics:")
        pip_install(['vendor/curses-2.2-cp35-none-win32.whl']) #Curses for Windows
    
    print_separator()
    print("Langwith: Installing dependencies for all platforms...")
    pip_install(generic_dependencies)
    print("Langwith: Finished installing dependencies, if you see no error messages you can now execute 'python main.py' to start running Langwith.")
    
else:
    print("Langwith: Please execute setup.py by itself.")
