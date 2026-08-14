const chatBox = document.getElementById("chat-box");
const input = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const typingEl = document.getElementById("typing");
let requestInFlight = false;

// Django CSRF token: prefer the <meta> tag, fall back to the cookie.
function getCsrfToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  if (meta && meta.content) return meta.content;
  const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : "";
}

function addMessage(content, role) {
  const div = document.createElement("div");
  div.className = `message ${role}`;
  div.textContent = content;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function setTyping(isTyping) {
  if (!typingEl) return;
  typingEl.classList.toggle("is-hidden", !isTyping);
}

function setRequestInFlight(isInFlight) {
  requestInFlight = isInFlight;
  input.disabled = isInFlight;
  sendBtn.disabled = isInFlight;
  setTyping(isInFlight);
}

async function sendMessage() {
  if (requestInFlight) return;

  const text = input.value.trim();
  if (!text) return;

  addMessage(text, "user");
  input.value = "";
  setRequestInFlight(true);

  try {
    const res = await fetch("/api/chat/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken(),
      },
      body: JSON.stringify({ message: text }),
    });

    if (!res.ok) {
      const errText = await res.text().catch(() => "");
      addMessage(
        `Server error (${res.status}). ${errText || "Please try again."}`,
        "bot"
      );
      return;
    }

    const data = await res.json();
    addMessage(data.answer || "Sorry, I could not find an answer.", "bot");
  } catch (err) {
    console.error(err);
    addMessage(
      "❌ Connection error. Please check the server and try again.",
      "bot"
    );
  } finally {
    setRequestInFlight(false);
    input.focus();
  }
}

sendBtn.addEventListener("click", sendMessage);
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendMessage();
});
