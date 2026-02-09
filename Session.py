import asyncio
from linkedin_scraper import BrowserManager, wait_for_manual_login

async def create_session():
    async with BrowserManager(headless=False) as browser:
        # Navigate to LinkedIn
        await browser.page.goto("https://www.linkedin.com/login")
        
        # Wait for manual login (opens browser)
        print("Please log in to LinkedIn...")
        await wait_for_manual_login(browser.page, timeout=60000)
        
        # Save session
        await browser.save_session("session.json")
        print("✓ Session saved!")

asyncio.run(create_session())