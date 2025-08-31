"""
Run this script on PythonAnywhere after uploading files.
This will set up the database and load Indian data.
"""
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_project.production_settings')
django.setup()

from django.core.management import call_command
from django.contrib.auth import get_user_model
from recommendations.ml_engine import retrain_models

def setup_application():
    print("🚀 Setting up AI Shop India...")
    
    # Create database tables
    print("📊 Creating database tables...")
    call_command('makemigrations', verbosity=1)
    call_command('migrate', verbosity=1)
    
    # Create superuser
    print("👤 Creating admin user...")
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123india'
        )
        print("✅ Admin user created (username: admin, password: admin123india)")
    else:
        print("ℹ️ Admin user already exists")
    
    # Load Indian data
    print("🇮🇳 Loading Indian e-commerce data...")
    call_command('populate_indian_data', verbosity=1)
    
    # Collect static files
    print("📁 Collecting static files...")
    call_command('collectstatic', '--noinput', verbosity=1)
    
    # Train ML models
    print("🤖 Training AI recommendation models...")
    retrain_models()
    
    print("🎉 Setup complete! Your AI Shop India is ready!")
    print("📝 Admin URL: /admin/")
    print("👤 Username: admin")
    print("🔑 Password: admin123india")

if __name__ == '__main__':
    setup_application()
