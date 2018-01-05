#!/bin/bash
set -e
set -x

sudo -u liquid-apps /opt/liquid-core/libexec/create-oauth-application "davros" "{{ http_scheme }}://davros.{{ liquid_domain }}/__auth/callback"

echo "Creating secret keys..."
set +x
source /var/lib/liquid/oauth_keys/davros
echo "LIQUID_CLIENT_ID = '$CLIENT_ID'" > /opt/davros/authproxy/config/oauth.py
echo "LIQUID_CLIENT_SECRET = '$CLIENT_SECRET'" >> /opt/davros/authproxy/config/oauth.py

if [ ! -s /opt/davros/authproxy/config/secret.py ]; then
    echo "SECRET_KEY = '`openssl rand -base64 48`'" > /opt/davros/authproxy/config/secret.py
fi

set -x

DAVROS_DATA_SYNC="/var/lib/liquid/data/davros-sync"
if ! $( mount | grep -q $DAVROS_DATA_SYNC ); then
    mount --bind /opt/davros/davros/data $DAVROS_DATA_SYNC
fi
