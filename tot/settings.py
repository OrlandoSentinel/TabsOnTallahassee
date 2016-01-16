import os
import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ],
        },
    },
]


if os.environ.get('DEBUG', 'true').lower() == 'false':
    DEBUG = False
    ALLOWED_HOSTS = ['*']
    DOMAIN = 'https://tabsontallahassee.com'
    SECRET_KEY = os.environ['SECRET_KEY']
    # ADMINS list should be 'Name Email, Name Email, Name Email...'
    ADMINS = [a.rsplit(' ', 1) for a in os.environ.get('ADMINS', '').split(',')]
    EMAIL_HOST = os.environ['EMAIL_HOST']
    EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
    EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
    EMAIL_PORT = '587'
    EMAIL_USE_TLS = True
    REGISTRATION_DEFAULT_FROM_EMAIL = DEFAULT_FROM_EMAIL = SERVER_EMAIL = os.environ[
        'DEFAULT_FROM_EMAIL']
    # enable once SSL is ready
    # SECURE_HSTS_SECONDS = 3600
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
else:
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY', 'debug-secret-key')
    ALLOWED_HOSTS = ['*']
    DOMAIN = 'http://localhost:8000'
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    REGISTRATION_DEFAULT_FROM_EMAIL = 'tot@tot.com'
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]


ANON_API_KEY = os.environ.get('ANON_API_KEY')

EMAIL_SUBJECT_PREFIX = '[ToT] '

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'opencivicdata.apps.BaseConfig',
    'pupa',
    'glossary',
    'boundaries',
    'registration',
    'preferences',
    'legislators',
    'bills',
    'api',
    'rest_framework',
    'corsheaders',
    'debug_toolbar',
]


MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tot.urls'


WSGI_APPLICATION = 'tot.wsgi.application'


DATABASE_URL = os.environ.get('DATABASE_URL',
                              'postgis://pupa:pupa@localhost/opencivicdata')
DATABASES = {'default': dj_database_url.parse(DATABASE_URL)}
CONN_MAX_AGE = 60


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
STATIC_ROOT = os.path.join(BASE_DIR, 'collected_static')
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

SITE_ID = 1

# registration
LOGIN_REDIRECT_URL = DOMAIN + '/preferences/'
ACCOUNT_ACTIVATION_DAYS = 7  # Account can be activated within 7 days
REGISTRATION_AUTO_LOGIN = True
INCLUDE_REGISTER_URL = False

# boundaries settings
BOUNDARIES_SHAPEFILES_DIR = 'shapefiles'
BOUNDARY_MAPPINGS = {
    'sldl-15': {'key': 'census_geoid_14',
                'prefix': 'sldl-',
                'ignore': '.*ZZZ',
                },
    'sldu-15': {'key': 'census_geoid_14',
                'prefix': 'sldu-',
                'ignore': '.*ZZZ',
                },
}

# API stuff
REST_FRAMEWORK = {
    'PAGE_SIZE': 50,
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework_json_api.pagination.PageNumberPagination',
    'URL_FIELD_NAME': 'resource_url',
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework_json_api.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_METADATA_CLASS': 'rest_framework_json_api.metadata.JSONAPIMetadata',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'preferences.authentication.KeyAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'api.throttling.BurstRateThrottle',
        'api.throttling.SustainedRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'burst': '60/min',
        'sustained': '10000/day',
    },
}

CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX = r'^/api/.*$'
CORS_ALLOW_HEADERS = (
    'x-requested-with',
    'content-type',
    'accept',
    'origin',
    'authorization',
    'x-csrftoken',
    'x-apikey',
)

# security check settings
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'

# tot-specific
CURRENT_SESSION = '2016 Regular Session'

# Number of latest actions to display
NUMBER_OF_LATEST_ACTIONS = 50
