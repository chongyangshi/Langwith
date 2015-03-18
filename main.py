import gevent
import socket
import greenlet
import urllib3
import requests
from time import sleep
from gevent import monkey

import checker
import utils

monkey.patch_socket()
socket.setdefaulttimeout(2)
urllib3.contrib.pyopenssl.inject_into_urllib3()
requests.packages.urllib3.disable_warnings()

servers = utils.parse_json()

#For testing, will be replaced with updates to user interface.
for item in servers:
    print item[0], item[1], item[2]

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

    gevent.joinall(gevent_jobs, timeout=10)

    for i in range(0,len(gevent_jobs)): #Copy the results into the result list.
        gevent_jobs_results[i][1] = gevent_jobs[i].value

    for item in gevent_jobs_results: #Match entries in the result list with servers list, and update corresponding values.
        for server in servers:
            if item[0] == server[0]:
                server[1] = item[1]

    #For testing, will be replaced with updates to user interface.
    for item in servers:
        print item[0], item[1], item[2]

    sleep(30)


                 
            