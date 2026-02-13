# How to Get Your Fiverr Session Key

## Desktop (Chrome/Edge/Brave)

1. **Open Fiverr** and log in: https://www.fiverr.com
2. **Press F12** (opens Developer Tools)
3. **Click "Application" tab** at the top
   - Can't see it? Click the >> arrows to show more tabs
4. **Expand "Cookies"** in left sidebar
5. **Click** `https://www.fiverr.com`
6. **Find cookie named:** `_session_id` or `__cfduid` or `session_token`
7. **Copy the Value** (long string of random characters)
8. **Paste into dashboard** and click "Fetch Jobs"

## Desktop (Firefox)

1. Open Fiverr and log in
2. Press **F12**
3. Click **Storage** tab
4. Click **Cookies** → https://www.fiverr.com
5. Find session cookie and copy value

## Mobile (Not Recommended)

Session cookies are hard to access on mobile. Use desktop to get the cookie, then:
- Access dashboard on phone
- Paste the saved cookie
- Works until you log out on desktop

## Important Notes

⚠️ **Session expires when:**
- You log out of Fiverr
- You clear browser data
- After ~30 days (Fiverr's timeout)

✅ **When it expires:**
- Just get a new one using these steps
- Paste into dashboard again
- Takes 30 seconds

🔒 **Security:**
- Don't share your session key with anyone
- It gives access to your Fiverr account
- The dashboard stores it locally (not sent anywhere except Fiverr)

## Troubleshooting

**"No jobs found":**
- Your session might be expired → Get a new one
- You might not have access to buyer requests → Check Fiverr account status

**"Error fetching jobs":**
- Session key might be wrong → Double-check you copied the full value
- Try a different cookie (e.g., `session_id` vs `__cfduid`)

**Still not working:**
- For now, the dashboard shows example jobs
- Real scraping requires backend API running (coming soon)
