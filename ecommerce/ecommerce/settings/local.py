from .base import *

# The idea is to cut settings from base settings file if it needs to be
# changed.
# And change it here.
# Also in manage.py file we can make
# the condition which settings to use depending on the DEBUG status.


REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}


SPECTACULAR_SETTINGS = {
    'TITLE': 'E-commerce',
    'DESCRIPTION': 'E store',
    'VERSION': '1.0.0',
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'drf_ecom_db',
        'USER': 'ecom_admin',
        'PASSWORD': 'ecom_admin',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
