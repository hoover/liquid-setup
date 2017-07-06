SECRET_KEY = '-- secret key --'
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

HYPOTHESIS_USER_SCRIPTS = {
    'create': '/opt/liquid-core/libexec/h_user_create',
    'delete': '/opt/liquid-core/libexec/h_user_delete',
    'passwd': '/opt/liquid-core/libexec/h_user_passwd',
}

HOOVER_APP_URL = 'http://hoover.{{ liquid_domain }}'
HYPOTHESIS_APP_URL = 'http://hypothesis.{{ liquid_domain }}'
LIQUID_DOMAIN = '{{ liquid_domain }}'
