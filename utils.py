#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# The MIT License (MIT)
# Copyright (c) 2015 icydoge (icydoge@gmail.com)
# For full license details, see LICENSE.
#
# Langwith.utils: this module provides utility functions for other parts of the program.

import socket
import json
import os.path
import re
import requests
from sys import exit
from datetime import datetime
from collections import OrderedDict


def parse_json():

    """ Parse the servers.json and settings.json configuration files, load JSON data into lists.
        Input: None
        Accesses: ./servers.json, ./settings.json
        Output: (servers, settings) % (list, list)
    """

    #Parse config file.
    if not os.path.isfile('./settings.json'):
        print "utils.py: settings.json does not exist!"
        exit(1)

    with open('settings.json') as SettingsFile:

        SettingsData = json.load(SettingsFile, object_pairs_hook=OrderedDict)

        refresh_interval = int(SettingsData['refresh_interval'])
        play_alarm = False
        
        if not (15 <= refresh_interval <= 300):
            print "utils.py: In settings.json, 'refresh_interval' can only be set between 15 and 300 (seconds)!"
            exit(1)

        if SettingsData['play_alarm'] == True:
            play_alarm = True

        if SettingsData['mail_notification'] == True:
            
            domain_check = re.compile("^([a-zA-Z0-9](?:(?:[a-zA-Z0-9-]*|(?<!-)\.(?![-.]))*[a-zA-Z0-9]+)?)$")
            key_check = re.compile("^[\w\d_-]*$")
            email_check = re.compile("([^@|\s]+@[^@]+\.[^@|\s]+)")
            
            if (domain_check.search(SettingsData['mailgun_domain']) is None) or (SettingsData['mailgun_domain'] == ""):
                print "utils.py: In settings.json, 'mailgun_domain' must be a valid domain name verified with Mailgun!"
                exit(1)

            if (not SettingsData['mailgun_key'].startswith("key-")) or (key_check.search(SettingsData['mailgun_key'][4:]) is None):
                print "utils.py: In settings.json, 'mailgun_key' must be a valid Mailgun API Key starts with 'key-'!"
                exit(1)

            mail_notification = True
            mailgun_domain = str(SettingsData['mailgun_domain'])
            mailgun_key = str(SettingsData['mailgun_key'])
            mail_recipients = []

            if SettingsData["mail_notification_recipients"] == []:
                print "utils.py: In settings.json, 'mail_notification_recipients' does not contain an email address to send notifications to!"
                exit(1)

            for email in SettingsData["mail_notification_recipients"]:
                if email_check.search(str(email)) is None:
                    print "utils.py: In settings.json, " + str(email) + " is not a valid email address!"
                    exit(1)
                else:
                    mail_recipients.append(str(email))

        else:

            mail_notification = False
            mailgun_domain = ""
            mailgun_key = ""
            mail_recipients = []

        settings = [refresh_interval, play_alarm, mail_notification, [mailgun_domain, mailgun_key], mail_recipients]

    #Parse servers config.
    if not os.path.isfile('./servers.json'):
        print "utils.py: servers.json does not exist!"
        exit(1)

    checks = []
    check_count = 0
    
    with open('servers.json') as JSONFile:
        
        JSONData = json.load(JSONFile, object_pairs_hook=OrderedDict)
        
        if len(JSONData) == 0:
            print "utils.py: servers.json contains no check."
            exit(1)

        for check in JSONData:
            checks_entry = [check_count, False, str(check)] #initialise current state, False = down, True = up; we start from down
            
            if JSONData[check]['type'] == 'port':

                if not (port_check(JSONData[check]['port'])):
                    print "utils.py: invalid port in servers.json for check ", str(check)
                    exit(1)

                checks_entry += ['port', str(JSONData[check]['host']), JSONData[check]['port'], False]  #Email notification sent, False = not sent, reset to False when back up.

            elif JSONData[check]['type'] == 'ping':
                checks_entry += ['ping', str(JSONData[check]['host']), False]  #Email notification sent, False = not sent, reset to False when back up.

            elif JSONData[check]['type'] == 'http':

                if not (JSONData[check]['url'].startswith('https://') or JSONData[check]['url'].startswith('http://')):
                    print "utils.py: invalid url in servers.json for HTTP/HTTPS check ", str(check)
                    exit(1)

                if not 'look_for' in JSONData[check]:
                    JSONData[check]['look_for'] = ''

                if 'verify_TLS' in JSONData[check]:

                    if not (JSONData[check]['verify_TLS'] == False):
                        JSONData[check]['verify_TLS'] = True

                else:
                    JSONData[check]['verify_TLS'] = True

                if ('auth_user' in JSONData[check]) and ('auth_pass' in JSONData[check]):

                    if (JSONData[check]['auth_user'] == '' and JSONData[check]['auth_pass'] == ''):
                        auth = None
                    
                    else:
                        auth = (JSONData[check]['auth_user'], JSONData[check]['auth_pass'])
                else:
                    auth = None
                
                checks_entry += ['http', str(JSONData[check]['url']), str(JSONData[check]['look_for']), auth, JSONData[check]['verify_TLS'], False]  #Email notification sent, False = not sent, reset to False when back up.

            else:
                print "utils.py: invalid check type in servers.json for check ", str(check)
                exit(1)

            checks += [checks_entry]
            check_count += 1

    JSONFile.close()
    SettingsFile.close()

    return checks, settings


