"""
Test script for LinkedIn Resume Verification API
Run this to verify all endpoints are working correctly.
"""

import requests
import json
import os

# # Base URL - change this to your Railway URL after deployment
# BASE_URL = os.environ.get('API_URL', 'http://localhost:5000')

# Base URL - Railway URL deployment
BASE_URL = os.environ.get('API_URL', 'https://web-production-f19a8.up.railway.app/')


def test_health():
    """Test health check endpoint."""
    print("\n=== Testing Health Check ===")
    response = requests.get(f'{BASE_URL}/health')
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    assert response.json()['status'] == 'healthy'
    print("✓ Health check passed")

def test_root():
    """Test root endpoint."""
    print("\n=== Testing Root Endpoint ===")
    response = requests.get(f'{BASE_URL}/')
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✓ Root endpoint passed")

def test_find_linkedin():
    """Test LinkedIn profile search."""
    print("\n=== Testing LinkedIn Profile Search ===")
    payload = {
        "name": "Zaoug Imad",
        "company": "École Centrale Casablanca"
    }
    response = requests.post(
        f'{BASE_URL}/api/find-linkedin',
        json=payload
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("✓ LinkedIn search executed")

def test_find_linkedin_bulk():
    """Test bulk LinkedIn profile search."""
    print("\n=== Testing Bulk LinkedIn Search ===")
    payload = {
        "people": [
            {"name": "John Doe", "company": "Google"},
            {"name": "Jane Smith", "company": "Microsoft"}
        ],
        "delay": 1
    }
    response = requests.post(
        f'{BASE_URL}/api/find-linkedin-bulk',
        json=payload
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("✓ Bulk LinkedIn search executed")

def test_parse_resume():
    """Test resume parsing (requires a PDF file)."""
    print("\n=== Testing Resume Parsing ===")
    
    # Check if test PDF exists
    pdf_path = 'test_resume.pdf'
    if not os.path.exists(pdf_path):
        print("⚠ Skipping: test_resume.pdf not found")
        print("  Create a test_resume.pdf file to test this endpoint")
        return
    
    with open(pdf_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(
            f'{BASE_URL}/api/parse-resume',
            files=files
        )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Success: {response.json()['success']}")
        print(f"Data: {response.json()['data']}")
        print("✓ Resume parsing passed")
    else:
        print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_scrape_linkedin():
    """Test LinkedIn scraping (requires session.json)."""
    print("\n=== Testing LinkedIn Scraping ===")
    
    # Check if session.json exists
    if not os.path.exists('session.json'):
        print("⚠ Skipping: session.json not found")
        print("  This endpoint requires LinkedIn authentication")
        return
    
    payload = {
        "profile_url": "https://www.linkedin.com/in/satyanadella/"
    }
    response = requests.post(
        f'{BASE_URL}/api/scrape-linkedin',
        json=payload
    )
    print(f"Status: {response.status_code}")
    print(f"Response preview: {json.dumps(response.json(), indent=2)[:500]}...")
    if response.status_code == 200:
        print("✓ LinkedIn scraping passed")

def test_verify():
    """Test resume verification (requires PDF and LinkedIn data)."""
    print("\n=== Testing Resume Verification ===")
    
    pdf_path = 'test_resume.pdf'
    if not os.path.exists(pdf_path):
        print("⚠ Skipping: test_resume.pdf not found")
        return
    
    if not os.path.exists('session.json'):
        print("⚠ Skipping: session.json not found")
        return
    
    with open(pdf_path, 'rb') as f:
        files = {'file': f}
        data = {'linkedin_url': 'https://www.linkedin.com/in/satyanadella/'}
        response = requests.post(
            f'{BASE_URL}/api/verify',
            files=files,
            data=data
        )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Confidence: {response.json()['data']['overall_confidence']}")
        print("✓ Verification passed")
    else:
        print(f"Response: {json.dumps(response.json(), indent=2)}")

def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("LinkedIn Resume Verification API - Test Suite")
    print("=" * 60)
    print(f"Testing API at: {BASE_URL}")
    
    tests = [
        ("Health Check", test_health),
        ("Root Endpoint", test_root),
        ("Find LinkedIn", test_find_linkedin),
        ("Bulk LinkedIn Search", test_find_linkedin_bulk),
        ("Parse Resume", test_parse_resume),]
    #     ("Scrape LinkedIn", test_scrape_linkedin),
    #     ("Verify Resume", test_verify)
    # ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_name} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test_name} error: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)

if __name__ == '__main__':
    run_all_tests()
