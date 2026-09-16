const logEl = document.getElementById('log');
const versionSelect = document.getElementById('versionSelect');
const artifactBadge = document.getElementById('artifactBadge');
const resetBtn = document.getElementById('resetBtn');
const input = document.getElementById('input');
const sendBtn = document.getElementById('sendBtn');
const hint = document.getElementById('hint');
const diffToggleBtn = document.getElementById('diffToggleBtn');
const diffPanel = document.getElementById('diffPanel');
const diffIntro = document.getElementById('diffIntro');
const diffWrap = document.getElementById('diffWrap');

let history = [];
let conversationId = crypto.randomUUID();
let turnIndex = 0;
let versions = [];
let toolsDrifted = false;

// Curated user prompts that expose exactly the behavior each version fixed.
// Sourced from the eval cases named in artifacts/version_log.csv's "reason"
// column (T09/T10/T18 -> v1, T16 -> v2, T07/M10 -> v3) so they stay tied to
// real, checked-in test cases instead of invented examples.
const EXAMPLE_PROMPTS = {
  v1: [
    { title: 'T09 — Tạo ticket mà chưa xác nhận', steps: ['Tạo ticket cho lỗi hủy phòng BK-1005.'] },
    { title: 'T10 — Priority cao vẫn phải confirm trước', steps: ['Tạo ticket mức critical cho sự cố phòng ở HTL-NT5.'] },
    { title: 'T18 — "Tôi xác nhận" nhưng chưa từng được hỏi yes/no', steps: ['Tôi muốn tạo ticket mức medium cho phản hồi về HTL-DN7. Tôi xác nhận.'] },
  ],
  v2: [
    { title: 'T16 — Câu hỏi SLA ticket phải vào policy_area=ticketing, không phải service_operations', steps: ['Thời gian phản hồi cho ticket priority critical là bao lâu?'] },
  ],
  v3: [
    { title: 'T07 — Số thiếu prefix BK-/CUST- phải hỏi lại, không được đoán', steps: ['Tôi muốn xem trạng thái booking số 1001.'] },
    { title: 'M10 — Payload đổi sau khi đã confirm: chỉ được gọi clarify, không gọi tool đọc để "kiểm tra lại" trước', steps: [
      'Tạo ticket BK-1001 mức medium. Tôi xác nhận.',
      'Khoan, đổi mức thành high và thêm nội dung phòng bị ẩm.',
      'Hãy cho tôi xem payload mới trước.',
    ] },
  ],
};

function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined) e.textContent = text;
  return e;
}

function addMessage(role, text, extraCls) {
  const wrap = el('div', 'msg ' + role);
  const bubble = el('div', 'bubble' + (extraCls ? ' ' + extraCls : ''), text);
  wrap.appendChild(bubble);
  logEl.appendChild(wrap);
  logEl.scrollTop = logEl.scrollHeight;
  return wrap;
}

function extractReply(assistantText) {
  if (!assistantText) return assistantText;
  try {
    const parsed = JSON.parse(assistantText);
    if (parsed && typeof parsed.reply === 'string') return parsed.reply;
  } catch (e) { /* not JSON, show as-is */ }
  return assistantText;
}

function fmtJson(obj) {
  try { return JSON.stringify(obj, null, 2); } catch (e) { return String(obj); }
}

function addTrace(container, rounds) {
  if (!rounds || !rounds.length) return;
  const details = el('details', 'trace');
  const summary = el('summary', null, `tool trace — ${rounds.length} round(s)`);
  details.appendChild(summary);
  rounds.forEach((round, i) => {
    const div = el('div', 'round');
    div.appendChild(el('div', 'rlabel', `Round ${round.round}`));
    (round.tool_calls || []).forEach(call => {
      const callDiv = el('div', 'call');
      const nameSpan = el('span', 'name', call.name + '(');
      const argsSpan = el('span', 'args', JSON.stringify(call.args) + ')');
      callDiv.appendChild(nameSpan);
      callDiv.appendChild(argsSpan);
      div.appendChild(callDiv);
    });
    (round.tool_results || []).forEach(ev => {
      const result = ev.result || {};
      const isErr = !!result.error;
      const resDiv = el('div', 'result' + (isErr ? ' err' : ''), fmtJson(result));
      div.appendChild(resDiv);
    });
    details.appendChild(div);
  });
  container.appendChild(details);
}

