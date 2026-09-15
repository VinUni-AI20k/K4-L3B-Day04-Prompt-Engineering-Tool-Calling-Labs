const prompts = [
  { label: "Trạng thái VPN production", text: "Dịch vụ VPN production hiện có đang gặp sự cố không?" },
  { label: "Thiếu asset ID", text: "Kiểm tra Wi-Fi trên laptop của mình giúp nhé." },
  { label: "Tạo ticket (cần xác nhận)", text: "Tạo ticket mức high cho lỗi VPN trên LT-204 giúp mình." },
  { label: "Hủy rồi tìm hướng dẫn in", text: "Tạo ticket lỗi máy in cho máy PR-505 mức medium." },
  { label: "Ngoài phạm vi", text: "Thời tiết Hà Nội hôm nay thế nào? Có cần mang ô không?" },
];

const logEl = document.getElementById("log");
const inputEl = document.getElementById("input");
const formEl = document.getElementById("composer");
const sendBtn = document.getElementById("btn-send");
const bannerEl = document.getElementById("status-banner");
const chipsEl = document.getElementById("meta-chips");
const sessionDl = document.getElementById("session-dl");
const promptsEl = document.getElementById("prompts");

let meta = null;

function pretty(value) {
  try { return JSON.stringify(value, null, 2); } catch { return String(value); }
}

function toolHasError(event) {
  const result = event && event.result;
  return Boolean(event && (event.error || (result && typeof result === "object" && result.error)));
}

function setBanner(turn) {
  if (!turn) { bannerEl.hidden = true; return; }
  bannerEl.hidden = false;
  bannerEl.className = "banner" + (turn.status === "provider_error" || turn.status === "max_tool_rounds" ? " error" : "");
  bannerEl.textContent = turn.status_label || turn.status;
}

function renderMeta(nextMeta) {
  meta = nextMeta;
  const chips = [
    ["version", meta.version],
    ["artifact", meta.artifact_version],
    ["provider", meta.provider],
    ["model", meta.model],
  ];
  chipsEl.innerHTML = chips.map(([k, v]) => `<span class="chip"><strong>${k}</strong> ${v || "—"}</span>`).join("");
  const rows = [
    ["Transcript", meta.transcript_id],
    ["Prompt hash", (meta.prompt_hash || "").slice(0, 12)],
    ["Tools hash", (meta.tools_hash || "").slice(0, 12)],
    ["Lượt", String(meta.turn_count || 0)],
  ];
  sessionDl.innerHTML = rows.map(([k, v]) => `<div><dt>${k}</dt><dd>${v || "—"}</dd></div>`).join("");
}

function appendUser(text) {
  const wrap = document.createElement("article");
  wrap.className = "msg user";
  wrap.innerHTML = `<div class="who"><span>Bạn</span></div><div>${escapeHtml(text)}</div>`;
  logEl.appendChild(wrap);
  wrap.scrollIntoView({ behavior: "smooth", block: "end" });
}

function appendAssistant(turn) {
  const wrap = document.createElement("article");
  wrap.className = "msg assistant";
  const status = turn.status || "answered";
  const tools = (turn.tool_events || []).map((event) => {
    const err = toolHasError(event);
    return `
      <div class="tool${err ? " error" : ""}">
        <header>
          <span class="name">${escapeHtml(event.tool || event.name || "tool")}</span>
          <span class="tag">${err ? "LỖI — không ẩn" : "OK"}</span>
        </header>
        <div>Args</div>
        <pre>${escapeHtml(pretty(event.args || {}))}</pre>
        <div>${err ? "Error / result" : "Result"}</div>
        <pre>${escapeHtml(pretty(event.result || event.error || {}))}</pre>
      </div>`;
  }).join("");
  wrap.innerHTML = `
    <div class="who">
      <span>Agent</span>
      <span class="status ${status}">${escapeHtml(turn.status_label || status)}</span>
    </div>
    <div>${escapeHtml(turn.assistant_text || turn.error || "")}</div>
    ${tools ? `<div class="tools">${tools}</div>` : ""}
  `;
  logEl.appendChild(wrap);
  wrap.scrollIntoView({ behavior: "smooth", block: "end" });
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

async function loadMeta() {
  const res = await fetch("/api/meta");
  const data = await res.json();
  renderMeta(data.meta);
  if (!logEl.children.length) {
    logEl.innerHTML = `<p class="empty">Hỏi trạng thái VPN, kiểm tra máy, hoặc tạo ticket. Mọi tool call, args và lỗi đều hiện trên UI.</p>`;
  }
}

async function sendMessage(text) {
  const empty = logEl.querySelector(".empty");
  if (empty) empty.remove();
  appendUser(text);
  sendBtn.disabled = true;
  bannerEl.hidden = false;
  bannerEl.className = "banner";
  bannerEl.textContent = "Đang gọi agent…";
  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    const data = await res.json();
    if (!data.ok) {
      appendAssistant({
        status: "provider_error",
        status_label: "Lỗi",
        assistant_text: data.error || "Không gửi được",
        tool_events: [],
      });
      setBanner({ status: "provider_error", status_label: data.error || "error" });
    } else {
      appendAssistant(data.turn);
      setBanner(data.turn);
      renderMeta(data.meta);
    }
  } catch (err) {
    appendAssistant({
      status: "provider_error",
      status_label: "Lỗi UI",
      assistant_text: String(err),
      tool_events: [],
    });
    setBanner({ status: "provider_error", status_label: String(err) });
  } finally {
    sendBtn.disabled = false;
    inputEl.focus();
  }
}

formEl.addEventListener("submit", (event) => {
  event.preventDefault();
  const text = inputEl.value.trim();
  if (!text || sendBtn.disabled) return;
  inputEl.value = "";
  sendMessage(text);
});

inputEl.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    formEl.requestSubmit();
  }
});

document.getElementById("btn-reset").addEventListener("click", async () => {
  const res = await fetch("/api/reset", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
  const data = await res.json();
  logEl.innerHTML = `<p class="empty">Hội thoại mới. Transcript file mới đã được tạo.</p>`;
  bannerEl.hidden = true;
  renderMeta(data.meta);
});

document.getElementById("btn-download").addEventListener("click", async () => {
  const res = await fetch("/api/transcript");
  const data = await res.json();
  const blob = new Blob([JSON.stringify(data.transcript, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${data.transcript.transcript_id || "transcript"}.json`;
  a.click();
  URL.revokeObjectURL(url);
});

prompts.forEach((item) => {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.textContent = item.label;
  btn.addEventListener("click", () => {
    inputEl.value = item.text;
    inputEl.focus();
  });
  promptsEl.appendChild(btn);
});

loadMeta().catch((err) => {
  chipsEl.innerHTML = `<span class="chip">Không tải được meta: ${escapeHtml(err)}</span>`;
});
