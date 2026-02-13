# Install Fiverr Job Scraper Extension

## 📱 For Kiwi Browser (Android)

### Step 1: Download Extension

Download: https://raw.githubusercontent.com/ERROR403agent/fiverr-dashboard/main/fiverr-scraper-extension.zip

Or from your EC2:
```
http://13.48.70.12:5000/static/fiverr-scraper-extension.zip
```

### Step 2: Extract ZIP

- Use any file manager app
- Extract `fiverr-scraper-extension.zip` to a folder
- Remember the folder location

### Step 3: Install in Kiwi Browser

1. Open **Kiwi Browser**
2. Type in address bar: `chrome://extensions`
3. Enable **Developer mode** (toggle in top right)
4. Click **Load unpacked**
5. Navigate to the extracted extension folder
6. Select the folder
7. Extension installed! ✅

### Step 4: Use It

1. Visit: https://www.fiverr.com/buyer_requests (log in)
2. Wait for page to load
3. Click the green **"📥 Extract Jobs"** button (bottom right)
4. Jobs automatically sent to your dashboard!

---

## 💻 For Desktop Chrome/Brave/Edge

Same steps as Kiwi Browser!

1. Download extension ZIP
2. Extract it
3. Go to `chrome://extensions`
4. Enable Developer mode
5. Click "Load unpacked"
6. Select extracted folder

---

## ✨ Features

- **Auto-detect jobs** on Fiverr buyer requests page
- **One-click extraction** with floating button
- **Auto-scrape mode** (optional - enable in extension popup)
- **Dashboard integration** - jobs appear instantly
- **Dark mode UI** - matches your dashboard

---

## 🔧 Settings

Click the extension icon (📥) to:
- Check connection status
- Enable/disable auto-scrape
- Open dashboard
- Go to buyer requests page

---

## ⚠️ Troubleshooting

**"Cannot reach dashboard"**
- Make sure EC2 server is running
- Check port 5000 is open
- Test: http://13.48.70.12:5000/jobs-cached

**"No jobs found"**
- Make sure you're on the buyer requests page
- Wait for page to fully load
- Try refreshing the page

**Button not showing**
- Refresh the page
- Check extension is enabled
- Look bottom-right corner

---

## 📊 How It Works

1. Extension runs when you visit Fiverr buyer requests
2. Scans page for job cards
3. Extracts: Title, Description, Budget
4. Sends each job to EC2 API
5. API scores jobs + generates proposals
6. Dashboard shows them instantly!

No manual copying - just click and done! 🚀
