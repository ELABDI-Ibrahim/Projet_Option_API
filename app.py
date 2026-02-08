"""
LinkedIn Resume Verification API
Main Flask application for scraping LinkedIn profiles, parsing resumes, and verification.
"""

import os
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Import services
from services.linkedin_scraper import scrape_linkedin_profile
from services.resume_parser import pdf_to_text_minimal_tokens, parse_resume_with_groq
from services.linkedin_finder import find_linkedin, find_linkedin_bulk
from services.verification import run_verification

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
ALLOWED_EXTENSIONS = {'pdf'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# =============================================================================
# HEALTH CHECK & ROOT
# =============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Railway."""
    return jsonify({
        'status': 'healthy',
        'service': 'LinkedIn Resume Verification API',
        'version': '1.0.0'
    }), 200


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API documentation."""
    return jsonify({
        'message': 'LinkedIn Resume Verification API',
        'version': '1.0.0',
        'endpoints': {
            'GET /health': 'Health check',
            'POST /api/parse-resume': 'Parse PDF resume to structured JSON',
            'POST /api/find-linkedin': 'Find LinkedIn profile by name/company',
            'POST /api/find-linkedin-bulk': 'Find LinkedIn profiles for multiple people',
            'POST /api/scrape-linkedin': 'Scrape LinkedIn profile data',
            'POST /api/verify': 'Verify resume against LinkedIn profile'
        },
        'documentation': 'See README.md for detailed usage'
    }), 200


# =============================================================================
# RESUME PARSING
# =============================================================================

@app.route('/api/parse-resume', methods=['POST'])
def parse_resume():
    """
    Parse a PDF resume to structured JSON.
    
    Expects:
        - PDF file in multipart/form-data with key 'file'
    
    Returns:
        - Structured resume data in JSON format
    """
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided. Use key "file" in form-data'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Only PDF allowed.'
            }), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract text from PDF
        resume_text = pdf_to_text_minimal_tokens(filepath)
        
        if not resume_text:
            os.remove(filepath)
            return jsonify({
                'success': False,
                'error': 'Failed to extract text from PDF'
            }), 500
        
        # Parse with Groq API
        structured_resume = parse_resume_with_groq(resume_text)
        
        # Clean up
        os.remove(filepath)
        
        if not structured_resume:
            return jsonify({
                'success': False,
                'error': 'Failed to parse resume with AI'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Resume parsed successfully',
            'data': structured_resume
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


# =============================================================================
# LINKEDIN PROFILE FINDING
# =============================================================================

@app.route('/api/find-linkedin', methods=['POST'])
def find_linkedin_endpoint():
    """
    Find LinkedIn profile using DuckDuckGo search.
    
    Expects JSON:
        {
            "name": "John Doe",
            "email": "john@example.com" (optional),
            "company": "Tech Corp" (optional),
            "location": "San Francisco" (optional),
            "debug": false (optional)
        }
    
    Returns:
        {
            "success": true,
            "data": {
                "url": "https://linkedin.com/in/johndoe",
                "name": "John Doe",
                "snippet": "..."
            }
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({
                'success': False,
                'error': 'Name is required'
            }), 400
        
        result = find_linkedin(
            name=data.get('name'),
            email=data.get('email'),
            company=data.get('company'),
            location=data.get('location'),
            debug=data.get('debug', False)
        )
        
        if result:
            return jsonify({
                'success': True,
                'message': 'LinkedIn profile found',
                'data': result
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'LinkedIn profile not found'
            }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


@app.route('/api/find-linkedin-bulk', methods=['POST'])
def find_linkedin_bulk_endpoint():
    """
    Find LinkedIn profiles for multiple people.
    
    Expects JSON:
        {
            "people": [
                {"name": "John Doe", "company": "Tech Corp"},
                {"name": "Jane Smith", "email": "jane@example.com"}
            ],
            "delay": 2 (optional, seconds between requests)
        }
    
    Returns:
        {
            "success": true,
            "data": [...],
            "total": 2,
            "found": 1
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'people' not in data:
            return jsonify({
                'success': False,
                'error': 'People array is required'
            }), 400
        
        people = data.get('people', [])
        delay = data.get('delay', 2)
        
        if not isinstance(people, list) or len(people) == 0:
            return jsonify({
                'success': False,
                'error': 'People must be a non-empty array'
            }), 400
        
        results = find_linkedin_bulk(people, delay=delay)
        
        return jsonify({
            'success': True,
            'message': f'Processed {len(results)} searches',
            'data': results,
            'total': len(results),
            'found': sum(1 for r in results if r.get('linkedin'))
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


# =============================================================================
# LINKEDIN SCRAPING
# =============================================================================

@app.route('/api/scrape-linkedin', methods=['POST'])
def scrape_linkedin():
    """
    Scrape a LinkedIn profile.
    
    Expects JSON:
        {
            "profile_url": "https://linkedin.com/in/username"
        }
    
    Returns:
        {
            "success": true,
            "data": {...profile data...}
        }
    
    Note: Requires valid LinkedIn session.json file.
    """
    try:
        data = request.get_json()
        
        if not data or 'profile_url' not in data:
            return jsonify({
                'success': False,
                'error': 'profile_url is required'
            }), 400
        
        profile_url = data.get('profile_url')
        
        # Check if session.json exists
        if not os.path.exists('session.json'):
            return jsonify({
                'success': False,
                'error': 'LinkedIn session not configured. Please add session.json file.'
            }), 503
        
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        profile_data = loop.run_until_complete(scrape_linkedin_profile(profile_url))
        loop.close()
        
        if profile_data:
            return jsonify({
                'success': True,
                'message': 'LinkedIn profile scraped successfully',
                'data': profile_data
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to scrape profile'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


# =============================================================================
# VERIFICATION
# =============================================================================

@app.route('/api/verify', methods=['POST'])
def verify():
    """
    Verify resume against LinkedIn profile.
    
    Method 1 - JSON with pre-parsed data:
        {
            "resume_data": {...parsed resume...},
            "linkedin_data": {...scraped LinkedIn...}
        }
    
    Method 2 - File upload with LinkedIn URL:
        - PDF file with key 'file'
        - 'linkedin_url' in form data
    
    Returns:
        {
            "success": true,
            "data": {
                "verification_summary": "...",
                "discrepancies": [...],
                "overall_confidence": 0.85,
                "statistics": {...}
            }
        }
    """
    try:
        # Check if this is a JSON request or multipart
        if request.is_json:
            # Method 1: JSON with pre-parsed data
            data = request.get_json()
            
            if not data or 'resume_data' not in data or 'linkedin_data' not in data:
                return jsonify({
                    'success': False,
                    'error': 'Both resume_data and linkedin_data are required'
                }), 400
            
            resume_data = data.get('resume_data')
            linkedin_data = data.get('linkedin_data')
        
        else:
            # Method 2: File upload + LinkedIn URL
            if 'file' not in request.files:
                return jsonify({
                    'success': False,
                    'error': 'No file provided. Use key "file" in form-data'
                }), 400
            
            if 'linkedin_url' not in request.form:
                return jsonify({
                    'success': False,
                    'error': 'No linkedin_url provided in form data'
                }), 400
            
            # Parse resume
            file = request.files['file']
            
            if not allowed_file(file.filename):
                return jsonify({
                    'success': False,
                    'error': 'Invalid file type. Only PDF allowed.'
                }), 400
            
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            resume_text = pdf_to_text_minimal_tokens(filepath)
            resume_data = parse_resume_with_groq(resume_text)
            os.remove(filepath)
            
            if not resume_data:
                return jsonify({
                    'success': False,
                    'error': 'Failed to parse resume'
                }), 500
            
            # Scrape LinkedIn
            linkedin_url = request.form.get('linkedin_url')
            
            if not os.path.exists('session.json'):
                return jsonify({
                    'success': False,
                    'error': 'LinkedIn session not configured'
                }), 503
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            linkedin_data = loop.run_until_complete(scrape_linkedin_profile(linkedin_url))
            loop.close()
            
            if not linkedin_data:
                return jsonify({
                    'success': False,
                    'error': 'Failed to scrape LinkedIn profile'
                }), 500
        
        # Run verification
        verification_result = run_verification(resume_data, linkedin_data)
        
        return jsonify({
            'success': True,
            'message': 'Verification completed',
            'data': verification_result
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        'success': False,
        'error': 'File too large (max 16MB)'
    }), 413


# =============================================================================
# RUN SERVER
# =============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug)