"""LinkedIn profile scraping service."""

import os
import json
import re
import asyncio
from linkedin_scraper import ConsoleCallback, PersonScraper, BrowserManager


def normalize_name(name: str) -> str:
    """Normalize name for comparison."""
    if not name:
        return ""
    # Remove non-alphanumeric, lower case, strip
    return re.sub(r'[^a-z0-9]', '', name.lower())


def find_local_profile(name: str) -> dict | None:
    """
    Search for a local JSON profile in 'Resumes LinkedIn' that matches the name.
    """
    if not name:
        return None
        
    # Get project root (assuming services/ is one level deep)
    # Current file: services/linkedin_scraper.py -> parent: project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    resumes_dir = os.path.join(project_root, 'Resumes LinkedIn')
    
    if not os.path.exists(resumes_dir):
        return None
        
    target_name = normalize_name(name)
    
    try:
        files = [f for f in os.listdir(resumes_dir) if f.endswith('.json')]
    except OSError:
        return None
        
    # Strategy 1: Exact containment of normalized name
    for filename in files:
        clean_filename = filename.replace('_profile.json', '').replace('.json', '')
        normalized_filename = normalize_name(clean_filename)
        
        if target_name in normalized_filename or normalized_filename in target_name:
            filepath = os.path.join(resumes_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                continue
                
    # Strategy 2: Check if all parts of the name are present
    name_parts = set(normalize_name(p) for p in name.split() if len(p) > 2)
    
    if not name_parts:
        return None
        
    for filename in files:
        clean_filename = filename.replace('_profile.json', '').replace('.json', '')
        normalized_filename = normalize_name(clean_filename)
        
        if all(part in normalized_filename for part in name_parts):
            filepath = os.path.join(resumes_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                continue
                
    return None


async def scrape_linkedin_profile(profile_url: str, name: str = None) -> dict:
    """
    Scrape a LinkedIn profile and return the data.
    Checks local 'Resumes LinkedIn' folder first.
    
    Args:
        profile_url: Full LinkedIn profile URL
        name: Name of the person (optional, for local search)
        
    Returns:
        Dictionary with profile data
    """
    # 1. Try to find locally first
    
    # If name is not provided, try to extract from URL
    # https://www.linkedin.com/in/john-doe-12345/ -> john-doe
    search_name = name
    if not search_name and "/in/" in profile_url:
        try:
            url_part = profile_url.split("/in/")[1].split("/")[0]
            # Remove trailing numbers like -12345 (common in linkedin urls)
            # This is heuristics, might not be perfect
            parts = url_part.split('-')
            alpha_parts = [p for p in parts if not p.isdigit()]
            if alpha_parts:
                search_name = " ".join(alpha_parts)
        except Exception:
            pass
            
    if search_name:
        local_data = find_local_profile(search_name)
        if local_data:
            print(f"Found local profile for {search_name}")
            return local_data

    # # 2. If not found locally, scrape it
    # async with BrowserManager(headless=True, slow_mo=1000, args=["--no-sandbox"]) as browser:
    #     callback = ConsoleCallback()
        
    #     # Load authenticated session
    #     await browser.load_session("session.json")
        
    #     # Create scraper
    #     scraper = PersonScraper(browser.page, callback=callback)
        
    #     # Scrape profile
    #     person = await scraper.scrape(profile_url)
        
    #     # Convert Pydantic model to dictionary
    #     profile_data = person.model_dump(mode="json")
        
    #     return profile_data

    print("Profile not found locally")
    return None