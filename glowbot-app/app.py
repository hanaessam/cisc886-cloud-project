#!/usr/bin/env python3
"""
GlowBot — Beauty AI Assistant
CISC 886 Cloud Computing · Queen's University
Streamlit frontend for cisc886-chatbot:latest via Ollama
"""

import streamlit as st
import urllib.request
import json
import random

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GlowBot 💄",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="expanded"
)

MODEL_NAME  = "cisc886-chatbot:latest"
OLLAMA_URL  = "http://127.0.0.1:11434/api/generate"
NUM_PREDICT = 200

# ── Full CSS — matches GlowBot palette exactly ────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,400;0,500;0,700;1,400&family=Playfair+Display:wght@700;900&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'DM Sans', sans-serif;
    background: #ffffff;
}

/* ── Floating beauty icons background ── */
[data-testid="stAppViewContainer"]::before {
    content: "💄  ✨  🌸  💅  🧴  💊  🌹  💆  🪞  💋  🧖  ✦";
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    font-size: 28px;
    line-height: 3.5;
    letter-spacing: 60px;
    word-spacing: 60px;
    opacity: 0.055;
    pointer-events: none;
    z-index: 0;
    color: #E91E8C;
    animation: bgFloat 20s ease-in-out infinite alternate;
    padding: 20px;
    overflow: hidden;
}

@keyframes bgFloat {
    0%   { transform: translateY(0px) rotate(0deg); opacity: 0.045; }
    50%  { transform: translateY(-18px) rotate(2deg); opacity: 0.07; }
    100% { transform: translateY(4px) rotate(-1deg); opacity: 0.055; }
}

/* ── Radial glow spots ── */
[data-testid="stMain"]::before {
    content: "";
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background:
        radial-gradient(ellipse 38% 32% at 15% 12%, rgba(244,143,177,0.18) 0%, transparent 70%),
        radial-gradient(ellipse 30% 28% at 88% 78%, rgba(233,30,140,0.10) 0%, transparent 70%),
        radial-gradient(ellipse 22% 20% at 60% 5%,  rgba(253,232,242,0.50) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #FFF7FB 0%, #FDE8F2 55%, #ffffff 100%) !important;
    border-right: 1px solid rgba(233,30,140,0.18) !important;
    box-shadow: 8px 0 32px rgba(194,24,91,0.08) !important;
}

section[data-testid="stSidebar"] > div {
    padding-top: 1.2rem;
}

/* ── Main content area ── */
[data-testid="stMain"] {
    background: transparent !important;
}

.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 1rem !important;
    max-width: 860px !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    border-radius: 22px !important;
    padding: 4px 8px !important;
    margin-bottom: 6px !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    animation: slideIn 0.28s cubic-bezier(.22,1,.36,1);
}

@keyframes slideIn {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* Bot bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: rgba(255,255,255,0.95) !important;
    border: 1px solid rgba(233,30,140,0.16) !important;
    box-shadow: 0 8px 28px rgba(194,24,91,0.10) !important;
}

/* User bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: linear-gradient(135deg, #F48FB1, #E91E8C) !important;
    border: none !important;
    box-shadow: 0 8px 28px rgba(233,30,140,0.28) !important;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) p,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) * {
    color: #ffffff !important;
}

/* Message text */
[data-testid="stChatMessage"] p {
    font-size: 15px !important;
    line-height: 1.72 !important;
    margin: 0 !important;
}

/* Avatars */
[data-testid="chatAvatarIcon-assistant"] {
    background: linear-gradient(135deg, #F48FB1, #E91E8C) !important;
    border-radius: 50% !important;
}

[data-testid="chatAvatarIcon-user"] {
    background: #C2185B !important;
    border-radius: 50% !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
    border-radius: 28px !important;
    border: 1.5px solid rgba(233,30,140,0.28) !important;
    background: rgba(255,255,255,0.96) !important;
    box-shadow: 0 12px 36px rgba(194,24,91,0.14) !important;
    padding: 4px 8px !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: #E91E8C !important;
    box-shadow: 0 0 0 3px rgba(233,30,140,0.12), 0 12px 36px rgba(194,24,91,0.18) !important;
}

[data-testid="stChatInput"] textarea {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 15px !important;
    color: #21151D !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #b28c9e !important;
}

/* Send button */
[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #F48FB1, #E91E8C) !important;
    border-radius: 50% !important;
    border: none !important;
    transition: transform 0.18s ease, box-shadow 0.18s ease !important;
}

[data-testid="stChatInput"] button:hover {
    transform: scale(1.1) !important;
    box-shadow: 0 6px 18px rgba(233,30,140,0.35) !important;
}

/* ── Sidebar buttons ── */
.stButton button {
    background: linear-gradient(135deg, rgba(244,143,177,0.22), rgba(233,30,140,0.14)) !important;
    color: #C2185B !important;
    border: 1px solid rgba(233,30,140,0.28) !important;
    border-radius: 16px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.18s ease !important;
    width: 100% !important;
}

.stButton button:hover {
    background: linear-gradient(135deg, #F48FB1, #E91E8C) !important;
    color: #ffffff !important;
    border-color: transparent !important;
    box-shadow: 0 6px 18px rgba(233,30,140,0.28) !important;
    transform: translateY(-1px) !important;
}

/* ── Markdown headings in sidebar ── */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #C2185B !important;
    font-family: 'Playfair Display', serif !important;
}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] li,
section[data-testid="stSidebar"] small {
    color: #7D6573 !important;
    font-size: 13px !important;
}

