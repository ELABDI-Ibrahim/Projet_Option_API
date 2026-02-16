import os
import json
import re
from groq import Groq
from PyPDF2 import PdfReader
import os
import json
from groq import Groq, BadRequestError


# --------------------------------------------------
# 1. PDF → CLEAN TEXT (LOW TOKEN, SAFE)
# --------------------------------------------------
# services/resume_parser.py

import os
import json
import base64
import requests
import fitz  # PyMuPDF
from groq import Groq

# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------
NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY")
INVOKE_URL = "https://ai.api.nvidia.com/v1/cv/baidu/paddleocr"

# --------------------------------------------------
# 1. PDF/IMAGE → TEXT (NVIDIA OCR)
# --------------------------------------------------

def get_headers():
    return {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Accept": "application/json"
    }

def ocr_image(image_bytes, ext):
    """Send image bytes to NVIDIA PaddleOCR and return JSON."""
    try:
        image_b64 = base64.b64encode(image_bytes).decode()
        # Handle extension for data URI
        ext_str = ext[1:] if ext.startswith('.') else ext
        
        payload = {
            "input": [
                {
                    "type": "image_url",
                    "url": f"data:image/{ext_str};base64,{image_b64}"
                }
            ]
        }

        print(f"Image sent to NVIDIA PaddleOCR API")

        response = requests.post(INVOKE_URL, headers=get_headers(), json=payload)

        if response.status_code == 200:
            print(f"response received")
            return response.json()
        else:
            return {"error": f"API Error {response.status_code}", "body": response.text}

    except Exception as e:
        return {"error": str(e)}

def extract_text_from_ocr_result(ocr_result):
    """Extract only text lines from NVIDIA PaddleOCR result."""
    text_lines = []

    if "data" in ocr_result:
        for page in ocr_result["data"]:
            # New key used by the API
            if "text_detections" in page:
                for det in page["text_detections"]:
                    # "text_prediction" contains the recognized text
                    if "text_prediction" in det:
                        txt = det["text_prediction"].get("text", "").strip()
                        if txt:
                            text_lines.append(txt)

            # ALSO support older versions (fallback)
            elif "items" in page:
                for item in page["items"]:
                    if "text_prediction" in item:
                        txt = item["text_prediction"].get("text", "").strip()
                        if txt:
                            text_lines.append(txt)

    return "\n".join(text_lines)


def process_pdf(file_path):
    """Extract text from PDF; OCR pages with no text."""
    results = []
    try:
        doc = fitz.open(file_path)

        for page_num, page in enumerate(doc):
            print(f"--- Processing Page {page_num + 1} ---")

            # Extract selectable text
            text = page.get_text()
            
            if len(text.strip()) > 1000:
                print("Found text directly in PDF.")
                results.append({
                    "page": page_num + 1,
                    "type": "text_extraction",
                    "content": text
                })
            else:
                print("No text found (or < 1000 chars) — performing OCR.")
                
                # --- FIX START ---
                # 2.0 = 2x zoom (approx 144 dpi). 
                # 3.0 = 3x zoom (approx 216 dpi). Recommended for Resume OCR.
                zoom_x = 3.0  
                zoom_y = 3.0
                mat = fitz.Matrix(zoom_x, zoom_y)
                
                # Pass the matrix to get_pixmap
                pix = page.get_pixmap(matrix=mat)
                # --- FIX END ---

                image_bytes = pix.tobytes("png")
                
                # Optional: Check size to ensure you don't hit NVIDIA API limits (e.g., 5MB or 10MB)
                print(f"Image size: {len(image_bytes) / 1024 / 1024:.2f} MB")
                
                ocr_result = ocr_image(image_bytes, "png")

                results.append({
                    "page": page_num + 1,
                    "type": "ocr",
                    "content": ocr_result
                })

        return results
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return []

def process_image(file_path, ext):
    """Process a single image file with OCR."""
    try:
        with open(file_path, "rb") as f:
            image_bytes = f.read()
            print("Image read successfully.")
        return ocr_image(image_bytes, ext)
    except Exception as e:
        return {"error": str(e)}

def process_file(file_path):
    """Route file to PDF or image handler."""
    if not os.path.exists(file_path):
        return {"error": "File not found"}

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        result = process_pdf(file_path)
        return format_ocr_output(result)
    elif ext in [".jpg", ".jpeg", ".png", ".bmp"]:
        result = process_image(file_path, ext)
        return format_ocr_output(result)
    else:
        return {"error": "Unsupported file type"}

def format_ocr_output(result):
    """Format OCR results into plain text only."""
    output_text = ""

    # PDF result
    if isinstance(result, list):
        for entry in result:
            output_text += f"\n--- Page {entry.get('page')} ---\n"

            if entry.get("type") == "text_extraction":
                output_text += entry.get("content", "").strip() + "\n"
            elif entry.get("type") == "ocr":
                output_text += extract_text_from_ocr_result(entry.get("content", {})) + "\n"

    # Single image result
    elif isinstance(result, dict):
        if "error" in result:
            output_text = f"Error: {result['error']}"
        else:
            output_text = extract_text_from_ocr_result(result)

    return output_text.strip()

# Wrapper to maintain compatibility
def pdf_to_text_minimal_tokens(pdf_path):
    return process_file(pdf_path)

