from .settings import *
import os

DEBUG = False

# Replace 'yourusername' with your actual PythonAnywhere username
ALLOWED_HOSTS = ['yourusername.pythonanywhere.com']

# Indian locale settings
LANGUAGE_CODE = 'en-in'
TIME_ZONE = 'Asia/Kolkata'

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = '/home/yourusername/ecommerce/staticfiles'

# Media files (User uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/yourusername/ecommerce/media'

# Database configuration for PythonAnywhere
# SQLite works fine for small to medium projects
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/home/yourusername/ecommerce/db.sqlite3',
    }
}

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# CORS settings
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "https://yourusername.pythonanywhere.com",
]

# Disable debug toolbar in production
if 'debug_toolbar' in INSTALLED_APPS:
    INSTALLED_APPS.remove('debug_toolbar')

# Email configuration (optional)
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
