const MODEL_NAME = "cisc886-chatbot:latest";
const API_URL = `${window.location.protocol}//${window.location.hostname}:11434/api/generate`;

const SYSTEM_PROMPT = `You are GlowBot, a warm and expert beauty advisor.
Specialize in skincare, makeup, haircare, fragrance, and wellness.
Use occasional beauty emojis 🌸💄✨.
Give specific, helpful, practical advice.`;

const sidebar = document.getElementById("sidebar");
const sidebarToggle = document.getElementById("sidebarToggle");
const collapseBtn = document.getElementById("collapseBtn");
const beautyBg = document.getElementById("beautyBg");
const chatArea = document.getElementById("chatArea");
const chatForm = document.getElementById("chatForm");
const userInput = document.getElementById("userInput");
const welcomeScreen = document.getElementById("welcomeScreen");
const newChatBtn = document.getElementById("newChatBtn");
const chatList = document.getElementById("chatList");
const modelTopName = document.getElementById("modelTopName");
const modelSideName = document.getElementById("modelSideName");

let conversation = [];
let typingRow = null;
let currentChatTitle = "";

modelTopName.textContent = MODEL_NAME;
modelSideName.textContent = MODEL_NAME;

const beautySvgs = [
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"><rect x="35" y="36" width="50" height="56" rx="8" fill="#F48FB1" stroke="#C2185B" stroke-width="4"/><rect x="48" y="22" width="24" height="18" rx="4" fill="#E91E8C" stroke="#C2185B" stroke-width="4"/><rect x="45" y="58" width="30" height="14" rx="4" fill="#FFFFFF" opacity=".75"/></svg>`,
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"><path d="M42 96h36v9H42z" fill="#E91E8C"/><path d="M48 86h24l8 10H40z" fill="#F48FB1" stroke="#C2185B" stroke-width="4"/><path d="M54 30h14v56H54z" fill="#E91E8C" stroke="#C2185B" stroke-width="4"/><path d="M54 30c4-16 18-16 14 0" fill="#FDE8F2" stroke="#C2185B" stroke-width="4"/></svg>`,
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"><path d="M34 42h42c17 0 30 13 30 29S93 100 76 100H34z" fill="#F48FB1" stroke="#C2185B" stroke-width="4"/><circle cx="64" cy="71" r="16" fill="#FDE8F2" stroke="#C2185B" stroke-width="4"/><rect x="14" y="55" width="22" height="34" rx="6" fill="#E91E8C" stroke="#C2185B" stroke-width="4"/></svg>`,
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"><circle cx="60" cy="66" r="34" fill="#F48FB1" stroke="#C2185B" stroke-width="4"/><circle cx="60" cy="66" r="23" fill="#FFFFFF" stroke="#C2185B" stroke-width="4"/><path d="M44 31l16-19 16 19z" fill="#8BE9F4" stroke="#C2185B" stroke-width="4"/></svg>`,
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"><path d="M22 78c30-33 60-45 77-36 10 6 4 20-12 20 16 6 18 22 2 28-22 8-48-4-67-12z" fill="#E91E8C" stroke="#C2185B" stroke-width="4"/></svg>`,
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"><ellipse cx="60" cy="62" rx="38" ry="26" fill="#FFFFFF" stroke="#C2185B" stroke-width="4"/><circle cx="60" cy="62" r="15" fill="#8BE9F4" stroke="#C2185B" stroke-width="4"/><circle cx="60" cy="62" r="6" fill="#C2185B"/><path d="M38 24v16M50 20v20M62 20v20M74 22v18" stroke="#C2185B" stroke-width="4" stroke-linecap="round"/></svg>`,
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"><circle cx="60" cy="60" r="36" fill="#BFEFF7" stroke="#C2185B" stroke-width="4"/><path d="M34 88h52" stroke="#E91E8C" stroke-width="8" stroke-linecap="round"/><path d="M42 78l36-36M48 54l12-12" stroke="#C2185B" stroke-width="4" stroke-linecap="round"/></svg>`,
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"><rect x="36" y="56" width="48" height="34" rx="4" fill="#F48FB1" stroke="#C2185B" stroke-width="4"/><path d="M48 56c0-20 24-20 24 0" fill="none" stroke="#C2185B" stroke-width="4"/><path d="M50 74h20" stroke="#C2185B" stroke-width="4" stroke-linecap="round"/></svg>`,
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"><circle cx="60" cy="60" r="28" fill="#FDE8F2" stroke="#C2185B" stroke-width="4"/><path d="M32 60c-12-18 8-34 20-18M88 60c12-18-8-34-20-18M44 36c0-16 32-16 32 0" fill="#F48FB1" stroke="#C2185B" stroke-width="4"/><circle cx="50" cy="62" r="7" fill="#A8E6B1" stroke="#C2185B" stroke-width="3"/><circle cx="70" cy="62" r="7" fill="#A8E6B1" stroke="#C2185B" stroke-width="3"/></svg>`,
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"><path d="M60 20l9 26 27 1-21 16 8 27-23-15-23 15 8-27-21-16 27-1z" fill="#FDE8F2" stroke="#E91E8C" stroke-width="5"/></svg>`,
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"><rect x="34" y="32" width="52" height="66" rx="12" fill="#FDE8F2" stroke="#C2185B" stroke-width="4"/><path d="M44 32c0-18 32-18 32 0" fill="none" stroke="#E91E8C" stroke-width="6"/><circle cx="50" cy="63" r="5" fill="#E91E8C"/><circle cx="70" cy="63" r="5" fill="#E91E8C"/><path d="M50 78c8 6 14 6 22 0" fill="none" stroke="#C2185B" stroke-width="4" stroke-linecap="round"/></svg>`,
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"><path d="M52 24h16v64H52z" fill="#F48FB1" stroke="#C2185B" stroke-width="4"/><path d="M35 90h50" stroke="#C2185B" stroke-width="6" stroke-linecap="round"/><path d="M38 48h44" stroke="#FFFFFF" stroke-width="8" stroke-linecap="round"/></svg>`
];

