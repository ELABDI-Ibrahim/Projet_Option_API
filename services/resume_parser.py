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
            page_text = ''.join(c for c in page_text if c.isprintable())
            page_text = re.sub(r'\s+', ' ', page_text).strip()
            text += page_text + "\n"

        # remove duplicated lines (basic header/footer cleanup)
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
# 2. GROQ RESUME PARSER (STRICT BUT SAFE)
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
                        "required": [
                            "position_title",
                            "institution_name"
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
                        "required": [
                            "degree",
                            "institution_name"
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
                        "required": ["project_name"],
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

            "required": [
                "linkedin_url",
                "name",
                "location",
                "about",
                "open_to_work",
                "experiences",
                "educations",
                "skills",
                "projects",
                "interests",
                "accomplishments",
                "contacts"
            ],

            "additionalProperties": False
        }
    }

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a resume extraction engine.\n\n"
                        "RULES:\n"
                        "1. Extract text EXACTLY as written.\n"
                        "2. Do NOT infer or summarize.\n"
                        "3. If a value is missing, use null or empty array.\n"
                        "4. Do NOT translate technical terms, tools, job titles, or company names.\n"
                        "5. Output ONLY valid JSON matching the schema.\n"
                        "6. Structural mapping only."
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
