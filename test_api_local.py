# """
# Test script for LinkedIn Resume Verification API - v2
# Includes tests for Local Cache functionality.
# """

# import requests
# import json
# import os
# import time

# # Base URL - Railway URL deployment
# BASE_URL = os.environ.get('API_URL', 'https://web-production-f19a8.up.railway.app/')
# # # For local testing, use localhost
# # BASE_URL = os.environ.get('API_URL', 'http://localhost:5000')


# def test_health():
#     """Test health check endpoint."""
#     print("\n=== Testing Health Check ===")
#     try:
#         response = requests.get(f'{BASE_URL}/health')
#         print(f"Status: {response.status_code}")
#         print(f"Response: {json.dumps(response.json(), indent=2)}")
#         assert response.status_code == 200
#         assert response.json()['status'] == 'healthy'
#         print("✓ Health check passed")
#     except Exception as e:
#         print(f"✗ Health check failed: {e}")

# def test_root():
#     """Test root endpoint."""
#     print("\n=== Testing Root Endpoint ===")
#     try:
#         response = requests.get(f'{BASE_URL}/')
#         print(f"Status: {response.status_code}")
#         print(f"Response: {json.dumps(response.json(), indent=2)}")
#         assert response.status_code == 200
#         print("✓ Root endpoint passed")
#     except Exception as e:
#         print(f"✗ Root endpoint failed: {e}")

# def test_scrape_linkedin_local_cache():
#     """Test LinkedIn scraping using LOCAL CACHE (bypassing browser)."""
#     print("\n=== Testing LinkedIn Scraping (Local Cache) ===")
    
#     # We use a name that we know exists locally: "Ayoub Bourhaim"
#     # This should return instantly and SUCCESS even if browser scraping fails
#     payload = {
#         "profile_url": "https://www.linkedin.com/in/ayoub-bourhaim-dummy-url",
#         "name": "Ayoub Bourhaim"
#     }
    
#     start_time = time.time()
#     try:
#         response = requests.post(
#             f'{BASE_URL}/api/scrape-linkedin',
#             json=payload
#         )
#         duration = time.time() - start_time
        
#         print(f"Status: {response.status_code}")
#         print(f"Duration: {duration:.2f}s")
        
#         if response.status_code == 200:
#             data = response.json()
#             print(f"Success: {data.get('success')}")
#             profile = data.get('data', {})
#             print(f"Name found: {profile.get('name')}")
            
#             # Verify it's the correct person
#             if "Ayoub" in profile.get('name', '') or "Bourhaim" in profile.get('name', ''):
#                 print("✓ Local cache retrieval passed")
#             else:
#                 print("✗ Name mismatch")
#         else:
#             print(f"Response: {response.text}")
#             print("✗ Local cache retrieval failed")

#         print(data)

#     except Exception as e:
#         print(f"✗ Request failed: {e}")


# import requests
# import json

# def test_find_linkedin(
#     base_url='https://web-production-f19a8.up.railway.app/',
#     name="EL ABDI IBRAHIM",
#     email=None,
#     company=None,
#     location=None,
#     debug=False
# ):
#     url = f"{base_url}/api/find-linkedin"

#     payload = {
#         "name": name,
#         "debug": debug
#     }

#     if email:
#         payload["email"] = email
#     if company:
#         payload["company"] = company
#     if location:
#         payload["location"] = location

#     response = requests.post(url, json=payload)

#     print("Status Code:", response.status_code)

#     try:
#         data = response.json()
#         print("Response JSON:")
#         print(json.dumps(data, indent=2))
#         return data
#     except ValueError:
#         print("Response is not valid JSON:")
#         print(response.text)
#         return None


# def run_all_tests():
#     """Run all tests."""
#     print("=" * 60)
#     print("LinkedIn Resume Verification API - Test Suite v2")
#     print("=" * 60)
#     print(f"Testing API at: {BASE_URL}")
#     print("Note: Ensure the local Flask server is running on port 5000")
#     print("      or update BASE_URL to point to the deployed instance.")
    
#     test_health()
#     test_root()
#     test_scrape_linkedin_local_cache()
#     test_find_linkedin()
    
#     print("\n" + "=" * 60)
#     print("Test Complete")
#     print("=" * 60)

# if __name__ == '__main__':
#     run_all_tests()


import subprocess
import time
import requests
import os
import sys
import json

def run_local_test():
    # Configuration
    API_URL = "http://127.0.0.1:5000/api/parse-resume"
    PDF_FILE = "test_resume.pdf"
    APP_FILE = "app.py"

    # 1. Check if files exist
    if not os.path.exists(PDF_FILE):
        print(f"❌ Error: '{PDF_FILE}' not found in current directory.")
        return
    if not os.path.exists(APP_FILE):
        print(f"❌ Error: '{APP_FILE}' not found. Make sure you are in the root directory.")
        return

    print(f"🚀 Starting Flask server ({APP_FILE})...")
    
    # 2. Start Flask Server in Background
    # We use sys.executable to ensure we use the same python interpreter (and venv) currently running
    # server_process = subprocess.Popen(
    #     [sys.executable, APP_FILE],
    #     stdout=subprocess.PIPE,
    #     stderr=subprocess.PIPE,
    #     text=True
    # )

    try:
        # 3. Wait for server to boot
        print("⏳ Waiting 5 seconds for server to initialize...")
        time.sleep(5)

        # # Check if server crashed immediately
        # if server_process.poll() is not None:
        #     stdout, stderr = server_process.communicate()
        #     print("❌ Server crashed on startup:")
        #     print(stderr)
        #     return

        # 4. Send Request
        print(f"📤 Sending '{PDF_FILE}' to {API_URL}...")
        
        with open(PDF_FILE, 'rb') as f:
            files = {'file': (PDF_FILE, f, 'application/pdf')}
            try:
                response = requests.post(API_URL, files=files)
                
                print(f"📥 Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print("\n✅ SUCCESS! Parsed Data Preview (Top 5 lines of JSON):")
                    print("-" * 50)
                    print(json.dumps(data, indent=2))
                    print("-" * 50)
                    
                    # Optional: Save to file to inspect full result
                    with open("parse_result.json", "w", encoding="utf-8") as out:
                        json.dump(data, out, indent=2)
                    print("💾 Full result saved to 'parse_result.json'")
                else:
                    print("❌ Request Failed:")
                    print(response.text)

            except requests.exceptions.ConnectionError:
                print("❌ Could not connect to server. Is it running on port 5000?")

    except Exception as e:
        print(f"❌ An error occurred: {e}")

    finally:
        # # 5. Cleanup
        # print("🛑 Stopping server...")
        # server_process.terminate()
        # server_process.wait()
        # print("👋 Done.")
        print("Finished")

if __name__ == "__main__":
    # Ensure requests is installed: pip install requests
    run_local_test()