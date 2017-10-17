#!/bin/bash
set -e
set -x

cd /opt/hoover

function wait_url {
    X=0
    until $(curl --output /dev/null --silent --head --fail $1); do
        sleep 3
        ((X=X+1))
        if [[ $X -gt 20 ]]; then
            echo "wait_url: $1 timed out" >&2
            exit 1;
        fi
    done
}

supervisorctl start hoover-elasticsearch
supervisorctl start davros

DAVROS_DATA_PATH=/var/lib/liquid/data/davros-sync

# if the davros-sync collection exists, exit
have_davros_sync=$(sudo -u liquid /opt/hoover/bin/hoover snoop collection | grep davros-sync | wc -l)
if [[ $have_davros_sync -ne 0 ]]; then exit 0; fi

# create the davros-sync collection
supervisorctl start hoover-tika
supervisorctl start hoover-snoop

# create the davros-sync collection and walk / digest it
sudo -u liquid bash <<EOF
set -x
/opt/hoover/bin/hoover snoop createcollection '$DAVROS_DATA_PATH' davros-sync davros-sync "Davros Upload", "Davros Upload"
/opt/hoover/bin/hoover snoop walk davros-sync
/opt/hoover/bin/hoover snoop digestqueue
EOF

# wait after hoover's tika
tika_url="http://localhost:15423"
wait_url $tika_url

sudo -u liquid bash <<EOF
set -x
/opt/hoover/bin/hoover snoop worker digest
EOF

supervisorctl stop hoover-tika
supervisorctl start hoover-elasticsearch

# wait after hoover's elasticsearch
es_url="http://localhost:14352"
wait_url $es_url

sudo -u liquid bash <<EOF
set -x
/opt/hoover/bin/hoover snoop resetindex davros-sync
EOF

snoop_url="http://localhost:11941"
wait_url $snoop_url/davros-sync/json


sudo -u liquid bash <<EOF
set -x
/opt/hoover/bin/hoover search addcollection davros-sync "$snoop_url/davros-sync/json"
/opt/hoover/bin/hoover search update davros-sync
EOF

# DON'T MAKE THIS COLLECTION PUBLIC
#sudo -u liquid /opt/hoover/bin/hoover search shell <<EOF
#from hoover.search.models import Collection
#c = Collection.objects.get(name='davros-sync')
#c.public = True
#c.save()
#EOF

supervisorctl stop hoover-snoop
supervisorctl stop hoover-elasticsearch

sudo -u liquid bash <<EOF
set -x
. /opt/hoover/venvs/snoop/bin/activate
cd /opt/hoover/snoop
#py.test
EOF
