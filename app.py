import os
import re
import html
import math
import pickle
import string
import inspect
from datetime import datetime

import nltk
import streamlit as st
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# ==============================================================================
# PAGE CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="Email Threat & Spam Detection System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Button compatibility helper
_BUTTON_PARAMS = inspect.signature(st.button).parameters
STRETCH = {"width": "stretch"} if "width" in _BUTTON_PARAMS else {"use_container_width": True}

# ==============================================================================
# HTML RENDER HELPER (Prevents Markdown from turning indented HTML into code blocks)
# ==============================================================================
def render_html(markup):
    """Strips leading whitespace from every line so Markdown never misinterprets it as a code block."""
    cleaned = "\n".join(line.lstrip() for line in markup.strip().splitlines())
    st.markdown(cleaned, unsafe_allow_html=True)

# ==============================================================================
# CLEAN & MODERN COLOR PALETTE (CSS)
# ==============================================================================
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg-main: #0f172a;
    --card-bg: rgba(30, 41, 59, 0.75);
    --card-border: rgba(148, 163, 184, 0.15);
    --primary: #6366f1;
    --primary-hover: #4f46e5;
    --accent: #38bdf8;
    --color-safe: #10b981;
    --color-warn: #f59e0b;
    --color-bad: #ef4444;
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
}

.stApp {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    background-color: var(--bg-main);
    background-image: 
        radial-gradient(800px 500px at 10% -5%, rgba(99, 102, 241, 0.18), transparent 60%),
        radial-gradient(800px 500px at 90% 5%, rgba(56, 189, 248, 0.14), transparent 55%),
        radial-gradient(600px 400px at 50% 110%, rgba(139, 92, 246, 0.12), transparent 60%);
    background-attachment: fixed;
    color: var(--text-primary);
}

.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2.5rem !important;
    max-width: 1240px !important;
}

/* Header Banner */
.hero {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(30, 41, 59, 0.8));
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 16px;
    padding: 22px 28px;
    margin-bottom: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
}

.hero h1 {
    margin: 0;
    font-size: 1.75rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.01em;
}

.hero .sub {
    color: var(--text-secondary);
    font-size: 0.95rem;
    margin-top: 4px;
}

