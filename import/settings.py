"""
Django settings for import project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'x8$zw0yjh^4-_svl(o@98r#_!9jub8c5gj7ul2ov4i9-qjx_xt'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
   'reviewer',
    'widget_tweaks',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'import.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'import.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.sqlite3',
        #'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),

        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'uklakniz',
        'USER' : 'uklakniz',
        'PASSWORD': 'Qwx8TLkiUPO4JI2fWswrmy7ZgnAZUrqA',
        'HOST': 'john.db.elephantsql.com',
        'PORT' : '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Manila'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_ROOT =  os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

LOGIN_URL = '/u/login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

AUTH_USER_MODEL = 'reviewer.ImportUser'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'noreply.import.csreps@gmail.com'
EMAIL_HOST_PASSWORD = "FreeCSEdukNow"
EMAIL_SUBJECT_PREFIX = '[Import*] '

GOOGLE_API_CREDS = {
    "type": "service_account",
    "project_id": "import-drive-api-python",
    "private_key_id": "ce8c40a87d010697340fa5f1e6ef929c910ce081",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCgtbV1d5h3C74T\naGpQGfs0xsrKGLkIFh1qEjH996hFRqnb/nkJyidFJD/qRlSYH5Ux/L298SyPQDPe\nnMwTpYAgzai0epUCUDmPpTZItl9BYN01K5Pzt0j7+C4z6iuiPuxJYmAj4N7MSdda\nUmgc28IKjsj5I9PhHN8tsaucri7jhcTJrDeeKUCSen8JTkGbOhIn4dFsafugZrP3\n+a8XL7/eW3+Eg9QgyWaAQ4zS25PCGIpjeOUuwIzhIy2zG2J5ukruz17/HqkxikPC\neGFvrWc7yNm6ClIdvnEc36XQj/6jB1vCblNYsHSgKbADbOVpINtEaFtIXyFf3PJO\nzWJea9KHAgMBAAECggEACMvJQcOo+aMP5ToKz5WMdUgII2WVAwdK1tpmGBNtB1Wl\nyF+2Oj3xRkyEnwr4aFcaMGE39WR03uZRsHZ+iPi++YyoFjC7ZSQE8oLFZNdugUKO\n+PEIqQc4HGpqBPdlKf0tq5qRzoTpTN8hxVTLVAEHLtK/1zsJxsFwyax2yx2RfWxn\noWOR898OZm7xDhGMvLffYXQuApq4ibLEb/2oSoJgacIoJ8pufOHHtUqlO4yhss0X\nF07kQMf52n3PLgZwPEap84jlmrNKa9DLIP8APzs+KBfVd86ZzZXYKIBVQ7bF2eTl\n1Z0sIet56UXeC8UUTVeWmLHtF2XikzIf7zM+WFL6eQKBgQDb1sR2sxXf/vVrYK+n\nctH3Ri49uQlDU2cBoV6KQSBwd/xEIhLczonCM7wSd7Pbq0GWXjUTIgwJR1DB/MhP\nfusfKMPcIercpY+peaFWv/laQQMn6O752zBSnGS2zJxrZGy8a5ClRtSR/obSo2Gq\nWjNUSPjlwrco6co2YrBq/dXDOwKBgQC7JRAyAaCrDOTRpEtUIDoi7EuhfYN3ZYcl\nHdxtHvN7Wnvtquj9FGyP4eECKDUeZrdqduKlwMCZ+jGmdefcC81e3AmTBa0LxaEu\ndhQduaj1+Y9FgSs3asLOwhq+xEmtUWRUgh1uMCWxVVvUet6euwGD0lxrOMsoRccl\nKww6I1QhJQKBgFwyRPC3CHyJc6mVwfUK3W3DvA7ctDrNFo0DfR+kUpN4bo6wb5K0\n9+c/RSfFleORfg8u8TlV9RBLHV5NwkA8rSTDNujyPIpO0OI1hWlZV5z3WPh64wZc\nW3a56i8TvqH3WvbmcaIvA2U7BpX+OS51Z8N4WxIYyDHbYpfOachlLioTAoGAUMLL\n3GirZ2WnEXlvMJy/ufZzJPu/UjU0PyZFy6mBtYf01zncVesMdoMp0P58/eOh34Xy\nhUlLVKeN6aIULvfA5uDaGOJoLR5aUmyOfc1zRsMtuvblKYMfEo7db9nRWcQ4IegM\nv1Jz0bVebbGghKt7GeIcFAFsWrLSIA4VtrksQykCgYAB5gXaw9lLcyV2nKfTBTRG\nMT+xbUV0zjqaIDMDxlgG7MPPjjuTygeWMqBNw3TvBx5Cd1uv8wtGXx51Zdkh1Ox0\nwQkLG4lCZ4C5s0oYWVK0wYYy9iscCF9BjuQZsiw5Isuz1zb3ZE7HgejrD+yGCviV\n2KVgfOIHlnRddtW/MoLULw==\n-----END PRIVATE KEY-----\n",
    "client_email": "import-service-account@import-drive-api-python.iam.gserviceaccount.com",
    "client_id": "113622126348758682817",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/import-service-account%40import-drive-api-python.iam.gserviceaccount.com"
}

GOOGLE_API_SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.appdata',
    'https://www.googleapis.com/auth/drive.metadata.readonly'
]