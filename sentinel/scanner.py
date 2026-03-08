import subprocess
import re
import math

SECRET_PATTERNS = {
    # Cloud providers
    "AWS Access Key":        r"AKIA[0-9A-Z]{16}",
    "AWS Secret Key":        r"(?i)aws_secret_access_key\s*=\s*[a-zA-Z0-9/+=]{40}",
    "Google API Key":        r"AIza[0-9A-Za-z\-_]{35}",
    "Google OAuth":          r"[0-9]+-[0-9A-Za-z_]{32}\.apps\.googleusercontent\.com",
    "Azure Storage Key":     r"(?i)DefaultEndpointsProtocol=https;AccountName=[^;]+;AccountKey=[a-zA-Z0-9+/=]{88}",

    # Version control
    "GitHub Token":          r"ghp_[a-zA-Z0-9]{36}",
    "GitHub OAuth":          r"gho_[a-zA-Z0-9]{36}",
    "GitHub App Token":      r"(ghu|ghs)_[a-zA-Z0-9]{36}",
    "GitLab Token":          r"glpat-[a-zA-Z0-9\-]{20}",

    # AI providers
    "OpenAI Key":            r"sk-[a-zA-Z0-9]{32,}",
    "Anthropic Key":         r"sk-ant-[a-zA-Z0-9\-]{32,}",

    # Payment
    "Stripe Live Key":       r"sk_live_[a-zA-Z0-9]{24,}",
    "Stripe Test Key":       r"sk_test_[a-zA-Z0-9]{24,}",
    "PayPal Token":          r"access_token\$production\$[a-z0-9]{16}\$[a-f0-9]{32}",

    # Communication
    "Slack Token":           r"xox[baprs]-[0-9a-zA-Z\-]{10,}",
    "Slack Webhook":         r"https://hooks\.slack\.com/services/T[a-zA-Z0-9]+/B[a-zA-Z0-9]+/[a-zA-Z0-9]+",
    "Twilio Key":            r"SK[a-z0-9]{32}",
    "SendGrid Key":          r"SG\.[a-zA-Z0-9\-_]{22}\.[a-zA-Z0-9\-_]{43}",

    # Database
    "MongoDB URI":           r"mongodb(\+srv)?://[a-zA-Z0-9]+:[a-zA-Z0-9]+@",
    "PostgreSQL URI":        r"postgres(ql)?://[a-zA-Z0-9]+:[a-zA-Z0-9]+@",
    "MySQL URI":             r"mysql://[a-zA-Z0-9]+:[a-zA-Z0-9]+@",

    # Private keys
    "RSA Private Key":       r"-----BEGIN RSA PRIVATE KEY-----",
    "EC Private Key":        r"-----BEGIN EC PRIVATE KEY-----",
    "Private Key":           r"-----BEGIN PRIVATE KEY-----",
    "SSH Private Key":       r"-----BEGIN OPENSSH PRIVATE KEY-----",

    # Generic
    "Password in env":       r"(?i)(password|passwd|pwd)\s*=\s*['\"]?\S{8,}",
    "Generic API Key":       r"(?i)api_key\s*=\s*['\"]?[a-zA-Z0-9\-_]{16,}",
    "Generic Secret":        r"(?i)secret\s*=\s*['\"]?[a-zA-Z0-9\-_]{16,}",
    "Bearer Token":          r"Bearer\s+[a-zA-Z0-9\-_\.]{20,}",
    "JWT Token":             r"eyJ[a-zA-Z0-9\-_]+\.eyJ[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+",
}

def get_staged_diff(repo_path=".") -> str:
    result = subprocess.run(
        ['git', 'diff', '--cached'],
        capture_output=True, text=True,
        cwd=repo_path
    )
    return result.stdout

    # loop through each line of the diff
    # only scan lines starting with "+" (new additions)
    # run SECRET_PATTERNS regex against each line
    # if match found append {"label":..., "value":..., "line":...}
    # return findings
def scan_diff(diff: str) -> list[dict]:
    findings = []
    for line_num, line in enumerate(diff.splitlines(), start=1):
        if line.startswith("+") and not line.startswith("+++"):
            # Pass 1 - regex
            for label, pattern in SECRET_PATTERNS.items():
                match = re.search(pattern, line)
                if match:
                    already_found = any(f['value'] == match.group() for f in findings)
                    if not already_found:
                     findings.append({
                        "label": label,
                        "value": match.group(),
                        "line": line_num
                    })
            
            # Pass 2 - entropy (inside the loop!)
            potential_secrets = re.findall(r'[\'"`]([a-zA-Z0-9+/=_\-]{20,})[\'"`]', line)
            for value in potential_secrets:
                if is_high_entropy(value):
                  
                   already_found = any(f['value'] == value for f in findings)
                   if not already_found:
                        findings.append({
                            "label": "High Entropy Secret",
                            "value": value,
                            "line": line_num
                        })
    return findings



def calculate_entropy(string : str) -> float: 
    "Calculate Shannon Entry of a string"
    if not string:
        return 0
    entropy  = 0
    for char in set(string):
        prob = string.count(char)/ len(string)
        entropy -= prob * math.log2(prob)
    return entropy

def is_high_entropy(value: str, threshold: float = 3.5) -> bool:
    """Returns True if string looks randomly generated"""
    return len(value) >= 20 and calculate_entropy(value) > threshold