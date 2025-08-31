"""
Run this script on Render after first deployment.
This will create admin user and ensure data is loaded.
"""
import os
import django

# Set up Django for Render
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_project.render_settings')
django.setup()

from django.core.management import call_command
from django.contrib.auth import get_user_model
from recommendations.ml_engine import retrain_models

def setup_application():
    print("🚀 Setting up AI Shop India on Render...")
    
    # Create superuser if not exists
    print("👤 Creating admin user...")
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@aishopindia.com',
            password='SecureAdmin@2024'
        )
        print("✅ Admin user created")
        print("👤 Username: admin")
        print("🔑 Password: SecureAdmin@2024")
    else:
        print("ℹ️ Admin user already exists")
    
    # Ensure ML models are trained
    print("🤖 Ensuring AI models are ready...")
    try:
        retrain_models()
        print("✅ AI models trained successfully")
    except Exception as e:
        print(f"⚠️ AI model training: {e}")
    
    print("🎉 Render deployment setup complete!")
    print("🌐 Your AI Shop India is ready!")

if __name__ == '__main__':
    setup_application()
