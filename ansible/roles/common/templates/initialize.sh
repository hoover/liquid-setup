#!/bin/bash
set -e
set -x

date

sudo -u postgres psql postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='liquid'" | grep -q 1 || sudo -u postgres createuser --superuser liquid

INITIALIZE_RESULT=0

set +e
for file in /opt/common/initialize.d/*
do
  "$file"
  RESULT=$?
  if [ 0 -ne $RESULT ]; then
      INITIALIZE_RESULT=$RESULT
  fi
  echo "$file $RESULT" >> /opt/common/first_boot_status
done

/opt/liquid-core/libexec/manage repairconfig
RESULT=$?
if [ 0 -ne $RESULT ]; then
    INITIALIZE_RESULT=$RESULT
fi
echo "/opt/liquid-core/libexec/manage repairconfig $RESULT" >> /opt/common/first_boot_status

set -e

echo "$0 $INITIALIZE_RESULT" >> /opt/common/first_boot_status

date

exit $INITIALIZE_RESULT
