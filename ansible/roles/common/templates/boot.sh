#!/bin/bash
set -e

cd /opt/common
if [ ! -f first_boot_done ]; then
  ./initialize.sh
  touch first_boot_done
fi

systemctl start postgresql

supervisorctl start nginx
supervisorctl start avahi-daemon
supervisorctl start liquid-core
supervisorctl start liquid-discover
supervisorctl start dokuwiki
supervisorctl start hoover-search
supervisorctl start hoover-snoop
supervisorctl start hoover-elasticsearch
supervisorctl start hoover-tika
supervisorctl start hypothesis-elasticsearch
supervisorctl start hypothesis-web
supervisorctl start hypothesis-websocket
supervisorctl start hypothesis-worker
supervisorctl start hypothesis-beat