def sanitize_json_output(data):
    """
    Recursively cleans string values in a JSON object/list:
    1. Replaces <br> variations with \n
    2. Removes HTML tags like <b>, <ul>, <li>
    3. Fixes multiple newlines
    """
    if isinstance(data, dict):
        return {k: sanitize_json_output(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_json_output(item) for item in data]
    elif isinstance(data, str):
        # 1. Replace <br> tags with \n
        text = re.sub(r'<\s*br\s*/?>', '\n', data, flags=re.IGNORECASE)
        # 2. Remove other common HTML tags (like <b>, </b>, <ul>)
        text = re.sub(r'<[^>]+>', '', text)
        # 3. Replace multiple newlines with a single newline (optional, depends on preference)
        text = re.sub(r'\n\s*\n', '\n', text)
        return text.strip()
    else:
        return data

# --------------------------------------------------
# 2. GROQ RESUME PARSER WITH AUTO-RETRY
# --------------------------------------------------
def parse_resume_with_groq(resume_text_content):
    if not resume_text_content:
        return None

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    # Define the schema (Same as your original)
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
                        "required": [
                            "project_name", "role", "from_date", "to_date", 
                            "duration", "technologies", "description", "url"
                        ],
                        "additionalProperties": False
                    }
                },
                "interests": {"type": "array", "items": {"type": "string"}},
                "accomplishments": {"type": "array", "items": {"type": "string"}},
                "contacts": {"type": "array", "items": {"type": "string"}}
            },
            "required": [
                "linkedin_url", "name", "location", "about", "open_to_work",
                "experiences", "educations", "skills", "projects",
                "interests", "accomplishments", "contacts"
            ],
            "additionalProperties": False
        }
    }

    # Initialize messages
    # ... inside parse_resume_with_groq ...

    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert Resume Parsing API designed to output strict JSON data.\n"
                "Your goal is to extract information accurately while sanitizing the formatting.\n\n"
                
                "### CORE INSTRUCTIONS:\n"
                "1. **Extraction:** Extract information accurately. Do not summarize or hallucinate.\n"
                "2. **Missing Data:** If a field is not present, return `null`.\n"
                "3. **Dates:** Keep dates in their original format (e.g., 'Jan 2020', '2020-01').\n\n"

                "### SKILLS EXTRACTION STRATEGY (CRITICAL):\n"
                "The schema requires an array of objects, where each object has a 'category' and a list of 'items'.\n"
                "1. **Identify:** Scan the *entire* resume (Summary, Experience, Projects, Skills section) for technical and professional skills.\n"
                "2. **Categorize:** You MUST group these skills into logical categories (e.g., 'Languages', 'Frameworks', 'Databases', 'Cloud', 'Soft Skills').\n"
                "3. **Infer:** If the resume lists skills in a single comma-separated list without headers, analyze the items and create your own categories to group them logically.\n"
                "4. **Format:** Ensure every skill is a distinct string item within its specific category list.\n\n"

                "### FORMATTING & CLEANING RULES:\n"
                "1. **Plain Text Only:** The output must be pure JSON strings. STRICTLY FORBIDDEN: HTML tags (e.g., <br>, <p>, <li>, <b>).\n"
                "2. **Line Breaks:** You must detect where a new sentence or bullet point begins.\n"
                "   - REPLACE all visual bullet points (•, -, *) with a standard newline character (`\\n`).\n"
                "   - REPLACE all HTML break tags (<br>) with a standard newline character (`\\n`).\n"
                "3. **Whitespace:** Trim excessive whitespace.\n"
            )
        },
        {
            "role": "user",
            "content": f"Parse the following resume content into the defined JSON schema:\n\n{resume_text_content}"
        }
    ]

    max_retries = 3
    attempt = 0

    while attempt < max_retries:
        try:
            print(f"--- Groq Parsing Attempt {attempt + 1} ---")
            
            completion = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=messages,
                response_format={
                    "type": "json_schema",
                    "json_schema": json_schema
                }
            )
            
            # Load the raw JSON
            raw_json = json.loads(completion.choices[0].message.content)
            
            # --- NEW: CLEAN THE JSON BEFORE RETURNING ---
            clean_json = sanitize_json_output(raw_json)
            
            return clean_json

        except BadRequestError as e:
            # Handle 400 Errors (Schema Validation Failed)
            error_data = e.body.get("error", {})
            code = error_data.get("code")
            
            if code == "json_validate_failed":
                failed_json = error_data.get("failed_generation", "")
                error_msg = error_data.get("message", "Unknown validation error")
                
                print(f"Validation failed: {error_msg}")
                
                # Append the error details to messages to give the LLM context
                # It acts like a conversation: User -> Assistant (Failed) -> User (Correction Request)
                
                # Note: We cannot append the 'failed' assistant message directly 
                # because it wasn't valid, so we tell the user what happened.
                messages.append({
                    "role": "user", 
                    "content": (
                        f"The JSON you generated failed validation.\n"
                        f"Error: {error_msg}\n"
                        f"Failed JSON: {failed_json}\n\n"
                        "Please regenerate the JSON, correcting the missing fields (like 'to_date') "
                        "ensure strict adherence to the schema."
                    )
                })
                attempt += 1
            else:
                # If it's a different 400 error, raise it immediately
                print(f"Critical API Error: {str(e)}")
                raise e

        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            raise e

    print("Max retries exceeded.")
    return None
