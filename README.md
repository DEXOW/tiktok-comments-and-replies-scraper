# 🕵️ TikTok Comment & Reply Scraper

This Python script allows you to **scrape top-level comments and nested replies** from a public TikTok video using a pre-authenticated session via cookie file.

Each comment and its replies are stored in real-time to a JSON file, and printed on the console with a serial count, emoji support, and human-readable date formatting (`YYYY:MM:DD-HH:MM`).

---

## 📌 Features

- ✅ Scrape public TikTok video comments & replies
- ✅ Load session from cookie JSON file (no need for login)
- ✅ Real-time saving to `comments_replies.json`
- ✅ Serial count logging with emoji support
- ✅ Timestamp format: `YYYY:MM:DD-HH:MM`
- ✅ Resilient file structure and human-readable output

---

## 🔧 Prerequisites

- Python 3.7 or higher
- TikTok account (to export session cookies)
- TikTok video URL (must be public)

---

## 🚀 Installation & Setup

### 1. Clone this repo or copy the script
Save the main script as `tiktok_scraper.py`.

### 2. Install dependencies

```bash
pip install requests
```

### 3. Export your TikTok cookies
Use a browser extension like CookieEditor to export your TikTok session cookies as a .json file.

Save it as cookies.json in the same directory.

✅ Make sure your cookie file includes keys like sessionid, tt_webid, etc.

### 4. Edit the config
Open the script and update the VIDEO_URL to your desired TikTok post:
```bash
VIDEO_URL = 'https://www.tiktok.com/@username/video/1234567890'
```

---

### ▶️ Usage
Run the script:
```bash
python tiktok_scraper.py
```
You'll see console output like:
```bash
[#1] 💬 Comment : A famous photographer | user1 2025:04:14-17:30
[#2] ↩️ Reply : Girll sameee.. | user2 2025:04:14-17:32
```
Meanwhile, all data is being saved live to comments_replies.json.

---

### 📁 Output Structure
Each comment and its replies are saved in a structured JSON format like:

```json
[
  {
    "comment_id": "123456",
    "username": "user1",
    "text": "A famous photographer....",
    "timestamp": "2025:04:14-17:30",
    "replies": [
      {
        "username": "user2",
        "text": "Girll sameee...",
        "timestamp": "2025:04:14-17:32"
      }
    ]
  }
]
```

---

### 🧠 Additional Details
Make sure the TikTok post is public.

This script does not use the official TikTok API — it mimics browser behavior using your session cookies.

Be mindful of rate limits; the script includes delays to avoid getting blocked.

---

### ❗ Disclaimer
This tool is intended for educational and personal use only.
Scraping TikTok may violate their Terms of Service — use at your own risk and always respect platform guidelines.

---

### ✨ Contributing
Feel free to fork, improve, or build on top of this script.
Pull requests and issues welcome!

---

Let me know if you want this turned into a nicely styled `README.md` preview with badges and images as well!
