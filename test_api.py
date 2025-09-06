#!/usr/bin/env python3
"""
Quick test script to verify the Django REST API is working correctly.
Run this script with the Django server running on localhost:8000
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_api_endpoints():
    """Test basic API endpoints"""
    
    print("Testing Courtside Control API...")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/arenas/")
        if response.status_code == 401:
            print("✅ Server is running and authentication is working (401 Unauthorized expected)")
        else:
            print(f"⚠️  Server responded with status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure Django server is running on localhost:8000")
        return False
    
    # Test 2: Test user registration
    print("\n🔐 Testing User Registration...")
    test_user_data = {
        "username": "testuser123",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "testpassword123456",
        "password_confirm": "testpassword123456"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register/", json=test_user_data)
        if response.status_code == 201:
            print("✅ User registration endpoint is working")
        elif response.status_code == 400:
            data = response.json()
            if "email" in data and "already exists" in str(data["email"]):
                print("✅ User registration endpoint is working (user already exists)")
            else:
                print(f"⚠️  Registration validation error: {data}")
        else:
            print(f"❌ Registration failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Registration test failed: {e}")
    
    # Test 3: Test arena endpoint structure
    print("\n🏟️  Testing Arena Endpoints...")
    try:
        response = requests.get(f"{BASE_URL}/arenas/")
        if response.status_code == 401:
            print("✅ Arena endpoints require authentication (401 expected)")
        else:
            print(f"Arena endpoint status: {response.status_code}")
    except Exception as e:
        print(f"❌ Arena endpoint test failed: {e}")
    
    # Test 4: Test device endpoint structure
    print("\n📱 Testing Device Endpoints...")
    try:
        response = requests.get(f"{BASE_URL}/devices/")
        if response.status_code == 401:
            print("✅ Device endpoints require authentication (401 expected)")
        else:
            print(f"Device endpoint status: {response.status_code}")
    except Exception as e:
        print(f"❌ Device endpoint test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 API structure test completed!")
    print("\nNext steps:")
    print("1. Start the React frontend: cd frontend && npm start")
    print("2. Open http://localhost:3000 in your browser")
    print("3. Test the full registration and login flow")
    
    return True

if __name__ == "__main__":
    test_api_endpoints()
