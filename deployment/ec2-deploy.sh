#!/bin/bash

# Complete EC2 Deployment Script for Courtside Control System
# Run this script on a fresh Ubuntu EC2 instance

set -e  # Exit on any error

echo "🚀 Starting complete EC2 deployment..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "🔧 Installing required packages..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    nginx \
    postgresql \
    postgresql-contrib \
    nodejs \
    npm \
    git \
    curl \
    ufw

# Configure firewall
echo "🛡️ Configuring firewall..."
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# Clone repository
echo "📥 Cloning repository..."
if [ ! -d "control_app" ]; then
    git clone https://github.com/ballaprr/control_app.git
    cd control_app
else
    cd control_app
    git pull origin main
fi

# Setup frontend
echo "🌐 Setting up React frontend..."
cd frontend
npm install

# Create production environment file for frontend
if [ ! -f ".env.production" ]; then
    echo "📝 Creating frontend production environment..."
    cat > .env.production << EOL
REACT_APP_API_URL=http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)/api
EOL
fi

# Build frontend
echo "🏗️ Building React frontend..."
npm run build

# Setup backend
echo "🐍 Setting up Django backend..."
cd ../backend/control_app

# Create production environment file for backend
if [ ! -f ".env" ]; then
    echo "📝 Creating backend production environment..."
    echo "❌ ERROR: Please create .env file from deployment/backend-production.env.example"
    echo "You need to configure:"
    echo "  - SECRET_KEY"
    echo "  - Database credentials"
    echo "  - API_KEY for Info Beamer"
    echo "  - Email settings"
    exit 1
fi

# Run Django deployment script
echo "🚀 Running Django deployment..."
../../deployment/django-deploy.sh

# Setup Nginx
echo "🌐 Setting up Nginx..."
sudo cp ../../deployment/nginx.conf /etc/nginx/sites-available/courtside-control

# Update Nginx config with actual server IP
SERVER_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
sudo sed -i "s/your-ec2-ip/$SERVER_IP/g" /etc/nginx/sites-available/courtside-control

# Enable site
sudo ln -sf /etc/nginx/sites-available/courtside-control /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test and reload Nginx
sudo nginx -t
sudo systemctl reload nginx

# Setup Django systemd service
echo "⚙️ Setting up Django service..."
sudo cp ../../deployment/django.service /etc/systemd/system/

# Update service file paths with actual user
sudo sed -i "s|/home/ubuntu|$HOME|g" /etc/systemd/system/django.service
sudo sed -i "s|User=ubuntu|User=$USER|g" /etc/systemd/system/django.service
sudo sed -i "s|Group=ubuntu|Group=$USER|g" /etc/systemd/system/django.service

# Start Django service
sudo systemctl daemon-reload
sudo systemctl enable django.service
sudo systemctl start django.service

# Check service status
echo "🔍 Checking service status..."
sudo systemctl status django.service --no-pager

echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "🌐 Your application should be available at:"
echo "   http://$SERVER_IP"
echo ""
echo "🔧 Useful commands:"
echo "   sudo systemctl status django.service    # Check Django service"
echo "   sudo systemctl restart django.service   # Restart Django"
echo "   sudo systemctl status nginx             # Check Nginx"
echo "   sudo tail -f /var/log/nginx/error.log   # Nginx error logs"
echo "   journalctl -u django.service -f         # Django logs"
echo ""
echo "📝 Next steps:"
echo "   1. Configure your domain name in Nginx config if needed"
echo "   2. Set up SSL certificates for HTTPS"
echo "   3. Configure backup strategy"
echo "   4. Set up monitoring and alerting"
