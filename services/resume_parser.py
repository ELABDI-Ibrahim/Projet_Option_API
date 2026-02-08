import os
from groq import Groq
import json
from PyPDF2 import PdfReader
import re

# Keep those only for local
# from dotenv import load_dotenv
# # Load environment variables from .env file
# load_dotenv()

# --- 1. Improved PDF to Text Conversion Function ---
def pdf_to_text_minimal_tokens(pdf_path):
    """
    Extracts and cleans text from a PDF file using PyPDF2.
    Cleans up:
    - Extra newlines
    - Repeated headers/footers (basic approach)
    - Multiple spaces
    - Non-printable characters
    """
    text = ""
    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            page_text = page.extract_text() or ""
            
            # Remove non-printable characters
            page_text = ''.join(c for c in page_text if c.isprintable())
            
            # Remove excessive whitespace and newlines
            page_text = re.sub(r'\s+', ' ', page_text).strip()
            
            # Add a single newline between pages
            text += page_text + "\n"
            
        # Optional: Remove repeated headers/footers (simple heuristic)
        lines = text.split('\n')
        seen = set()
        clean_lines = []
        for line in lines:
            if line not in seen and line.strip() != "":
                clean_lines.append(line.strip())
                seen.add(line)
        text = "\n".join(clean_lines)

    except FileNotFoundError:
        print(f"Error: File not found at {pdf_path}")
        return None
    except Exception as e:
        print(f"An error occurred while reading the PDF: {e}")
        return None

    return text.strip()



# --- 2. Groq API Structured Output Call ---
def parse_resume_with_groq(resume_text_content):
    """
    Calls the Groq API to parse resume text into a structured JSON format.
    """
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    if not resume_text_content:
        print("Error: No resume text provided.")
        return None

    # Define the target JSON schema
    json_schema = {
        "name": "resume_extraction_schema",
        "strict": True,  # Enable strict mode for guaranteed adherence
        "schema": {
            "type": "object",
            "properties": {
                "linkedin_url": {"type": "string"},
                "name": {"type": "string"},
                "location": {"type": "string"},
                "about": {"type": ["string", "null"]},
                "open_to_work": {"type": "boolean"},
                "experiences": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "position_title": {"type": "string"},
                            "institution_name": {"type": "string"},
                            "linkedin_url": {"type": "string"},
                            "from_date": {"type": "string"},
                            "to_date": {"type": "string"},
                            "duration": {"type": "string"},
                            "location": {"type": "string"},
                            "description": {"type": "string"}
                        },
                        "required": ["position_title", "institution_name", "linkedin_url", "from_date", "to_date", "duration", "location", "description"],
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
                             "linkedin_url": {"type": "string"},
                             "from_date": {"type": "string"},
                             "to_date": {"type": "string"},
                             "duration": {"type": "string"},
                             "location": {"type": "string"},
                             "description": {"type": "string"}
                         },
                         "required": ["degree", "institution_name", "linkedin_url", "from_date", "to_date", "duration", "location", "description"],
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
            "required": ["linkedin_url", "name", "location", "about", "open_to_work", "experiences", "educations", "interests", "accomplishments", "contacts"],
            "additionalProperties": False
        }
    }

    try:
        # Make the API call
        chat_completion = client.chat.completions.create(
            # Use a model that supports Structured Outputs in strict mode, e.g., openai/gpt-oss-20b
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at parsing resumes. Extract the information into the provided JSON schema. If a field cannot be found in the resume, return an appropriate default value (e.g., empty string for strings, null for nullable fields, empty array for arrays). Do not include any explanations outside the JSON object."
                },
                {
                    "role": "user",
                    "content": f"Please parse the following resume text:\n\n{resume_text_content}"
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": json_schema
            }
        )

        # Extract the response content
        raw_response = chat_completion.choices[0].message.content

        # Parse the JSON response
        parsed_resume = json.loads(raw_response)

        return parsed_resume

    except Exception as e:
        print(f"An error occurred during Groq API call: {e}")
        return None