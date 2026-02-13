#!/usr/bin/env python3
"""
Fiverr Buyer Request Scraper
Fetches live buyer requests and scores them
"""

import json
import re
from datetime import datetime
from fiverr_api import session

# Categories we can deliver
CATEGORIES = {
    'website': ['website', 'web development', 'landing page', 'html', 'css'],
    'scraping': ['scraping', 'web scraping', 'data extraction', 'scraper'],
    'writing': ['writing', 'content', 'blog', 'article', 'copywriting'],
    'data': ['data entry', 'research', 'excel', 'spreadsheet', 'data analysis'],
    'graphics': ['logo', 'graphic design', 'social media', 'banner'],
    'api': ['api', 'integration', 'webhook', 'automation']
}

def calculate_score(job):
    """Score a job 0-100 based on budget, clarity, and effort"""
    score = 0
    
    # Budget scoring (0-40 points)
    budget = job.get('budget', 0)
    if budget >= 150:
        score += 40
    elif budget >= 100:
        score += 30
    elif budget >= 50:
        score += 20
    
    # Clarity scoring (0-30 points) - check for specific details
    description = job.get('description', '').lower()
    clarity_indicators = ['need', 'must', 'deadline', 'specific', 'example', 'attached']
    clarity_score = sum(1 for word in clarity_indicators if word in description)
    score += min(clarity_score * 5, 30)
    
    # Effort scoring (0-30 points) - prefer quick wins
    quick_indicators = ['simple', 'quick', 'basic', 'small', 'short']
    effort_score = sum(1 for word in quick_indicators if word in description)
    score += min(effort_score * 6, 30)
    
    return min(score, 100)

def estimate_effort(description):
    """Estimate hours needed based on description"""
    description = description.lower()
    
    if any(word in description for word in ['simple', 'quick', 'basic', 'small']):
        return 1.5
    elif any(word in description for word in ['medium', 'standard', 'regular']):
        return 2.5
    else:
        return 4

def categorize_job(title, description):
    """Determine which category this job fits"""
    text = (title + ' ' + description).lower()
    
    for category, keywords in CATEGORIES.items():
        if any(keyword in text for keyword in keywords):
            return category
    
    return 'other'

def generate_proposal(job):
    """Generate proposal template based on job category"""
    category = job['category']
    budget = job['budget']
    effort = job['effort']
    delivery = int(effort * 24)  # hours to delivery time
    
    templates = {
        'website': f"""Hi! I can build your {job['title'].lower()} with clean, mobile-responsive design.

My approach:
1. Design mockup based on your requirements
2. Build responsive HTML/CSS/JS
3. Optimize for mobile and speed

Price: €{budget} | Delivery: {delivery}h

Question: Do you need any specific features like contact forms or booking systems?""",
        
        'scraping': f"""Hi! I can extract that data cleanly and reliably using Python.

My approach:
1. Build scraper with error handling
2. Extract and validate all data
3. Export to your preferred format

Price: €{budget} | Delivery: {delivery}h

Question: Do you need this as one-time or recurring updates?""",
        
        'writing': f"""Hi! I can create engaging, SEO-optimized content that resonates with your audience.

My approach:
1. Research keywords and structure
2. Write clear, actionable content
3. Optimize for search and readability

Price: €{budget} | Delivery: {delivery}h

Question: Do you have specific keywords or topics in mind?""",
        
        'data': f"""Hi! I can handle this data work efficiently and accurately.

My approach:
1. Clean and organize the data
2. Perform required analysis/entry
3. Deliver in your preferred format

Price: €{budget} | Delivery: {delivery}h

Question: What format would you like the final deliverable in?""",
        
        'api': f"""Hi! I can integrate those services seamlessly.

My approach:
1. Set up secure API connections
2. Build error handling and logging
3. Test thoroughly and document

Price: €{budget} | Delivery: {delivery}h

Question: Do you have API credentials ready?"""
    }
    
    return templates.get(category, f"Hi! I can help with this project.\n\nPrice: €{budget} | Delivery: {delivery}h")

