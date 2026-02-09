# API Updates - Local Profile Caching

We have optimized the LinkedIn Scraper to prioritize existing local profile data over fresh scraping. This reduces execution time and avoids potential browser instability.

## New Features

### 1. Local Cache Lookup
The system now checks the `Resumes LinkedIn` directory for an existing JSON profile before launching the browser scraper.
-   **Exact Match**: Matches filename (e.g., `ayoub_bourhaim_profile.json` matches "Ayoub Bourhaim").
-   **Fuzzy Match**: Matches if all parts of the name are present in the filename (e.g., "Bourhaim Ayoub").

### 2. Endpoint Changes

#### `POST /api/scrape-linkedin`
Accepts an optional `name` parameter to guide the local search.

```bash
POST /api/scrape-linkedin
Content-Type: application/json

{
  "profile_url": "https://www.linkedin.com/in/username",
  "name": "Jane Doe"  # <--- NEW: Optional parameter
}
```

-   **If `name` is provided**: The system searches for `jane_doe_profile.json` (and variations). If found, returns content immediately.
-   **If `name` is NOT provided**: The system attempts to extract a name from the URL (e.g., `jane-doe` from `/in/jane-doe`) and searches locally.
-   **Fallback**: If no local file is found, it proceeds with the browser-based scraping.

#### `POST /api/verify`
Automatically extracts the candidate's name from the parsed resume PDF and passes it to the internal scraping service to trigger the local cache lookup.

## Benefits
-   **Performance**: Local retrieval is near-instantaneous vs. 30+ seconds for scraping.
-   **Stability**: Bypasses browser interactions which can be flaky (e.g., "Target crashed" errors).
-   **Efficiency**: Reduces unnecessary network traffic and LinkedIn account usage.
