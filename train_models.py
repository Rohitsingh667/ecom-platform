import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_project.settings')
django.setup()

from recommendations.ml_engine import retrain_models

print("Training recommendation models...")
retrain_models()
print("Models trained successfully!")
