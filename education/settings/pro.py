from .base import *
DEBUG = False

ADMINS = (
    ('Martin', 'martin.mkhitaryan2000@gmail.com'),

)
SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'edu',
        'USER': 'edu',
        'PASSWORD': 'fdsa1234',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
