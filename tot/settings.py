import os
import datetime
import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '...'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DOMAIN = 'http://localhost:8000'

ALLOWED_HOSTS = ['*']


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
    'glossary',
    'boundaries',
    'registration',
    'preferences',
    'api',
    'rest_framework',
]


MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'preferences.middleware.AuthMiddleware',
]

ROOT_URLCONF = 'tot.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'tot.wsgi.application'


# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgis://pupa:pupa@localhost/opencivicdata')
DATABASES = {'default': dj_database_url.parse(DATABASE_URL)}


# Password validation
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(
        os.path.dirname(__file__),
        # '..', # up one level from the settings directory
        'static',
    ),
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_ROOT = os.path.join('..', BASE_DIR, 'static')
# STATIC_URL = '{}/static/'.format(DOMAIN)

STATIC_URL = '/static/'

SITE_ID = 1

LOGIN_REDIRECT_URL = DOMAIN + '/preferences/'

ACCOUNT_ACTIVATION_DAYS = 7  # Account can be activated within 7 days

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

REGISTRATION_DEFAULT_FROM_EMAIL = 'tot@tot.com'

REGISTRATION_AUTO_LOGIN = True

INCLUDE_REGISTER_URL = False

CURRENT_SESSION = '2016 Regular Session'

# Imago/Boundaries settings
BOUNDARIES_SHAPEFILES_DIR = 'shapefiles'
IMAGO_COUNTRY = 'us'
IMAGO_BOUNDARY_MAPPINGS = {
    'sldl-15': {'key': 'census_geoid_14',
                #'start': datetime.date(2015,1,1),
                'prefix': 'sldl-',
                'ignore': '.*ZZZ',
                },
    'sldu-15': {'key': 'census_geoid_14',
                #'start': datetime.date(2015,1,1),
                'prefix': 'sldu-',
                'ignore': '.*ZZZ',
                },
}

REST_FRAMEWORK = {
    'PAGINATE_BY': 10,
    'PAGINATE_BY_PARAM': 'page_size',
    'MAX_PAGINATE_BY': 100,
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
    )
}
