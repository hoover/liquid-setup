#!/usr/bin/env python3

# Waits for the initial boot process to finish, which
# consists of the /opt/common/boot.sh calling initialize.sh.

# Waits for either first_boot_done OR first_boot_failed to exist in
# /opt/common.

# Runs all tests and saves them under setup/testa/results as
# junit xml files.

import shutil
import sys
from os.path import exists
import os
from time import sleep
from sys import exit
import subprocess

FILE_FAIL = '/opt/common/first_boot_failed'
FILE_DONE = '/opt/common/first_boot_done'
FILE_LOG = '/var/log/rc.local.log'

SLEEP_SECS = 3

def cat(filename):
    with open(filename, 'r') as f:
        shutil.copyfileobj(f, sys.stdout)


def cat_log(message, log_filename=FILE_LOG):
    print(message)
    print("See the log below.\n")
    cat(log_filename)
    print("\n" + message)
    print("See the log above.\n")


class PyTestWrapper:
    pre_commands = []
    pytest = 'py.test'
    chdir = None
    xml_file = None
    env = None

    def run(self):
        if self.env:
            env = os.environ.copy()
            env.update(self.env)
        else:
            env = None
        for command in self.pre_commands:
            print("+", command)
            subprocess.run([command], shell=True, check=True, env=env)
        pytest_cmd = [self.pytest, '--junit-xml', self.xml_file]
        print("+", " ".join(pytest_cmd))
        subprocess.run(pytest_cmd, cwd=self.chdir, env=env, check=True)


class CoreTest(PyTestWrapper):
    pytest = "/opt/liquid-core/venv/bin/py.test"
    chdir = "/opt/liquid-core/liquid-core"
    xml_file = "/mnt/setup/tests/results/liquid-core.xml"
    env = {
        "PYTHONPATH": "/opt/liquid-core/liquid-core:{}".format(
            os.environ.get("PYTHONPATH",'')
        ),
    }


class SetupTest(PyTestWrapper):
    pre_commands = [
        "virtualenv -p python3 /mnt/setup/tests/venv",
        "/mnt/setup/tests/venv/bin/pip install -qqr /mnt/setup/tests/requirements.txt",
    ]
    pytest = "/mnt/setup/tests/venv/bin/py.test"
    chdir = "/mnt/setup/tests"
    xml_file = "/mnt/setup/tests/results/liquid-setup.xml"


def run_tests():
    fail = False
    for test_cls in [CoreTest, SetupTest]:
        try:
            test_cls().run()
        except subprocess.CalledProcessError:
            print(test_cls.__name__, "failed")
            fail = True

    if fail:
        return 1


def wait_for_first_boot(wait_mins=10):
    print("Waiting for first boot to happen for {} mins.".format(wait_mins))
    seconds = 0
    while not exists(FILE_FAIL) and not exists(FILE_DONE):
        sleep(SLEEP_SECS)
        seconds += SLEEP_SECS

        if seconds > wait_mins * 60:
            cat_log("First boot timed out after {} mins.".format(wait_mins))
            exit(1)


def cat_first_boot_logs():
    if exists(FILE_FAIL):
        cat_log("First boot failed!")
        cat('/opt/common/first_boot_status')
    elif exists(FILE_DONE):
        cat_log("First boot done.")
    else:
        print("This should never happen")
        exit(1)


if __name__ == '__main__':
    wait_for_first_boot()
    cat_first_boot_logs()
    sys.exit(run_tests())
