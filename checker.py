#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# The MIT License (MIT)
# Copyright (c) 2015 icydoge (icydoge@gmail.com)
# For full license details, see LICENSE.
#
# Langwith.checker: this module contains the three functions for checking if a target hostname/IP/url is reachable.

import socket
from os import system

import requests
import urllib3.contrib.pyopenssl
from gevent import monkey

import utils

#Initialise socket and requests configs.
monkey.patch_socket()
socket.setdefaulttimeout(2)
urllib3.contrib.pyopenssl.inject_into_urllib3()
requests.packages.urllib3.disable_warnings()


def check_port_open(target):

    """ Check if a TCP port is open on the target server. 
        If the first attempt failed, function will make two more attempts before returning False.
        Otherwise, True will be returned.
        The function assumes that the server IP and Port passed in are valid.
        Input: ((server_ip, server_port) % (str, int))
        Outout: Boolean
        For this function, passing in a host name is not allowed.
    """

    if not isinstance(target, tuple):
        raise ValueError("check_port_open(): expecting a tuple as target IP and port.")
    
    try:
        test_result = socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect_ex(target)
        
        if test_result == 0:
            return True
        
        else:
            retry_count = 0
            while retry_count <= 2:
                if socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect_ex(target) == 0:
                    return True
                    break
                else:
                    retry_count += 1
            return False
   
    except:
        error_log = "check_port_open(): " + str(target) + " is not a valid IP to test."
        utils.log_error(error_log)
        return False


def check_remote_ping(target):

    """ Send two ping tests to a remote server.
        Return True if ping reachable, False otherwise.
        Input: (server_ip) % (string)
        Output: Boolean
    """

    if not utils.ip_check(target):
        error_log = "check_remote_ping(): " + str(target) + " is not a valid IP to test."
        utils.log_error(error_log)
        return False

    else:
        ping_response = system("ping -c 2 -t 2 " + target + " > /dev/null 2>&1")
        if ping_response == 0:
            return True
        else:
            return False


def check_HTTP_response_content(target, test_string='', auth_credentials=None, verify_TLS_certificate=True):

    """ This function makes a GET request to the target.
        A two-second timeout is enforced to prevent issues due to large responses.
        Optionally the function can utilise HTTP Auth credentials. Note that if HTTP Auth fails, then 
        Optionally the function can check if a string is present in the response.
        Optionally the function can be set to not verify remote TLS identity. If the function verifies remote identity,
        and the remote identity cannot be validated, then the function WILL return False.
        The function assumes that the target address and Port passed in are valid.
        Input: (target, test_string, TLS_verify, auth_credentials) % (str, str, Boolean, tuple)        
                target is a full URL.
        Outout: Boolean
    """
    if verify_TLS_certificate != True:
        verify_TLS_certificate == False 

    try:
        if auth_credentials != None:
            if not isinstance(auth_credentials, tuple):
                raise ValueError("check_HTTP_response_content(): expecting a tuple of authentication credentials credentials.")
            response = requests.get(str(target), timeout=2, verify=verify_TLS_certificate, auth=auth_credentials)
        else:
            response = requests.get(str(target), timeout=2, verify=verify_TLS_certificate)
        
        if test_string != '':
            response_content = response.content
            if str(test_string) in response_content:
                return True
            else:
                return False
        
        else:
            if (200 <= response.status_code < 400):
                return True
            else:
                return False

    except requests.exceptions.InvalidSchema: #malformed target URL
        error_log = "check_HTTP_response_content(): " + str(target) + " is not a valid URL to GET."
        utils.log_error(error_log)
        return False

    except requests.exceptions.SSLError: #TLS verification error
        error_log = "check_HTTP_response_content(): " + str(target) + " does not bear a valid TLS certificate!"
        utils.log_error(error_log)
        return False

    except:
        error_log = "check_HTTP_response_content(): " + str(target) + " triggered an unknown error."
        utils.log_error(error_log)
        return False

