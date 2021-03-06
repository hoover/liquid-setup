# FQDN for current machine
LIQUID_DOMAIN = "{{ liquid_domain }}"

# Network interface used for the DNS server.
# The machine must have a single IPv4 address on this interface.
# Set to None to omit using a DNS server
DNSMASQ_INTERFACE = None

# Flask debug
DEBUG = {% if devel %}True{% else %}False{% endif %}
