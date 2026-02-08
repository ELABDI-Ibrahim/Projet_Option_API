"""LinkedIn profile scraping service."""

import asyncio
from linkedin_scraper import ConsoleCallback, PersonScraper, BrowserManager


async def scrape_linkedin_profile(profile_url: str) -> dict:
    """
    Scrape a LinkedIn profile and return the data.
    
    Args:
        profile_url: Full LinkedIn profile URL
        
    Returns:
        Dictionary with profile data
    """
    async with BrowserManager(headless=True, slow_mo=1000) as browser:
        callback = ConsoleCallback()
        
        # Load authenticated session
        await browser.load_session("session.json")
        
        # Create scraper
        scraper = PersonScraper(browser.page, callback=callback)
        
        # Scrape profile
        person = await scraper.scrape(profile_url)
        
        # Convert Pydantic model to dictionary
        profile_data = person.model_dump(mode="json")
        
        return profile_data