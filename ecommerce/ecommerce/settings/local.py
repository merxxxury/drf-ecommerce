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
    'DESCRIPTION': 'Matcha store',
    'VERSION': '1.0.0',
}
