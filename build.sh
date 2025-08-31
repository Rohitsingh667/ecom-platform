#!/usr/bin/env bash
# exit on error
set -o errexit

echo "🔧 Installing dependencies..."
pip install -r requirements.txt

echo "📊 Running database migrations..."
python manage.py migrate --settings=ecommerce_project.render_settings

echo "🇮🇳 Loading Indian e-commerce data..."
python manage.py populate_indian_data --settings=ecommerce_project.render_settings

echo "📁 Collecting static files..."
python manage.py collectstatic --no-input --settings=ecommerce_project.render_settings

echo "🤖 Training AI models..."
python train_models.py

echo "🎉 Build completed successfully!"
