import os
import requests
import threading
import time
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, HTTPServer

# ==========================================
# CONFIGURATION
# ==========================================
NTFY_TOPIC = "justin_leads_55"

# 1. Reddit JSON Endpoints
REDDIT_URLS = [
    "https://www.reddit.com/r/PythonJobs/new.json?limit=5",
    "https://www.reddit.com/r/slavelabour/new.json?limit=5",
    "https://www.reddit.com/r/forhire/new.json?limit=5"
]

# 2. We Work Remotely RSS Feed (Full Programming Category)
WWR_FEED_URL = "https://weworkremotely.com/categories/remote-programming-jobs.rss"

# 3. Freelancer.com Public API Endpoint (Looking for Python/Automation keyword projects)
FREELANCER_API_URL = "https://www.freelancer.com/api/projects/0.1/projects/active/?keywords[]=python&keywords[]=web-scraping&keywords[]=automation&limit=10"

# Cache to prevent duplicate alerts across all platforms
SEEN_POSTS = set()

# Request Headers to bypass basic bot blocks
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def send_phone_notification(title, platform, url, details=""):
    """Pushes a clean text alert straight to your phone via ntfy."""
    ntfy_url = f"https://ntfy.sh/{NTFY_TOPIC}"
    
    message_body = f"""### LIVE GIG DETECTED ###
* Platform: {platform}
* Link: {url}
* Details: {details[:150]}..."""

    try:
        requests.post(
            ntfy_url,
            data=message_body.encode('utf-8'),
            headers={"Title": title.encode('utf-8')}
        )
    except Exception as e:
        print(f"Failed to send notification: {e}")

# ==========================================
# SCRAPER ENGINES
# ==========================================

def check_reddit():
    """Scrapes the target subreddits for fresh posts."""
    for url in REDDIT_URLS:
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                data = response.json()
                posts = data.get("data", {}).get("children", [])
                for post in posts:
                    post_data = post.get("data", {})
                    post_id = post_data.get("id")
                    
                    if post_id and post_id not in SEEN_POSTS:
                        SEEN_POSTS.add(post_id)
                        title = post_data.get("title", "New Reddit Post")
                        permalink = f"https://reddit.com{post_data.get('permalink')}"
                        selftext = post_data.get("selftext", "")
                        
                        send_phone_notification(title, "Reddit", permalink, selftext)
        except Exception as e:
            print(f"Reddit scrape error: {e}")

def check_we_work_remotely():
    """Scrapes We Work Remotely's programming RSS feed."""
    try:
        response = requests.get(WWR_FEED_URL, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            for item in root.findall('.//item'):
                guid = item.find('guid').text if item.find('guid') is not None else None
                
                if guid and guid not in SEEN_POSTS:
                    SEEN_POSTS.add(guid)
                    title = item.find('title').text if item.find('title') is not None else "New WWR Job"
                    link = item.find('link').text if item.find('link') is not None else "https://weworkremotely.com"
                    description = item.find('description').text if item.find('description') is not None else ""
                    
                    send_phone_notification(title, "We Work Remotely", link, description)
    except Exception as e:
        print(f"WWR scrape error: {e}")

def check_freelancer():
    """Queries the Freelancer.com Public API for relevant contract gigs."""
    try:
        response = requests.get(FREELANCER_API_URL, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            projects = data.get("result", {}).get("projects", [])
            for project in projects:
                proj_id = str(project.get("id"))
                
                if proj_id and proj_id not in SEEN_POSTS:
                    SEEN_POSTS.add(proj_id)
                    title = project.get("title", "New Freelancer Project")
                    seo_url = project.get("seo_url")
                    link = f"https://www.freelancer.com/projects/{seo_url}" if seo_url else f"https://www.freelancer.com/projects/{proj_id}"
                    description = project.get("preview_description", "")
                    
                    send_phone_notification(title, "Freelancer", link, description)
    except Exception as e:
        print(f"Freelancer scrape error: {e}")

def aggregate_all_feeds():
    """Runs all scrapers sequentially to build a master cache baseline."""
    print("Refreshing contract feeds...")
    check_reddit()
    check_we_work_remotely()
    check_freelancer()

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
    server = HTTPServer(('0.0.0.0', 10000), SimpleServer)
    server.serve_forever()

def continuous_loop():
    """Checks all feeds every 2 minutes for new updates."""
    # First pass runs instantly on boot to populate baseline cache without spamming
    aggregate_all_feeds()
    
    while True:
        try:
            time.sleep(120)
            aggregate_all_feeds()
        except Exception as e:
            print(f"Loop error: {e}")

if __name__ == "__main__":
    # Run the continuous 2-minute scraper loop in the background
    threading.Thread(target=continuous_loop, daemon=True).start()
    print("Starting background listener on port 10000...")
    start_web_server()
