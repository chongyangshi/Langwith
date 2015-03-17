import socket
import gevent
from gevent import monkey

monkey.patch_socket()
socket.setdefaulttimeout(2)

TEST_URL = '5.39.93.149'
TEST_PORT1 = 80
TEST_PORT2 = 222

def check_open(target):
    if not isinstance(target, tuple):
        raise ValueError("check_open(): expecting a tuple as target IP and port.")
    test_result = socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect_ex(target)
    if test_result == 0:
        return True
    else:
        return False

queries = [(TEST_URL,TEST_PORT1),(TEST_URL,TEST_PORT2)]
jobs = [gevent.spawn(check_open, target) for target in queries]
gevent.joinall(jobs, timeout=3)

print [job.value for job in jobs]