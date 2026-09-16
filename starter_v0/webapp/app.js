"use strict";

const el = (id) => document.getElementById(id);

const els = {
  sidebar: el("sidebar"),
  sidebarToggle: el("sidebarToggle"),
  sidebarBackdrop: el("sidebarBackdrop"),
  badgeVersionText: el("badgeVersionText"),
  badgeProviderText: el("badgeProviderText"),
  inpProvider: el("inpProvider"),
  inpModel: el("inpModel"),
  inpVersion: el("inpVersion"),
  inpHistoryWindow: el("inpHistoryWindow"),
  inpMaxRounds: el("inpMaxRounds"),
  btnStart: el("btnStart"),
  infoTranscript: el("infoTranscript"),
  infoArtifact: el("infoArtifact"),
  infoTurns: el("infoTurns"),
  btnCopyTranscript: el("btnCopyTranscript"),
  messages: el("messages"),
  emptyState: el("emptyState"),
  typing: el("typing"),
  inpMessage: el("inpMessage"),
  btnSend: el("btnSend"),
};

const state = { sessionId: null, busy: false, transcriptPath: "" };

/* ---------- Tiện ích ---------- */

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = String(text ?? "");
  return div.innerHTML;
}

function prettyJson(value) {
  if (value === null || value === undefined) return "—";
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

function scrollBottom() {
  requestAnimationFrame(() => {
    els.messages.scrollTop = els.messages.scrollHeight;
  });
}

let toastTimer = null;
function toast(message) {
  let node = document.querySelector(".toast");
  if (!node) {
    node = document.createElement("div");
    node.className = "toast";
    document.body.appendChild(node);
  }
  node.textContent = message;
  node.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => node.classList.remove("show"), 2200);
}

async function api(path, body) {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body || {}),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.error || `Lỗi HTTP ${res.status}`);
  }
  return data;
}

/* ---------- Cập nhật thông tin phiên ---------- */

function updateSessionInfo(info) {
  state.sessionId = info.session_id;
  state.transcriptPath = info.transcript_path;
  els.badgeVersionText.textContent = info.artifact_version;
  els.badgeProviderText.textContent = `${info.provider} · ${info.model || "mặc định"}`;
  els.infoTranscript.textContent = info.transcript_id;
  els.infoTranscript.title = info.transcript_path;
  els.infoArtifact.textContent = info.artifact_version;
  els.infoTurns.textContent = String(info.turns);
  els.btnSend.disabled = false;
}

/* ---------- Render tin nhắn ---------- */

function appendUserMessage(text) {
  const msg = document.createElement("div");
  msg.className = "msg msg-user";
  msg.innerHTML = `
    <svg class="msg-avatar"><use href="#icon-user"/></svg>
    <div class="msg-content"><div class="msg-bubble">${escapeHtml(text)}</div></div>`;
  els.messages.appendChild(msg);
  scrollBottom();
}

function buildToolCard(event) {
  const result = event.result ?? {};
  const isError = result && typeof result === "object" && result.error !== undefined;

  const card = document.createElement("div");
  card.className = `tool-card${isError ? " is-error" : ""}`;

  const head = document.createElement("button");
  head.type = "button";
  head.className = "tool-head";
  head.innerHTML = `
    <svg class="ic ic-tool"><use href="#icon-tool"/></svg>
    <span class="tool-name">${escapeHtml(event.tool)}</span>
    <span class="tool-status">
      <svg class="ic"><use href="#icon-${isError ? "error" : "check"}"/></svg>
      ${isError ? "lỗi" : "thành công"}
    </span>
    <svg class="ic tool-chevron"><use href="#icon-chevron"/></svg>`;

  const body = document.createElement("div");
  body.className = "tool-body";
  const resultSection = isError ? "tool-section is-error" : "tool-section";
  body.innerHTML = `
    <div class="tool-section"><label>Đầu vào</label><pre>${escapeHtml(prettyJson(event.args))}</pre></div>
    <div class="${resultSection}"><label>${isError ? "Lỗi" : "Kết quả"}</label><pre>${escapeHtml(prettyJson(result))}</pre></div>`;

  head.addEventListener("click", () => card.classList.toggle("open"));
  card.appendChild(head);
  card.appendChild(body);
  return card;
}

function statusBadge(status) {
  const map = {
    waiting_for_user: ["icon-ask", "status-waiting", "Chờ bạn bổ sung thông tin"],
    max_tool_rounds: ["icon-error", "status-max-rounds", "Dừng vì vượt số vòng tool"],
    provider_error: ["icon-error", "status-error", "Lỗi provider"],
  };
  const conf = map[status];
  if (!conf) return null;
  const span = document.createElement("span");
  span.className = `msg-status ${conf[1]}`;
  span.innerHTML = `<svg class="ic"><use href="#${conf[0]}"/></svg>${conf[2]}`;
  return span;
}

