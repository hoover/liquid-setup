#!/bin/bash
set -e

cd /opt/common
if [ ! -f first_boot_done ]; then
  ./initialize.sh
  touch first_boot_done
  echo "First boot completed successfully"
fi

supervisorctl start all