def ip_check(serverip):

    """ Taken from EARCIS code.
        Check if the server IP passed in is a valid IPv4/v6 address, if not, return False; otherwise, return True.
        Input: (serverip) % (str)
        Output: Boolean
    """

    try:
        socket.inet_aton(serverip) #Would fail if it is not a valid IPv4 address.
    
    except socket.error:
        
        try:
            socket.inet_pton(socket.AF_INET6, serverip) #Would fail if it is not a valid IPv6 address.
        
        except socket.error:
            return False
    
    return True


def port_check(serverport):

    """ Taken from EARCIS code.
        Check if the server port passed in is a valid TCP port if not, return False; otherwise, return True.
        Input: (serverport) % (int)
        Output: Boolean
    """

    if not (0 < serverport < 65536):
        return False
    
    return True


def log_error(error_content):

    """ Log error into log file.
        Input: (error_content) % (str)
        Output: None
    """
    error_content = str(datetime.now()) + " " + str(error_content) + "\n"
    with open("logs.txt", "a") as log_file:
        log_file.write(error_content)


def fix_width(width, input_string):

    """ Cut or stuff the input string into a fixed width, by truncating longer ones and adding spaces to shorter ones.
        Input: (width, input_string) % (int, str)
        Output: (fixed_width_string) % (str)
    """
    input_string = str(input_string)
    width = int(width)

    if len(input_string) >= width:
        input_string = input_string[:width-3] + "..."
    else:
        input_string = input_string + ' ' * (width - len(input_string))

    return input_string


def send_down_notification(monitor_name, monitor_type, mailgun_credentials, mail_recipients):

    """ Send email notification to defined recipients through Mailgun API, if desired in the settings.
        Input: (monitor_name, monitor_type, mailgun_credentials, recipients) % (str, str, [str, str], [mail_notification_recipients])
        Output: (send_result) % (Boolean)
    """

    if monitor_type == "port":
        down_message = "This is an automated email sent by Langwith. \n\nLangwith has detected that TCP Port Monitor '" + monitor_name + "' is down as of system time " + str(datetime.now()) + ". \n\nRegards, \nLangwith Monitoring running on " + str(os.uname()[1])
    elif monitor_type == "ping":
        down_message = "This is an automated email sent by Langwith. \n\nLangwith has detected that ICMP Ping Monitor '" + monitor_name + "' is down as of system time " + str(datetime.now()) + ". \n\nRegards, \nLangwith Monitoring running on " + str(os.uname()[1])
    elif monitor_type == "http":
        down_message = "This is an automated email sent by Langwith. \n\nLangwith has detected that HTTP/HTTPS Monitor '" + monitor_name + "' is down as of system time " + str(datetime.now()) + ". \n\nRegards, \nLangwith Monitoring running on " + str(os.uname()[1])
    else:
        return False    #should never happen, since we have checked the type of a monitor in configuration parse_json().

    down_subject = monitor_name + " Is Down. (Langwith Monitoring)"
    down_email_sender = "Langwith Monitoring <monitoring@" + str(mailgun_credentials[0]) + ">"
    mailgun_api_url = "https://api.mailgun.net/v2/" + str(mailgun_credentials[0]) + "/messages"
    requests.post(mailgun_api_url, auth=("api", mailgun_credentials[1]), data={"from": down_email_sender, "to": mail_recipients, "subject": down_subject, "text": down_message})

    return True




