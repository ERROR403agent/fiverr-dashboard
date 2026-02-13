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
    if scraper_api_key:
        session.set_scraper_api_key(scraper_api_key)
    
    # Buyer requests URL (requires login)
    url = "https://www.fiverr.com/buyer_requests"
    
    try:
        # Note: This will only work if you're logged in
        # You'll need to pass session cookies or use ScraperAPI with authentication
        response = session.get(url)
        soup = response.soup
        
        jobs = []
        
        # This is a placeholder - actual scraping logic depends on Fiverr's HTML structure
        # You'd need to inspect the buyer requests page and extract:
        # - Title
        # - Description  
        # - Budget
        # - Posted time
        # - Category
        
        # For now, return empty to avoid errors
        return []
        
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
