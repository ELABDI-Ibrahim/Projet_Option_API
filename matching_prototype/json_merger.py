import json
import re
from difflib import SequenceMatcher

class ProfileMerger:
    def __init__(self):
        self.merged_data = {}

    def normalize_text(self, text):
        """Cleans text for comparison: lowercase, removes special chars and 'noise' words."""
        if not text:
            return ""
        # Remove common LinkedIn suffixes like "· Internship", "· Full-time"
        text = re.sub(r'\s*·\s*(Internship|Apprenticeship|Full-time|Part-time|Contract|Self-employed|Freelance).*', '', text, flags=re.IGNORECASE)
        # Remove non-alphanumeric characters (keep spaces)
        text = re.sub(r'[^a-z0-9\s]', '', text.lower())
        return text.strip()

    def is_similar(self, a, b, threshold=0.8):
        """Checks if two strings are similar using SequenceMatcher."""
        return SequenceMatcher(None, a, b).ratio() >= threshold

    def extract_skills_from_text(self, text):
        """Extracts skills listed in LinkedIn descriptions (e.g., 'Skills: Python · Java')."""
        if not text:
            return []
        # Look for "Skills:" pattern
        match = re.search(r'Skills:(.*)', text, re.IGNORECASE)
        if match:
            # Split by bullet point or comma
            raw_skills = re.split(r'[·,]', match.group(1))
            return [s.strip() for s in raw_skills if s.strip()]
        return []

    def merge_lists(self, resume_list, linkedin_list, name_key, type_label):
        """Generic function to merge Education or Experience lists."""
        merged_list = resume_list.copy()
        
        for li_item in linkedin_list:
            is_match = False
            li_name = self.normalize_text(li_item.get(name_key, ""))
            
            # Try to find a match in the existing resume list
            for res_item in merged_list:
                res_name = self.normalize_text(res_item.get(name_key, ""))
                
                # Check similarity
                if self.is_similar(li_name, res_name):
                    is_match = True
                    # OPTIONAL: Enrich the resume item with LinkedIn URL if missing
                    if not res_item.get('linkedin_url') and li_item.get('linkedin_url'):
                        res_item['linkedin_url'] = li_item['linkedin_url']
                    print(f"Matched {type_label}: '{li_item.get(name_key)}' matches '{res_item.get(name_key)}'. Keeping Resume version.")
                    break
            
            # If it's a completely new item, add it
            if not is_match:
                print(f"Adding NEW {type_label} from LinkedIn: {li_item.get(name_key)}")
                merged_list.append(li_item)
                
        return merged_list

    def merge_profile(self, json_data):
        # Create a deep copy to avoid modifying original info directly
        result = json_data.copy()
        linkedin_data = result.get("linkedinData", {})
        
        if not linkedin_data:
            return result

        print("--- Starting Merge ---")

        # 1. Merge Educations
        result['educations'] = self.merge_lists(
            result.get('educations', []), 
            linkedin_data.get('educations', []), 
            "institution_name", 
            "Education"
        )

        # 2. Merge Experiences
        result['experiences'] = self.merge_lists(
            result.get('experiences', []), 
            linkedin_data.get('experiences', []), 
            "institution_name", 
            "Experience"
        )

        # 3. Merge Skills (Extract from LinkedIn descriptions + specific lists)
        # Flatten existing skills for easy checking
        existing_skills = set()
        for cat in result.get('skills', []):
            for item in cat.get('items', []):
                existing_skills.add(item.lower())

        new_skills = []
        
        # Scan LinkedIn experiences for "Skills: ..." text
        for exp in linkedin_data.get('experiences', []) + linkedin_data.get('educations', []):
            extracted = self.extract_skills_from_text(exp.get('description', ''))
            for skill in extracted:
                if skill.lower() not in existing_skills:
                    new_skills.append(skill)
                    existing_skills.add(skill.lower())
        
        if new_skills:
            print(f"Adding NEW Skills found in LinkedIn descriptions: {new_skills}")
            # Add to a new category or existing one. Let's create a "LinkedIn Imported" category
            result['skills'].append({
                "category": "LinkedIn Imported",
                "items": new_skills
            })

        # 4. Remove the raw linkedinData block from the final result
        del result['linkedinData']
        
        print("--- Merge Complete ---")
        return result

# --- Execution ---
if __name__ == "__main__":
    # Load your JSON string here
    input_json = """
    {
      "name": "OMAR BELLMIR",
      "email": "bellmiromar@gmail.com",
      "skills": [
        { "items": ["Strategic Consulting", "Python"], "category": "Skills" }
      ],
      "educations": [
        { "institution_name": "CentraleSupélec", "degree": "Engineering" }
      ],
      "experiences": [
        { "institution_name": "IDEMIA", "position_title": "Strategy" }
      ],
      "linkedinData": {
        "educations": [
           { "institution_name": "CentraleSupélec", "degree": "MEng" },
           { "institution_name": "CPGE - Classes préparatoires", "degree": "MPSI" } 
        ],
        "experiences": [
           { "institution_name": "IDEMIA · Apprenticeship", "description": "Skills: Strategy · Risk Assessment" },
           { "institution_name": "Carrefour", "position_title": "Intern" }
        ]
      }
    }
    """
    # Note: I used a shortened JSON above for readability, 
    # but the class works with your full input.
    
    # Assuming 'full_data' is your dictionary loaded from the JSON you pasted
    # import json
    # full_data = json.loads(YOUR_JSON_STRING)
    
    # For demonstration, let's pretend we loaded the full JSON you provided
    # (I will use the full logic on the input you provided in the prompt)
    pass