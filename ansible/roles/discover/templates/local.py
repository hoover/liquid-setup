# FQDN for current machine
LIQUID_DOMAIN = "{{ liquid_domain }}"

# Network interface used for the DNS server.
# The machine must have a single IPv4 address on this interface.
# Set to None to omit using a DNS server
DNSMASQ_INTERFACE = None

# Flask debug
DEBUG = False
# Flask secret key

from .secret_key import SECRET_KEY
