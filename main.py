import os
import json
import asyncio
import aiohttp
from datetime import datetime

# CONFIG
COOKIES_FOLDER = 'cookies' # Path to the folder containing cookie files
VIDEO_URL = 'https://www.tiktok.com/@username/video/1234567890' # URL of the TikTok video
OUTPUT_FILE = 'comments_replies.json' # File to save comments
MAX_CONCURRENT_TASKS = 20 # Maximum concurrent tasks for fetching replies (Leave as is for now)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'Referer': 'https://www.tiktok.com/',
}


def format_datetime(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y:%m:%d-%H:%M')


def extract_video_id(url):
    return url.strip('/').split('/')[-1]


def load_all_cookie_files(folder_path):
    cookie_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.json')]
    cookies_list = []
    for path in cookie_files:
        with open(path, 'r') as f:
            cookie_data = json.load(f)
            cookies_list.append({cookie['name']: cookie['value'] for cookie in cookie_data})
    return cookies_list


def load_existing_comments():
    try:
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_all_comments(comments):
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(comments, f, indent=4, ensure_ascii=False)


def get_resume_point(comments):
    if not comments:
        return None, None
    last_comment = comments[-1]
    comment_id = last_comment.get('comment_id')
    last_reply_id = last_comment['replies'][-1]['reply_id'] if last_comment.get('replies') else None
    return comment_id, last_reply_id


async def fetch_json(session, url, cookies):
    try:
        async with session.get(url, headers=HEADERS, cookies=cookies) as response:
            if response.status != 200:
                print(f"[ERROR] {response.status}: {url}")
                return None
            return await response.json()
    except Exception as e:
        print(f"[ERROR] Fetch failed: {e}")
        return None


async def fetch_replies(comment_data, video_id, cookies, session, continue_from=None):
    comment_id = comment_data['comment_id']
    reply_cursor = 0
    reply_has_more = True
    found_last_reply = continue_from is None
    replies = []

    while reply_has_more:
        reply_api = (
            f"https://www.tiktok.com/api/comment/list/reply/?aid=1988"
            f"&comment_id={comment_id}&cursor={reply_cursor}&count=10&item_id={video_id}"
        )

        data = await fetch_json(session, reply_api, cookies)
        if not data:
            break

        reply_cursor = data.get('cursor', 0)
        reply_has_more = data.get('has_more', False)

        for reply in data.get('comments', []):
            reply_id = reply.get('cid')

            if continue_from and not found_last_reply:
                if reply_id == continue_from:
                    found_last_reply = True
                continue

            reply_obj = {
                'reply_id': reply_id,
                'username': reply.get('user', {}).get('nickname'),
                'text': reply.get('text'),
                'timestamp': format_datetime(reply.get('create_time'))
            }
            replies.append(reply_obj)

        await asyncio.sleep(0.2)

    return comment_id, replies


async def scrape_comments(video_id, cookies_pool, fetch_replies_enabled: bool):
    existing_comments = load_existing_comments()
    processed_comment_ids = {c['comment_id'] for c in existing_comments}
    last_comment_id, last_reply_id = get_resume_point(existing_comments)

    cursor = 0
    has_more = True
    global_count = sum(1 + len(c.get('replies', [])) for c in existing_comments)
    comment_count = len(existing_comments) + 1
    continue_reply_mode = bool(last_reply_id)
    cookie_index = 0
    total_cookies = len(cookies_pool)

    async with aiohttp.ClientSession() as session:
        while has_more:
            current_cookies = cookies_pool[cookie_index % total_cookies]
            cookie_index += 1

            comment_api = f"https://www.tiktok.com/api/comment/list/?aid=1988&aweme_id={video_id}&cursor={cursor}&count=20"
            data = await fetch_json(session, comment_api, current_cookies)
            if not data:
                break

            comments = data.get('comments', [])
            has_more = data.get('has_more', False)
            cursor = data.get('cursor', 0)

            new_comments = []
            tasks = []

            for idx, comment in enumerate(comments):
                comment_id = comment.get('cid')
                timestamp = format_datetime(comment.get('create_time'))

                if comment_id in processed_comment_ids and not (continue_reply_mode and comment_id == last_comment_id):
                    continue

                comment_data = {
                    'comment_id': comment_id,
                    'username': comment.get('user', {}).get('nickname'),
                    'text': comment.get('text'),
                    'timestamp': timestamp,
                    'replies': []
                }

                print(f"[#{global_count+1}] 💬 Comment {comment_count}: {comment_data['text']} | {comment_data['username']} {timestamp} | ID: {comment_id}")
                new_comments.append(comment_data)
                global_count += 1
                comment_count += 1

                if fetch_replies_enabled:
                    reply_cookies = cookies_pool[(cookie_index + idx) % total_cookies]
                    task = fetch_replies(
                        comment_data,
                        video_id,
                        reply_cookies,
                        session,
                        last_reply_id if continue_reply_mode and comment_id == last_comment_id else None
                    )
                    tasks.append(task)

            if fetch_replies_enabled:
                reply_results = await asyncio.gather(*tasks)
                for comment_id, replies in reply_results:
                    for comment in new_comments:
                        if comment['comment_id'] == comment_id:
                            comment['replies'].extend(replies)
                            for reply in replies:
                                print(f"[#{global_count+1}] ↩️ Reply: {reply['text']} | {reply['username']} {reply['timestamp']} | ID: {reply['reply_id']}")
                                global_count += 1
                            break
            else:
                for comment in new_comments:
                    comment.pop('replies', None)

            existing_comments.extend(new_comments)
            save_all_comments(existing_comments)
            continue_reply_mode = False
            await asyncio.sleep(0.5)


def main():
    cookies_pool = load_all_cookie_files(COOKIES_FOLDER)
    if not cookies_pool:
        print("[ERROR] No cookie files found.")
        return

    fetch_replies_enabled = input("🔁 Do you want to fetch replies? (y/n): ").strip().lower() == 'y'

    video_id = extract_video_id(VIDEO_URL)
    print(f"[INFO] Scraping comments for video ID: {video_id}")
    print(f"[INFO] Using {len(cookies_pool)} accounts asynchronously.")
    print(f"[INFO] Fetching replies: {'Yes' if fetch_replies_enabled else 'No'}")

    asyncio.run(scrape_comments(video_id, cookies_pool, fetch_replies_enabled))


if __name__ == '__main__':
    main()
