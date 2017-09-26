#!/bin/bash
set -x

# Errors off, tasks that must be run before first boot
echo "Starting firewall"
/opt/common/libexec/firewall

# Errors on, try to start first boot.
set -e
cd /opt/common
if [ ! -f first_boot_done ] && [ ! -f first_boot_failed ]; then
  echo "Starting first boot."
  if ./initialize.sh ; then
    echo "First boot done."
    touch first_boot_done
  else
    echo "First boot failed."
    touch first_boot_failed
  fi
else
  echo "Not starting first boot, already done."
fi

# Errors off, start services and run on-boot hooks.
set +e
echo "Starting all services."
# TODO: only start enabled services
supervisorctl start all

echo "Running on-boot hook."
/opt/common/libexec/invoke-hook on-boot

echo "Boot scripts done."
