#!/usr/bin/env python3
import sys
import os
import subprocess
from dotenv import load_dotenv
load_dotenv()
from sentinel.scanner import get_staged_diff, scan_diff
from sentinel.replacer import replace_secret_in_file
from sentinel.notifier import notify_slack
from sentinel.vault import init_vault, store_secret, log_push , init_db


    
def get_changed_files(repo_path="."):
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True, text=True,
        cwd=repo_path
    )
    files = result.stdout.strip().splitlines()
    return [os.path.join(repo_path, f) for f in files 
            if not f.endswith(('.pyc', '.png', '.jpg', '.db', '.key'))]


def main():
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."
    
    init_vault()
    init_db()
    diff = get_staged_diff(repo_path)
    findings = scan_diff(diff)

    if not findings:
        log_push(repo_path, [], "ALLOWED")
        print("No secrets found. Push allowed.")
        sys.exit(0)

    changed_files = get_changed_files(repo_path)
    
    print(" SentinelAI: Secrets detected!\n")
    seen = set()
    for finding in findings:
        reference = store_secret(finding["label"], finding["value"])
        if finding["label"] not in seen:
           print(f"  Found: {finding['label']}")
           print(f"  Replacing with: {reference}\n")
           seen.add(finding["label"])
        for filepath in changed_files:
            replace_secret_in_file(filepath, finding["value"], reference)
    
    unique_findings = list({f["label"]: f for f in findings}.values())
    log_push(repo_path, findings, "BLOCKED")
    result = notify_slack(findings, repo_path)
    print(f"Slack notification: {'sent' if result else 'failed'}")
    print(" Push blocked. Secrets have been replaced with vault references.")
    print("   Review the changes and re-push.")
    sys.exit(1)

if __name__ == "__main__":
    main()