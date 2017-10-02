#!/bin/bash
set -e
printf '\n\n=== INITIALIZE HOOVER ===\n\n'
set -x

cd /opt/hoover

if [ ! -s /opt/hoover/search-settings/secret_key.py ]; then
(
    # create secret keys without echoing
    set +x
    echo "SECRET_KEY = '`openssl rand -base64 48`'" > /opt/hoover/search-settings/secret_key.py
    echo "SECRET_KEY = '`openssl rand -base64 48`'" > /opt/hoover/snoop-settings/secret_key.py
    sudo -u liquid /opt/liquid-core/libexec/create-oauth-application "hoover" "{{ http_scheme }}://hoover.{{ liquid_domain }}/accounts/oauth2-exchange/"
    source /var/lib/liquid/oauth_keys/hoover
    echo "CLIENT_ID = '$CLIENT_ID'" > /opt/hoover/search-settings/oauth.py
    echo "CLIENT_SECRET = '$CLIENT_SECRET'" >> /opt/hoover/search-settings/oauth.py
)
fi

# create and migrate dbs
docker-compose run --rm snoop /wait-for-it snoop-pg:5432 -- ./manage.py migrate
docker-compose run --rm search /wait-for-it search-pg:5432 -- ./manage.py migrate

# build the ui
/opt/hoover/libexec/build_ui

# create testdata collection
/opt/hoover/libexec/import_testdata