function appendAgentTurn(turn) {
  const msg = document.createElement("div");
  msg.className = "msg msg-agent";
  const content = document.createElement("div");
  content.className = "msg-content";

  const avatar = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  avatar.setAttribute("class", "msg-avatar");
  const use = document.createElementNS("http://www.w3.org/2000/svg", "use");
  use.setAttribute("href", "#icon-mascot");
  avatar.appendChild(use);
  msg.appendChild(avatar);
  msg.appendChild(content);

  const toolEvents = turn.tool_events || [];
  if (toolEvents.length) {
    const stack = document.createElement("div");
    stack.className = "tool-stack";
    toolEvents.forEach((event) => stack.appendChild(buildToolCard(event)));
    content.appendChild(stack);
  }

  const badge = statusBadge(turn.status);
  if (badge) content.appendChild(badge);

  if (turn.error) {
    const box = document.createElement("div");
    box.className = "msg-error-box";
    box.textContent = turn.error;
    content.appendChild(box);
  }

  const bubble = document.createElement("div");
  bubble.className = "msg-bubble";
  bubble.textContent = turn.assistant_text || "(trợ lý không trả lời được, xem chi tiết tool ở trên)";
  content.appendChild(bubble);

  els.messages.appendChild(msg);
  scrollBottom();
}

/* ---------- Luồng chính ---------- */

async function startSession({ silent = false } = {}) {
  if (state.busy) return false;
  state.busy = true;
  els.btnStart.disabled = true;
  try {
    const info = await api("/api/session", {
      provider: els.inpProvider.value,
      model: els.inpModel.value.trim(),
      version: els.inpVersion.value,
      history_window: Number(els.inpHistoryWindow.value) || 5,
      max_tool_rounds: Number(els.inpMaxRounds.value) || 4,
    });
    els.messages.querySelectorAll(".msg").forEach((n) => n.remove());
    els.emptyState.hidden = false;
    updateSessionInfo(info);
    els.inpMessage.focus();
    if (!silent) {
      toast("Đã tạo phiên mới");
      closeSidebar();
    }
    return true;
  } catch (err) {
    toast(err.message);
    return false;
  } finally {
    state.busy = false;
    els.btnStart.disabled = false;
  }
}

async function sendMessage() {
  const text = els.inpMessage.value.trim();
  if (!text || state.busy) return;
  els.inpMessage.value = "";
  autoResize();

  if (!state.sessionId) {
    els.btnSend.disabled = true;
    els.emptyState.hidden = true;
    els.typing.hidden = false;
    scrollBottom();
    const ok = await startSession({ silent: true });
    els.typing.hidden = true;
    if (!ok) {
      els.btnSend.disabled = false;
      return;
    }
  }

  await doSend(text);
}

async function doSend(text) {
  state.busy = true;
  els.btnSend.disabled = true;
  els.emptyState.hidden = true;
  appendUserMessage(text);
  els.typing.hidden = false;
  scrollBottom();

  try {
    const data = await api("/api/chat", {
      session_id: state.sessionId,
      message: text,
    });
    els.typing.hidden = true;
    appendAgentTurn(data.turn);
    updateSessionInfo(data.session);
  } catch (err) {
    els.typing.hidden = true;
    toast(err.message);
  } finally {
    state.busy = false;
    els.btnSend.disabled = false;
    els.inpMessage.focus();
  }
}

/* ---------- Ô nhập ---------- */

function autoResize() {
  const ta = els.inpMessage;
  ta.style.height = "auto";
  ta.style.height = Math.min(ta.scrollHeight, 130) + "px";
}

els.inpMessage.addEventListener("input", autoResize);

els.inpMessage.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

els.btnSend.addEventListener("click", sendMessage);
els.btnStart.addEventListener("click", startSession);

/* ---------- Sidebar mobile ---------- */

function openSidebar() {
  els.sidebar.classList.add("open");
  els.sidebarBackdrop.classList.add("show");
}

function closeSidebar() {
  els.sidebar.classList.remove("open");
  els.sidebarBackdrop.classList.remove("show");
}

els.sidebarToggle.addEventListener("click", () => {
  els.sidebar.classList.contains("open") ? closeSidebar() : openSidebar();
});
els.sidebarBackdrop.addEventListener("click", closeSidebar);

/* ---------- Copy transcript ---------- */

els.btnCopyTranscript.addEventListener("click", async () => {
  if (!state.transcriptPath) {
    toast("Chưa có phiên nào");
    return;
  }
  try {
    await navigator.clipboard.writeText(state.transcriptPath);
    toast("Đã sao chép đường dẫn transcript");
  } catch {
    toast(state.transcriptPath);
  }
});
