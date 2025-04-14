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


def scrape_comments(video_id, cookies):
    existing_comments = load_existing_comments()
    processed_comment_ids = {c['comment_id'] for c in existing_comments}
    last_comment_id, last_reply_id = get_resume_point(existing_comments)

    cursor = 0
    has_more = True
    global_count = sum(1 + len(c['replies']) for c in existing_comments)
    comment_count = len(existing_comments) + 1
    continue_reply_mode = bool(last_reply_id)

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

            if comment_id in processed_comment_ids and not (continue_reply_mode and comment_id == last_comment_id):
                continue

            if comment_id not in processed_comment_ids:
                comment_data = {
                    'comment_id': comment_id,
                    'username': comment.get('user', {}).get('nickname'),
                    'text': comment.get('text'),
                    'timestamp': timestamp,
                    'replies': []
                }

                print(f"[#{global_count+1}] 💬 Comment {comment_count}: {comment_data['text']} | {comment_data['username']} {timestamp} | ID: {comment_id}")
                existing_comments.append(comment_data)
                save_all_comments(existing_comments)
                global_count += 1
                comment_count += 1

            # Fetch replies
            reply_cursor = 0
            reply_has_more = True
            reply_count = len(existing_comments[-1]['replies']) + 1 if continue_reply_mode else 1
            found_last_reply = not continue_reply_mode

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
                    reply_id = reply.get('cid')

                    # Skip replies we've already processed
                    if continue_reply_mode and not found_last_reply:
                        if reply_id == last_reply_id:
                            found_last_reply = True
                        continue

                    reply_timestamp = format_datetime(reply.get('create_time'))
                    reply_obj = {
                        'reply_id': reply_id,
                        'username': reply.get('user', {}).get('nickname'),
                        'text': reply.get('text'),
                        'timestamp': reply_timestamp,
                    }

                    print(f"[#{global_count+1}] ↩️ Reply {reply_count}: {reply_obj['text']} | {reply_obj['username']} {reply_timestamp} | ID: {reply_id}")
                    existing_comments[-1]['replies'].append(reply_obj)
                    save_all_comments(existing_comments)
                    global_count += 1
                    reply_count += 1

                time.sleep(0.5)

            continue_reply_mode = False
            time.sleep(1)


def main():
    cookies = load_cookies_from_json(COOKIE_FILE)
    video_id = extract_video_id(VIDEO_URL)
    print(f"[INFO] Scraping comments for video ID: {video_id}")
    scrape_comments(video_id, cookies)


if __name__ == '__main__':
    main()
