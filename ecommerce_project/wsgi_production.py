import os
import sys

# Add your project directory to the Python path
path = '/home/yourusername/ecommerce'
if path not in sys.path:
    sys.path.insert(0, path)

# Set the Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'ecommerce_project.production_settings'

# Import Django's WSGI handler
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
