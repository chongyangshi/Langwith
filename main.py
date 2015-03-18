#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# The MIT License (MIT)
# Copyright (c) 2015 icydoge (icydoge@gmail.com)
# For full license details, see LICENSE.
#
# Langwith.main: this is the main module that should be ran from the command line.

import socket
import curses
from time import sleep
from sys import exit

import gevent
import greenlet
import urllib3
import requests
from gevent import monkey

import checker
import utils

#Initialise socket and requests configs.
monkey.patch_socket()
socket.setdefaulttimeout(2)
urllib3.contrib.pyopenssl.inject_into_urllib3()
requests.packages.urllib3.disable_warnings()

#Read config.
servers, settings = utils.parse_json()

#Initialise curses.
stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
curses.start_color()
stdscr.keypad(1)
curses.use_default_colors()
curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)   #Colour scheme for entries that are UP.
curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_GREEN) #Colour scheme for entries that are DOWN.
stdscr.clear()
stdscr.refresh()

try:
    current_window_size = stdscr.getmaxyx()
    if current_window_size[1] < 62:
        raise SystemExit
except SystemExit:
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()
    curses.nocbreak() 
    print "Curses Error: Oops, the current terminal window size is not wide enough for the program. Please try to adjust font size or enlarge the window."
    exit(0)

def interface_keystroke():
    """Captures user keystrokes on the interface."""
    key_event = stdscr.getch()
    if key_event == ord("q"):
        interface_quit()

        
def interface_quit():
    """ Exit the interface on request ("q" press)."""
    curses.nocbreak() 
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()
    exit(0)

#Loading screen.
stdscr.addstr(0, 0, "Langwith Server Monitoring System", curses.color_pair(0) | curses.A_BOLD)
stdscr.addstr(3, 0, "Initialising, please wait...", curses.color_pair(0) | curses.A_DIM)
stdscr.addstr(6, 0, "Press Ctrl+C to exit monitoring.", curses.color_pair(0) | curses.A_DIM)
stdscr.refresh()


try:
    while True:

        gevent_jobs = []
        gevent_jobs_results = []

        for item in servers:
            if item[3] == 'port':
                if not utils.ip_check(item[4]): #Request DNS resolve every time for domain entries.
                    try:
                        port_check_host_name = socket.gethostbyname(item[4])
                    except socket.gaierror:     #When domain cannot be resolved.
                        item[1] = False         #If unresolvable, it is down.
                        continue
                else:
                    port_check_host_name = item[4]
                gevent_jobs += [gevent.spawn(checker.check_port_open, (port_check_host_name, item[5]))]
                gevent_jobs_results += [[item[0], False]]

            elif item[3] == 'ping':
                if not utils.ip_check(item[4]): #Request DNS resolve every time for domain entries.
                    try:
                        ping_check_host_name = socket.gethostbyname(item[4])
                    except socket.gaierror:     #When domain cannot be resolved.
                        item[1] = False         #If unresolvable, it is down.
                        continue
                else:
                    ping_check_host_name = item[4]
                gevent_jobs += [gevent.spawn(checker.check_remote_ping, ping_check_host_name)]
                gevent_jobs_results += [[item[0], False]]

            elif item[3] == 'http':
                gevent_jobs += [gevent.spawn(checker.check_HTTP_response_content, item[4], item[5], item[6], item[7])]
                gevent_jobs_results += [[item[0], False]]

        gevent.joinall(gevent_jobs, timeout=13)

        for i in range(0,len(gevent_jobs)): #Copy the results into the result list.
            gevent_jobs_results[i][1] = gevent_jobs[i].value

        for item in gevent_jobs_results: #Match entries in the result list with servers list, and update corresponding values.
            for server in servers:
                if item[0] == server[0]:
                    server[1] = item[1]
        at_least_one_server_down = False
        for item in servers:
            if item[1] == False:   #Trigger at-least-one-server-down indicator.
                at_least_one_server_down = True
                utils.log_error(server[2] + " is checked to be down.")
                break
        
        display_matrix = []
        for item in servers:
            if item[1] == True:     #Entry is UP.
                display_matrix += [[True, utils.fix_width(4, str(item[0]+1)) + utils.fix_width(30, str(item[2])) + "   " + str(item[3])]]
            elif item[1] == False:  #Entry is DOWN.
                display_matrix += [[False, utils.fix_width(4, str(item[0]+1)) + utils.fix_width(30, str(item[2])) + "   " + str(item[3])]]
            #item[0]+1 so that server ID starts from 1 on display

        #Start drawing.
        stdscr.clear()
        stdscr.refresh()
        
        #Drawing header.
        stdscr.addstr(0, 0, "Langwith Server Monitoring System", curses.color_pair(0) | curses.A_BOLD)
        if at_least_one_server_down == True:
            stdscr.addstr(0, 38, "At least one entry DOWN!", curses.color_pair(1) | curses.A_BOLD | curses.A_BLINK)
        else:
            stdscr.addstr(0, 38, "All entries are UP.", curses.color_pair(2) | curses.A_BOLD)
        stdscr.addstr(1, 0, "", curses.color_pair(0))
        stdscr.addstr(2, 0, "Status  No.  Monitor Name                   Monitor Type ", curses.color_pair(0) | curses.A_STANDOUT)
        
        #Drawing body.
        line_counter = 3
        for item in display_matrix:
            stdscr.addstr(line_counter,0,"", curses.color_pair(0))
            if item[0] == True:
                stdscr.addstr(line_counter+1, 0, "IS UP", curses.color_pair(2) | curses.A_BOLD)
                stdscr.addstr(line_counter+1, 8, item[1], curses.color_pair(0))  
            else:
                stdscr.addstr(line_counter+1, 0, "DOWN!", curses.color_pair(1) | curses.A_BOLD | curses.A_BLINK)
                stdscr.addstr(line_counter+1, 8, item[1], curses.color_pair(0))  
            line_counter += 2

        #Drawing footer.
        stdscr.addstr(line_counter, 0, "", curses.color_pair(0))
        stdscr.addstr(line_counter+1, 0, "", curses.color_pair(0))
        refresh_interval_string = "Refresh Interval: " + str(settings[0]) + " seconds."
        stdscr.addstr(line_counter+2, 0, refresh_interval_string, curses.color_pair(0))
        stdscr.addstr(line_counter+3, 0, "", curses.color_pair(0))
        stdscr.addstr(line_counter+4, 0, "Press Ctrl+C to exit monitoring.", curses.color_pair(0) | curses.A_DIM)
        stdscr.refresh()

        #Play alarm if needed.
        if (settings[1] == True) and (at_least_one_server_down):
            curses.beep()
            curses.beep()
            curses.beep()

        sleep(int(settings[0]))

except curses.error:       #Clean-up before quitting.
    curses.nocbreak() 
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()
    print "Curses Error: Oops, the current terminal window is not long enough for the program. Please try to adjust font size or enlarge the window."
    exit(1)

except (KeyboardInterrupt, SystemExit): #Clean-up before quitting.
    interface_quit()
    raise
            