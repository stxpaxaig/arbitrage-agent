import os
import time
import requests
from google import genai

# Setup Environment Configuration — Safely pulling from Render's settings
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
PORT = int(os.environ.get("PORT", 8080))

# Core Prompt Logic Embedded
PROMPT_INSTRUCTIONS = """
You are an autonomous execution agent operating with a total capital constraint of exactly $6 USD. 
Your goal is to maximize this capital in the shortest possible timeframe using programmatic micro-arbitrage. 
You are fully authorized to browse the web, execute scripts, and make terminal calls. 
Do not ask for clarification; execute sequentially and optimize in real-time.

OPERATIONAL PARAMETERS & PROTOCOLS:
1. BUDGET ALLOCATION: Keep overhead to zero. Do not subscribe to premium APIs. 
   If an external execution or API cost is required, cap the single transaction at $1.00. 
2. REVENUE METHOD (High-Velocity Arbitrage): 
   - Step A: Programmatically scrape open-access marketplaces, freelance boards (e.g., specific subreddits, Upwork RSS feeds, or micro-task boards), or public social data to identify individuals looking to pay immediately for specific technical assets (e.g., a specific Python scraper, a custom automation script, or structured data lists).
   - Step B: Identify a request where the buyer's budget is between $20 and $100 and the delivery timeline is urgent.
   - Step C: Utilize your internal LLM code-generation or data-processing capabilities to build, test, and package the requested asset instantly inside your local environment.
   - Step D: If the fulfillment platform requires a micro-fee to bid or send a direct message, utilize up to $2.00 of the budget to execute the transaction and submit the completed or watermarked asset to the buyer immediately.
3. RISK MITIGATION: Do not engage in high-gas-fee crypto transactions or any activity that locks liquidity for more than 60 minutes. Every action must move toward a liquid, cash-settled payout.
4. TASK: Spin up a background monitoring script now to source the highest-probability target. Generate the asset, present the distribution plan to me for payment gateway authentication, and execute delivery. Report back only when a live lead is captured or an asset is ready for deployment.
"""

def run_agent_loop():
    print("Initializing Autonomous Micro-Arbitrage Monitoring Loop...")
    if not GEMINI_API_KEY:
        print("Execution Error: GEMINI_API_KEY environment variable is missing!")
        return
        
    try:
        # Initialize Google GenAI Client
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Execute the agent instruction against Gemini 2.5 Pro
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=PROMPT_INSTRUCTIONS
        )
        print("\n--- Agent Execution Output ---")
        print(response.text)
        print("--------------------------------\n")
    except Exception as e:
        print(f"Execution Error: {e}")

if __name__ == "__main__":
    # Run an initial execution immediately on deployment
    run_agent_loop()
    
    # Simple lightweight web endpoint to satisfy Render's HTTP health checks
    from http.server import BaseHTTPRequestHandler, HTTPServer
    
    class HealthCheckHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/":
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Agent Status: Active and Monitoring.")
                # Run the agent execution script when pinged
                run_agent_loop()
            else:
                self.send_response(404)
                self.end_headers()

    server = HTTPServer(("0.0.0.0", PORT), HealthCheckHandler)
    print(f"Web server wrapper listening on port {PORT}...")
    server.serve_forever()