async function loadVersions() {
  const res = await fetch('/api/versions');
  const data = await res.json();
  versions = data.versions;
  toolsDrifted = !!data.tools_drifted;
  versionSelect.innerHTML = '';
  versions.forEach(v => {
    const opt = el('option');
    opt.value = v.key;
    opt.textContent = `${v.key}  (${v.artifact_version})`;
    versionSelect.appendChild(opt);
  });
  const def = versions[versions.length - 1];
  if (def) versionSelect.value = def.key;
  renderDiffPanel();
  updateArtifactBadge();
}

function updateArtifactBadge() {
  const v = versions.find(x => x.key === versionSelect.value);
  artifactBadge.textContent = v ? v.artifact_version : '';
  highlightCurrentCard();
}

// "final" (and any future alias) has no card of its own in the diff panel —
// it isn't a hypothesis-driven step, just a pointer to another version's
// file — so highlighting falls back to whichever real version it points at.
function effectiveDiffKey() {
  const v = versions.find(x => x.key === versionSelect.value);
  if (!v) return versionSelect.value;
  return v.has_log_row ? v.key : (v.prev_key || v.key);
}

function highlightCurrentCard() {
  const key = effectiveDiffKey();
  diffWrap.querySelectorAll('.vcard').forEach(card => {
    const isCurrent = card.dataset.key === key;
    card.classList.toggle('current', isCurrent);
    if (isCurrent) card.open = true;
  });
}

function renderDiffIntro() {
  let html =
    '<strong>Vì sao V0 vẫn gọi được tool?</strong> Khả năng gọi tool KHÔNG đến từ nội dung system prompt — nó đến từ việc ' +
    'server luôn đính kèm cùng một danh sách tool declarations (<code>artifacts/tools.yaml</code>) cho mọi request, ở mọi version ' +
    '(xem <code>AppState.openai_tools</code> trong <code>webui.py</code>, dùng chung, không đổi theo version_key). ' +
    'Cái duy nhất khác nhau giữa các version là phần "Rules" trong <code>system_prompt_*.md</code> — nó chỉ quyết định ' +
    '<em>KHI NÀO / tool nào</em> nên gọi (rào chắn xác nhận, phân loại policy_area, format ID…), chứ không quyết định ' +
    '<em>CÓ ĐƯỢC PHÉP</em> gọi tool hay không. V0 chỉ có câu "You may use the declared travel-operations support tools." nên ' +
    'model vẫn đủ quyền gọi tool — chỉ là thiếu rào chắn nên hay chọn sai tool hoặc sai thời điểm.<br><br>' +
    '<strong>File nào đổi giữa các version?</strong> Mỗi card bên dưới ghi rõ <code>system_prompt.md</code> và/hoặc ' +
    '<code>tools.yaml</code> có đổi so với version liền trước không, dựa trên đúng <code>prompt_hash</code>/<code>tools_hash</code> ' +
    'được ghi lại trong <code>artifacts/version_log.csv</code> tại thời điểm chạy eval của version đó — không suy đoán từ tên file.';
  const aliases = versions.filter(v => !v.has_log_row);
  if (aliases.length) {
    const names = aliases.map(v => `<code>${v.key}</code> (= <code>${v.prev_key}</code>)`).join(', ');
    html += `<br><br>Không thấy card cho ${names} ở dưới: đó không phải một bước cải tiến có hypothesis/reason riêng trong ` +
      'version_log.csv, chỉ là alias trỏ tới đúng file của version trước (0 dòng diff) — vẫn chọn được ở dropdown để chat, ' +
      'nhưng không đáng để giải thích như một version thật.';
  }
  if (toolsDrifted) {
    html +=
      '<br><br>⚠️ <strong>Lưu ý:</strong> <code>artifacts/tools.yaml</code> hiện tại trên đĩa KHÔNG còn khớp hash đã ghi cho ' +
      'chu trình v0→v3 (nó đã được sửa sau đó — đổi mô tả <code>search_travel_info</code> từ Tavily sang OpenAI web search, ' +
      'không liên quan tới các rule trong system prompt). Vì webui.py dùng chung một <code>tools.yaml</code> hiện hành cho mọi ' +
      'version, các badge "tools.yaml" bên dưới phản ánh lịch sử lúc chạy eval, không phải trạng thái tool đang chạy ngay bây giờ.';
  }
  diffIntro.innerHTML = html;
}

