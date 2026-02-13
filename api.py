#!/usr/bin/env python3
"""
Simple API server for Fiverr job dashboard
Run: python3 api.py
Then update the dashboard to fetch from http://localhost:5000/jobs
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import scraper

app = Flask(__name__)
CORS(app)  # Allow requests from the HTML dashboard

# Store API keys (in production, use environment variables)
config = {
    'scraper_api_key': None,
    'fiverr_session': None
}

@app.route('/scrape', methods=['POST'])
def scrape_jobs():
    """Scrape Fiverr with provided session key"""
    try:
        data = request.json
        session_key = data.get('sessionKey', '')
        
        if not session_key:
            return jsonify({
                'success': False,
                'error': 'Session key required'
            }), 400
        
        # Try to scrape real Fiverr data
        raw_jobs = scraper.scrape_buyer_requests(
            fiverr_session_cookie=session_key
        )
        
        # If no jobs found, use mock data as fallback
        if not raw_jobs:
            print("No jobs scraped, using mock data")
            raw_jobs = [
                {
                    'id': 1,
                    'title': 'Simple Landing Page for Local Business',
                    'description': 'Need a clean, professional landing page for my plumbing business. Must be mobile-friendly. I have logo and photos ready.',
                    'budget': 120,
                    'posted': '2h ago',
                    'url': 'https://www.fiverr.com/buyer_requests'
                },
                {
                    'id': 2,
                    'title': 'Scrape Product Data from E-commerce Site',
                    'description': 'Extract product names, prices, and descriptions from competitor website. About 200 products. CSV output needed.',
                    'budget': 80,
                    'posted': '4h ago',
                    'url': 'https://www.fiverr.com/buyer_requests'
                },
            ]
        
        processed_jobs = scraper.process_jobs(raw_jobs)
        
        return jsonify({
            'success': True,
            'jobs': processed_jobs,
            'total': len(processed_jobs),
            'source': 'fiverr' if raw_jobs else 'mock'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/jobs', methods=['GET'])
def get_jobs():
    """Get scored and filtered buyer requests (legacy endpoint)"""
    try:
        # Mock data for testing
        mock_jobs = [
            {
                'id': 1,
                'title': 'Simple Landing Page for Local Business',
                'description': 'Need a clean, professional landing page for my plumbing business. Must be mobile-friendly. I have logo and photos ready.',
                'budget': 120,
                'posted': '2h ago',
                'url': 'https://www.fiverr.com/buyer_requests'
            },
            {
                'id': 2,
                'title': 'Scrape Product Data from E-commerce Site',
                'description': 'Extract product names, prices, and descriptions from competitor website. About 200 products. CSV output needed.',
                'budget': 80,
                'posted': '4h ago',
                'url': 'https://www.fiverr.com/buyer_requests'
            },
            {
                'id': 3,
                'title': 'Write 5 Blog Posts About Fitness',
                'description': 'Need 5 articles, 800 words each, about home workouts and nutrition. SEO optimized. Deadline: 1 week.',
                'budget': 150,
                'posted': '1h ago',
                'url': 'https://www.fiverr.com/buyer_requests'
            },
            {
                'id': 4,
                'title': 'Create Quote Calculator for My Business',
                'description': "I'm an electrician and need a simple web app where I can input materials, labor hours, and get PDF quotes for clients.",
                'budget': 200,
                'posted': '30m ago',
                'url': 'https://www.fiverr.com/buyer_requests'
            },
            {
                'id': 5,
                'title': 'Data Entry - 500 Contacts to Spreadsheet',
                'description': 'Copy contact information from business cards into Excel. Name, phone, email, company. Simple and straightforward.',
                'budget': 60,
                'posted': '5h ago',
                'url': 'https://www.fiverr.com/buyer_requests'
            }
        ]
        
        processed_jobs = scraper.process_jobs(mock_jobs)
        
        # Apply filters from query params
        category = request.args.get('category', 'all')
        min_budget = int(request.args.get('min_budget', 0))
        max_budget = int(request.args.get('max_budget', 9999))
        
        if category != 'all':
            processed_jobs = [j for j in processed_jobs if j['category'] == category]
        
        processed_jobs = [j for j in processed_jobs if min_budget <= j['budget'] <= max_budget]
        
        return jsonify({
            'success': True,
            'jobs': processed_jobs,
            'total': len(processed_jobs),
            'timestamp': scraper.datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/config', methods=['POST'])
def set_config():
    """Set API keys and credentials"""
    data = request.json
    
    if 'scraper_api_key' in data:
        config['scraper_api_key'] = data['scraper_api_key']
    
    if 'fiverr_session' in data:
        config['fiverr_session'] = data['fiverr_session']
    
    return jsonify({
        'success': True,
        'message': 'Configuration updated'
    })

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics"""
    jobs = scraper.process_jobs([])  # Would use real data
    
    high_score = sum(1 for j in jobs if j['score'] >= 70)
    total_revenue = sum(j['budget'] for j in jobs)
    
    return jsonify({
        'total_jobs': len(jobs),
        'high_score_count': high_score,
        'potential_revenue': total_revenue
    })

if __name__ == '__main__':
    print("🚀 Fiverr Job API running on http://localhost:5000")
    print("📱 Open your dashboard and it will fetch jobs from this API")
    print("\nEndpoints:")
    print("  GET  /jobs         - Get scored buyer requests")
    print("  POST /config       - Set API keys")
    print("  GET  /stats        - Get statistics")
    print("\nPress Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
