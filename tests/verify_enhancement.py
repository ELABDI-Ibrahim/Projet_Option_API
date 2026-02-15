import json
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from services.enrichement import EnrichmentAgent

# Define Data from the User's new example ("Omar Bellmir")

# 1. Resume Data (Parsed from "english_resume_omar.pdf")
# User provided: 
# "Professional Experience ... Strategy and CSR apprentice ... Analyzed SBTi reduction target ... Recommended the optimal reduction ..."
# And "Supply Chain Backhauling ... Carrefour ... Contributed to ... Assisted in ..."

resume_data_omar = {
  "parsed_data": {
    "name": "OMAR BELLMIR",
    "skills": [
      "Strategic Consulting", "Data Analysis (Python, Excel, KPI Tracking, Financial Modeling)",
      "Business Strategy", "Supply Chain Optimization", "Cost-Benefit Analysis", "Project Management (Agile, Scrum)"
    ],
    "experiences": [
      {
        "position_title": "Strategy and CSR apprentice",
        "institution_name": "IDEMIA",
        "from_date": "Sep 2024",
        "to_date": "Sep 2025",
        "description": "Analyzed SBTi reduction target of 58.8% for Scopes 1, 2, and 3 through scenario modeling and cost assessment. Recommended the optimal reduction pathway based on ROI analysis linked to the Green Cover Bond framework. Conducted natural disaster risk assessments (floods, heatwaves, water stress) for IDEMIA’s sites, guiding site-location decisions."
      },
      {
        "position_title": "Packaging Circularity Optimization",
        "institution_name": "GE Healthcare",
        "from_date": "Jun 2024",
        "to_date": "Sep 2024",
        "description": "Analyzed packaging lifecycle costs, identifying inefficiencies that led to a projected 15% cost reduction and 25% waste minimization."
      },
      {
        "position_title": "Supply Chain Backhauling",
        "institution_name": "Carrefour",
        "from_date": "Feb 2024",
        "to_date": "Jun 2024",
        "description": "Contributed to a supply chain audit, improving logistics efficiency by 10%. Assisted in implementing a backhauling strategy, reducing transportation costs by 2.4%."
      }
    ],
    "projects": [], # Not provided in snippet
    "educations": [] # Not focused on in this test
  }
}

# 2. LinkedIn Data (Enriched / Reference)
# User provided:
# "Strategy and CSR apprentice ... Analyzed SBTi ... Recommended ... Conducted ... Analyzed SBTi ... Recommended ... (Repeated?)"
# AND "Skills: problem modeling · Strategy · Risk Assessment" appended?
# Let's construct the Reference JSON based on "Enriched Data Sourced from LinkedIn Profile" section.

reference_data_omar = {
    # Assuming standard structure
    "name": "OMAR BELLMIR",
    "skills": ["Strategic Consulting", "Problem Solving", "Data Analysis"], # Simplified for brevity
    "experiences": [
      {
        "position_title": "Strategy and CSR apprentice",
        "institution_name": "IDEMIA",
        "from_date": "Sep 2024",
        "to_date": "Sep 2025",
        # NOTE: User showed the text repeated twice in their example snippet? 
        # "Analyzed... decisions. Analyzed... decisions. Skills: problem modeling..."
        # I will include the repeat + the new "Skills: ..." part to test "missing content" detection.
        "description": "Analyzed SBTi reduction target of 58.8% for Scopes 1, 2, and 3 through scenario modeling and cost assessment. Recommended the optimal reduction pathway based on ROI analysis linked to the Green Cover Bond framework. Conducted natural disaster risk assessments (floods, heatwaves, water stress) for IDEMIA’s sites, guiding site location decisions. Skills: problem modeling · Strategy · Risk Assessment" 
      },
      {
        "position_title": "Supply Chain Backhauling Intern", # Note: "Intern" added
        "institution_name": "Carrefour",
        "from_date": "Feb 2024",
        "to_date": "Jun 2024",
        "description": "Contributed to a supply chain audit, improving logistics efficiency by 10%. Assisted in implementing a backhauling strategy, reducing transportation costs by 2.4%. Skills: Logistics · Backhauling" # Added skills
      }
    ],
    "educations": [],
    "projects": []
}

print("Initializing EnrichmentAgent...")
agent = EnrichmentAgent()

print("Running Enrichment on Omar Bellmir Data...")
try:
    result = agent.enrich_resume(resume_data_omar, reference_data_omar)
    print(json.dumps(result, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