section[data-testid="stSidebar"] strong {
    color: #C2185B !important;
}

/* ── Dividers ── */
hr {
    border-color: rgba(233,30,140,0.15) !important;
    margin: 12px 0 !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] {
    color: #E91E8C !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: rgba(233,30,140,0.25);
    border-radius: 99px;
}

/* ── Example question chips ── */
.example-chip {
    display: inline-block;
    background: rgba(253,232,242,0.85);
    border: 1px solid rgba(233,30,140,0.22);
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 13px;
    color: #C2185B;
    margin: 3px 2px;
    cursor: pointer;
    transition: all 0.15s ease;
    font-family: 'DM Sans', sans-serif;
}

.example-chip:hover {
    background: linear-gradient(135deg, #F48FB1, #E91E8C);
    color: white;
    border-color: transparent;
}

/* ── Model status badge ── */
.model-badge {
    display: flex;
    align-items: center;
    gap: 10px;
    background: rgba(255,255,255,0.78);
    border: 1px solid rgba(233,30,140,0.18);
    border-radius: 16px;
    padding: 12px 14px;
    margin: 8px 0;
}

.model-badge-dot {
    width: 10px;
    height: 10px;
    background: #22c55e;
    border-radius: 50%;
    box-shadow: 0 0 0 4px rgba(34,197,94,0.15);
    flex-shrink: 0;
}

.model-badge-text strong {
    display: block;
    color: #C2185B !important;
    font-size: 13px;
    font-weight: 700;
}

.model-badge-text small {
    color: #7D6573 !important;
    font-size: 11px;
}

/* ── Welcome card ── */
.welcome-card {
    text-align: center;
    padding: 52px 32px 48px;
    margin: 20px auto;
    max-width: 540px;
}

.bag-wrap {
    filter: drop-shadow(0 18px 32px rgba(194,24,91,0.20));
    margin-bottom: 28px;
}

.bag-handle {
    width: 120px;
    height: 56px;
    border: 10px solid rgba(244,143,177,0.88);
    border-bottom: 0;
    border-radius: 80px 80px 0 0;
    margin: 0 auto -8px;
    background: transparent;
    position: relative;
    z-index: 1;
}

.bag-body {
    background: linear-gradient(135deg, #FDE8F2 0%, #F48FB1 55%, #E91E8C 120%);
    border: 3px solid rgba(194,24,91,0.18);
    border-radius: 42px 42px 30px 30px;
    padding: 32px 28px 36px;
    position: relative;
    overflow: hidden;
}

.bag-body::before {
    content: "";
    position: absolute;
    top: 14px; left: 50%;
    width: 60px; height: 10px;
    transform: translateX(-50%);
    border-radius: 999px;
    background: rgba(255,255,255,0.55);
}

.bag-icons { font-size: 26px; margin-bottom: 8px; }

.bag-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(44px, 8vw, 72px);
    font-weight: 900;
    color: #ffffff;
    text-shadow: 0 4px 14px rgba(194,24,91,0.26);
    margin: 0;
    line-height: 1;
}

.bag-sub {
    color: rgba(255,255,255,0.92);
    font-size: 18px;
    font-weight: 600;
    margin-top: 10px;
    text-shadow: 0 2px 8px rgba(194,24,91,0.20);
}

.welcome-hint {
    color: #7D6573;
    font-size: 15px;
    margin-top: 20px;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:4px;">
        <div style="width:40px;height:40px;border-radius:14px;background:linear-gradient(135deg,#F48FB1,#E91E8C);
                    display:grid;place-items:center;font-size:20px;box-shadow:0 8px 18px rgba(233,30,140,0.28);">💄</div>
        <span style="font-family:'Playfair Display',serif;font-size:22px;color:#C2185B;font-weight:700;">GlowBot</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Model status
    st.markdown(f"""
    <div class="model-badge">
        <div class="model-badge-dot"></div>
        <div class="model-badge-text">
            <strong>{MODEL_NAME}</strong>
            <small>Fine-tuned model · online</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # New chat button
    if st.button("＋  New chat", key="new_chat"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")

    # Example questions
    st.markdown("<p style='color:#C2185B;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px;'>Try asking</p>", unsafe_allow_html=True)

    examples = [
        "What moisturizer is best for dry skin?",
        "Compare CeraVe vs Neutrogena",
        "What ingredients should I avoid?",
        "Skincare routine for oily skin",
        "Best budget-friendly serums?",
    ]

    for ex in examples:
        if st.button(ex, key=f"ex_{ex[:20]}"):
            st.session_state.pending_prompt = ex
            st.rerun()

    st.markdown("---")

    # Footer
    st.markdown("""
    <div style="text-align:center;padding-top:8px;">
        <p style="color:#b28c9e;font-size:11px;line-height:1.6;margin:0;">
            CISC 886 · Cloud Computing<br>
            Queen's University<br>
            <span style="color:#E91E8C;">🌸</span>
        </p>
    </div>
    """, unsafe_allow_html=True)


# ── Session state ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 0 16px 0;
    border-bottom: 1px solid rgba(233,30,140,0.14);
    margin-bottom: 20px;
    position: relative;
    z-index: 2;
">
    <div>
        <h1 style="
            margin:0;
            font-family:'Playfair Display',serif;
            font-size:28px;
            font-weight:900;
            color:#C2185B;
            line-height:1;
        ">GlowBot <span style="font-size:16px;font-weight:400;font-family:'DM Sans',sans-serif;">⌄</span></h1>
        <p style="margin:4px 0 0;color:#7D6573;font-size:13px;display:flex;align-items:center;gap:6px;">
            <span style="width:8px;height:8px;background:#22c55e;border-radius:50%;display:inline-block;"></span>
            cisc886-chatbot:latest &nbsp;·&nbsp; Fine-tuned on Amazon Beauty Reviews
        </p>
    </div>
    <div style="
        width:40px;height:40px;
        background:linear-gradient(135deg,#F48FB1,#E91E8C);
        border-radius:50%;
        display:grid;place-items:center;
        color:white;font-weight:700;font-size:14px;
        box-shadow:0 6px 16px rgba(233,30,140,0.28);
    ">GB</div>
</div>
""", unsafe_allow_html=True)


# ── Welcome screen (shown when no messages) ────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-card">
        <div class="bag-wrap">
            <div class="bag-handle"></div>
            <div class="bag-body">
                <div class="bag-icons">💄 ✨ 🌸</div>
                <h2 class="bag-title">GlowBot</h2>
                <p class="bag-sub">Your Beauty AI Assistant</p>
            </div>
        </div>
        <p class="welcome-hint">
            Ask me anything about skincare, makeup, haircare,<br>
            or beauty products — powered by real Amazon reviews.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ── Chat history ───────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    avatar = "💄" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])


