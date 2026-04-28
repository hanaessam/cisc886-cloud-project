#!/usr/bin/env python3
"""
GlowBot — Beauty AI Assistant
CISC 886 Cloud Computing · Queen's University
"""

import streamlit as st
import urllib.request
import json

st.set_page_config(
    page_title="GlowBot",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="expanded"
)

MODEL_NAME  = "cisc886-chatbot:latest"
OLLAMA_URL  = "http://127.0.0.1:11434/api/generate"
NUM_PREDICT = 200

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@700;900&display=swap');

:root {
  --hot:    #E91E8C;
  --deep:   #C2185B;
  --light:  #F48FB1;
  --soft:   #FDE8F2;
  --soft2:  #FFF5FA;
  --muted:  #9E7A8A;
  --text:   #2A1520;
  --white:  #FFFFFF;
  --grad:   linear-gradient(135deg, #F48FB1 0%, #E91E8C 100%);
  --border: rgba(233,30,140,0.15);
  --sh-s:   0 4px 16px rgba(194,24,91,0.11);
  --sh-m:   0 8px 28px rgba(194,24,91,0.15);
}

*, *::before, *::after { box-sizing: border-box; }
html, body { font-family: 'DM Sans', sans-serif; color: var(--text); background: var(--white); }

/* ── Animated floating icons background ── */
[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(ellipse 52% 42% at 6%  8%,  rgba(244,143,177,0.13) 0%, transparent 68%),
    radial-gradient(ellipse 42% 36% at 94% 82%, rgba(233,30,140,0.07) 0%, transparent 68%),
    radial-gradient(ellipse 28% 24% at 52% 48%, rgba(253,232,242,0.28) 0%, transparent 68%),
    #ffffff;
}

[data-testid="stAppViewContainer"]::before {
  content: "💄  ✨  🌸  💅  🌹  💆  🪞  💋  🌷  ✦  🧴  🧖";
  position: fixed; inset: 0;
  font-size: 30px;
  line-height: 5;
  letter-spacing: 56px;
  word-spacing: 56px;
  opacity: 0.07;
  pointer-events: none;
  z-index: 0;
  color: var(--hot);
  animation: floatBg 22s ease-in-out infinite alternate;
  padding: 30px;
  overflow: hidden;
}

@keyframes floatBg {
  0%   { transform: translateY(0px)   rotate(0deg)    scale(1);    opacity: 0.055; }
  40%  { transform: translateY(-20px) rotate(1.2deg)  scale(1.02); opacity: 0.085; }
  75%  { transform: translateY(-9px)  rotate(-0.7deg) scale(0.99); opacity: 0.07;  }
  100% { transform: translateY(5px)   rotate(-1.4deg) scale(1.01); opacity: 0.06;  }
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
  background: linear-gradient(174deg, var(--soft2) 0%, var(--soft) 45%, var(--soft2) 100%) !important;
  border-right: 1.5px solid var(--border) !important;
  box-shadow: 3px 0 20px rgba(194,24,91,0.06) !important;
}

section[data-testid="stSidebar"] > div {
  padding: 22px 18px 24px !important;
}

section[data-testid="stSidebar"] * {
  font-family: 'DM Sans', sans-serif !important;
}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] li,
section[data-testid="stSidebar"] small {
  color: var(--muted) !important;
}

section[data-testid="stSidebar"] strong,
section[data-testid="stSidebar"] b,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
  color: var(--deep) !important;
}

section[data-testid="stSidebar"] hr {
  border-color: var(--border) !important;
  margin: 14px 0 !important;
}

/* All sidebar buttons */
section[data-testid="stSidebar"] .stButton button {
  width: 100% !important;
  background: rgba(255,255,255,0.75) !important;
  color: var(--deep) !important;
  border: 1.5px solid var(--border) !important;
  border-radius: 13px !important;
  font-size: 13.5px !important;
  font-weight: 600 !important;
  padding: 0.52rem 1rem !important;
  text-align: left !important;
  transition: all 0.15s ease !important;
  box-shadow: var(--sh-s) !important;
  margin-bottom: 4px !important;
}

section[data-testid="stSidebar"] .stButton button:hover {
  background: var(--grad) !important;
  color: var(--white) !important;
  border-color: transparent !important;
  box-shadow: var(--sh-m) !important;
  transform: translateX(4px) !important;
}

/* ── Main area ── */
[data-testid="stMain"] { background: transparent !important; }

.block-container {
  padding-top: 1.4rem !important;
  padding-bottom: 0.5rem !important;
  max-width: 820px !important;
}

#MainMenu, footer, header, [data-testid="stToolbar"] { display: none !important; }

/* ── Chat bubbles ── */
[data-testid="stChatMessage"] {
  border-radius: 20px !important;
  padding: 4px 6px !important;
  margin-bottom: 8px !important;
  animation: msgIn 0.24s cubic-bezier(0.22,1,0.36,1) both;
}

