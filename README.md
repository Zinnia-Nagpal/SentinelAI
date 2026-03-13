#  SentinelAI
GitGuardian tells you your house is on fire. SentinelAI puts it out.

## What it does
SentinelAI is a pre-push git hook that scans staged code for exposed secrets before they reach your repository. When a secret is detected it:
-  Blocks the push
-  Automatically replaces the raw secret with a vault reference (`op://vault/sentinelai/key-name`)
-  Stores the encrypted value in a local vault
-  Sends a real-time Slack alert to your team

## How it detects secrets
- **30+ regex patterns** — AWS, OpenAI, GitHub, Stripe, Twilio, JWT and more
- **Shannon entropy detection** — catches unknown high-entropy strings that no regex could find

## Setup
```cmd
git clone https://github.com/Zinnia-Nagpal/SentinelAI
cd SentinelAI
pip install -r requirements.txt
copy hooks\pre-push .git\hooks\pre-push
```

Create `.env`:
```
SLACK_WEBHOOK_URL=your_slack_webhook_here
```

## Run dashboard
```cmd
python -m streamlit run dashboard/app.py
```

## How it works
```
git push
    ↓
pre-push hook triggers
    ↓
scans staged diff for secrets
    ↓
secret found → encrypt → vault → replace with op:// reference
    ↓
Slack alert sent
    ↓
push blocked
```

## Built with
Python, SQLite, Fernet AES encryption, Streamlit, Slack webhooks, Shannon entropy

## What's next
- 1Password SDK integration for cloud vault
- `sentinelai install` CLI for any repo
- VS Code extension
- Real-time screen monitoring

## Built solo at cmd-f 2026 by Zinnia Nagpal

