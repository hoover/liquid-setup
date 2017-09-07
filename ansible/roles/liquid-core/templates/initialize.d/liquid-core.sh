#!/bin/bash

set -e
set -x

cd /opt/liquid-core/liquid-core
../venv/bin/python ./manage.py migrate
