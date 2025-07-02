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
EMAIL_HOST='server362.web-hosting.com'
EMAIL_USE_SSL=True
EMAIL_PORT=465
EMAIL_HOST_USER=config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD=config("EMAIL_HOST_PASSWORD")

# Media
STATIC_ROOT = '/home/arctoiuu/public_html/static'
MEDIA_ROOT = '/home/arctoiuu/public_html/media'

HTTP = 'https://'
