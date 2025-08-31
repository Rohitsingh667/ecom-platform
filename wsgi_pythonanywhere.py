"""
WSGI config for PythonAnywhere deployment.

Copy this content to your PythonAnywhere WSGI configuration file.
Replace 'yourusername' with your actual PythonAnywhere username.
"""

import os
import sys

# Add your project directory to the Python path
# Replace 'yourusername' with your actual username
path = '/home/yourusername/ecommerce'
if path not in sys.path:
    sys.path.insert(0, path)

# Point to your production settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'ecommerce_project.production_settings'

# Import Django's WSGI handler
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
