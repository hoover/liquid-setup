#!/bin/bash

set -e

if [ ! -s /opt/discover/discover/settings/secret_key.py ]; then
    echo "SECRET_KEY = '`openssl rand -base64 48`'" > /opt/discover/discover/settings/secret_key.py
fi
