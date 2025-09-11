#!/usr/bin/env python3
"""
Test script for LoginManager authentication implementation.

This script tests the basic functionality of the LoginManager authentication
system to ensure it's working correctly.
"""

import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_login_manager_auth():
    """Test the LoginManager authentication system."""
    print("Testing LoginManager Authentication System")
    print("=" * 50)
    
    # Test data
    test_user = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    # Test 1: Login
    print("\n1. Testing login endpoint...")
    try:
        login_response = requests.post(
            f"{API_BASE}/auth/login",
            data=test_user,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            print("✅ Login successful!")
            print(f"   Access Token: {login_data.get('access_token', 'N/A')[:50]}...")
            print(f"   Refresh Token: {login_data.get('refresh_token', 'N/A')[:50]}...")
            print(f"   Expires In: {login_data.get('expires_in', 'N/A')} seconds")
            
            # Store tokens for further tests
            access_token = login_data.get('access_token')
            refresh_token = login_data.get('refresh_token')
            
        else:
            print(f"❌ Login failed with status {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            return
            
    except Exception as e:
        print(f"❌ Login test failed with error: {e}")
        return
    
    # Test 2: Access protected endpoint
    print("\n2. Testing protected endpoint access...")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        profile_response = requests.get(
            f"{API_BASE}/users/me",
            headers=headers
        )
        
        if profile_response.status_code == 200:
            profile_data = profile_response.json()
            print("✅ Protected endpoint access successful!")
            print(f"   User: {profile_data.get('username', 'N/A')}")
            print(f"   Email: {profile_data.get('email', 'N/A')}")
        else:
            print(f"❌ Protected endpoint access failed with status {profile_response.status_code}")
            print(f"   Response: {profile_response.text}")
            
    except Exception as e:
        print(f"❌ Protected endpoint test failed with error: {e}")
    
    # Test 3: Refresh token
    print("\n3. Testing token refresh...")
    try:
        refresh_data = {"refresh_token": refresh_token}
        refresh_response = requests.post(
            f"{API_BASE}/auth/refresh",
            json=refresh_data,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if refresh_response.status_code == 200:
            refresh_result = refresh_response.json()
            print("✅ Token refresh successful!")
            print(f"   New Access Token: {refresh_result.get('access_token', 'N/A')[:50]}...")
        else:
            print(f"❌ Token refresh failed with status {refresh_response.status_code}")
            print(f"   Response: {refresh_response.text}")
            
    except Exception as e:
        print(f"❌ Token refresh test failed with error: {e}")
    
    # Test 4: Logout
    print("\n4. Testing logout...")
    try:
        logout_data = {"access_token": access_token}
        logout_response = requests.post(
            f"{API_BASE}/auth/logout",
            json=logout_data
        )
        
        if logout_response.status_code == 200:
            logout_result = logout_response.json()
            print("✅ Logout successful!")
            print(f"   Message: {logout_result.get('msg', 'N/A')}")
        else:
            print(f"❌ Logout failed with status {logout_response.status_code}")
            print(f"   Response: {logout_response.text}")
            
    except Exception as e:
        print(f"❌ Logout test failed with error: {e}")
    
    # Test 5: Access after logout (should fail)
    print("\n5. Testing access after logout (should fail)...")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        profile_response = requests.get(
            f"{API_BASE}/users/me",
            headers=headers
        )
        
        if profile_response.status_code == 401:
            print("✅ Access correctly denied after logout!")
        else:
            print(f"❌ Access should have been denied, but got status {profile_response.status_code}")
            print(f"   Response: {profile_response.text}")
            
    except Exception as e:
        print(f"❌ Post-logout test failed with error: {e}")
    
    print("\n" + "=" * 50)
    print("LoginManager Authentication Test Complete!")

if __name__ == "__main__":
    test_login_manager_auth()