@keyframes msgIn {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
  background: rgba(255,255,255,0.97) !important;
  border: 1.5px solid var(--border) !important;
  box-shadow: var(--sh-s) !important;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
  background: var(--grad) !important;
  border: none !important;
  box-shadow: var(--sh-m) !important;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) p,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) * {
  color: var(--white) !important;
}

[data-testid="stChatMessage"] p {
  font-size: 15px !important;
  line-height: 1.74 !important;
}

[data-testid="chatAvatarIcon-assistant"] {
  background: var(--grad) !important;
  border-radius: 50% !important;
}
[data-testid="chatAvatarIcon-user"] {
  background: var(--deep) !important;
  border-radius: 50% !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
  border-radius: 26px !important;
  border: 1.5px solid rgba(233,30,140,0.22) !important;
  background: rgba(255,255,255,0.98) !important;
  box-shadow: var(--sh-m) !important;
}

[data-testid="stChatInput"]:focus-within {
  border-color: var(--hot) !important;
  box-shadow: 0 0 0 3px rgba(233,30,140,0.09), var(--sh-m) !important;
}

[data-testid="stChatInput"] textarea {
  font-family: 'DM Sans', sans-serif !important;
  font-size: 15px !important;
  color: var(--text) !important;
}

[data-testid="stChatInput"] textarea::placeholder { color: #C4A0B2 !important; }

[data-testid="stChatInput"] button {
  background: var(--grad) !important;
  border-radius: 50% !important;
  border: none !important;
  box-shadow: 0 4px 14px rgba(233,30,140,0.30) !important;
  transition: transform 0.15s ease, box-shadow 0.15s ease !important;
}

[data-testid="stChatInput"] button:hover {
  transform: scale(1.1) !important;
  box-shadow: 0 6px 20px rgba(233,30,140,0.40) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(233,30,140,0.20); border-radius: 99px; }

/* ── Custom HTML components ── */
.sb-brand { display:flex; align-items:center; gap:12px; margin-bottom:18px; }
.sb-icon {
  width:42px; height:42px; border-radius:13px;
  background:var(--grad); display:grid; place-items:center;
  font-size:21px; box-shadow:0 7px 18px rgba(233,30,140,0.30); flex-shrink:0;
}
.sb-title {
  font-family:'Playfair Display',serif !important;
  font-size:21px !important; font-weight:900 !important;
  color:var(--deep) !important; line-height:1 !important;
}
.sb-subtitle { font-size:11px !important; color:var(--muted) !important; margin-top:2px; }

.model-badge {
  display:flex; align-items:center; gap:10px;
  background:rgba(255,255,255,0.80); border:1.5px solid var(--border);
  border-radius:13px; padding:10px 13px; margin-bottom:16px;
}
.badge-dot {
  width:9px; height:9px; background:#22c55e; border-radius:50%;
  box-shadow:0 0 0 4px rgba(34,197,94,0.16); flex-shrink:0;
}
.badge-name { font-size:12px !important; font-weight:700 !important; color:var(--deep) !important; display:block; }
.badge-sub  { font-size:10.5px !important; color:var(--muted) !important; display:block; margin-top:1px; }

.sb-label {
  display:block; font-size:10px !important; font-weight:700 !important;
  color:var(--deep) !important; text-transform:uppercase !important;
  letter-spacing:0.09em !important; margin:16px 0 8px !important;
}

.sb-footer {
  text-align:center; padding-top:14px;
  border-top:1.5px solid var(--border); margin-top:8px;
}
.sb-footer p { font-size:11px !important; color:var(--muted) !important; line-height:1.7 !important; }

.topbar {
  display:flex; align-items:center; justify-content:space-between;
  padding-bottom:16px; border-bottom:1.5px solid var(--border); margin-bottom:22px;
}
.topbar h1 {
  font-family:'Playfair Display',serif; font-size:25px; font-weight:900;
  color:var(--deep); line-height:1; margin:0;
}
.topbar p { margin:5px 0 0; font-size:12.5px; color:var(--muted); display:flex; align-items:center; gap:6px; }
.gdot { width:8px; height:8px; background:#22c55e; border-radius:50%; display:inline-block; }
.topbar-av {
  width:38px; height:38px; background:var(--grad); border-radius:50%;
  display:grid; place-items:center; color:var(--white);
  font-weight:700; font-size:13px; box-shadow:0 5px 14px rgba(233,30,140,0.25);
}

.welcome { text-align:center; padding:32px 16px 20px; max-width:340px; margin:0 auto; }
.bag-wrap { filter:drop-shadow(0 10px 20px rgba(194,24,91,0.20)); margin-bottom:18px; display:inline-block; }
.bag-handle {
  width:62px; height:29px; border:7px solid rgba(244,143,177,0.84);
  border-bottom:0; border-radius:50px 50px 0 0; margin:0 auto -4px; background:transparent;
}
.bag-body {
  background:var(--grad); border:2px solid rgba(194,24,91,0.12);
  border-radius:24px 24px 18px 18px; padding:15px 22px 18px;
  position:relative; overflow:hidden;
}
.bag-body::before {
  content:""; position:absolute; top:8px; left:50%;
  width:34px; height:5px; transform:translateX(-50%);
  border-radius:99px; background:rgba(255,255,255,0.48);
}
.bag-icons { font-size:16px; margin-bottom:5px; }
.bag-title {
  font-family:'Playfair Display',serif; font-size:clamp(26px,5.5vw,42px);
  font-weight:900; color:var(--white); text-shadow:0 3px 10px rgba(194,24,91,0.26); line-height:1;
}
.bag-sub { font-size:12px; font-weight:600; color:rgba(255,255,255,0.86); margin-top:5px; }
.welcome-hint { font-size:13.5px; color:var(--muted); line-height:1.65; margin-top:16px; }
.disclaimer { text-align:center; font-size:11.5px; color:#C4A0B2; margin-top:10px; padding-bottom:4px; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "messages"       not in st.session_state: st.session_state.messages       = []
if "pending_prompt" not in st.session_state: st.session_state.pending_prompt = None

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class="sb-brand">
        <div class="sb-icon">💄</div>
        <div>
            <div class="sb-title">GlowBot</div>
            <div class="sb-subtitle">Beauty AI Assistant</div>
        </div>
    </div>
    <div class="model-badge">
        <div class="badge-dot"></div>
        <div style="overflow:hidden;min-width:0;">
            <span class="badge-name">{MODEL_NAME}</span>
            <span class="badge-sub">Fine-tuned · online</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("＋  New chat", key="new_chat"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("<span class='sb-label'>Try asking</span>", unsafe_allow_html=True)

    examples = [
        "💧 Best moisturizer for dry skin?",
        "🔬 CeraVe vs Neutrogena?",
        "🚫 Ingredients to avoid?",
        "✨ Skincare routine for oily skin",
        "💰 Best budget-friendly serums?",
    ]
    for ex in examples:
        if st.button(ex, key=f"ex_{ex[:18]}"):
            st.session_state.pending_prompt = ex
            st.rerun()

    st.markdown("""
    <div class="sb-footer">
        <p>CISC 886 · Cloud Computing<br>Queen's University 🌸</p>
    </div>
    """, unsafe_allow_html=True)

# ── Top header ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="topbar">
    <div>
        <h1>GlowBot 💄</h1>
        <p><span class="gdot"></span>{MODEL_NAME} &nbsp;·&nbsp; Fine-tuned on Amazon Beauty Reviews</p>
    </div>
    <div class="topbar-av">GB</div>
</div>
""", unsafe_allow_html=True)

# ── Welcome screen ─────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome">
        <div class="bag-wrap">
            <div class="bag-handle"></div>
            <div class="bag-body">
                <div class="bag-icons">💄 ✨ 🌸</div>
                <div class="bag-title">GlowBot</div>
                <div class="bag-sub">Your Beauty AI Assistant</div>
            </div>
        </div>
        <p class="welcome-hint">
            Ask me anything about skincare, makeup,<br>
            haircare, or beauty products.<br>
            Powered by real Amazon reviews 🌸
        </p>
    </div>
    """, unsafe_allow_html=True)

# ── Chat history ───────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="💄" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])

# ── Streaming Ollama ───────────────────────────────────────────────────────────
def stream_ollama(prompt: str):
    body = json.dumps({
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": True,
        "options": {"num_predict": NUM_PREDICT, "temperature": 0.7, "repeat_penalty": 1.1}
    }).encode()
    req = urllib.request.Request(
        OLLAMA_URL, data=body,
        headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        for line in resp:
            if line.strip():
                try:
                    chunk = json.loads(line.decode())
                    token = chunk.get("response", "")
                    if token: yield token
                    if chunk.get("done"): break
                except Exception:
                    continue

# ── Handle prompt ──────────────────────────────────────────────────────────────
def handle_prompt(user_text: str):
    clean = user_text.lstrip("💧🔬🚫✨💰 ")
    st.session_state.messages.append({"role": "user", "content": clean})
    with st.chat_message("user", avatar="👤"):
        st.markdown(clean)
    with st.chat_message("assistant", avatar="💄"):
        try:
            full_reply = st.write_stream(stream_ollama(clean))
        except Exception as e:
            full_reply = f"Sorry, I couldn't reach the model right now. 🌸\n\n`{e}`"
            st.markdown(full_reply)
    st.session_state.messages.append({"role": "assistant", "content": full_reply})

# ── Pending prompt ─────────────────────────────────────────────────────────────
if st.session_state.pending_prompt:
    p = st.session_state.pending_prompt
    st.session_state.pending_prompt = None
    handle_prompt(p)
    st.rerun()

# ── Chat input ─────────────────────────────────────────────────────────────────
if user_input := st.chat_input("Message GlowBot..."):
    handle_prompt(user_input)
    st.rerun()

st.markdown('<p class="disclaimer">GlowBot can make mistakes. Consider checking important information.</p>', unsafe_allow_html=True)