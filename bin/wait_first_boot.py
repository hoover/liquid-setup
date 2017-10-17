#!/usr/bin/env python3

# waits for the initial boot process to finish, which
# consists of the /opt/common/boot.sh calling initialize.sh.

# waits for either first_boot_done OR first_boot_failed to exist in
# /opt/common.

# Returns 0 if first boot done and 1 if first boot failed

import shutil
import sys
from os.path import exists
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


def wait_for_first_boot(wait_mins=30):
    print("Waiting for first boot to happen for {} mins.".format(wait_mins))
    seconds = 0
    while not exists(FILE_FAIL) and not exists(FILE_DONE):
        sleep(SLEEP_SECS)
        seconds += SLEEP_SECS

        if seconds > wait_mins * 60:
            cat_log("First boot timed out after {} mins.".format(wait_mins))
            exit(1)


def cat_logs_and_exit():
    if exists(FILE_FAIL):
        cat_log("First boot failed!")
        cat('/opt/common/first_boot_status')
        exit(1)

    elif exists(FILE_DONE):
        cat_log("First boot done.")
        exit(0)

    print("This should never happen")
    exit(1)


if __name__ == '__main__':
    wait_for_first_boot()
    cat_logs_and_exit()
