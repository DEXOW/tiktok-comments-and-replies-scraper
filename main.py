import json
import time
import requests
from datetime import datetime

# CONFIG
COOKIE_FILE = 'cookies.json'
VIDEO_URL = 'https://www.tiktok.com/@rizzcado/photo/7491129701956652306'
OUTPUT_FILE = 'comments_replies.json'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'Referer': 'https://www.tiktok.com/',
}


def load_cookies_from_json(file_path):
    with open(file_path, 'r') as f:
        cookies_json = json.load(f)
    return {cookie['name']: cookie['value'] for cookie in cookies_json}


def extract_video_id(url):
    return url.strip('/').split('/')[-1]


def format_datetime(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y:%m:%d-%H:%M')


def save_comment(comment):
    try:
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            comments = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        comments = []

    comments.append(comment)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(comments, f, indent=4, ensure_ascii=False)


def add_reply_to_comment(comment_id, reply_obj):
    try:
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            comments = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return

    for comment in comments:
        if comment.get('comment_id') == comment_id:
            comment['replies'].append(reply_obj)
            break

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(comments, f, indent=4, ensure_ascii=False)


def scrape_comments(video_id, cookies):
    cursor = 0
    has_more = True
    global_count = 1
    comment_count = 1

    while has_more:
        comment_api = f"https://www.tiktok.com/api/comment/list/?aid=1988&aweme_id={video_id}&cursor={cursor}&count=20"
        res = requests.get(comment_api, headers=HEADERS, cookies=cookies)
        if res.status_code != 200:
            print(f"[ERROR] Status {res.status_code}: {res.text}")
            break

        data = res.json()
        comments = data.get('comments', [])
        has_more = data.get('has_more', False)
        cursor = data.get('cursor', 0)

        for comment in comments:
            comment_id = comment.get('cid')
            timestamp = format_datetime(comment.get('create_time'))
            comment_data = {
                'comment_id': comment_id,
                'username': comment.get('user', {}).get('nickname'),
                'text': comment.get('text'),
                'timestamp': timestamp,
                'replies': []
            }

            print(f"[#{global_count}] 💬 Comment {comment_count}: {comment_data['text']} | {comment_data['username']} {timestamp} | ID: {comment_id}")
            save_comment(comment_data)
            global_count += 1
            comment_count += 1

            # Fetch replies
            reply_cursor = 0
            reply_has_more = True
            reply_count = 1  # Reset per comment

            while reply_has_more:
                reply_api = (
                    f"https://www.tiktok.com/api/comment/list/reply/?aid=1988"
                    f"&comment_id={comment_id}&cursor={reply_cursor}&count=10&item_id={video_id}"
                )
                reply_res = requests.get(reply_api, headers=HEADERS, cookies=cookies)
                if reply_res.status_code != 200:
                    break

                reply_data = reply_res.json()
                replies = reply_data.get('comments', [])
                reply_has_more = reply_data.get('has_more', False)
                reply_cursor = reply_data.get('cursor', 0)

                for reply in replies:
                    reply_timestamp = format_datetime(reply.get('create_time'))
                    reply_id = reply.get('cid')
                    reply_obj = {
                        'reply_id': reply_id,
                        'username': reply.get('user', {}).get('nickname'),
                        'text': reply.get('text'),
                        'timestamp': reply_timestamp,
                    }
                    print(f"[#{global_count}] ↩️ Reply {reply_count}: {reply_obj['text']} | {reply_obj['username']} {reply_timestamp} | ID: {reply_id}")
                    global_count += 1
                    reply_count += 1
                    add_reply_to_comment(comment_id, reply_obj)

                time.sleep(0.5)

            time.sleep(1)


def main():
    cookies = load_cookies_from_json(COOKIE_FILE)
    video_id = extract_video_id(VIDEO_URL)
    print(f"[INFO] Scraping comments for video ID: {video_id}")
    scrape_comments(video_id, cookies)


if __name__ == '__main__':
    main()
