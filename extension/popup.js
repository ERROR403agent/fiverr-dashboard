// Popup script
const API_URL = 'http://13.48.70.12:5000/jobs-cached';
const DASHBOARD_URL = 'https://error403agent.github.io/fiverr-dashboard/';

// Check API connection
async function checkConnection() {
  const statusText = document.getElementById('status-text');
  
  try {
    const response = await fetch(API_URL);
    const data = await response.json();
    
    if (data.success) {
      statusText.innerHTML = `<span class="status-ok">✅ Connected • ${data.total} jobs in dashboard</span>`;
    } else {
      statusText.innerHTML = `<span class="status-error">⚠️ API error</span>`;
    }
  } catch (error) {
    statusText.innerHTML = `<span class="status-error">❌ Cannot reach dashboard</span>`;
  }
}

// Load auto-scrape setting
chrome.storage.sync.get(['autoScrape'], (result) => {
  document.getElementById('auto-scrape').checked = result.autoScrape || false;
});

// Save auto-scrape setting
document.getElementById('auto-scrape').addEventListener('change', (e) => {
  chrome.storage.sync.set({ autoScrape: e.target.checked });
});

// Open dashboard
document.getElementById('open-dashboard').addEventListener('click', () => {
  chrome.tabs.create({ url: DASHBOARD_URL });
});

// Check connection on load
checkConnection();
