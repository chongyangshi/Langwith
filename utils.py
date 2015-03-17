import socket
import json
import os.path
from sys import exit
from re import match
from datetime import datetime
from collections import OrderedDict


def parse_json():

    """ Parse the servers.json configuration file, load JSON data into a 2-D list.
        Input: None
        Accesses: ./servers.json
        Output: (servers) % (list)
    """
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
            checks_entry = [check_count, str(check)]
            
            if JSONData[check]['type'] == 'port':
                if not (0 < JSONData[check]['port'] < 65536):
                    print "utils.py: invalid port in servers.json for check ", str(check)
                    exit(1)
                checks_entry += ['port', str(JSONData[check]['host']), JSONData[check]['port']]

            elif JSONData[check]['type'] == 'ping':
                checks_entry += ['ping', str(JSONData[check]['host'])]

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
                checks_entry += ['http', str(JSONData[check]['url']), str(JSONData[check]['look_for']), auth, JSONData[check]['verify_TLS']]

            else:
                print "utils.py: invalid check type in servers.json for check ", str(check)
                exit(1)

            checks += [checks_entry]
            check_count += 1

    JSONFile.close()
    return checks


def ip_check(serverip):

    """ Taken from EARCIS code.
        Check if the server IP passed in is a valid IPv4/v6 address, if not, return False; otherwise, return True.
        Input: (serverip) % (str)
        Outout: Boolean
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
        Outout: Boolean
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

