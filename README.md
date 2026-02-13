# Fiverr Job Dashboard

Mobile-friendly dashboard that finds, scores, and tracks Fiverr buyer requests you can actually deliver.

## ⚡ Quick Start

```bash
cd ~/fiverr-dashboard
./setup.sh
python3 api.py
```

Then open `index.html` in your browser or deploy to GitHub Pages for mobile access.

## 🎯 What It Does

1. **Monitors** buyer requests across 6 categories you can deliver
2. **Scores** each job 0-100 (budget + clarity + effort)
3. **Generates** custom proposal templates
4. **Filters** by budget and category
5. **Tracks** potential revenue

## 📱 Mobile Access (GitHub Pages)

1. Create repo: https://github.com/new
   - Name: `fiverr-dashboard`
   - Public

2. Push code:
```bash
cd ~/fiverr-dashboard
git remote add origin https://github.com/YOUR-USERNAME/fiverr-dashboard.git
git branch -M main
git push -u origin main
```

3. Enable Pages:
   - Settings → Pages
   - Source: `main` branch, `/` root

4. Access from phone: `https://YOUR-USERNAME.github.io/fiverr-dashboard/`

## 🔧 Configuration

The dashboard works with mock data out of the box. For live Fiverr data:

**Option 1: ScraperAPI (Recommended)**
- Get key: https://www.scraperapi.com
- Set in `api.py`: `config['scraper_api_key'] = 'YOUR_KEY'`

**Option 2: Manual Integration**
- Export buyer requests from Fiverr as JSON
- Replace mock data in `api.py`

## 🎨 Categories Monitored

Jobs we can actually deliver:
- **Website Development** - landing pages, portfolios
- **Web Scraping** - data extraction, automation
- **Content Writing** - blogs, product descriptions
- **Data & Research** - market research, data entry
- **Graphics Design** - logos, social media graphics
- **API Integration** - webhooks, automation

## 📊 Scoring System

Jobs scored 0-100 based on:
- **Budget** (40pts): €150+ = full points
- **Clarity** (30pts): Clear requirements = higher score
- **Effort** (30pts): Quick wins score higher

Target: 70+ score jobs for best ROI

## 🚀 Workflow

1. Dashboard shows top scored jobs
2. Click "View Proposal Template"
3. Customize proposal in Fiverr
4. Track which jobs you applied to
5. Deliver work with AI assistance

## 📁 Files

- `index.html` - Mobile dashboard (works offline)
- `api.py` - Flask API server
- `scraper.py` - Job scoring and processing
- `setup.sh` - One-command installation

## 💡 Tips

- Target 70+ score jobs first
- Respond within 1-2 hours of posting
- Quality > quantity (3-5 proposals/day)
- Use proposal templates as starting points
- Let AI help deliver the actual work

## ⚠️ Notes

- Currently uses mock data (5 example jobs)
- Real scraping requires Fiverr login or ScraperAPI
- Automated bidding not recommended (ToS violation)
- This is a research/filtering tool, not a bot
