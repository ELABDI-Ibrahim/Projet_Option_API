"""Verify resume against LinkedIn data."""

from services.utils import normalize_text, parse_date, months_difference, semantic_similarity
from services.matching import fuzzy_company_match, fuzzy_title_match, find_matching_experience, tfidf_match


def verify_experience(resume_exp: dict, linkedin_exp: dict) -> list[dict]:
    """Verify a single experience entry."""
    discrepancies = []
    
    # Company name
    company_score = fuzzy_company_match(
        resume_exp.get("institution_name", ""),
        linkedin_exp.get("institution_name", "")
    )
    if company_score < 80:
        discrepancies.append({
            "section": "experience.company_name",
            "resume_value": resume_exp.get("institution_name", ""),
            "linkedin_value": linkedin_exp.get("institution_name", ""),
            "severity": "medium" if company_score >= 60 else "high",
            "reason": f"Company name match: {company_score}%"
        })
    
    # Job title
    title_score = fuzzy_title_match(
        resume_exp.get("position_title", ""),
        linkedin_exp.get("position_title", "")
    )
    if title_score < 70:
        discrepancies.append({
            "section": "experience.position_title",
            "resume_value": resume_exp.get("position_title", ""),
            "linkedin_value": linkedin_exp.get("position_title", ""),
            "severity": "medium" if title_score >= 50 else "high",
            "reason": f"Job title match: {title_score}%"
        })
    
    # Start date
    resume_start = parse_date(resume_exp.get("from_date", ""))
    linkedin_start = parse_date(linkedin_exp.get("from_date", ""))
    if resume_start and linkedin_start:
        diff = months_difference(resume_start, linkedin_start)
        if diff > 3:
            discrepancies.append({
                "section": "experience.from_date",
                "resume_value": resume_exp.get("from_date", ""),
                "linkedin_value": linkedin_exp.get("from_date", ""),
                "severity": "high" if diff > 6 else "medium",
                "reason": f"Start date difference: {diff} months"
            })
    
    # End date
    resume_end = parse_date(resume_exp.get("to_date", ""))
    linkedin_end = parse_date(linkedin_exp.get("to_date", ""))
    if resume_end and linkedin_end:
        diff = months_difference(resume_end, linkedin_end)
        if diff > 3:
            discrepancies.append({
                "section": "experience.to_date",
                "resume_value": resume_exp.get("to_date", ""),
                "linkedin_value": linkedin_exp.get("to_date", ""),
                "severity": "high" if diff > 6 else "medium",
                "reason": f"End date difference: {diff} months"
            })
    
    # Description similarity
    resume_desc = resume_exp.get("description", "")
    linkedin_desc = linkedin_exp.get("description", "")
    if resume_desc and linkedin_desc:
        similarity = semantic_similarity(resume_desc, linkedin_desc)
        if similarity < 0.7:
            discrepancies.append({
                "section": "experience.description",
                "resume_value": resume_desc[:100] + "..." if len(resume_desc) > 100 else resume_desc,
                "linkedin_value": linkedin_desc[:100] + "..." if len(linkedin_desc) > 100 else linkedin_desc,
                "severity": "low" if similarity >= 0.5 else "medium",
                "reason": f"Description similarity: {similarity:.2f}"
            })
    
    return discrepancies


def verify_education(resume_edu: dict, linkedin_edu: dict) -> list[dict]:
    """Verify a single education entry."""
    discrepancies = []
    
    score = tfidf_match(
        resume_edu.get("institution_name", ""),
        linkedin_edu.get("institution_name", "")
    )
    if score < 80:
        discrepancies.append({
            "section": "education.institution_name",
            "resume_value": resume_edu.get("institution_name", ""),
            "linkedin_value": linkedin_edu.get("institution_name", ""),
            "severity": "medium",
            "reason": f"Institution match: {score}%"
        })
    
    return discrepancies


def run_verification(resume: dict, linkedin: dict) -> dict:
    """Run full verification between resume and LinkedIn."""
    discrepancies = []
    matched = 0
    total = len(resume.get("experiences", []))
    
    # Verify experiences
    for resume_exp in resume.get("experiences", []):
        linkedin_exp = find_matching_experience(resume_exp, linkedin.get("experiences", []))
        
        if linkedin_exp:
            matched += 1
            discrepancies.extend(verify_experience(resume_exp, linkedin_exp))
        else:
            discrepancies.append({
                "section": "experience",
                "resume_value": f"{resume_exp.get('position_title', '')} at {resume_exp.get('institution_name', '')}",
                "linkedin_value": "Not found",
                "severity": "high",
                "reason": "Experience not found in LinkedIn"
            })
    
    # Check LinkedIn-only experiences
    for linkedin_exp in linkedin.get("experiences", []):
        if not find_matching_experience(linkedin_exp, resume.get("experiences", [])):
            discrepancies.append({
                "section": "experience",
                "resume_value": "Not found",
                "linkedin_value": f"{linkedin_exp.get('position_title', '')} at {linkedin_exp.get('institution_name', '')}",
                "severity": "medium",
                "reason": "LinkedIn experience not in resume"
            })
    
    # Verify education
    for i, resume_edu in enumerate(resume.get("educations", [])):
        linkedin_edus = linkedin.get("educations", [])
        if i < len(linkedin_edus):
            discrepancies.extend(verify_education(resume_edu, linkedin_edus[i]))
    
    # Calculate confidence
    high = sum(1 for d in discrepancies if d.get("severity") == "high")
    medium = sum(1 for d in discrepancies if d.get("severity") == "medium")
    low = sum(1 for d in discrepancies if d.get("severity") == "low")
    
    confidence = max(0.0, min(1.0, 1.0 - (high * 0.15) - (medium * 0.05) - (low * 0.02)))
    
    if confidence >= 0.9:
        summary = "High consistency between resume and LinkedIn."
    elif confidence >= 0.7:
        summary = "Good consistency with minor discrepancies."
    elif confidence >= 0.5:
        summary = "Moderate consistency - review needed."
    else:
        summary = "Low consistency - significant discrepancies."
    
    return {
        "verification_summary": summary,
        "discrepancies": discrepancies,
        "overall_confidence": round(confidence, 2),
        "statistics": {
            "total_discrepancies": len(discrepancies),
            "high_severity": high,
            "medium_severity": medium,
            "low_severity": low,
            "matched_experiences": f"{matched}/{total}"
        }
    }