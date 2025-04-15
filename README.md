# 🕵️ TikTok Comment & Reply Scraper (Async Edition)

A high-performance Python scraper to **extract top-level comments and nested replies** from public TikTok videos using pre-authenticated session cookies.  

Built with `asyncio` and `aiohttp` for **speed**, **scalability**, and **resilience**.

---

## 📌 Features

- ✅ Scrape comments & replies from public TikTok videos
- ✅ Fully **asynchronous** with concurrency support
- ✅ Load multiple session cookies from `/cookies` folder
- ✅ Real-time, resumable scraping with incremental JSON saves
- ✅ Emoji-enhanced terminal logs with serial counters
- ✅ Human-readable timestamps: `YYYY:MM:DD-HH:MM`
- ✅ Resumes from the last processed comment/reply on restart

---

## 🔧 Prerequisites

- Python **3.7+**
- At least one authenticated TikTok session (via cookies)
- Public TikTok video URL (no login wall or geo-block)

---

## 🚀 Installation & Setup

### 1. Clone the repo or copy the script

```bash
git clone https://github.com/yourusername/tiktok-comment-scraper.git
cd tiktok-comment-scraper
```

Save the main script as `main.py`.

---

### 2. Install dependencies

```bash
pip install aiohttp
```

---

### 3. Export your TikTok cookies

Use a browser extension like **Cookie Editor** to export your TikTok session cookies as `.json` files.

- Place **all cookie `.json` files** inside the `/cookies` folder.
- Each cookie file should contain session values like `sessionid`, `tt_webid`, etc.

✅ You can add **multiple cookie files** to improve performance and avoid rate-limits.

---

### 4. Set the video URL

Edit the `VIDEO_URL` variable at the top of the script:

```python
VIDEO_URL = 'https://www.tiktok.com/@username/video/1234567890'
```

---

## ▶️ Usage

Run the script:

```bash
python main.py
```

You'll be prompted:

```
🔁 Do you want to fetch replies? (y/n):
```

Sample output in terminal:

```
[#1] 💬 Comment 1: A famous photographer | user1 2025:04:14-17:30 | ID: 123
[#2] ↩️ Reply: Girll sameee.. | user2 2025:04:14-17:32 | ID: 456
```

All data is **saved live** to `comments_replies.json`.

---

## 📁 Output Structure

```json
[
  {
    "comment_id": "123456",
    "username": "user1",
    "text": "A famous photographer....",
    "timestamp": "2025:04:14-17:30",
    "replies": [
      {
        "reply_id": "456789",
        "username": "user2",
        "text": "Girll sameee...",
        "timestamp": "2025:04:14-17:32"
      }
    ]
  }
]
```

---

## 🔄 Resume Support

If the script is interrupted or re-run, it automatically:
- Resumes from the **last saved comment**
- Continues fetching missing replies (if enabled)

No duplicates. No re-fetching.

---

## 💡 Tips

- Rotate cookies by placing multiple `.json` files in the `cookies/` folder.
- Let replies load by answering `y` when prompted.
- Avoid modifying `comments_replies.json` while scraping.

---

## ⚠️ Disclaimer

This tool is intended for **educational and personal use** only.

Using this script may **violate TikTok’s Terms of Service** — use responsibly, and only on content you’re authorized to access.

---

## ✨ Contributing

Have ideas? Found a bug?  
PRs and issues are welcome!