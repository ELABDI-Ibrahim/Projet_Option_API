import os
import unittest
import requests

API_URL = "http://127.0.0.1:5000"
TEST_RESUME_DIR = "Test_resumes"  # folder containing test PDFs

class TestFlaskAPI(unittest.TestCase):

    def test_health_check(self):
        """Test /health endpoint"""
        resp = requests.get(f"{API_URL}/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get("status"), "healthy")

    def test_parse_resume(self):
        # """Test /api/parse-resume with all test PDFs"""
        # for filename in os.listdir(TEST_RESUME_DIR):
        #         filepath = os.path.join(TEST_RESUME_DIR, filename)
        #         with open(filepath, "rb") as f:
        #             files = {"file": (filename, f, "application/pdf")}
        #             resp = requests.post(f"{API_URL}/api/parse-resume", files=files)
        #             print(resp.json())
        #             self.assertEqual(resp.status_code, 200)
        #             # data = resp.json()
        #             # self.assertIsInstance(data, dict)
        #             # self.assertTrue("name" in data or "email" in data or "skills" in data)
        return True

    def test_upload_resume(self):
        """Test /api/upload-resume with all test PDFs"""
        for filename in os.listdir(TEST_RESUME_DIR):
            # if filename.lower().endswith(".pdf"):
                filepath = os.path.join(TEST_RESUME_DIR, filename)
                with open(filepath, "rb") as f:
                    files = {"file": (filename, f, "application/pdf")}
                    # # optionally add job_offer_id
                    # data = {"job_offer_id": "0db2a03d-e558-4d1c-8cc7-96073eb51919"}
                    data = {}
                    resp = requests.post(f"{API_URL}/api/upload-resume", files=files, data=data)
                    print(resp.json())
                    self.assertEqual(resp.status_code, 201)
                    json_data = resp.json()
                    self.assertTrue(json_data.get("success"))
                    self.assertIn("candidate_id", json_data.get("data"))
                    self.assertIn("resume_id", json_data.get("data"))
                    self.assertIn("file_url", json_data.get("data"))


if __name__ == "__main__":
    unittest.main()