def scrape_buyer_requests(scraper_api_key=None, fiverr_session_cookie=None):
    """
    Scrape buyer requests from Fiverr
    Note: Requires being logged in to see buyer requests
    """
    import requests
    from bs4 import BeautifulSoup
    
    url = "https://www.fiverr.com/buyer_requests"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        
        cookies = {}
        if fiverr_session_cookie:
            cookies['session_id'] = fiverr_session_cookie
        
        # Use ScraperAPI if provided
        if scraper_api_key:
            url = f"http://api.scraperapi.com?api_key={scraper_api_key}&url={url}"
        
        response = requests.get(url, headers=headers, cookies=cookies, timeout=15)
        
        if response.status_code != 200:
            print(f"Error: Status {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        jobs = []
        
        # Try to find buyer request cards
        # Fiverr's structure may vary, these are common selectors
        request_cards = soup.find_all('div', class_=['request-card', 'buyer-request', 'offer-card'])
        
        if not request_cards:
            # Try alternative selectors
            request_cards = soup.select('[data-type="buyer-request"]')
        
        for idx, card in enumerate(request_cards[:10]):  # Limit to 10 jobs
            try:
                # Extract title
                title_elem = card.find(['h3', 'h4', 'a'], class_=['title', 'request-title'])
                title = title_elem.get_text(strip=True) if title_elem else f"Request #{idx+1}"
                
                # Extract description
                desc_elem = card.find(['p', 'div'], class_=['description', 'request-description', 'body'])
                description = desc_elem.get_text(strip=True) if desc_elem else ""
                
                # Extract budget
                budget_elem = card.find(['span', 'div'], class_=['budget', 'price', 'amount'])
                budget_text = budget_elem.get_text(strip=True) if budget_elem else "0"
                budget = int(''.join(filter(str.isdigit, budget_text))) or 100
                
                # Extract posted time
                time_elem = card.find(['span', 'time'], class_=['time', 'posted', 'date'])
                posted = time_elem.get_text(strip=True) if time_elem else "recently"
                
                # Extract link
                link_elem = card.find('a', href=True)
                link = "https://www.fiverr.com" + link_elem['href'] if link_elem and link_elem['href'].startswith('/') else "https://www.fiverr.com/buyer_requests"
                
                if title and description:
                    jobs.append({
                        'id': idx + 1,
                        'title': title,
                        'description': description[:300],  # Limit length
                        'budget': budget,
                        'posted': posted,
                        'url': link
                    })
            except Exception as e:
                print(f"Error parsing card {idx}: {e}")
                continue
        
        return jobs
        
    except Exception as e:
        print(f"Error scraping: {e}")
        return []

def process_jobs(raw_jobs):
    """Process and score raw job data"""
    processed = []
    
    for job in raw_jobs:
        category = categorize_job(job['title'], job['description'])
        
        # Skip jobs we can't deliver
        if category == 'other':
            continue
        
        effort = estimate_effort(job['description'])
        
        processed_job = {
            'id': job.get('id', hash(job['title'])),
            'title': job['title'],
            'description': job['description'],
            'budget': job.get('budget', 0),
            'category': category,
            'effort': effort,
            'posted': job.get('posted', 'recently'),
            'url': job.get('url', 'https://www.fiverr.com/buyer_requests'),
            'tags': extract_tags(job)
        }
        
        processed_job['score'] = calculate_score(processed_job)
        processed_job['proposal'] = generate_proposal(processed_job)
        
        processed.append(processed_job)
    
    # Sort by score descending
    processed.sort(key=lambda x: x['score'], reverse=True)
    
    return processed

def extract_tags(job):
    """Extract relevant tags from job description"""
    description = job.get('description', '').lower()
    
    tag_keywords = {
        'HTML': ['html', 'web page'],
        'CSS': ['css', 'styling', 'design'],
        'JavaScript': ['javascript', 'js', 'interactive'],
        'Python': ['python', 'scraping', 'automation'],
        'SEO': ['seo', 'search engine'],
        'Mobile': ['mobile', 'responsive'],
        'Quick': ['urgent', 'asap', 'fast', 'quick'],
        'PDF': ['pdf', 'document'],
        'API': ['api', 'integration']
    }
    
    tags = []
    for tag, keywords in tag_keywords.items():
        if any(kw in description for kw in keywords):
            tags.append(tag)
    
    return tags[:6]  # Limit to 6 tags

if __name__ == "__main__":
    # For testing with mock data
    mock_jobs = [
        {
            'title': 'Need Simple Landing Page',
            'description': 'Quick landing page for my plumbing business. Must be mobile-friendly.',
            'budget': 120,
            'posted': '2h ago'
        }
    ]
    
    processed = process_jobs(mock_jobs)
    print(json.dumps(processed, indent=2))
