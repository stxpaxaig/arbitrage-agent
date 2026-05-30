
import os
import requests
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from google import genai
from google.genai import types

# ==========================================
# 1. YOUR NOTIFICATION SETTINGS
# ==========================================
NTFY_TOPIC = "justin_leads_55"

# ==========================================
# 2. AGENT CONFIGURATION & INSTRUCTIONS
# ==========================================
PROMPT_INSTRUCTIONS = """
You are a live web-scraping search engine. Do not simulate, do not roleplay, and do not invent example data. 

Using your Google Search tool, scan the live internet for actual, real-time posts, threads, or listings from the last 24 hours related to Python automation, data scraping, or micro-gigs on open platforms like Reddit or freelance boards.

Your output must use this exact layout:
---
### LIVE TRACKING ACTIVE ###
* **Source Platform:** [Name of real site]
* **Live Verified URL:** [Paste the actual, exact live URL found via search]
* **Date/Time Discovered:** [Current timestamp]
* **Actual Request Details:** [Brief summary of what the real post is asking for]
---
If no new live matches are found in the last 24 hours, print exactly: "SEARCH COMPLETE: No new live listings detected in this window." Do not invent an example.
def send_phone_notification(message_body):
    """Sends a free instant alert banner straight to the phone app."""
    url = f"https://ntfy.sh/{NTFY_TOPIC}"
    try:
        # Emojis stripped out to prevent the latin-1 encoding crash
        response = requests.post(
            url,
            data=message_body.encode('utf-8'),
            headers={
                "Title": "New Live Lead Found",
                "Priority": "high"
            }
        )
        if response.status_code == 200:
            print("Instant phone notification sent successfully.")
        else:
            print(f"Notification status error: {response.status_code}")
    except Exception as e:
        print(f"Failed to push phone alert: {e}")


def run_agent():
    """Executes the Google Search query using Gemini 2.5 Flash."""
    print("Initializing Live Market Scan...")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is missing.")
        return

    client = genai.Client(api_key=api_key)

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=PROMPT_INSTRUCTIONS,
            config=types.GenerateContentConfig(
                tools=[{"google_search": {}}],
            )
        )
        
        output_text = response.text
        print(output_text)

        if "LIVE TRACKING ACTIVE" in output_text:
            send_phone_notification(output_text)

    except Exception as e:
        print(f"Error during agent execution: {e}")

# ==========================================
# 3. RENDER ALIVE LISTENER
# ==========================================
class SimpleServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Agent Active")

    def log_message(self, format, *args):
        return # Keeps the logs clean from standard web traffic pings

def start_web_server():
    # Binds to the port Render requires to declare a service active
    server = HTTPServer(('0.0.0.0', 10000), SimpleServer)
    server.serve_forever()

if __name__ == "__main__":
    # 1. Fire the market search immediately on boot
    threading.Thread(target=run_agent).start()
    
    # 2. Keep the server up so the build status switches to "Live"
    print("Starting background listener on port 10000...")
    start_web_server()
