## 📍 Endpoints

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

### 5. Scrape LinkedIn
```bash
POST /api/scrape-linkedin
Content-Type: application/json

# Body:
{
  "profile_url": "https://linkedin.com/in/username"
}

# Response: Full profile data
# ⚠️ Requires session.json
```

### 6. Verify Resume
```bash
POST /api/verify

# Method A: File Upload
Content-Type: multipart/form-data
Body: file=resume.pdf, linkedin_url=...

# Method B: JSON
Content-Type: application/json
Body: {"resume_data": {...}, "linkedin_data": {...}}

# Response: Verification report with confidence score
```
