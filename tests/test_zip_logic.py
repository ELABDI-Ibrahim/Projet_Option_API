import sys
import os

# Add parent directory to path to allow importing app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import io
import zipfile
from unittest.mock import MagicMock, patch
import app

class TestZipUpload(unittest.TestCase):
    def setUp(self):
        app.app.config['TESTING'] = True
        app.app.config['UPLOAD_FOLDER'] = './test_uploads_zip'
        os.makedirs(app.app.config['UPLOAD_FOLDER'], exist_ok=True)
        self.client = app.app.test_client()
        
    def tearDown(self):
        import shutil
        if os.path.exists(app.app.config['UPLOAD_FOLDER']):
            shutil.rmtree(app.app.config['UPLOAD_FOLDER'])

    def create_dummy_pdf(self, content="dummy pdf content"):
        return io.BytesIO(content.encode('utf-8'))

    def create_zip_with_files(self, files):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as zf:
            for filename, content in files.items():
                zf.writestr(filename, content)
        buffer.seek(0)
        return buffer

    @patch('app.process_single_resume')
    def test_zip_upload(self, mock_process):
        # Setup mock return
        mock_process.return_value = {'id': '123', 'status': 'processed'}
        
        # Create ZIP
        zip_file = self.create_zip_with_files({
            'resume1.pdf': 'content1',
            'resume2.pdf': 'content2',
            'image.png': 'image_content',
            'bad_file.txt': 'text_content' # Should be ignored/error
        })
        
        # Send Request
        response = self.client.post('/api/upload-resume', data={
            'file': (zip_file, 'resumes.zip')
        }, content_type='multipart/form-data')
        
        # Verify Response
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.json}")
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertTrue(data['success'])
        
        # Verify call count
        # Should call 3 times (resume1.pdf, resume2.pdf, image.png)
        # bad_file.txt should be skipped or fail validation inside loop
        # My implementation checks extension against ALLOWED_EXTENSIONS
        # ALLOWED_EXTENSIONS = ['pdf', 'jpg', 'jpeg', 'png', 'bmp']
        
        # txt is NOT allowed. So it should produce an error in 'errors' list or just skip?
        # Implementation says: if file_ext not in ALLOWED_EXTENSIONS: errors.append(...)
        
        self.assertEqual(mock_process.call_count, 3) 
        
        # Check errors
        errors = data.get('errors', [])
        print(f"Errors: {errors}")
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['filename'], 'bad_file.txt')
        self.assertIn('Invalid file type', errors[0]['error'])

if __name__ == '__main__':
    unittest.main()
