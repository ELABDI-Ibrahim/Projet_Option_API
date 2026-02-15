## Endpoints

### 1. Health Check
```bash
GET /health
# Response: {"status": "healthy"}
```

### 2. Parse Resume
```bash
POST /api/parse-resume
Content-Type: multipart/form-data

# Body: file=resume.pdf
# Response: Structured resume JSON
```

### 3. Find LinkedIn
```bash
POST /api/find-linkedin
Content-Type: application/json

# Body:
{
  "name": "John Doe",
  "company": "Google",      # optional
  "location": "California"  # optional
}

# Response: LinkedIn profile URL
```

### 4. Bulk LinkedIn Search
```bash
POST /api/find-linkedin-bulk
Content-Type: application/json

# Body:
{
  "people": [
    {"name": "Person 1", "company": "Company 1"},
    {"name": "Person 2", "company": "Company 2"}
  ],
  "delay": 2  # seconds between requests
}

# Response: Array of results
```

### 5. Scrape LinkedIn (Enhanced)
Now supports local caching. If a `name` is provided, it checks for an existing profile JSON locally before scraping.

```bash
POST /api/scrape-linkedin
Content-Type: application/json

# Body:
{
  "profile_url": "https://linkedin.com/in/username",
  "name": "John Doe"        # <--- NEW: Optional. Triggers local cache lookup.
}

# Response: Full profile data
# Response: Full profile data
# ⚠️ Requires session.json (unless found locally)
```

### 6. Enrich Resume
Merges resume data with LinkedIn data.

```bash
POST /api/enrich-resume
Content-Type: application/json

# Body:
{
  "resume_data": { ...parsed resume json... },
  "linkedin_url": "https://linkedin.com/in/username", # optional
  "name": "John Doe" # optional
}

# Response: Merged profile data with [Linkedin] tags
```

### 6. Upload Resume
Uploads a resume PDF, parses it using AI, uploads it to storage, and creates database records.

```bash
POST /api/upload-resume
Content-Type: multipart/form-data

# Request Body (form-data):
# - file: (File) The resume PDF file. [Required]
# - job_offer_id: (String/UUID) ID of the job offer to apply for. [Optional]

# Response (JSON):
{
  "success": true,
  "message": "Resume uploaded and application created",
  "data": {
    "candidate_id": "uuid-string",
    "resume_id": "uuid-string",
    "application_id": "uuid-string" or null,
    "file_url": "https://[project-ref].supabase.co/storage/v1/object/public/Resumes_lake/resumes/[timestamp]_[filename].pdf",
    "parsed_data": {
      "name": "Candidate Name",
      "email": "candidate@email.com",
      "skills": ["Python", "SQL", ...],
      ...
    }
  }
}
```
