import requests
import os
import json
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env'))

def notify_slack(findings: list, repo_path: str):
    # get webhook from env
    # build message
    # post to slack
    # return True if success
   # Right
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print("Error: No SLACK_WEBHOOK_URL found in environment.")
        return False
      
    repo_name = os.path.basename(repo_path)        # just the folder name
    count = len(findings) 
    secret_types = ", ".join(f["label"] for f in findings)                          # how many found
    message = f"SentinelAI blocked a push in `{repo_name}` — {count} secrets found: {secret_types}"
    
    payload = {"text": message}
    try:
        response = requests.post(webhook_url, json=payload)
        # 4. Return True if success
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending to Slack: {e}")
        return False