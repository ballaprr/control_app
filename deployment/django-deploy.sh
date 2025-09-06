#!/bin/bash

# Django Production Deployment Script for EC2
# Run this script on your EC2 instance

set -e  # Exit on any error

echo "🚀 Starting Django deployment..."

# Navigate to project directory
cd ~/control_app/backend/control_app

# Check if virtual environment exists
if [ ! -d "show-courtside-env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv show-courtside-env
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source show-courtside-env/bin/activate

# Install production requirements
echo "📥 Installing production requirements..."
pip install --upgrade pip
pip install -r requirements_production.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ ERROR: .env file not found!"
    echo "Please create .env file from deployment/backend-production.env.example"
    exit 1
fi

# Load environment variables
echo "🔐 Loading environment variables..."
export $(grep -v '^#' .env | xargs)

# Database migrations
echo "🗃️  Running database migrations..."
python manage.py migrate --settings=control_app.settings_production

# Collect static files
echo "📂 Collecting static files..."
python manage.py collectstatic --noinput --settings=control_app.settings_production

# Create superuser (if needed)
echo "👤 Creating superuser (if needed)..."
python manage.py shell --settings=control_app.settings_production << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Superuser created: admin/admin123")
else:
    print("Superuser already exists")
EOF

echo "✅ Django deployment completed successfully!"
echo ""
echo "🚀 To start the production server:"
echo "gunicorn --bind 0.0.0.0:8000 control_app.wsgi:application --settings=control_app.settings_production"
echo ""
echo "🔧 To run with systemd service, see deployment/django.service example"