function fileBadges(changedFiles) {
  if (!changedFiles || !changedFiles.length) return '';
  return changedFiles.map(f => {
    if (f === 'baseline') return '<span class="vfile vfile-base">baseline</span>';
    const cls = f === 'tools.yaml' ? 'vfile vfile-tools' : 'vfile vfile-prompt';
    return `<span class="${cls}">${f}</span>`;
  }).join('');
}

function renderChangeSummary(v) {
  if (!v.prev_key) {
    return '<div class="vlabel">So với version trước</div><div class="changerow">Đây là baseline — chưa có version trước để so sánh.</div>';
  }
  const files = v.changed_files || [];
  const promptChanged = files.includes('system_prompt.md');
  const toolsChanged = files.includes('tools.yaml');
  const promptLine = promptChanged
    ? `✅ <strong>system_prompt.md</strong> đã đổi so với ${v.prev_key}`
    : `⬜ <strong>system_prompt.md</strong> không đổi so với ${v.prev_key}`;
  const toolsLine = toolsChanged
    ? `✅ <strong>tools.yaml</strong> đã đổi so với ${v.prev_key}`
    : `⬜ <strong>tools.yaml</strong> không đổi so với ${v.prev_key}`;
  return `<div class="vlabel">So với ${v.prev_key}</div><div class="changerow">${promptLine}</div><div class="changerow">${toolsLine}</div>`;
}

function metricArrow(before, after) {
  if (!after) return '';
  const b = before && before !== 'N/A' ? before : null;
  return b ? `${b} <span class="up">→ ${after}</span>` : `<span class="up">${after}</span>`;
}

function renderDiffLines(diff) {
  if (!diff || !diff.length) return '<span class="ctx">(không có thay đổi so với version trước — nội dung giống hệt)</span>';
  return diff.map(l => {
    const escaped = l.text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    const prefix = l.type === 'add' ? '+ ' : l.type === 'del' ? '- ' : '  ';
    return `<span class="${l.type}">${prefix}${escaped}</span>`;
  }).join('');
}

