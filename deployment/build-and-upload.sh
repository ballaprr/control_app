#!/bin/bash

# Quick deployment script: Build locally and upload to EC2
# Usage: ./build-and-upload.sh your-ec2-ip

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <ec2-ip-address>"
    exit 1
fi

EC2_IP=$1

echo "🏗️ Building React frontend locally..."
cd frontend

# Set production API URL
export REACT_APP_API_URL=http://$EC2_IP/api

# Build
npm run build

echo "📤 Uploading build to EC2..."
scp -r build/ ubuntu@$EC2_IP:~/control_app/frontend/

echo "✅ Upload complete!"
echo "Your frontend is now available at: http://$EC2_IP"
