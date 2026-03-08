import streamlit as st
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from sentinel.vault import get_audit_log, init_db

st.set_page_config(page_title="Audit Log — SentinelAI", page_icon="📋", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=JetBrains+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #080b0f; color: #e0e6f0; }
#MainMenu, footer, header { visibility: hidden; }

.hero { padding: 40px 0 20px; text-align: center; }
.hero-title {
    font-family: 'Syne', sans-serif; font-size: 42px; font-weight: 800;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #fff 0%, #4af0a0 50%, #00c8ff 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0; line-height: 1;
}
.hero-sub { font-size: 14px; color: #5a6a7a; margin-top: 10px; font-weight: 300; }

.metric-card {
    background: #0d1117; border: 1px solid #1e2730;
    border-radius: 12px; padding: 20px 24px; text-align: center;
}
.metric-value { font-family: 'Syne', sans-serif; font-size: 36px; font-weight: 800; color: #4af0a0; line-height: 1; }
.metric-label { font-size: 11px; color: #5a6a7a; margin-top: 6px; letter-spacing: 0.08em; text-transform: uppercase; font-family: 'JetBrains Mono', monospace; }

.section-header {
    font-family: 'JetBrains Mono', monospace; font-size: 11px;
    letter-spacing: 0.15em; text-transform: uppercase; color: #3a5a7a;
    margin: 32px 0 16px; border-bottom: 1px solid #1a2530; padding-bottom: 8px;
}

.log-card {
    background: #0d1117; border: 1px solid #1e2730;
    border-radius: 8px; padding: 16px 20px; margin-bottom: 10px;
}
.log-blocked { border-left: 3px solid #ff5f57; }
.log-allowed { border-left: 3px solid #4af0a0; }
.log-action-blocked { color: #ff5f57; font-weight: 700; font-family: 'Syne', sans-serif; font-size: 13px; }
.log-action-allowed { color: #4af0a0; font-weight: 700; font-family: 'Syne', sans-serif; font-size: 13px; }
.log-meta { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #5a6a7a; margin-top: 6px; }
.log-types { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #7ac8ff; margin-top: 6px; }
.empty { color: #3a5a7a; font-family: 'JetBrains Mono', monospace; font-size: 13px; padding: 20px 0; }
</style>
""", unsafe_allow_html=True)

# ── Init ──────────────────────────────────────────────────────────────────────
init_db()
logs = get_audit_log()

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-title">📋 Audit Log</div>
    <div class="hero-sub">Full history of every push scanned by SentinelAI</div>
</div>
""", unsafe_allow_html=True)

# ── Stats ─────────────────────────────────────────────────────────────────────
total = len(logs)
blocked = sum(1 for l in logs if l['action'] == 'BLOCKED')
allowed = total - blocked
total_secrets = sum(l['secrets_found'] for l in logs)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{total}</div><div class="metric-label">Total Scans</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#ff5f57">{blocked}</div><div class="metric-label">🚨 Blocked</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{allowed}</div><div class="metric-label">✅ Allowed</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#febc2e">{total_secrets}</div><div class="metric-label">🔑 Secrets Caught</div></div>', unsafe_allow_html=True)

# ── Log entries ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">// push history</div>', unsafe_allow_html=True)

if not logs:
    st.markdown('<p class="empty">No push attempts logged yet.</p>', unsafe_allow_html=True)
else:
    for log in logs:
        is_blocked = log['action'] == 'BLOCKED'
        card_class = "log-blocked" if is_blocked else "log-allowed"
        action_class = "log-action-blocked" if is_blocked else "log-action-allowed"
        icon = "🚨" if is_blocked else "✅"
        types = log['secret_types'] if log['secret_types'] else "none"

        st.markdown(f"""
        <div class="log-card {card_class}">
            <div class="{action_class}">{icon} {log['action']} — {log['secrets_found']} secret(s) found</div>
            <div class="log-meta">📁 {log['repo_name']} &nbsp;|&nbsp; 🕒 {log['timestamp']}</div>
            <div class="log-types">{types}</div>
        </div>""", unsafe_allow_html=True)