function renderExamples(key) {
  const items = EXAMPLE_PROMPTS[key];
  if (!items || !items.length) return '';
  const body = items.map(ex => {
    const chips = ex.steps.map((s, i) => {
      const label = ex.steps.length > 1 ? `<span class="step">B${i + 1}</span>` : '';
      const escaped = s.replace(/"/g, '&quot;');
      return `<button type="button" class="chip" data-fill="${escaped}">${label}${s}</button>`;
    }).join('');
    return `<div class="example"><div class="etitle">${ex.title}</div>${chips}</div>`;
  }).join('');
  return `<div class="vlabel">Prompt demo (bấm để điền vào ô chat, thử ở version này rồi đổi version chạy lại)</div><div class="examples">${body}</div>`;
}

function renderDiffPanel() {
  renderDiffIntro();
  diffWrap.innerHTML = '';
  const effectiveKey = effectiveDiffKey();
  // Only real hypothesis-driven steps (a row in version_log.csv) get a card.
  // An alias like "final" that just points at another version's file with
  // zero diff and no reason/hypothesis would otherwise look like a fake step.
  versions.filter(v => v.has_log_row).forEach(v => {
    const details = el('details', 'vcard');
    details.dataset.key = v.key;
    details.open = v.key === effectiveKey;
    const summary = el('summary');
    summary.innerHTML =
      `<span class="vkey">${v.key}</span>` +
      fileBadges(v.changed_files) +
      (v.metric_after ? `<span class="vmetric">${v.metric_name || 'metric'}: ${metricArrow(v.metric_before, v.metric_after)}</span>` : '');
    details.appendChild(summary);

    const body = el('div', 'vbody');
    const changeSummary = el('div');
    changeSummary.innerHTML = renderChangeSummary(v);
    body.appendChild(changeSummary);

    if (v.reason) {
      body.appendChild(el('div', 'vlabel', 'Thay đổi & vì sao'));
      const reason = el('div', 'vreason');
      reason.textContent = v.reason;
      body.appendChild(reason);
    }
    if (v.hypothesis) {
      const hyp = el('div', 'vhyp', `Giả thuyết: ${v.hypothesis}`);
      body.appendChild(hyp);
    }
    body.appendChild(el('div', 'vlabel', v.prev_key ? `Diff system_prompt so với ${v.prev_key}` : 'Baseline — chưa có gì để diff'));
    const diffDiv = el('div', 'difflines');
    diffDiv.innerHTML = renderDiffLines(v.diff);
    body.appendChild(diffDiv);

    const examplesHtml = renderExamples(v.key);
    if (examplesHtml) {
      const exWrap = el('div');
      exWrap.innerHTML = examplesHtml;
      body.appendChild(exWrap);
    }

    details.appendChild(body);
    diffWrap.appendChild(details);
  });
  diffWrap.querySelectorAll('.chip').forEach(btn => {
    btn.addEventListener('click', () => {
      input.value = btn.dataset.fill;
      input.focus();
    });
  });
  highlightCurrentCard();
}

diffToggleBtn.addEventListener('click', () => {
  diffPanel.hidden = !diffPanel.hidden;
  diffToggleBtn.textContent = diffPanel.hidden ? 'So sánh version ▸' : 'Ẩn so sánh version ▸';
});

function resetConversation(note) {
  history = [];
  turnIndex = 0;
  conversationId = crypto.randomUUID();
  logEl.innerHTML = '';
  if (note) addMessage('system', note);
  hint.textContent = `conversation: ${conversationId.slice(0, 8)}`;
}

versionSelect.addEventListener('change', () => {
  updateArtifactBadge();
  resetConversation(`Switched to ${versionSelect.value} — new conversation started.`);
});

resetBtn.addEventListener('click', () => resetConversation('New conversation started.'));

async function send() {
  const text = input.value.trim();
  if (!text) return;
  input.value = '';
  sendBtn.disabled = true;
  addMessage('user', text);
  turnIndex += 1;

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        version: versionSelect.value,
        message: text,
        history,
        conversation_id: conversationId,
        turn_index: turnIndex,
      }),
    });
    const data = await res.json();

    if (data.status === 'error' || data.status === 'provider_error') {
      addMessage('assistant', data.error || 'Provider error.', 'error');
      return;
    }

    const cls = data.status === 'waiting_for_user' ? 'waiting' : (data.status === 'max_tool_rounds' ? 'error' : '');
    const displayText = extractReply(data.assistant_text);
    const wrap = addMessage('assistant', displayText, cls);
    if (displayText !== data.assistant_text && data.assistant_text) {
      const rawDetails = el('details', 'trace');
      rawDetails.appendChild(el('summary', null, 'raw JSON output'));
      const rawDiv = el('div', 'round');
      rawDiv.appendChild(el('div', 'result', data.assistant_text));
      rawDetails.appendChild(rawDiv);
      wrap.appendChild(rawDetails);
    }
    const metaLine = el('div', 'meta', `status: ${data.status} · version: ${data.version_key} (${data.artifact_version}) · provider: ${data.provider}/${data.model}`);
    wrap.appendChild(metaLine);
    addTrace(wrap, data.rounds);

    history.push({ role: 'user', content: text });
    history.push({ role: 'assistant', content: data.assistant_text || '' });

    hint.textContent = `provider: ${data.provider} · model: ${data.model} · conversation: ${conversationId.slice(0, 8)}`;
  } catch (err) {
    addMessage('assistant', 'Network/UI error: ' + err.message, 'error');
  } finally {
    sendBtn.disabled = false;
    input.focus();
  }
}

sendBtn.addEventListener('click', send);
input.addEventListener('keydown', e => { if (e.key === 'Enter') send(); });

loadVersions();
resetConversation();
