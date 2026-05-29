import os
import requests
from google import genai
from google.genai import types

# ==========================================
# 1. YOUR NOTIFICATION SETTINGS
# ==========================================
# Locked into your specific ntfy app channel
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
"""

def send_phone_notification(message_body):
    """Sends a free instant alert banner straight to the phone app."""
    url = f"https://ntfy.sh/{NTFY_TOPIC}"
    try:
        # Pushes an instantaneous banner alert to your phone
        response = requests.post(
            url,
            data=message_body.encode('utf-8'),
            headers={
                "Title": "🎯 New Live Lead Found!",
                "Priority": "high",
                "Tags": "moneybag,monocle"
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

        # Trigger the alert immediately if a verified live lead hits
        if "LIVE TRACKING ACTIVE" in output_text:
            send_phone_notification(output_text)

    except Exception as e:
        print(f"Error during agent execution: {e}")

if __name__ == "__main__":
    run_agent()
