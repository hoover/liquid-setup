#!/bin/bash

set -e
printf '\n\n=== INITIALIZE LIQUID-CORE DEVEL ===\n\n'
set -x

cd /opt/liquid-core

# create initial users from list, if it exists
if [ -f users.json ]; then
  sudo -u liquid venv/bin/python liquid-core/manage.py createusers users.json
  rm users.json
fi
