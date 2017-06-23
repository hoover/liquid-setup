#!/usr/bin/env python3
import socket
import subprocess

def dig_for(hostname):
    proc = subprocess.run(['dig', hostname, '@localhost', '+short'], check=False, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    return proc.stdout.decode('latin-1').strip()

def json_for(hostname):
    return json.loads(urllib.request.urlopen('http://{}/nodes'.format(hostname)).read().decode('utf-8'))

def get_hostname():
    return socket.gethostname()

RIGHT_IP_ADDRESSES = {
    'vagrant-box-one.liquid': '10.0.0.20',
    'vagrant-box-two.liquid': '10.0.0.27',
    'vagrant-box-three.liquid': '10.0.0.23',
}

def test_dns_addresses():
    hostname = get_hostname()
    if hostname not in RIGHT_IP_ADDRESSES:
        print("Error: current hostname not recognised!")
        return False
    for node in RIGHT_IP_ADDRESSES:
        addr = dig_for(node)
        expected = RIGHT_IP_ADDRESSES[node]
        if addr != expected:
             print("Error in getting record for", node, ": was expecting addr =", expected, "but found addr =", addr)
             return False

if __name__ == '__main__':
    test_dns_addresses()
