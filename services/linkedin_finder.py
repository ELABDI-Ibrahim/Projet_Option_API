#!/usr/bin/env python3
"""
LinkedIn Profile Finder - Using duckduckgo-search library
pip install duckduckgo-search
"""

from ddgs import DDGS
import re

def find_linkedin(name, email=None, company=None, location=None, debug=False):
    """
    Find LinkedIn profile using DuckDuckGo.
    """
    # Build query
    query = f'site:linkedin.com/in/ "{name}"'
    if company:
        query += f' "{company}"'
    if location:
        query += f' "{location}"'
    if email and "@" in email:
        domain = email.split("@")[1].split(".")[0]
        if domain.lower() not in ["gmail", "yahoo", "hotmail", "outlook"]:
            query += f' "{domain}"'
    
    if debug:
        print(f"[DEBUG] Query: {query}")
    
    # Search using duckduckgo-search library
    results = DDGS().text(query, max_results=10)
    
    if debug:
        print(f"[DEBUG] Found {len(results)} results")
        for i, r in enumerate(results):
            print(f"[DEBUG] {i}: {r['href']}")
            print(f"         Title: {r['title']}")
    
    # Find LinkedIn profile in results
    for r in results:
        url = r.get('href', '')
        match = re.search(r'linkedin\.com/in/([a-zA-Z0-9\-_%]+)', url)
        if match:
            username = match.group(1).split("?")[0]
            return {
                "url": f"https://www.linkedin.com/in/{username}",
                "name": r.get('title', '').split(' - ')[0].split(' | ')[0],
                "snippet": r.get('body', '')
            }
    
    return None


def find_linkedin_bulk(people, delay=2):
    """Find LinkedIn for multiple people."""
    import time
    results = []
    
    for i, p in enumerate(people):
        print(f"[{i+1}/{len(people)}] {p.get('name')}")
        result = find_linkedin(
            name=p.get("name", ""),
            email=p.get("email"),
            company=p.get("company"),
            location=p.get("location")
        )
        results.append({"input": p, "linkedin": result})
        
        if result:
            print(f"  ✓ {result['url']}")
        else:
            print(f"  ✗ Not found")
        
        if i < len(people) - 1:
            time.sleep(delay)
    
    return results