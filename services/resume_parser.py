import os
import json
import re
from groq import Groq
from PyPDF2 import PdfReader


# --------------------------------------------------
# 1. PDF → CLEAN TEXT (LOW TOKEN, SAFE)
# --------------------------------------------------
# services/resume_parser.py

import os
import json
import re
from groq import Groq
from PyPDF2 import PdfReader

# --------------------------------------------------
# 1. PDF → CLEAN TEXT (LOW TOKEN, SAFE)
# --------------------------------------------------
def pdf_to_text_minimal_tokens(pdf_path):
    text = ""
    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            page_text = page.extract_text() or ""
            # Filter non-printable characters and extra spaces
            page_text = ''.join(c for c in page_text if c.isprintable())
            page_text = re.sub(r'\s+', ' ', page_text).strip()
            text += page_text + "\n"

        # Remove duplicated lines (basic header/footer cleanup)
        seen = set()
        clean_lines = []
        for line in text.split("\n"):
            if line and line not in seen:
                clean_lines.append(line)
                seen.add(line)

        return "\n".join(clean_lines).strip()

    except Exception as e:
        print(f"PDF error: {e}")
        return None

# --------------------------------------------------
# 2. GROQ RESUME PARSER (STRICT COMPLIANT)
# --------------------------------------------------
def parse_resume_with_groq(resume_text_content):
    if not resume_text_content:
        return None

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    json_schema = {
        "name": "resume_extraction_schema",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "linkedin_url": {"type": ["string", "null"]},
                "name": {"type": "string"},
                "location": {"type": ["string", "null"]},
                "about": {"type": ["string", "null"]},
                "open_to_work": {"type": ["boolean", "null"]},

                "experiences": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "position_title": {"type": "string"},
                            "institution_name": {"type": "string"},
                            "linkedin_url": {"type": ["string", "null"]},
                            "from_date": {"type": ["string", "null"]},
                            "to_date": {"type": ["string", "null"]},
                            "duration": {"type": ["string", "null"]},
                            "location": {"type": ["string", "null"]},
                            "description": {"type": ["string", "null"]}
                        },
                        # STRICT MODE FIX: All properties must be in required
                        "required": [
                            "position_title", "institution_name", "linkedin_url",
                            "from_date", "to_date", "duration", "location", "description"
                        ],
                        "additionalProperties": False
                    }
                },

                "educations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "degree": {"type": "string"},
                            "institution_name": {"type": "string"},
                            "linkedin_url": {"type": ["string", "null"]},
                            "from_date": {"type": ["string", "null"]},
                            "to_date": {"type": ["string", "null"]},
                            "duration": {"type": ["string", "null"]},
                            "location": {"type": ["string", "null"]},
                            "description": {"type": ["string", "null"]}
                        },
                        # STRICT MODE FIX: All properties must be in required
                        "required": [
                            "degree", "institution_name", "linkedin_url",
                            "from_date", "to_date", "duration", "location", "description"
                        ],
                        "additionalProperties": False
                    }
                },

                "skills": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "category": {"type": "string"},
                            "items": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["category", "items"],
                        "additionalProperties": False
                    }
                },

                "projects": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "project_name": {"type": "string"},
                            "role": {"type": ["string", "null"]},
                            "from_date": {"type": ["string", "null"]},
                            "to_date": {"type": ["string", "null"]},
                            "duration": {"type": ["string", "null"]},
                            "technologies": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "description": {"type": ["string", "null"]},
                            "url": {"type": ["string", "null"]}
                        },
                        # STRICT MODE FIX: All properties must be in required
                        "required": [
                            "project_name", "role", "from_date", "to_date", 
                            "duration", "technologies", "description", "url"
                        ],
                        "additionalProperties": False
                    }
                },

                "interests": {
                    "type": "array",
                    "items": {"type": "string"}
                },

                "accomplishments": {
                    "type": "array",
                    "items": {"type": "string"}
                },

                "contacts": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            # STRICT MODE FIX: All root properties must be in required
            "required": [
                "linkedin_url", "name", "location", "about", "open_to_work",
                "experiences", "educations", "skills", "projects",
                "interests", "accomplishments", "contacts"
            ],
            "additionalProperties": False
        }
    }

    try:
        # Note: 'openai/gpt-oss-120b' might be deprecated or invalid on Groq.
        # Switched to a reliable standard model. Change back if your specific endpoint requires it.
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b", 
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a resume extraction engine.\n"
                        "Extract text EXACTLY as written. Do NOT infer or summarize.\n"
                        "If a value is missing, return null."
                    )
                },
                {
                    "role": "user",
                    "content": f"Parse this resume:\n\n{resume_text_content}"
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": json_schema
            }
        )

        return json.loads(completion.choices[0].message.content)

    except Exception as e:
        print("Groq parsing error:", str(e))
        raise
