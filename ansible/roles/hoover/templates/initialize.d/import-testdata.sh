#!/bin/bash
set -e
set -x

cd /opt/hoover

function wait_url {
    X=0
    until $(curl --connect-timeout 3 --max-time 20 --output /dev/null --silent --head --fail $1); do
        sleep 3
        ((X=X+1))
        if [[ $X -gt 20 ]]; then
            echo "wait_url: $1 timed out" >&2
            exit 1;
        fi
    done
}

supervisorctl start hoover-elasticsearch

# if the testdata collection exists, exit
have_testdata=$(sudo -u liquid-apps /opt/hoover/bin/hoover snoop collection | grep testdata | wc -l)
if [[ $have_testdata -ne 0 ]]; then exit 0; fi

# create the testdata collection
supervisorctl start hoover-tika
supervisorctl start hoover-snoop

# create the testdata collection and walk / digest it
sudo -u liquid-apps bash <<EOF
set -x
/opt/hoover/bin/hoover snoop createcollection /opt/hoover/testdata testdata testdata "Hoover Test Data", "Hoover Test Data"
/opt/hoover/bin/hoover snoop walk testdata
EOF

# wait after hoover's tika
tika_url="http://localhost:15423"
wait_url $tika_url

sudo -u liquid-apps bash <<EOF
set -x
/opt/hoover/bin/hoover snoop worker digest
EOF

supervisorctl stop hoover-tika
supervisorctl start hoover-elasticsearch

# wait after hoover's elasticsearch
es_url="http://localhost:14352"
wait_url $es_url

X=0
until [ $X -ge 5 ]; do
    sudo -u liquid-apps/opt/hoover/bin/hoover snoop resetindex testdata && break
    ((X=X+1))
    sleep 3
done
if [ $X -ge 5 ]; then
    exit 1
fi


snoop_url="http://localhost:11941"
wait_url $snoop_url/testdata/json


sudo -u liquid-apps bash <<EOF
set -x
/opt/hoover/bin/hoover search addcollection testdata "$snoop_url/testdata/json"
/opt/hoover/bin/hoover search update testdata
EOF

sudo -u liquid-apps /opt/hoover/bin/hoover search shell <<EOF
from hoover.search.models import Collection
c = Collection.objects.get(name='testdata')
c.public = True
c.save()
EOF

supervisorctl stop hoover-snoop
supervisorctl stop hoover-elasticsearch

sudo -u liquid-apps bash <<EOF
set -x
. /opt/hoover/venvs/snoop/bin/activate
cd /opt/hoover/snoop
#py.test
EOF
