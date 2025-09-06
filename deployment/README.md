# 🚀 EC2 Deployment Guide

Complete deployment guide for Courtside Control System on Amazon EC2.

## 📋 Prerequisites

1. **EC2 Instance**: Ubuntu 20.04+ LTS with at least 2GB RAM
2. **Security Groups**: Allow HTTP (80), HTTPS (443), and SSH (22)
3. **Domain Name** (optional): Point your domain to the EC2 IP
4. **Database**: PostgreSQL (can be on same instance or RDS)

## 🎯 Quick Deployment

### Option 1: Automated Script (Recommended)

```bash
# On your EC2 instance
wget https://raw.githubusercontent.com/ballaprr/control_app/main/deployment/ec2-deploy.sh
chmod +x ec2-deploy.sh
./ec2-deploy.sh
```

### Option 2: Manual Step-by-Step

#### 1. Frontend Build (Local Development)

```bash
# On your development machine
cd frontend
npm install
REACT_APP_API_URL=http://YOUR-EC2-IP/api npm run build
```

#### 2. Deploy to EC2

```bash
# Upload your code to EC2
scp -r build/ ubuntu@your-ec2-ip:~/
scp -r backend/ ubuntu@your-ec2-ip:~/
```

#### 3. Backend Setup

```bash
# On EC2 instance
cd backend/control_app
cp deployment/backend-production.env.example .env
# Edit .env with your actual values

./deployment/django-deploy.sh
```

## 🔧 Configuration Files

### Frontend Environment (`frontend/.env.production`)
```env
REACT_APP_API_URL=http://your-ec2-ip/api
```

### Backend Environment (`backend/control_app/.env`)
```env
SECRET_KEY=your_django_secret_key
DEBUG=False
ALLOWED_HOSTS=your-ec2-ip,your-domain.com

DB_NAME=courtside_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

API_KEY=your_info_beamer_api_key

EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

## 🌐 Architecture

```
Internet → Nginx → React Build (Frontend)
                → Django API (Backend) → PostgreSQL
```

### How It Works:

1. **Nginx** serves the React build files and proxies API requests
2. **React Build** contains your optimized frontend assets
3. **Django** runs as a Gunicorn WSGI application
4. **PostgreSQL** stores your application data

## 🔧 Management Commands

### Service Management
```bash
# Django service
sudo systemctl start django.service
sudo systemctl stop django.service
sudo systemctl restart django.service
sudo systemctl status django.service

# Nginx
sudo systemctl restart nginx
sudo systemctl status nginx
```

### Logs
```bash
# Django logs
journalctl -u django.service -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Database
```bash
# Connect to PostgreSQL
sudo -u postgres psql courtside_db

# Django migrations
cd ~/control_app/backend/control_app
source show-courtside-env/bin/activate
python manage.py migrate --settings=control_app.settings_production
```

## 🔒 Security Checklist

- [ ] Change default Django secret key
- [ ] Set `DEBUG=False` in production
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Use strong database passwords
- [ ] Enable firewall (UFW)
- [ ] Set up SSL certificates
- [ ] Regular security updates

## 🚀 Performance Optimization

### Gunicorn Workers
Adjust workers in `deployment/django.service`:
```ini
# Formula: (2 x CPU cores) + 1
--workers 5  # For 2 CPU cores
```

### Database Optimization
```sql
# PostgreSQL tuning
shared_buffers = 256MB
effective_cache_size = 1GB
```

## 🆘 Troubleshooting

### Frontend Not Loading
```bash
# Check Nginx status
sudo systemctl status nginx

# Check build files exist
ls -la ~/control_app/frontend/build/

# Check Nginx config
sudo nginx -t
```

### API Calls Failing
```bash
# Check Django service
sudo systemctl status django.service

# Check Django logs
journalctl -u django.service -f

# Test Django directly
curl http://localhost:8000/api/auth/login/
```

### Database Connection Issues
```bash
# Check PostgreSQL
sudo systemctl status postgresql

# Test connection
sudo -u postgres psql -c "SELECT version();"
```

## 📊 Monitoring

### Basic Monitoring
```bash
# System resources
htop
df -h
free -h

# Application logs
journalctl -u django.service --since "1 hour ago"
```

### Health Checks
```bash
# Django health check
curl http://localhost:8000/api/health/

# Nginx status
curl -I http://localhost/
```

## 🔄 Updates and Maintenance

### Updating Code
```bash
cd ~/control_app
git pull origin main

# Update frontend
cd frontend
npm run build

# Update backend
cd ../backend/control_app
source show-courtside-env/bin/activate
pip install -r requirements_production.txt
python manage.py migrate --settings=control_app.settings_production
python manage.py collectstatic --noinput --settings=control_app.settings_production

# Restart services
sudo systemctl restart django.service
sudo systemctl reload nginx
```

### Backup Strategy
```bash
# Database backup
sudo -u postgres pg_dump courtside_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Code backup
tar -czf code_backup_$(date +%Y%m%d_%H%M%S).tar.gz ~/control_app/
```

## 📞 Support

For issues with deployment:
1. Check the troubleshooting section above
2. Review logs for error messages
3. Ensure all environment variables are set correctly
4. Verify network connectivity and security groups
