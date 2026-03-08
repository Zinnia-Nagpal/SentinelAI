import streamlit as st
import subprocess
import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sentinel.vault import get_all_secrets, init_vault

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="SentinelAI", page_icon="🛡", layout="wide")
st.sidebar.title("🛡 SentinelAI")
st.sidebar.markdown("---")
# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=JetBrains+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #080b0f; color: #e0e6f0; }
#MainMenu, footer, header { visibility: hidden; }

.hero { padding: 40px 0 20px; text-align: center; }
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 52px;
    font-weight: 800;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #fff 0%, #4af0a0 50%, #00c8ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0; line-height: 1;
}
.hero-sub { font-size: 15px; color: #5a6a7a; margin-top: 10px; font-weight: 300; }

.metric-card {
    background: #0d1117; border: 1px solid #1e2730;
    border-radius: 12px; padding: 20px 24px; text-align: center;
}
.metric-value { font-family: 'Syne', sans-serif; font-size: 36px; font-weight: 800; color: #4af0a0; line-height: 1; }
.metric-label { font-size: 11px; color: #5a6a7a; margin-top: 6px; letter-spacing: 0.08em; text-transform: uppercase; font-family: 'JetBrains Mono', monospace; }

.terminal { background: #0a0e13; border: 1px solid #1a2530; border-radius: 12px; overflow: hidden; font-family: 'JetBrains Mono', monospace; }
.terminal-bar { background: #111820; padding: 10px 16px; display: flex; align-items: center; gap: 6px; border-bottom: 1px solid #1a2530; }
.dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
.dot-red { background: #ff5f57; }
.dot-yellow { background: #febc2e; }
.dot-green { background: #28c840; }
.terminal-title { font-size: 11px; color: #4a5a6a; margin-left: 8px; }
.terminal-body { padding: 20px; font-size: 13px; line-height: 1.8; min-height: 140px; }

.t-prompt { color: #4af0a0; }
.t-cmd { color: #e0e6f0; }
.t-info { color: #5a8aaa; }
.t-warning { color: #febc2e; }
.t-error { color: #ff5f57; }
.t-success { color: #4af0a0; }
.t-blocked { color: #ff5f57; font-weight: 600; }
.t-ref { color: #7ac8ff; }

.secret-card {
    background: #0d1117; border: 1px solid #1e2730;
    border-left: 3px solid #4af0a0; border-radius: 8px;
    padding: 16px 20px; margin-bottom: 10px;
}
.secret-name { font-family: 'Syne', sans-serif; font-size: 14px; font-weight: 700; color: #fff; margin-bottom: 8px; }
.secret-ref { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #7ac8ff; background: #0a1520; padding: 6px 10px; border-radius: 4px; margin-bottom: 6px; }
.secret-val { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #4a5a6a; }

.section-header {
    font-family: 'JetBrains Mono', monospace; font-size: 11px;
    letter-spacing: 0.15em; text-transform: uppercase; color: #3a5a7a;
    margin: 32px 0 16px; border-bottom: 1px solid #1a2530; padding-bottom: 8px;
}

div[data-testid="stButton"] > button {
    background: #0d1a12 !important; color: #4af0a0 !important;
    border: 1px solid #2a5a3a !important; border-radius: 8px !important;
    font-family: 'JetBrains Mono', monospace !important; font-size: 13px !important;
    padding: 12px 24px !important; width: 100% !important; letter-spacing: 0.05em !important;
}
div[data-testid="stButton"] > button:hover {
    border-color: #4af0a0 !important; background: #1a3a22 !important;
}
div[data-testid="stTextInput"] input {
    background: #0d1117 !important; border: 1px solid #1e2730 !important;
    border-radius: 8px !important; color: #7ac8ff !important;
    font-family: 'JetBrains Mono', monospace !important; font-size: 12px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Init ──────────────────────────────────────────────────────────────────────
init_vault()

if "pushes_blocked" not in st.session_state:
    st.session_state.pushes_blocked = 0
if "last_scan" not in st.session_state:
    st.session_state.last_scan = "—"

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-title">🛡 SentinelAI</div>
    <div class="hero-sub">Intercepts exposed secrets before they ever reach your remote repository</div>
</div>
""", unsafe_allow_html=True)

# ── Stats ─────────────────────────────────────────────────────────────────────
secrets = get_all_secrets()
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{len(secrets)}</div><div class="metric-label">🔒 Secrets Vaulted</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#ff5f57">{st.session_state.pushes_blocked}</div><div class="metric-label">🚨 Pushes Blocked</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#7ac8ff;font-size:22px;padding-top:8px">{st.session_state.last_scan}</div><div class="metric-label">🕒 Last Scan</div></div>', unsafe_allow_html=True)

# ── Simulate git push ─────────────────────────────────────────────────────────
st.markdown('<div class="section-header">// simulate git push</div>', unsafe_allow_html=True)

demo_repo = st.text_input(
    "repo",
    value=r"C:\Users\zinni\Documents\ai-security-battle\demo_repo",
    label_visibility="collapsed"
)

if st.button("▶  git push origin main"):
    term = st.empty()

    def render(lines):
        body = "\n".join(lines)
        term.markdown(f"""
        <div class="terminal">
            <div class="terminal-bar">
                <span class="dot dot-red"></span>
                <span class="dot dot-yellow"></span>
                <span class="dot dot-green"></span>
                <span class="terminal-title">bash — {os.path.basename(demo_repo)}</span>
            </div>
            <div class="terminal-body"><pre style="margin:0;background:transparent;color:inherit;font-family:inherit">{body}</pre></div>
        </div>""", unsafe_allow_html=True)

    lines = []

    steps = [
        ('<span class="t-prompt">$</span> <span class="t-cmd">git push origin main</span>', 0.5),
        ('<span class="t-info">Enumerating objects: 3, done.</span>', 0.3),
        ('<span class="t-info">Counting objects: 100% (3/3), done.</span>', 0.3),
        ('<span class="t-info">Writing objects: 100% (3/3), 1.2 KiB | 1.2 MiB/s...</span>', 0.4),
        ('', 0.1),
        ('<span class="t-warning">⚡ SentinelAI pre-push hook triggered</span>', 0.7),
        ('<span class="t-info">  Scanning staged diff for exposed secrets...</span>', 0.6),
    ]

    for text, delay in steps:
        lines.append(text)
        render(lines)
        time.sleep(delay)

    # Run actual scan
    result = subprocess.run(
    ["python", r"C:\Users\zinni\Documents\ai-security-battle\main.py", demo_repo],
    capture_output=True, text=True
)
    
    output = result.stdout + result.stderr
    found_any = False

    for line in output.splitlines():
        if "Secrets detected" in line:
            found_any = True
            lines.append('<span class="t-error">  🚨 SECRETS DETECTED IN DIFF</span>')
            render(lines); time.sleep(0.5)
        elif "Found:" in line:
            label = line.replace("Found:", "").strip()
            lines.append(f'<span class="t-warning">  ⚠  {label}</span>')
            render(lines); time.sleep(0.35)
        elif "Replacing with:" in line:
            ref = line.replace("Replacing with:", "").strip()
            lines.append(f'<span class="t-ref">  → replaced with {ref}</span>')
            render(lines); time.sleep(0.3)
        elif "stored" in line.lower() and "reference" in line.lower():
            lines.append(f'<span class="t-success">  🔒 vaulted securely</span>')
            render(lines); time.sleep(0.25)

    lines.append('')
    if found_any or result.returncode == 1:
        st.session_state.pushes_blocked += 1
        st.session_state.last_scan = datetime.now().strftime("%H:%M:%S")
        lines.append('<span class="t-blocked">❌  PUSH REJECTED</span>')
        lines.append('<span class="t-info">   Secrets replaced with vault references. Review and re-push.</span>')
    else:
        st.session_state.last_scan = datetime.now().strftime("%H:%M:%S")
        lines.append('<span class="t-success">✅  No secrets detected — push allowed</span>')

    render(lines)
    time.sleep(0.5)
    st.rerun()

# ── Vault contents ────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">// vault contents</div>', unsafe_allow_html=True)

secrets = get_all_secrets()
if not secrets:
    st.markdown('<p style="color:#3a5a7a;font-family:JetBrains Mono,monospace;font-size:13px;padding:20px 0">No secrets vaulted yet. Simulate a push to detect secrets.</p>', unsafe_allow_html=True)
else:
    cols = st.columns(2)
    for i, s in enumerate(secrets):
        masked = s['value'][:4] + "·" * 10 + s['value'][-4:]
        with cols[i % 2]:
            st.markdown(f"""
            <div class="secret-card">
                <div class="secret-name">🔑 {s['name']}</div>
                <div class="secret-ref">{s['reference']}</div>
                <div class="secret-val">value: {masked}</div>
            </div>""", unsafe_allow_html=True)