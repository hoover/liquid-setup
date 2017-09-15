#!/bin/bash

set -e
printf '\n\n=== INITIALIZE LIQUID-CORE ===\n\n'
set -x

if [ -z $(grep -q "-- placeholder --" /opt/liquid-core/liquid-core/liquidcore/site/settings/secret_key.py) ]; then
(
    # create secret keys without echoing
    set +x
    echo "SECRET_KEY = '`openssl rand -base64 48`'" > /opt/liquid-core/liquid-core/liquidcore/site/settings/secret_key.py
)
fi

cd /opt/liquid-core/liquid-core
../venv/bin/python ./manage.py migrate
chown liquid: ../var/db.sqlite3