const svgToDataUri = (svg) => `url("data:image/svg+xml;utf8,${encodeURIComponent(svg)}")`;

const generateBeautyBackground = () => {
  beautyBg.innerHTML = "";
  const count = 36;
  const usedPositions = [];

  for (let i = 0; i < count; i += 1) {
    const icon = document.createElement("div");
    const size = Math.floor(Math.random() * 46) + 62;

    let top = 0;
    let left = 0;
    let isSafe = false;
    let attempts = 0;

    while (!isSafe && attempts < 100) {
      top = Math.random() * 88 + 3;
      left = Math.random() * 92 + 3;

      isSafe = usedPositions.every((pos) => {
        const dx = pos.left - left;
        const dy = pos.top - top;
        return Math.sqrt(dx * dx + dy * dy) > 12;
      });

      attempts += 1;
    }

    usedPositions.push({ top, left });

    const svg = beautySvgs[i % beautySvgs.length];
    const rotate = Math.floor(Math.random() * 36) - 18;
    const delay = Math.random() * 6;
    const duration = Math.random() * 5 + 8;

    icon.className = "beauty-icon";
    icon.style.width = `${size}px`;
    icon.style.height = `${size}px`;
    icon.style.top = `${top}%`;
    icon.style.left = `${left}%`;
    icon.style.backgroundImage = svgToDataUri(svg);
    icon.style.animationDelay = `${delay}s`;
    icon.style.animationDuration = `${duration}s`;
    icon.style.setProperty("--rotate", `${rotate}deg`);

    beautyBg.appendChild(icon);
  }
};

const autoResizeInput = () => {
  userInput.style.height = "auto";
  userInput.style.height = `${Math.min(userInput.scrollHeight, 170)}px`;
};

const formatTime = () => {
  return new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit"
  });
};

const hideWelcome = () => welcomeScreen.classList.add("hidden");
const showWelcome = () => welcomeScreen.classList.remove("hidden");

const updateChatTitle = (text) => {
  if (currentChatTitle) return;

  currentChatTitle = text.length > 34 ? `${text.slice(0, 34)}...` : text;
  chatList.classList.remove("empty");
  chatList.innerHTML = "";

  const item = document.createElement("button");
  item.className = "history-item active";
  item.innerHTML = `<span>▢</span><span>${currentChatTitle}</span><b>⋯</b>`;
  chatList.appendChild(item);
};

