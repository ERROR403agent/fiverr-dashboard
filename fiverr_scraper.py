#!/usr/bin/env python3
"""
Real Fiverr scraper using headless Chrome
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json
import time

def scrape_fiverr_with_cookies(hodor_creds):
    """Scrape Fiverr buyer requests using Selenium with authentication"""
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    try:
        # Initialize driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # First, visit Fiverr to establish domain
        driver.get("https://www.fiverr.com")
        time.sleep(2)
        
        # Add authentication cookie
        driver.add_cookie({
            'name': 'hodor_creds',
            'value': hodor_creds,
            'domain': '.fiverr.com',
            'path': '/',
            'secure': False,
            'httpOnly': True
        })
        
        # Now visit buyer requests page
        driver.get("https://www.fiverr.com/buyer_requests")
        time.sleep(5)  # Wait for page to load
        
        # Wait for buyer request cards to load
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "buyer-request-card"))
            )
        except:
            # Try alternative selectors
            print("Waiting for alternative elements...")
            time.sleep(3)
        
        jobs = []
        
        # Try multiple selectors
        selectors = [
            "buyer-request-card",
            "request-card",
            "offer-card-wrapper",
            "co-buyer-request-offer",
        ]
        
        elements = []
        for selector in selectors:
            elements = driver.find_elements(By.CLASS_NAME, selector)
            if elements:
                print(f"Found {len(elements)} elements with class: {selector}")
                break
        
        # If no class-based selectors work, try data attributes
        if not elements:
            elements = driver.find_elements(By.CSS_SELECTOR, "[data-cy*='request'], [data-testid*='request']")
            print(f"Found {len(elements)} elements with data attributes")
        
        for idx, element in enumerate(elements[:10]):  # Limit to 10 jobs
            try:
                # Extract text content
                text = element.text
                
                # Try to find title
                title_elem = element.find_elements(By.TAG_NAME, "h3") or \
                            element.find_elements(By.TAG_NAME, "h4")
                title = title_elem[0].text if title_elem else f"Job Request #{idx+1}"
                
                # Try to find description
                p_elements = element.find_elements(By.TAG_NAME, "p")
                description = " ".join([p.text for p in p_elements if len(p.text) > 20])[:300]
                
                # Try to find budget
                budget = 100  # Default
                for line in text.split('\n'):
                    if '€' in line or '$' in line or 'budget' in line.lower():
                        nums = [int(s) for s in line.split() if s.isdigit()]
                        if nums:
                            budget = nums[0]
                            break
                
                if title and description:
                    jobs.append({
                        'id': int(time.time() * 1000) + idx,
                        'title': title,
                        'description': description,
                        'budget': budget,
                        'posted': 'recently',
                        'url': 'https://www.fiverr.com/buyer_requests'
                    })
                    
            except Exception as e:
                print(f"Error extracting job {idx}: {e}")
                continue
        
        driver.quit()
        return jobs
        
    except Exception as e:
        print(f"Scraping error: {e}")
        try:
            driver.quit()
        except:
            pass
        return []

if __name__ == "__main__":
    # Test
    hodor = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJmaXZlcnIvaG9kb3JfcGVnYXN1cyIsInVpZCI6MTEzMzAyNTI2LCJzaWQiOiI2MTc3ZDk3NDgyOTA3NjNiZGM1MDlkMWFkM2Y5MGY5MCIsImlhdCI6MTc3MDk4MzUwNywiZXhwIjoxODAyNTQxMTA3fQ.O9xi8UgNKq-SkrrMljGQ4ZptWf_Vy7Ml9eh9OZOG6Rk"
    jobs = scrape_fiverr_with_cookies(hodor)
    print(f"Found {len(jobs)} jobs")
    print(json.dumps(jobs, indent=2))
