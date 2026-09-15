const logEl = document.getElementById('log');
const versionSelect = document.getElementById('versionSelect');
const artifactBadge = document.getElementById('artifactBadge');
const resetBtn = document.getElementById('resetBtn');
const input = document.getElementById('input');
const sendBtn = document.getElementById('sendBtn');
const hint = document.getElementById('hint');

let history = [];
let conversationId = crypto.randomUUID();
let turnIndex = 0;
let versions = [];

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
  versionSelect.innerHTML = '';
  versions.forEach(v => {
    const opt = el('option');
    opt.value = v.key;
    opt.textContent = `${v.key}  (${v.artifact_version})`;
    versionSelect.appendChild(opt);
  });
  const def = versions.find(v => v.key === 'final') || versions[versions.length - 1];
  if (def) versionSelect.value = def.key;
  updateArtifactBadge();
}

function updateArtifactBadge() {
  const v = versions.find(x => x.key === versionSelect.value);
  artifactBadge.textContent = v ? v.artifact_version : '';
}

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