const buildPrompt = () => {
  const history = conversation
    .map((message) => `${message.role === "user" ? "User" : "GlowBot"}: ${message.text}`)
    .join("\n\n");

  return `${SYSTEM_PROMPT}

Conversation:
${history}

GlowBot:`;
};

const appendMessage = (role, text) => {
  hideWelcome();

  const row = document.createElement("div");
  row.className = `message-row ${role === "user" ? "user-row" : "bot-row"}`;

  const avatar = document.createElement("div");
  avatar.className = `avatar ${role === "user" ? "user-avatar-chat" : "bot-avatar"}`;
  avatar.textContent = role === "user" ? "You" : "GB";

  const content = document.createElement("div");
  content.className = "message-content";

  const bubble = document.createElement("div");
  bubble.className = "message-bubble";
  bubble.textContent = text;

  const meta = document.createElement("div");
  meta.className = "message-meta";
  meta.textContent = formatTime();

  content.appendChild(bubble);
  content.appendChild(meta);

  if (role === "user") {
    row.appendChild(content);
  } else {
    row.appendChild(avatar);
    row.appendChild(content);
  }

  chatArea.appendChild(row);
  chatArea.scrollTop = chatArea.scrollHeight;
};

const showTyping = () => {
  hideWelcome();

  typingRow = document.createElement("div");
  typingRow.className = "message-row bot-row";

  const avatar = document.createElement("div");
  avatar.className = "avatar bot-avatar";
  avatar.textContent = "GB";

  const content = document.createElement("div");
  content.className = "message-content";

  const bubble = document.createElement("div");
  bubble.className = "message-bubble";

  const dots = document.createElement("div");
  dots.className = "typing-dots";
  dots.innerHTML = "<span></span><span></span><span></span>";

  bubble.appendChild(dots);
  content.appendChild(bubble);
  typingRow.appendChild(avatar);
  typingRow.appendChild(content);

  chatArea.appendChild(typingRow);
  chatArea.scrollTop = chatArea.scrollHeight;
};

const hideTyping = () => {
  if (typingRow) {
    typingRow.remove();
    typingRow = null;
  }
};

const clearChat = () => {
  conversation = [];
  currentChatTitle = "";
  hideTyping();

  const messages = chatArea.querySelectorAll(".message-row");
  messages.forEach((message) => message.remove());

  chatList.classList.add("empty");
  chatList.innerHTML = `<p class="empty-chat">No chats yet. Start a new beauty chat ✨</p>`;

  showWelcome();
  chatArea.scrollTop = 0;
};

const sendMessage = async () => {
  const text = userInput.value.trim();
  if (!text) return;

  updateChatTitle(text);
  appendMessage("user", text);
  conversation.push({ role: "user", text });

  userInput.value = "";
  autoResizeInput();
  showTyping();

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model: MODEL_NAME,
        prompt: buildPrompt(),
        stream: false
      })
    });

    if (!response.ok) {
      throw new Error(`Ollama request failed with status ${response.status}`);
    }

    const data = await response.json();
    const reply = (data.response || "").trim() || "I could not generate a response right now 🌸";

    hideTyping();
    appendMessage("bot", reply);
    conversation.push({ role: "assistant", text: reply });
  } catch (error) {
    hideTyping();
    appendMessage(
      "bot",
      "Sorry, I could not connect to the model. Please check that Ollama is running and that the model name is correct ✨"
    );
  }
};

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  await sendMessage();
});

userInput.addEventListener("input", autoResizeInput);

userInput.addEventListener("keydown", async (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    await sendMessage();
  }
});

newChatBtn.addEventListener("click", clearChat);

const toggleSidebar = () => {
  sidebar.classList.toggle("collapsed");
  sidebarToggle.textContent = sidebar.classList.contains("collapsed") ? "›" : "‹";
};

sidebarToggle.addEventListener("click", toggleSidebar);
collapseBtn.addEventListener("click", toggleSidebar);

generateBeautyBackground();
autoResizeInput();