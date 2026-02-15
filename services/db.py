
import os
import mimetypes
from supabase import create_client, Client

# from dotenv import load_dotenv

# load_dotenv()

# Constants
SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
BUCKET_NAME = os.environ.get("NEXT_PUBLIC_SUPABASE_STORAGE_BUCKET", "Resumes_lake")

_supabase: Client = None

def init_supabase() -> Client:
    """Initialize Supabase client."""
    global _supabase
    if _supabase is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("Supabase credentials not found in environment variables.")
        _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase

def upload_resume_file(file_bytes: bytes, filename: str, content_type: str = "application/pdf") -> str:
    """
    Upload resume file to Supabase Storage and return public URL.
    
    Args:
        file_bytes: File content in bytes
        filename: Name of the file (should be unique/timestamped)
        content_type: MIME type of the file
        
    Returns:
        str: Public URL of the uploaded file
    """
    supabase = init_supabase()
    
    # Path in bucket: resumes/filename
    file_path = f"resumes/{filename}"
    
    try:
        # Upload file
        # Using upsert=False to avoid overwriting existing files with same name if that happens, 
        # but robust filename generation should prevent this.
        # Actually user code used 'timestamp_filename'.
        res = supabase.storage.from_(BUCKET_NAME).upload(
            path=file_path,
            file=file_bytes,
            file_options={"content-type": content_type}
        )
        
        # Construct Public URL manually as requested to ensure format
        # https://[project_id].supabase.co/storage/v1/object/public/Resumes_lake/resumes/[filename]
        # SUPABASE_URL is https://[project_id].supabase.co
        
        # Remove trailing slash if present
        base_url = SUPABASE_URL.rstrip('/')
        public_url = f"{base_url}/storage/v1/object/public/{BUCKET_NAME}/{file_path}"
        
        print(f"File uploaded to: {public_url}")
        return public_url
        
    except Exception as e:
        print(f"Error uploading file to Supabase: {e}")
        raise e

def create_candidate(parsed_data: dict) -> str:
    """
    Create or get candidate based on email.
    
    Args:
        parsed_data: Parsed resume data containing basic info
        
    Returns:
        str: Candidate ID (UUID)
    """
    supabase = init_supabase()
    
    # Extract info
    name = parsed_data.get("name", "Unknown Candidate")
    email = None
    phone = None
    
    # Contact info is typicaly in 'contacts' array or top level fields in schema
    # The schema used in resume_parser.py puts contacts in a list of strings.
    # We need to extract email from there.
    if "contacts" in parsed_data:
        for contact in parsed_data["contacts"]:
            if "@" in contact:
                email = contact
            elif any(char.isdigit() for char in contact):
                phone = contact
    
    # Schema also has 'name', 'location', 'linkedin_url'
    linkedin_url = parsed_data.get("linkedin_url")
    location = parsed_data.get("location")
    
    # If no email, we create a new candidate every time? Or try to match by name?
    # Matching by name is risky. Let's assume unique email if present.
    
    candidate_id = None
    
    if email:
        # Check if exists
        res = supabase.table("candidates").select("id").eq("email", email).execute()
        if res.data:
            candidate_id = res.data[0]["id"]
            print(f"Found existing candidate: {candidate_id}")
            return candidate_id
            
    # Create new
    candidate_data = {
        "full_name": name,
        "email": email,
        "phone": phone,
        "linkedin_url": linkedin_url,
        "location": location,
        "source": "upload"
    }
    
    res = supabase.table("candidates").insert(candidate_data).execute()
    if res.data:
        candidate_id = res.data[0]["id"]
        print(f"Created new candidate: {candidate_id}")
        return candidate_id
    
    raise Exception("Failed to create candidate")

def create_resume(candidate_id: str, parsed_data: dict, file_url: str, resume_text: str = None) -> str:
    """
    Insert resume record.
    
    Args:
        candidate_id: UUID of candidate
        parsed_data: JSON data
        file_url: URL to file in storage
        resume_text: Raw text content (optional)
        
    Returns:
        str: Resume ID (UUID)
    """
    supabase = init_supabase()
    
    resume_data = {
        "candidate_id": candidate_id,
        "parsed_data": parsed_data,
        "file_url": file_url,
        "source": "upload",
        "enriched": False
        # "parsed_text": resume_text # If we want to store it, we need to handle tsvector conversion or just text
        # The schema says parsed_text is tsvector. Supabase/Postgres handles cast if we pass string? 
        # Usually client sends string, Postgres casts.
    }
    
    res = supabase.table("resumes").insert(resume_data).execute()
    if res.data:
        resume_id = res.data[0]["id"]
        print(f"Created resume record: {resume_id}")
        return resume_id
        
    raise Exception("Failed to create resume record")

def create_application(candidate_id: str, resume_id: str, job_offer_id: str) -> str:
    """
    Create application record.
    
    Args:
        candidate_id: UUID
        resume_id: UUID
        job_offer_id: UUID
        
    Returns:
        str: Application ID (UUID)
    """
    supabase = init_supabase()
    
    app_data = {
        "candidate_id": candidate_id,
        "resume_id": resume_id,
        "job_offer_id": job_offer_id,
        "status": "applied"
    }
    
    res = supabase.table("applications").insert(app_data).execute()
    if res.data:
        app_id = res.data[0]["id"]
        print(f"Created application: {app_id}")
        return app_id
        
    raise Exception("Failed to create application")

def add_attachment(resume_id: str, storage_path: str, filename: str, content_type: str, size: int) -> str:
    """
    Add record to attachments table.
    """
    supabase = init_supabase()
    
    attachment_data = {
        "resume_id": resume_id,
        "storage_path": storage_path,
        "filename": filename,
        "content_type": content_type,
        "size_bytes": size
    }
    
    res = supabase.table("attachments").insert(attachment_data).execute()
    if res.data:
        return res.data[0]["id"]
    return None
