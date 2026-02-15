import requests
import json
import os
import time

# Base URL - Localhost
BASE_URL = os.environ.get('API_URL', 'http://127.0.0.1:5000')

BASE_URL = 'https://web-production-f19a8.up.railway.app/'

def test_enrich_resume():
    """Test the enrichment endpoint."""
    print("\n=== Testing Enrichment Endpoint ===")
    
    # 1. Load Dummy Data (or use hardcoded)
    # Ideally we'd use the files the user has open, but let's keep it self-contained or use those if available.
    # The user has: Resumes LinkedIn/ibrahim_elabdi_profile.json and Resumes Parsed/ibrahim_elabdi_parsed.json
    
    parsed_path = r"Resumes Parsed/ibrahim_elabdi_parsed.json"
    
    if os.path.exists(parsed_path):
        print(f"Loading parsed resume from: {parsed_path}")
        with open(parsed_path, 'r', encoding='utf-8') as f:
            resume_data = json.load(f)
            # If it's wrapped in 'data', extract it
            if 'data' in resume_data and isinstance(resume_data['data'], dict):
                resume_data = resume_data['data']
    else:
        print("Parsed resume file not found, using dummy data.")
    
    
    resume_path = r"Resumes Parsed/ibrahim_elabdi_parsed.json"
    with open(resume_path, "r", encoding="utf-8") as f: resume_data = json.load(f)

    payload = {
        "resume_data": resume_data,
        "name": "Ibrahim El Abdi",
        "linkedin_url": "https://www.linkedin.com/in/ibrahim-elabdi" 
    }
    
    start_time = time.time()
    try:
        url = f"{BASE_URL}/api/enrich-resume"
        print(f"POST {url}")
        
        response = requests.post(url, json=payload)
        duration = time.time() - start_time
        
        print(f"Status: {response.status_code}")
        print(f"Duration: {duration:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Success")
            
            merged_data = data.get('data', {})
            
            # fast check checks
            print("\nPreview of Merged Data:")
            print(json.dumps(merged_data, indent=2, ensure_ascii=False)[:500] + "...")
            
            # Check for [Linkedin] tags
            json_str = json.dumps(merged_data)
            tag_count = json_str.count("[Linkedin]")
            print(f"\nFound {tag_count} '[Linkedin]' tags in the response.")
            
            with open("data.json", "w") as f:
                json.dump(merged_data, f, indent=4)

        else:
            print("✗ Failed")
            print(response.text)

    except Exception as e:
        print(f"✗ Request failed: {e}")
        print("Ensure the Flask server is running on port 5000.")

if __name__ == "__main__":
    test_enrich_resume()
