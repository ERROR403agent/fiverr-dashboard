// Fiverr Job Scraper - Content Script
// Runs automatically on buyer_requests page

console.log('🚀 Fiverr Job Scraper loaded');

const API_URL = 'http://13.48.70.12:5000/add-job';

function extractJobs() {
  const jobs = [];
  
  // Try multiple selectors to find job cards
  const selectors = [
    '.buyer-request-card',
    '.request-card',
    '.offer-card',
    '[data-cy*="buyer-request"]',
    '[data-testid*="buyer-request"]',
    'article',
    '.co-buyer-request-offer'
  ];
  
  let elements = [];
  for (const selector of selectors) {
    elements = document.querySelectorAll(selector);
    if (elements.length > 0) {
      console.log(`Found ${elements.length} jobs with selector: ${selector}`);
      break;
    }
  }
  
  elements.forEach((card, idx) => {
    try {
      // Extract title
      const titleElem = card.querySelector('h3, h4, h5, [class*="title"]');
      const title = titleElem ? titleElem.textContent.trim() : `Job Request #${idx + 1}`;
      
      // Extract description
      const descElem = card.querySelector('p, [class*="description"], [class*="body"]');
      const description = descElem ? descElem.textContent.trim() : '';
      
      // Extract budget
      let budget = 100; // Default
      const budgetElem = card.querySelector('[class*="budget"], [class*="price"], [class*="amount"]');
      if (budgetElem) {
        const budgetText = budgetElem.textContent;
        const match = budgetText.match(/\d+/);
        if (match) budget = parseInt(match[0]);
      }
      
      // Skip if no meaningful content
      if (description.length < 20) return;
      
      jobs.push({
        title: title.substring(0, 200),
        description: description.substring(0, 500),
        budget: budget
      });
      
    } catch (e) {
      console.error('Error extracting job:', e);
    }
  });
  
  return jobs;
}

async function sendJobToDashboard(job) {
  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(job)
    });
    
    const data = await response.json();
    return data.success;
    
  } catch (error) {
    console.error('Error sending job to dashboard:', error);
    return false;
  }
}

function createFloatingButton() {
  const button = document.createElement('div');
  button.id = 'fiverr-scraper-btn';
  button.innerHTML = `
    <div style="
      position: fixed;
      bottom: 20px;
      right: 20px;
      background: #1dbf73;
      color: white;
      padding: 15px 20px;
      border-radius: 50px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      cursor: pointer;
      font-weight: bold;
      font-size: 14px;
      z-index: 999999;
      font-family: -apple-system, sans-serif;
      user-select: none;
    " id="scraper-btn-inner">
      📥 Extract Jobs
    </div>
    <div id="scraper-status" style="
      position: fixed;
      bottom: 80px;
      right: 20px;
      background: #2a2a2a;
      color: #e0e0e0;
      padding: 10px 15px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      z-index: 999999;
      font-size: 13px;
      font-family: -apple-system, sans-serif;
      display: none;
    "></div>
  `;
  
  document.body.appendChild(button);
  
  const btnInner = document.getElementById('scraper-btn-inner');
  const status = document.getElementById('scraper-status');
  
  btnInner.addEventListener('click', async () => {
    btnInner.textContent = '⏳ Extracting...';
    btnInner.style.background = '#ffb33e';
    
    const jobs = extractJobs();
    
    if (jobs.length === 0) {
      status.textContent = '❌ No jobs found on page';
      status.style.display = 'block';
      status.style.background = '#ff4444';
      setTimeout(() => status.style.display = 'none', 3000);
      btnInner.textContent = '📥 Extract Jobs';
      btnInner.style.background = '#1dbf73';
      return;
    }
    
    let sent = 0;
    for (const job of jobs) {
      const success = await sendJobToDashboard(job);
      if (success) sent++;
      await new Promise(r => setTimeout(r, 200)); // Small delay between requests
    }
    
    status.textContent = `✅ Sent ${sent}/${jobs.length} jobs to dashboard!`;
    status.style.display = 'block';
    status.style.background = '#1dbf73';
    setTimeout(() => status.style.display = 'none', 5000);
    
    btnInner.textContent = '📥 Extract Jobs';
    btnInner.style.background = '#1dbf73';
  });
}

// Auto-scrape on page load (optional)
function autoScrape() {
  chrome.storage.sync.get(['autoScrape'], (result) => {
    if (result.autoScrape) {
      setTimeout(() => {
        const jobs = extractJobs();
        jobs.forEach(job => sendJobToDashboard(job));
      }, 3000); // Wait for page to fully load
    }
  });
}

// Initialize
setTimeout(() => {
  createFloatingButton();
  autoScrape();
}, 2000);
