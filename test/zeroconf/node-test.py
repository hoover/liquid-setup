#!/usr/bin/env python3
import socket
import subprocess

def dig_for(hostname):
    proc = subprocess.run(['dig', hostname, '@localhost', '+short'], check=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    return proc.stdout.decode('latin-1').strip()

def get_hostname():
    return socket.gethostname()

RIGHT_IP_ADDRESSES = {
    'vagrant-box-one.liquid': '10.0.0.20',
    'vagrant-box-two.liquid': '10.0.0.27',
    'vagrant-box-three.liquid': '10.0.0.23',
}

RIGHT_HOSTNAMES = [h.split('.')[0] for h in RIGHT_IP_ADDRESSES]

SAMPLE_SERVICES = [
    'hoover',
    'matrix',
    'hypothesis'
]

ALL_DOMAINS = [service + '.' + domain for service in SAMPLE_SERVICES for domain in RIGHT_IP_ADDRESSES.keys()]

def test_dns_addresses():
    hostname = get_hostname()
    if hostname not in RIGHT_HOSTNAMES:
        print("Error: current hostname not recognised!")
        return False
    for node in RIGHT_IP_ADDRESSES:
        addr = dig_for(node)
        expected = RIGHT_IP_ADDRESSES[node]
        if node != hostname and addr != expected:
             print("Error in getting record for", node, ": was expecting addr =", expected, "but found addr =", addr)
             return False
    for domain in ALL_DOMAINS:
        assert dig_for(domain)
    print("Success.")

if __name__ == '__main__':
    test_dns_addresses()
