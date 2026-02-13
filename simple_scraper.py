#!/usr/bin/env python3
"""
Simplified Fiverr scraper - tries multiple approaches
"""

import requests
from bs4 import BeautifulSoup
import json
import re

def scrape_with_requests(hodor_creds):
    """Try direct HTTP requests with full browser headers"""
    
    session = requests.Session()
    
    # Full browser headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    
    cookies = {
        'hodor_creds': hodor_creds,
        'logged_in_currency_v2': 'EUR',
        'session_locale': 'en-US',
    }
    
    # First visit homepage to establish session
    session.get('https://www.fiverr.com', headers=headers, cookies=cookies)
    
    # Now try buyer requests
    url = 'https://www.fiverr.com/buyer_requests'
    
    try:
        resp = session.get(url, headers=headers, cookies=cookies, timeout=15)
        print(f"Status: {resp.status_code}")
        print(f"Content length: {len(resp.text)}")
        
        # Save HTML for debugging
        with open('/tmp/fiverr_page.html', 'w') as f:
            f.write(resp.text[:50000])
        print("Saved page HTML to /tmp/fiverr_page.html")
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Look for any cards/offers
        possible_containers = [
            soup.find_all('div', class_=re.compile(r'buyer.*request', re.I)),
            soup.find_all('article'),
            soup.find_all('div', {'data-impression-collected': True}),
            soup.find_all('div', class_=re.compile(r'card|offer|request', re.I)),
        ]
        
        jobs = []
        for containers in possible_containers:
            if containers:
                print(f"Found {len(containers)} potential containers")
                for idx, elem in enumerate(containers[:5]):
                    text = elem.get_text(strip=True)
                    if len(text) > 50:  # Has substantial content
                        jobs.append({
                            'id': idx + 1,
                            'title': text[:100],
                            'description': text[100:400] if len(text) > 100 else text,
                            'budget': 100,
                            'posted': 'recently',
                            'url': 'https://www.fiverr.com/buyer_requests'
                        })
                if jobs:
                    break
        
        return jobs
        
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    hodor = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJmaXZlcnIvaG9kb3JfcGVnYXN1cyIsInVpZCI6MTEzMzAyNTI2LCJzaWQiOiI2MTc3ZDk3NDgyOTA3NjNiZGM1MDlkMWFkM2Y5MGY5MCIsImlhdCI6MTc3MDk4MzUwNywiZXhwIjoxODAyNTQxMTA3fQ.O9xi8UgNKq-SkrrMljGQ4ZptWf_Vy7Ml9eh9OZOG6Rk"
    jobs = scrape_with_requests(hodor)
    print(f"\nFound {len(jobs)} jobs:")
    for job in jobs:
        print(f"- {job['title']}")