# ── Ollama call ────────────────────────────────────────────────────────────────
def call_ollama(prompt: str) -> str:
    body = json.dumps({
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": NUM_PREDICT,
            "temperature": 0.7,
            "repeat_penalty": 1.1,
        }
    }).encode()

    req = urllib.request.Request(
        OLLAMA_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read())

    return data.get("response", "").strip()


# ── Handle pending prompt from sidebar example buttons ────────────────────────
def handle_prompt(user_text: str):
    st.session_state.messages.append({"role": "user", "content": user_text})

    with st.chat_message("user", avatar="👤"):
        st.markdown(user_text)

    with st.chat_message("assistant", avatar="💄"):
        with st.spinner("GlowBot is thinking... 🌸"):
            try:
                reply = call_ollama(user_text)
            except Exception as e:
                reply = f"Sorry, I could not connect to the model. Please check that Ollama is running. 🌸\n\n`{e}`"

        st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})


if st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None
    handle_prompt(prompt)
    st.rerun()


# ── Chat input ─────────────────────────────────────────────────────────────────
if user_input := st.chat_input("Message GlowBot..."):
    handle_prompt(user_input)
    st.rerun()


# ── Disclaimer ────────────────────────────────────────────────────────────────
st.markdown("""
<p style="text-align:center;color:#b28c9e;font-size:12px;margin-top:12px;">
    GlowBot can make mistakes. Consider checking important information.
</p>
""", unsafe_allow_html=True)