.pills {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.pill {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid var(--card-border);
    border-radius: 9999px;
    padding: 6px 14px;
    font-size: 0.84rem;
    color: var(--text-primary);
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.dot-online {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: var(--color-safe);
    box-shadow: 0 0 8px var(--color-safe);
}

/* Cards */
.card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 14px;
    padding: 18px 20px;
    height: 100%;
    transition: transform 0.2s ease, border-color 0.2s ease;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.card:hover {
    border-color: rgba(99, 102, 241, 0.4);
    transform: translateY(-2px);
}

.card .ic { font-size: 1.6rem; }
.card .t { font-weight: 700; font-size: 1.05rem; margin-top: 8px; color: #ffffff; }
.card .d { color: var(--text-secondary); font-size: 0.88rem; margin: 4px 0 10px; line-height: 1.45; }
.card .v { font-size: 1.7rem; font-weight: 800; letter-spacing: -0.01em; }
.card .l { color: var(--text-muted); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; }

/* Sections */
.sec {
    font-size: 1.25rem;
    font-weight: 700;
    color: #ffffff;
    margin: 26px 0 6px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.sec:before {
    content: "";
    width: 4px;
    height: 1.1em;
    border-radius: 4px;
    background: linear-gradient(180deg, var(--primary), var(--accent));
}

.secd {
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin-bottom: 14px;
}

/* Badges */
.badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 600;
    border: 1px solid;
}

.b-ok { background: rgba(16, 185, 129, 0.15); color: #34d399; border-color: rgba(16, 185, 129, 0.4); }
.b-warn { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border-color: rgba(245, 158, 11, 0.4); }
.b-bad { background: rgba(239, 68, 68, 0.15); color: #f87171; border-color: rgba(239, 68, 68, 0.4); }

.t-ok { color: #34d399; }
.t-warn { color: #fbbf24; }
.t-bad { color: #f87171; }

/* Status Box */
.status {
    border-radius: 16px;
    padding: 24px 28px;
    border: 1px solid;
    display: flex;
    gap: 28px;
    align-items: center;
    flex-wrap: wrap;
    margin-bottom: 20px;
}

.status > .sbody { flex: 1; min-width: 260px; }
.s-ok { background: linear-gradient(135deg, rgba(16, 185, 129, 0.12), rgba(30, 41, 59, 0.85)); border-color: rgba(16, 185, 129, 0.45); }
.s-warn { background: linear-gradient(135deg, rgba(245, 158, 11, 0.12), rgba(30, 41, 59, 0.85)); border-color: rgba(245, 158, 11, 0.45); }
.s-bad { background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(30, 41, 59, 0.85)); border-color: rgba(239, 68, 68, 0.45); }

.status h2 { margin: 4px 0 8px; font-size: 1.5rem; color: #ffffff; }
.status p { margin: 0; color: #cbd5e1; line-height: 1.55; font-size: 0.95rem; }

/* SVG Gauge */
.gauge { position: relative; width: 140px; height: 140px; flex-shrink: 0; }
.gauge svg { display: block; width: 140px; height: 140px; }
.gnum { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.gnum b { font-size: 2.3rem; font-weight: 800; line-height: 1; }
.gnum small { color: var(--text-muted); font-size: 0.8rem; font-weight: 600; margin-top: 2px; }

/* Progress Bars */
.bar { height: 8px; background: rgba(15, 23, 42, 0.8); border-radius: 9999px; overflow: hidden; margin: 6px 0 14px; }
.bar i { display: block; height: 100%; border-radius: 9999px; transition: width 0.6s ease; }
.barl { display: flex; justify-content: space-between; font-size: 0.88rem; color: var(--text-secondary); }

/* Threat Level Scale */
.scale { margin-top: 14px; }
.strack { position: relative; display: flex; gap: 4px; height: 7px; }
.strack i { display: block; border-radius: 9999px; opacity: 0.6; }
.strack em {
    position: absolute; top: -4px; width: 4px; height: 15px; border-radius: 3px;
    background: #ffffff; transform: translateX(-50%); box-shadow: 0 0 8px rgba(255, 255, 255, 0.8);
}
.slabels { display: flex; gap: 4px; margin-top: 6px; font-size: 0.72rem; letter-spacing: 0.05em; color: var(--text-muted); font-weight: 600; }
.slabels span { text-align: center; }

/* Tables */
.tw { overflow-x: auto; margin-top: 10px; }
.tbl { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.tbl th { text-align: left; color: var(--text-secondary); font-weight: 600; padding: 10px; border-bottom: 1px solid var(--card-border); }
.tbl td { padding: 10px; border-bottom: 1px solid rgba(148, 163, 184, 0.08); vertical-align: top; }
.tbl tr:hover td { background: rgba(99, 102, 241, 0.04); }
.mono { font-family: Consolas, Menlo, monospace; word-break: break-all; font-size: 0.85rem; }
.rs { color: var(--text-secondary); font-size: 0.84rem; margin-top: 4px; }

/* Navigation Radio Styling */
div[role="radiogroup"] {
    gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 16px;
    background: rgba(30, 41, 59, 0.5);
    padding: 6px;
    border-radius: 14px;
    border: 1px solid var(--card-border);
}

div[role="radiogroup"] > label {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 10px;
    padding: 8px 24px;
    transition: all 0.2s ease;
    cursor: pointer;
}

div[role="radiogroup"] > label:hover {
    background: rgba(99, 102, 241, 0.15);
}

div[role="radiogroup"] > label > div:first-child { display: none; }
div[role="radiogroup"] > label:has(input:checked) {
    background: linear-gradient(135deg, #6366f1, #4f46e5);
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
}

div[role="radiogroup"] > label p {
    font-weight: 600;
    color: var(--text-primary) !important;
    font-size: 0.92rem;
    margin: 0;
}

/* Streamlit Native Tweaks */
.stTextArea textarea {
    background: rgba(15, 23, 42, 0.75) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
    font-size: 0.95rem !important;
}

.stTextArea textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.25) !important;
}

.stButton > button {
    border-radius: 10px !important;
    border: 1px solid var(--card-border) !important;
    background: rgba(30, 41, 59, 0.8) !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    border-color: var(--primary) !important;
    transform: translateY(-1px);
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
    border: none !important;
    box-shadow: 0 4px 16px rgba(99, 102, 241, 0.35) !important;
}

.stButton > button[kind="primary"]:hover {
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5) !important;
}

.side-item {
    display: flex;
    justify-content: space-between;
    font-size: 0.88rem;
    padding: 7px 0;
    border-bottom: 1px solid rgba(148, 163, 184, 0.1);
}

.side-item span:first-child { color: var(--text-secondary); }
.side-item span:last-child { color: var(--text-primary); font-weight: 600; }

.foot {
    text-align: center;
    color: var(--text-muted);
    margin-top: 40px;
    padding-top: 18px;
    border-top: 1px solid var(--card-border);
    font-size: 0.85rem;
}
"""

st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
esc = html.escape

# ==============================================================================
# NLTK INITIALIZATION
# ==============================================================================
try:
    stop_words = set(stopwords.words("english"))
except LookupError:
    nltk.download("stopwords", quiet=True)
    stop_words = set(stopwords.words("english"))

stemmer = PorterStemmer()

# ==============================================================================
# LOAD PRE-TRAINED ML ASSETS
# ==============================================================================
if not (os.path.exists("model.pkl") and os.path.exists("vectorizer.pkl")):
    st.error("⚠️ ML model files are missing. Please run train_model.py first.")
    st.stop()

try:
    with open("model.pkl", "rb") as file:
        model = pickle.load(file)
    with open("vectorizer.pkl", "rb") as file:
        vectorizer = pickle.load(file)
except Exception:
    st.error("⚠️ Unable to load the detection engine. Re-run train_model.py and try again.")
    st.stop()

# ==============================================================================
# HEURISTIC RULES (Original preserved)
# ==============================================================================
phishing_keywords = [
    "verify your account", "login immediately", "click here",
    "password expired", "bank account", "urgent action required",
    "account suspended", "security alert", "confirm your identity",
    "update your payment details", "verify now", "payment failed",
    "unauthorized login", "confirm password", "reset password"
]

dangerous_extensions = [
    ".exe", ".bat", ".cmd", ".scr", ".js", ".vbs", ".ps1", ".msi", ".com"
]

LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
LEVEL_FLOOR = [0, 20, 45, 70]
LEVEL_COLOR = {"LOW": "#10b981", "MEDIUM": "#f59e0b", "HIGH": "#fb923c", "CRITICAL": "#ef4444"}

# ==============================================================================
# BACKEND DETECTION FUNCTIONS (Original preserved)
# ==============================================================================
def preprocess(text):
    text = str(text).lower()
    cleaned = "".join(char for char in text if char not in string.punctuation)
    words = cleaned.split()
    words = [word for word in words if word not in stop_words]
    words = [stemmer.stem(word) for word in words]
    return " ".join(words)


def detect_phishing(text):
    score = 0
    found_keywords = []
    lower_text = text.lower()
    for keyword in phishing_keywords:
        if keyword in lower_text:
            score += 1
            found_keywords.append(keyword)
    return score, found_keywords


def extract_urls(text):
    urls = re.findall(r'https?://[^\s<>"\']+', text)
    return [url.rstrip(".,);!?") for url in urls]


def is_suspicious_url(url):
    suspicious_keywords = [
        "login", "verify", "update", "secure", "account", "bank",
        "reward", "gift", "prize", "claim", "bonus", "free"
    ]
    suspicious_tlds = [".xyz", ".top", ".ru", ".tk", ".ml", ".ga", ".cf"]

    score = 0
    reasons = []
    lower_url = url.lower()

    for keyword in suspicious_keywords:
        if keyword in lower_url:
            score += 1
            reasons.append(f"Suspicious URL keyword: {keyword}")

    for tld in suspicious_tlds:
        if tld in lower_url:
            score += 1
            reasons.append(f"Potentially suspicious domain ending: {tld}")

    ip_pattern = r'https?://(?:\d{1,3}\.){3}\d{1,3}'
    if re.search(ip_pattern, lower_url):
        score += 2
        reasons.append("URL uses an IP address instead of a domain name")

    return score, reasons


def scan_attachment(filename):
    risk_score = 0
    reasons = []
    filename = filename.lower()

    for extension in dangerous_extensions:
        if filename.endswith(extension):
            risk_score += 50
            reasons.append(f"Suspicious file extension detected: {extension}")

    if filename.count(".") > 1:
        risk_score += 20
        reasons.append("Multiple file extensions detected")

    return risk_score, reasons


def compute_threat(pred, spam_prob, phish_count, url_results, attach_risk):
    url_points = sum(u["score"] for u in url_results)
    points = (
        spam_prob * 0.40
        + min(phish_count * 12, 30)
        + min(url_points * 8, 20)
        + min(attach_risk * 0.6, 30)
    )
    score = int(min(round(points), 100))
    rank = 0 if score < 20 else 1 if score < 45 else 2 if score < 70 else 3

    has_ip = any("IP address" in r for u in url_results for r in u["reasons"])
    if pred == 1:
        rank = max(rank, 1)
    if pred == 1 and (phish_count > 0 or url_points > 0):
        rank = max(rank, 2)
    if phish_count >= 3 or has_ip or attach_risk >= 50:
        rank = max(rank, 2)

    return max(score, LEVEL_FLOOR[rank]), LEVELS[rank]


def run_analysis(message, uploaded_file):
    vec = vectorizer.transform([preprocess(message)])
    pred = int(model.predict(vec)[0])
    proba = model.predict_proba(vec)[0]
    spam_prob = float(proba[1] * 100)
    safe_prob = float(proba[0] * 100)

    phish_count, phish_found = detect_phishing(message)

    url_results = []
    for url in extract_urls(message):
        score, reasons = is_suspicious_url(url)
        url_results.append({"url": url, "score": score, "reasons": reasons})

    attachment = None
    attach_risk = 0
    if uploaded_file is not None:
        fname = getattr(uploaded_file, "name", str(uploaded_file))
        attach_risk, attach_reasons = scan_attachment(fname)
        attachment = {
            "name": fname,
            "ext": os.path.splitext(fname)[1].lower() or "none",
            "risk": attach_risk,
            "reasons": attach_reasons,
        }

    score, level = compute_threat(pred, spam_prob, phish_count, url_results, attach_risk)

    why = []
    if pred == 1:
        why.append(f"the ML model classified it as spam ({spam_prob:.1f}% spam probability)")
    if phish_count:
        why.append(f"{phish_count} phishing phrase(s) were found")
    flagged = [u for u in url_results if u["score"] > 0]
    if flagged:
        why.append(f"{len(flagged)} of {len(url_results)} URL(s) matched suspicious patterns")
    if attachment and attach_risk > 0:
        why.append("the attachment filename looks risky")

    return {
        "pred": pred, "spam_prob": spam_prob, "safe_prob": safe_prob,
        "phish_count": phish_count, "phish_found": phish_found,
        "urls": url_results, "attachment": attachment,
        "score": score, "level": level, "why": why,
        "time": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
    }

# ==============================================================================
# UI COMPONENTS & CARDS
# ==============================================================================
def status_for(level):
    if level == "LOW":
        return "s-ok", "🟢", "NO SIGNIFICANT THREAT DETECTED"
    if level == "MEDIUM":
        return "s-warn", "🟡", "SUSPICIOUS EMAIL DETECTED"
    return "s-bad", "🔴", "HIGH-RISK EMAIL DETECTED"


def card(icon, title, desc, value="", label=""):
    body = f'<div class="v">{value}</div><div class="l">{label}</div>' if value else ""
    return f'<div class="card"><div class="ic">{icon}</div><div class="t">{title}</div><div class="d">{desc}</div>{body}</div>'


def metric(title, value, label, tone):
    return f'<div class="card"><div class="l">{title}</div><div class="v t-{tone}">{value}</div><div class="l">{label}</div></div>'


def bar(label, pct, color):
    return (f'<div class="barl"><span>{label}</span><b>{pct:.1f}%</b></div>'
            f'<div class="bar"><i style="width:{pct:.1f}%;background:{color}"></i></div>')


def url_badge(score):
    if score == 0:
        return '<span class="badge b-ok">🟢 Safe</span>'
    if score == 1:
        return '<span class="badge b-warn">🟡 Suspicious</span>'
    return '<span class="badge b-bad">🔴 High Risk</span>'


def attachment_label(att):
    if att is None:
        return "N/A", "ok", "No file uploaded"
    if att["risk"] >= 50:
        return "HIGH", "bad", "High-risk extension"
    if att["risk"] > 0:
        return "MEDIUM", "warn", "Suspicious filename"
    return "SAFE", "ok", "Clean extension"


def gauge_svg(score, color):
    r = 54
    circ = 2 * math.pi * r
    clamped = max(0, min(score, 100))
    offset = circ * (1 - clamped / 100)
    return (
        f'<div class="gauge">'
        f'<svg viewBox="0 0 140 140">'
        f'<circle cx="70" cy="70" r="{r}" fill="none" stroke="rgba(15, 23, 42, 0.7)" stroke-width="10"/>'
        f'<circle cx="70" cy="70" r="{r}" fill="none" stroke="{color}" stroke-width="10" '
        f'stroke-linecap="round" stroke-dasharray="{circ:.2f}" stroke-dashoffset="{offset:.2f}" '
        f'transform="rotate(-90 70 70)" style="filter: drop-shadow(0 0 6px {color});" />'
        f'</svg>'
        f'<div class="gnum"><b style="color:{color}">{clamped}</b><small>/ 100</small></div>'
        f'</div>'
    )


def level_scale(score):
    segs = [("LOW", 20, "#10b981"), ("MEDIUM", 25, "#f59e0b"), ("HIGH", 25, "#fb923c"), ("CRITICAL", 30, "#ef4444")]
    bars = "".join(f'<i style="flex:{w};background:{c}"></i>' for _, w, c in segs)
    labels = "".join(f'<span style="flex:{w}">{n}</span>' for n, w, _ in segs)
    return f'<div class="scale"><div class="strack">{bars}<em style="left:{max(0, min(score, 100))}%"></em></div><div class="slabels">{labels}</div></div>'


def build_report_text(r, message):
    lines = [
        "EMAIL THREAT DETECTION SYSTEM - AUDIT REPORT",
        f"Generated: {r['time']}", "=" * 52,
        f"Overall Threat Level : {r['level']} ({r['score']}/100)",
        "",
        "[Email Classification]",
        f"  Result           : {'Spam' if r['pred'] == 1 else 'Not Spam'}",
        f"  Spam Probability : {r['spam_prob']:.2f}%",
        f"  Safe Probability : {r['safe_prob']:.2f}%",
        "",
        f"[Phishing Analysis] Indicators Found: {r['phish_count']}"
    ]
    lines += [f"  - {k}" for k in r["phish_found"]]
    lines += ["", f"[URL Analysis] URLs Found: {len(r['urls'])}"]
    for u in r["urls"]:
        lines.append(f"  - {u['url']} (Risk score: {u['score']})")
        lines += [f"      * {x}" for x in u["reasons"]]
    lines += ["", "[Attachment Analysis]"]
    att = r["attachment"]
    if att:
        lines += [f"  Filename: {att['name']}", f"  Risk Score: {att['risk']}"]
        lines += [f"      * {x}" for x in att["reasons"]]
    else:
        lines.append("  No attachment uploaded.")
    lines += ["", "=" * 52]
    return "\n".join(lines)

# ==============================================================================
# DEMO SAMPLES & STATE
# ==============================================================================
DEMO_SAFE = (
    "Hi team,\n\n"
    "This is a quick reminder that our quarterly project review meeting is on Friday at 3 PM "
    "in Conference Room 2. Please bring your team progress updates and slide deck.\n\n"
    "Thanks,\n"
    "Project Coordinator"
)

DEMO_SUSPICIOUS = (
    "Dear Valued Customer,\n\n"
    "Security alert: your bank account has been suspended due to unauthorized login attempts. "
    "Urgent action required! Please click here to verify your account and confirm your identity:\n"
    "http://secure-online-ebanking.xyz/login\nhttp://192.168.1.105/update\n\n"
    "You have also won a free gift prize. Claim your bonus immediately!"
)

if "email_text" not in st.session_state:
    st.session_state.email_text = ""
if "result" not in st.session_state:
    st.session_state.result = None
if "history" not in st.session_state:
    st.session_state.history = []

PAGES = ["🏠 Home", "🔍 Analyze", "📊 Result", "ℹ️ About"]
if "page" not in st.session_state:
    st.session_state.page = PAGES[0]

def go(p):
    st.session_state.page = p

def load_demo(txt):
    st.session_state.email_text = txt
    st.session_state.result = None

def clear_all():
    st.session_state.email_text = ""
    st.session_state.result = None

def on_nav():
    st.session_state.page = st.session_state.nav_choice

def section(title, desc=""):
    render_html(f'<div class="sec">{title}</div><div class="secd">{desc}</div>')

# ==============================================================================
# PAGE 1: HOME
# ==============================================================================
def page_home():
    hist = st.session_state.history
    threats = sum(1 for h in hist if h["level"] != "LOW")
    last = st.session_state.result

    render_html("""
    <div class="card" style="padding: 28px; margin-bottom: 20px; background: linear-gradient(135deg, rgba(99, 102, 241, 0.12), rgba(30, 41, 59, 0.85));">
        <span class="badge b-ok">● ML Model Online</span>
        <h1 style="font-size: 2rem; font-weight: 800; color: #ffffff; margin: 12px 0 8px;">
            Email Threat & Spam Detection System
        </h1>
        <p style="color: #cbd5e1; font-size: 1rem; max-width: 760px; line-height: 1.5; margin: 0;">
            A simple, fast, and reliable tool to inspect emails for spam, phishing keywords, malicious links, 
            and risky attachments using Machine Learning and heuristic rules.
        </p>
    </div>
    """)

    c1, c2, _ = st.columns([1.2, 1.2, 2])
    c1.button("🔍 Start Email Analysis", type="primary", on_click=go, args=(PAGES[1],), **STRETCH)
    c2.button("📊 View Last Result", on_click=go, args=(PAGES[2],), disabled=last is None, **STRETCH)

    section("Core Security Checks", "Four automated checks run on every message:")
    cols = st.columns(4)
    modules = [
        ("📧", "Spam Detection", "Multinomial Naive Bayes classifier trained with TF-IDF features."),
        ("🎣", "Phishing Radar", "Detects urgent credential and banking phishing phrases."),
        ("🌐", "URL Inspector", "Flags suspicious domains, risky endings (.xyz, .top), and raw IPs."),
        ("📎", "Attachment Check", "Screens filenames for executable or double extensions (.pdf.exe)."),
    ]
    for col, (ic, t, d) in zip(cols, modules):
        col.markdown(card(ic, t, d), unsafe_allow_html=True)

    section("How It Works")
    step_cols = st.columns(4)
    steps = [
        ("1. Enter Message", "Paste any email text and optionally attach a file."),
        ("2. Instant Scan", "ML classifier and rule-based heuristics analyze the content."),
        ("3. Review Score", "Get a clear 0-100 threat score with plain explanations."),
        ("4. Save Report", "Download a formatted text audit report for your records.")
    ]
    for col, (t, d) in zip(step_cols, steps):
        col.markdown(f'<div class="card"><div class="t">{t}</div><div class="d">{d}</div></div>', unsafe_allow_html=True)

    section("Current Session Summary")
    m1, m2, m3 = st.columns(3)
    m1.markdown(metric("Total Scanned", str(len(hist)), "Emails checked this session", "ok"), unsafe_allow_html=True)
    m2.markdown(metric("Threats Flagged", str(threats), "Medium or high risk emails", "warn" if threats else "ok"), unsafe_allow_html=True)
    last_lvl = last["level"] if last else "—"
    tone = "ok" if last_lvl == "LOW" else "warn" if last_lvl == "MEDIUM" else "bad" if last else "ok"
    m3.markdown(metric("Last Result", last_lvl, "Most recent scan level", tone), unsafe_allow_html=True)

# ==============================================================================
# PAGE 2: ANALYZE
# ==============================================================================
def page_analyze():
    section("Analyze Email Content", "Paste an email below or click a sample to test the detector:")

    st.text_area(
        "Email Message",
        key="email_text",
        height=220,
        placeholder="Paste your email content here (e.g., subject line, message body, links)..."
    )

    b1, b2, b3 = st.columns(3)
    b1.button("📄 Load Safe Demo", on_click=load_demo, args=(DEMO_SAFE,), **STRETCH)
    b2.button("⚠️ Load Suspicious Demo", on_click=load_demo, args=(DEMO_SUSPICIOUS,), **STRETCH)
    b3.button("🗑️ Clear Text", on_click=clear_all, **STRETCH)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("📎 Upload Email Attachment (Optional)", type=None)
    st.caption("Heuristic filename scan for dangerous scripts (.exe, .bat, .vbs, .js) or double extensions.")

    if st.button("🔍 ANALYZE EMAIL NOW", type="primary", **STRETCH):
        msg = st.session_state.email_text
        if not msg.strip():
            st.warning("⚠️ Please enter email text or load a demo before analyzing.")
            return

        with st.spinner("Analyzing message..."):
            res = run_analysis(msg, uploaded_file)
            st.session_state.result = res
            st.session_state.report_message = msg
            st.session_state.history.insert(0, {
                "time": res["time"],
                "cls": "Spam" if res["pred"] == 1 else "Not Spam",
                "level": res["level"],
                "score": res["score"],
                "phish": res["phish_count"],
                "urls": len(res["urls"])
            })
            st.session_state.page = PAGES[2]
            st.rerun()

# ==============================================================================
# PAGE 3: RESULT
# ==============================================================================
def page_result():
    r = st.session_state.result
    if r is None:
        render_html("""
        <div class="card" style="text-align: center; padding: 40px 20px;">
            <div style="font-size: 3rem; margin-bottom: 8px;">🛡️</div>
            <h3 style="color:#ffffff; margin: 4px 0;">No Result Yet</h3>
            <p style="color:#94a3b8; font-size: 0.95rem;">Please analyze an email first to see the threat report.</p>
        </div>
        """)
        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
        st.button("🔍 Go to Analyze Page", type="primary", on_click=go, args=(PAGES[1],))
        return

    att = r["attachment"]
    att_text, att_tone, att_sub = attachment_label(att)
    spam_tone = "bad" if r["spam_prob"] >= 50 else "warn" if r["spam_prob"] >= 25 else "ok"
    phish_tone = "bad" if r["phish_count"] >= 3 else "warn" if r["phish_count"] else "ok"
    flagged = [u for u in r["urls"] if u["score"] > 0]

    # Overall Status Banner
    cls, icon, title = status_for(r["level"])
    color = LEVEL_COLOR[r["level"]]
    why_text = ("This email was rated " + r["level"] + " risk because " + "; ".join(r["why"]) + "."
                if r["why"] else "No spam classification, phishing phrases, suspicious URLs, or risky attachment patterns were found.")

    section("Threat Assessment Result")
    status_html = (
        f'<div class="status {cls}">'
        f'{gauge_svg(r["score"], color)}'
        f'<div class="sbody">'
        f'<div class="l" style="color: {color}; font-weight:700;">Overall Threat Level: {r["level"]}</div>'
        f'<h2>{icon} {title}</h2>'
        f'<p>{esc(why_text)}</p>'
        f'{level_scale(r["score"])}'
        f'</div>'
        f'</div>'
    )
    render_html(status_html)

    # 4 Key Metrics
    section("Security Vectors Overview")
    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(metric("Spam Risk", f"{r['spam_prob']:.1f}%", "ML spam probability", spam_tone), unsafe_allow_html=True)
    m2.markdown(metric("Phishing Phrases", f"{r['phish_count']} Found", "Known attack keywords", phish_tone), unsafe_allow_html=True)
    m3.markdown(metric("URLs Detected", str(len(r["urls"])), f"{len(flagged)} flagged risky", "warn" if flagged else "ok"), unsafe_allow_html=True)
    m4.markdown(metric("Attachment Risk", att_text, att_sub, att_tone), unsafe_allow_html=True)

    # Breakdown Columns
    col_left, col_right = st.columns(2)

    with col_left:
        section("📨 Spam Classification")
        verdict_badge = '<span class="badge b-bad">🚨 Spam</span>' if r["pred"] == 1 else '<span class="badge b-ok">✅ Not Spam</span>'
        spam_card_html = (
            f'<div class="card">'
            f'<div class="l">Model Verdict</div>'
            f'<div style="margin: 6px 0 14px;">{verdict_badge}</div>'
            f'{bar("Spam Probability", r["spam_prob"], "#ef4444")}'
            f'{bar("Safe Probability", r["safe_prob"], "#10b981")}'
            f'</div>'
        )
        render_html(spam_card_html)

    with col_right:
        section("🎣 Phishing Indicator Analysis")
        if r["phish_count"]:
            items = "".join(f"<li class='mono'>{esc(k)}</li>" for k in r["phish_found"])
            phish_body = (
                f'<span class="badge b-bad">⚠️ {r["phish_count"]} phishing phrase(s) matched</span>'
                f'<div class="l" style="margin-top: 12px;">Detected phrases:</div>'
                f'<ul style="color:#f87171;margin-top:6px;">{items}</ul>'
            )
        else:
            phish_body = '<span class="badge b-ok">✅ No predefined phishing phrases found</span><div class="rs" style="margin-top:10px;">The email text does not match common credential harvesting patterns.</div>'
        
        phish_card_html = f'<div class="card"><div class="l">Phishing Check</div><div style="margin-top:8px;">{phish_body}</div></div>'
        render_html(phish_card_html)

    # URL Inspection
    section("🌐 Embedded URLs & Links")
    if r["urls"]:
        rows = ""
        for u in r["urls"]:
            reasons = "".join(f"<div class='rs'>• {esc(x)}</div>" for x in u["reasons"]) if u["reasons"] else "<span style='color:#10b981;'>Clean URL</span>"
            rows += f"<tr><td class='mono'>{esc(u['url'])}</td><td><b>{u['score']}</b></td><td>{url_badge(u['score'])}</td><td>{reasons}</td></tr>"
        url_card_html = (
            f'<div class="card">'
            f'<div class="l">Total Links: <b>{len(r["urls"])}</b></div>'
            f'<div class="tw">'
            f'<table class="tbl">'
            f'<tr><th>URL</th><th>Score</th><th>Status</th><th>Heuristic Reasons</th></tr>'
            f'{rows}'
            f'</table>'
            f'</div>'
            f'</div>'
        )
        render_html(url_card_html)
    else:
        render_html('<div class="card"><span class="badge b-ok">✅ No URLs found in this email</span></div>')

    # Attachment Inspection
    section("📎 Attachment Check")
    if att:
        badge = '<span class="badge b-bad">🔴 High Risk Attachment</span>' if att["risk"] >= 50 else '<span class="badge b-warn">🟡 Suspicious Extension</span>' if att["risk"] > 0 else '<span class="badge b-ok">🟢 Clean Extension</span>'
        reasons = "".join(f"<div class='rs'>• {esc(x)}</div>" for x in att["reasons"]) if att["reasons"] else "No suspicious pattern detected."
        att_card_html = (
            f'<div class="card">'
            f'{badge}'
            f'<div class="tw">'
            f'<table class="tbl" style="margin-top: 10px;">'
            f'<tr><th>Filename</th><th>Extension</th><th>Risk Score</th></tr>'
            f'<tr><td class="mono">{esc(att["name"])}</td><td class="mono">{esc(att["ext"])}</td><td><b>{att["risk"]}</b></td></tr>'
            f'</table>'
            f'</div>'
            f'<div style="margin-top: 8px;">{reasons}</div>'
            f'</div>'
        )
        render_html(att_card_html)
    else:
        render_html('<div class="card"><span class="badge b-ok">ℹ️ No attachment was uploaded</span></div>')

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # Action Buttons
    c_btn1, c_btn2 = st.columns([1, 1])
    with c_btn1:
        st.download_button(
            "⬇️ Download Audit Report (.txt)",
            data=build_report_text(r, st.session_state.get("report_message", "")),
            file_name=f"threat_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            **STRETCH
        )
    with c_btn2:
        st.button("🔄 Analyze Another Email", on_click=go, args=(PAGES[1],), **STRETCH)

    # Scan History
    hist = st.session_state.history
    if hist:
        section("Recent Scans This Session")
        rows = "".join(
            f"<tr><td>{esc(h['time'])}</td><td>{h['cls']}</td><td>{h['phish']}</td><td>{h['urls']}</td>"
            f"<td><b>{h['score']}</b></td><td><span class='badge b-{'ok' if h['level']=='LOW' else 'warn' if h['level']=='MEDIUM' else 'bad'}'>{h['level']}</span></td></tr>"
            for h in hist[:8]
        )
        history_card_html = (
            f'<div class="card">'
            f'<div class="tw">'
            f'<table class="tbl">'
            f'<tr><th>Time</th><th>Spam Verdict</th><th>Phishing Matches</th><th>URLs</th><th>Score</th><th>Level</th></tr>'
            f'{rows}'
            f'</table>'
            f'</div>'
            f'</div>'
        )
        render_html(history_card_html)

# ==============================================================================
# PAGE 4: ABOUT
# ==============================================================================
def page_about():
    render_html("""
    <div class="card" style="padding: 24px; margin-bottom: 20px;">
        <h2 style="color: #ffffff; margin: 0 0 8px;">About This System</h2>
        <p style="color: #cbd5e1; line-height: 1.5; margin: 0;">
            This application is an educational cybersecurity prototype combining a Machine Learning spam classifier 
            with rule-based heuristic checks for phishing phrases, malicious URLs, and suspicious attachments.
        </p>
    </div>
    """)

    section("Machine Learning & Heuristic Pipeline")
    cols = st.columns(4)
    info_cards = [
        ("1. Preprocessing", "NLTK lowercasing, punctuation removal, stopword filtering, and Porter stemming."),
        ("2. TF-IDF Features", "Converts processed text into term-frequency inverse document frequency vectors."),
        ("3. Naive Bayes", "Multinomial Naive Bayes predicts class probabilities (Ham vs. Spam)."),
        ("4. Threat Scoring", "Combines ML prediction with phishing, URL, and attachment heuristics (0-100 score).")
    ]
    for col, (t, d) in zip(cols, info_cards):
        col.markdown(f'<div class="card"><div class="t">{t}</div><div class="d">{d}</div></div>', unsafe_allow_html=True)

    left, right = st.columns(2)
    with left:
        section("Dataset & Model Specifications")
        render_html("""
        <div class="card">
            <ul style="color: #cbd5e1; line-height: 1.8; margin: 0; padding-left: 20px;">
                <li><b>Dataset:</b> SMS & Email Spam Collection (5,572 rows)</li>
                <li><b>Distribution:</b> 4,825 Ham (86.6%) / 747 Spam (13.4%)</li>
                <li><b>Algorithm:</b> Multinomial Naive Bayes (Laplace smoothing α=1.0)</li>
                <li><b>Evaluation:</b> 80/20 stratified split, ~98% accuracy</li>
            </ul>
        </div>
        """)

    with right:
        section("Educational Limitations")
        render_html("""
        <div class="card">
            <ul style="color: #cbd5e1; line-height: 1.8; margin: 0; padding-left: 20px;">
                <li>URL checks use pattern heuristics (no live DNS reputation query).</li>
                <li>Attachments are evaluated by file extension only (no sandbox execution).</li>
                <li>Designed as an educational project, not commercial enterprise software.</li>
            </ul>
        </div>
        """)

# ==============================================================================
# SIDEBAR
# ==============================================================================
with st.sidebar:
    st.markdown("### 🛡️ System Telemetry")
    for k, v in [
        ("Status", "● Online"),
        ("Classifier", "Multinomial NB"),
        ("Features", "TF-IDF (7,118 vocab)"),
        ("Dataset", "5,572 Messages"),
        ("Scans Run", str(len(st.session_state.history)))
    ]:
        render_html(f'<div class="side-item"><span>{k}</span><span>{v}</span></div>')

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    if st.button("🗑️ Reset All Data", **STRETCH):
        clear_all()
        st.session_state.history = []
        st.rerun()

    st.markdown("---")
    st.caption("Email Threat Detection System &bull; Machine Learning + Heuristic Cyber Defense Prototype")

# ==============================================================================
# HEADER + TOP NAVIGATION BAR
# ==============================================================================
render_html("""
<div class="hero">
    <div>
        <h1>🛡️ Email Threat Detection System</h1>
        <div class="sub">AI spam classification with phishing, URL, and attachment security checks</div>
    </div>
    <div class="pills">
        <span class="pill"><span class="dot-online"></span>Model Active</span>
        <span class="pill">TF-IDF + Naive Bayes</span>
    </div>
</div>
""")

st.session_state.nav_choice = st.session_state.page
st.radio("Navigation", PAGES, horizontal=True, key="nav_choice", on_change=on_nav, label_visibility="collapsed")

# Page Routing
page_map = {
    PAGES[0]: page_home,
    PAGES[1]: page_analyze,
    PAGES[2]: page_result,
    PAGES[3]: page_about
}
page_map[st.session_state.page]()

# ==============================================================================
# FOOTER
# ==============================================================================
render_html("""
<div class="foot">
    <b>Email Threat & Spam Detection System</b> &bull; Simple, Fast & Easy to Use<br>
    Machine Learning + Cybersecurity Project
</div>
""")
