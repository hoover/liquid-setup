#!/bin/sh
set -e
set -x
TESTPY=/home/vagrant/setup/test/zeroconf/node-test.py
vagrant ssh one   -c "python3 $TESTPY"
vagrant ssh two   -c "python3 $TESTPY"
vagrant ssh three -c "python3 $TESTPY"
