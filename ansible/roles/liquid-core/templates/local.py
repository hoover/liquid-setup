DEBUG = True
ALLOWED_HOSTS = ['{{ liquid_domain }}']
AUTH_PASSWORD_VALIDATORS = []
CORS_ORIGIN_ALLOW_ALL = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/opt/liquid-core/var/db.sqlite3',
    }
}

INVOKE_HOOK = 'sudo /opt/common/libexec/invoke-hook'

HOOVER_APP_URL = 'http://hoover.{{ liquid_domain }}'
HYPOTHESIS_APP_URL = 'http://hypothesis.{{ liquid_domain }}'
DOKUWIKI_APP_URL = 'http://dokuwiki.{{ liquid_domain }}'
MATRIX_APP_URL = 'http://matrix.{{ liquid_domain }}'
DAVROS_APP_URL = 'http://davros.{{ liquid_domain }}'
LIQUID_DOMAIN = '{{ liquid_domain }}'
DISCOVERY_URL = 'http://localhost:13777'

from .secret_key import SECRET_KEY
