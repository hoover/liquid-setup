from urllib.parse import urlparse
from pathlib import Path

base_dir = Path(__file__).absolute().parent.parent.parent.parent

(base_dir / 'hoover' / 'site' / 'settings' / 'local.py').touch()
from hoover.site.settings.common import *

from .secret_key import SECRET_KEY

DEBUG = {{ 'True' if devel else 'False' }}

HOOVER_BASE_URL = "{{ http_scheme }}://hoover.{{liquid_domain}}"
ALLOWED_HOSTS = [urlparse(HOOVER_BASE_URL).netloc]

INSTALLED_APPS = (
    'hoover.contrib.oauth2',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'hoover.search',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'search',
        'USER': 'search',
        'HOST': 'search-pg',
        'PORT': 5432,
    },
}

STATIC_ROOT = str(base_dir / 'static')

HOOVER_UPLOADS_ROOT = str(base_dir / 'uploads')
HOOVER_UI_ROOT = str(base_dir.parent / 'ui' / 'build')
HOOVER_ELASTICSEARCH_URL = 'http://search-es:9200'

HOOVER_OAUTH_LIQUID_URL = "{{ http_scheme }}://{{ liquid_domain }}"

from .oauth import CLIENT_ID as HOOVER_OAUTH_LIQUID_CLIENT_ID
from .oauth import CLIENT_SECRET as HOOVER_OAUTH_LIQUID_CLIENT_SECRET
