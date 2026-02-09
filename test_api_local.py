"""
Test script for LinkedIn Resume Verification API - v2
Includes tests for Local Cache functionality.
"""

import requests
import json
import os
import time

# Base URL - Railway URL deployment
BASE_URL = os.environ.get('API_URL', 'https://web-production-f19a8.up.railway.app/')
# # For local testing, use localhost
# BASE_URL = os.environ.get('API_URL', 'http://localhost:5000')


def test_health():
    """Test health check endpoint."""
    print("\n=== Testing Health Check ===")
    try:
        response = requests.get(f'{BASE_URL}/health')
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200
        assert response.json()['status'] == 'healthy'
        print("✓ Health check passed")
    except Exception as e:
        print(f"✗ Health check failed: {e}")

def test_root():
    """Test root endpoint."""
    print("\n=== Testing Root Endpoint ===")
    try:
        response = requests.get(f'{BASE_URL}/')
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200
        print("✓ Root endpoint passed")
    except Exception as e:
        print(f"✗ Root endpoint failed: {e}")

def test_scrape_linkedin_local_cache():
    """Test LinkedIn scraping using LOCAL CACHE (bypassing browser)."""
    print("\n=== Testing LinkedIn Scraping (Local Cache) ===")
    
    # We use a name that we know exists locally: "Ayoub Bourhaim"
    # This should return instantly and SUCCESS even if browser scraping fails
    payload = {
        "profile_url": "https://www.linkedin.com/in/ayoub-bourhaim-dummy-url",
        "name": "Ayoub Bourhaim"
    }
    
    start_time = time.time()
    try:
        response = requests.post(
            f'{BASE_URL}/api/scrape-linkedin',
            json=payload
        )
        duration = time.time() - start_time
        
        print(f"Status: {response.status_code}")
        print(f"Duration: {duration:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            profile = data.get('data', {})
            print(f"Name found: {profile.get('name')}")
            
            # Verify it's the correct person
            if "Ayoub" in profile.get('name', '') or "Bourhaim" in profile.get('name', ''):
                print("✓ Local cache retrieval passed")
            else:
                print("✗ Name mismatch")
        else:
            print(f"Response: {response.text}")
            print("✗ Local cache retrieval failed")

        print(data)

    except Exception as e:
        print(f"✗ Request failed: {e}")


import requests
import json

def test_find_linkedin(
    base_url='https://web-production-f19a8.up.railway.app/',
    name="EL ABDI IBRAHIM",
    email=None,
    company=None,
    location=None,
    debug=False
):
    url = f"{base_url}/api/find-linkedin"

    payload = {
        "name": name,
        "debug": debug
    }

    if email:
        payload["email"] = email
    if company:
        payload["company"] = company
    if location:
        payload["location"] = location

    response = requests.post(url, json=payload)

    print("Status Code:", response.status_code)

    try:
        data = response.json()
        print("Response JSON:")
        print(json.dumps(data, indent=2))
        return data
    except ValueError:
        print("Response is not valid JSON:")
        print(response.text)
        return None


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("LinkedIn Resume Verification API - Test Suite v2")
    print("=" * 60)
    print(f"Testing API at: {BASE_URL}")
    print("Note: Ensure the local Flask server is running on port 5000")
    print("      or update BASE_URL to point to the deployed instance.")
    
    test_health()
    test_root()
    test_scrape_linkedin_local_cache()
    test_find_linkedin()
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)

if __name__ == '__main__':
    run_all_tests()
