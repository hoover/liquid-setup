#!/bin/bash
set -e

cd /opt/common
if [ ! -f first_boot_done ]; then
  ./initialize.sh
  touch first_boot_done
  echo "First boot completed successfully"
fi

echo "Starting firewall"
/opt/common/libexec/firewall

echo "Starting all services"
# TODO: only start enabled services
supervisorctl start all

echo "Running on-boot hook"
for file in /opt/common/hooks/on-boot.d/*
do
  "$file"
done
