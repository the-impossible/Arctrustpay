from .base import *

ALLOWED_HOSTS = ['www.arctrustpay.com', 'arctrustpay.com']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': 3306,
    }
}

#Email
EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST='live.smtp.mailtrap.io'
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_PORT=587
EMAIL_HOST_USER=config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD=config("EMAIL_HOST_PASSWORD")

# Media
STATIC_ROOT = '/home/arctoiuu/public_html/static'
MEDIA_ROOT = '/home/arctoiuu/public_html/media'

HTTP = 'https://'
