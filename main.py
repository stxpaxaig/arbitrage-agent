import os
import requests
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

# ==========================================
# CONFIGURATION
# ==========================================
NTFY_TOPIC = "justin_leads_55"
REDDIT_URLS = [
    "https://www.reddit.com/r/PythonJobs/new.json?limit=5",
    "https://www.reddit.com/r/slavelabour/new.json?limit=5",
    "https://www.reddit.com/r/forhire/new.json?limit=5"

]



# Cache to prevent duplicate alerts
SEEN_POSTS = set()

def send_phone_notification(title, platform, url, details):
    """Pushes a clean text alert straight to your phone via ntfy."""
    ntfy_url = f"https://ntfy.sh/{NTFY_TOPIC}"
    
    message_body = f"""
### LIVE GIG DETECTED ###
* Platform: {platform}
* Link: {url}
* Details: {details}
"""
    try:
        requests.post(
            ntfy_url,
            data=message_body.strip().encode('utf-8'),
            headers={
                "Title": f"🔥 NEW LEAD: {title[:30]}...",
                "Priority": "high"
            }
        )
        print(f"Real-time alert pushed for: {title}")
    except Exception as e:
        print(f"Notification failed: {e}")

def check_feeds():
    """Scrapes the live raw data feeds directly, bypassing Google entirely."""
    print("Scanning source platforms for brand new posts...")
    headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android) MarketAgent/1.0'}
    
    for url in REDDIT_URLS:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                continue
                
            data = response.json()
            posts = data.get('data', {}).get('children', [])
            
            for post in posts:
                post_data = post.get('data', {})
                post_id = post_data.get('id')
                title = post_data.get('title', '')
                permalink = post_data.get('permalink', '')
                full_url = f"https://reddit.com{permalink}"
                selftext = post_data.get('selftext', '')
                
                # Filter keywords for matching gigs
                keywords = ['leads', 'lead gen', 'lead generation', 'find clients', 'contact list', 'data entry', 'emails', 'scraped list']
                match = any(word in title.lower() or word in selftext.lower() for word in keywords)
                
                if match and post_id not in SEEN_POSTS:
                    # Only alert on posts discovered AFTER the script starts running
                    if len(SEEN_POSTS) > 0:
                        send_phone_notification(title, "Reddit", full_url, title)
                    SEEN_POSTS.add(post_id)
                    
        except Exception as e:
            print(f"Feed error: {e}")

# ==========================================
# RENDER SERVER & LOOP SETUP
# ==========================================
class SimpleServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Radar Active")
    def log_message(self, format, *args): return

def start_web_server():
    HTTPServer(('0.0.0.0', 10000), SimpleServer).serve_forever()

def continuous_loop():
    """Checks the direct raw feeds every 2 minutes for zero lag."""
    while True:
        try:
            check_feeds()
        except Exception as e:
            print(f"Loop error: {e}")
        time.sleep(120)

if __name__ == "__main__":
    # Initialize cache on boot up
    check_feeds()
    
    # Run the continuous 2-minute scraper loop
    threading.Thread(target=continuous_loop, daemon=True).start()
    print("Starting background listener on port 10000...")
    start_web_server()
