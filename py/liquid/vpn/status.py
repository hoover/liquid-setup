import json
import subprocess

OVPN_SERVER_STATUS_FILE = '/var/lib/liquid/vpn/server/status.log'


def running_services():
    out = subprocess.check_output(['supervisorctl', 'status'])
    for line in out.decode('latin1').splitlines():
        bits = line.split()
        if bits[1] == 'RUNNING':
            yield bits[0]


def get_vpn_server_clients():
    rv = []

    with open(OVPN_SERVER_STATUS_FILE, encoding='latin1') as f:
        skip = True
        for line in f:
            line = line.strip()

            if 'Bytes Received' in line:
                skip = False
                columns = line.split(',')
                continue

            if skip:
                continue

            if line == 'ROUTING TABLE':
                break

            rv.append(dict(zip(columns, line.split(','))))

    return rv


def report():
    rv = {}

    for service in running_services():
        if service == 'vpn-server':
            rv['vpn-server-running'] = True
            rv['vpn-server-clients'] = get_vpn_server_clients()
        if service == 'vpn-client':
            rv['vpn-client-running'] = True

    print(json.dumps(rv, indent=2, sort_keys=True))
