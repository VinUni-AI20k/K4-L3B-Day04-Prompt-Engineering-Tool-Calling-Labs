/* ===========================================================================
   NovaPC Console — Vue 3 (global build, không cần bước build)
   ---------------------------------------------------------------------------
   UI cố ý KHÔNG hard-code tên tool. Danh sách tool, tham số và nhãn đều lấy từ
   /api/meta (đọc artifacts/tools.yaml) và web/ui.config.json, nên khi nhóm
   thay bộ tool Helpdesk bằng bộ tool bán PC thì UI chạy đúng mà không sửa code.
   =========================================================================== */

const { createApp, ref, reactive, computed, nextTick, onMounted } = Vue;

/* --------------------------------- helpers -------------------------------- */

const TONE_VARS = {
  ask: 'var(--info)',
  read: 'var(--accent)',
  write: 'var(--warn)',
  sensitive: 'var(--sensitive)',
  external: 'var(--accent-2)',
  compose: 'var(--ok)',
  unknown: 'var(--text-dim)',
};

const TONE_NOTES = {
  write: 'Ghi dữ liệu',
  sensitive: 'Dữ liệu cá nhân',
  external: 'Gọi ra ngoài',
};

function formatJson(value) {
  try {
    return JSON.stringify(value, null, 2);
  } catch (err) {
    return String(value);
  }
}

function shortValue(value) {
  if (value === null || value === undefined) return '—';
  if (typeof value === 'string') return value;
  return formatJson(value);
}

function formatTime(value) {
  const date = value ? new Date(value) : new Date();
  if (Number.isNaN(date.getTime())) return '';
  return date.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
}

/** Trạng thái tool result, suy ra từ hình dạng kết quả nên không phụ thuộc tên tool. */
function resultStatus(result) {
  if (result === null || result === undefined) return { kind: 'warn', label: 'no_result' };
  if (typeof result !== 'object') return { kind: 'ok', label: 'ok' };
  if (result.error) return { kind: 'error', label: String(result.error) };
  if (result.awaiting_user) return { kind: 'info', label: 'awaiting_user' };
  if (result.status === 'needs_confirmation') return { kind: 'warn', label: 'needs_confirmation' };
  if (result.status) return { kind: 'ok', label: String(result.status) };
  return { kind: 'ok', label: 'ok' };
}

/** System prompt yêu cầu agent trả JSON; tách phần reply để hiển thị cho người dùng. */
function parseAgentPayload(text) {
  const raw = text === null || text === undefined ? '' : String(text);
  let candidate = raw.trim();
  const fenced = candidate.match(/^```(?:json)?\s*([\s\S]*?)\s*```$/i);
  if (fenced) candidate = fenced[1].trim();
  if (!candidate.startsWith('{') || !candidate.endsWith('}')) {
    return { reply: raw, payload: null, raw };
  }
  try {
    const parsed = JSON.parse(candidate);
    if (parsed && typeof parsed === 'object' && !Array.isArray(parsed) && 'reply' in parsed) {
      return { reply: String(parsed.reply === null || parsed.reply === undefined ? '' : parsed.reply), payload: parsed, raw };
    }
  } catch (err) {
    /* không phải JSON hợp lệ: hiển thị nguyên văn */
  }
  return { reply: raw, payload: null, raw };
}

async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    try {
      const area = document.createElement('textarea');
      area.value = text;
      area.style.position = 'fixed';
      area.style.opacity = '0';
      document.body.appendChild(area);
      area.select();
      const ok = document.execCommand('copy');
      document.body.removeChild(area);
      return ok;
    } catch (inner) {
      return false;
    }
  }
}

async function api(path, options) {
  const response = await fetch(path, Object.assign({ headers: { 'Content-Type': 'application/json' } }, options || {}));
  const text = await response.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch (err) {
    data = { detail: text };
  }
  if (!response.ok) {
    const detail = data && data.detail ? data.detail : response.statusText;
    throw new Error(response.status + ' ' + detail);
  }
  return data;
}

/* -------------------------------- components ------------------------------ */

const JsonView = {
  props: {
    value: { default: null },
    startCollapsed: { type: Boolean, default: false },
  },
  setup(props) {
    const collapsed = ref(props.startCollapsed);
    const copied = ref(false);
    const text = computed(() => formatJson(props.value));
    const lineCount = computed(() => text.value.split('\n').length);
    const long = computed(() => lineCount.value > 6);
    const hiddenLines = computed(() => Math.max(lineCount.value - 5, 1));

    async function copy() {
      copied.value = await copyText(text.value);
      setTimeout(() => { copied.value = false; }, 1400);
    }

    return { collapsed, copied, text, long, hiddenLines, copy };
  },
  template: `
    <div class="json-view" :class="{ 'json-view--collapsed': collapsed && long }">
      <div class="json-view__actions">
        <button v-if="long" class="btn btn--sm btn--ghost" type="button" @click="collapsed = !collapsed">
          {{ collapsed ? 'Mở rộng' : 'Thu gọn' }}
        </button>
        <button class="btn btn--sm btn--ghost" type="button" @click="copy">
          {{ copied ? 'Đã copy' : 'Copy' }}
        </button>
      </div>
      <pre>{{ text }}</pre>
      <button v-if="collapsed && long" class="json-view__more" type="button" @click="collapsed = false">
        <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M6 9l6 6 6-6" />
        </svg>
        còn {{ hiddenLines }} dòng
      </button>
    </div>
  `,
};

const ToolCallCard = {
  components: { JsonView },
  props: {
    event: { type: Object, required: true },
    meta: { type: Object, default: () => ({}) },
    open: { type: Boolean, default: false },
  },
  setup(props) {
    const expanded = ref(props.open);
    const name = computed(() => props.event.tool || 'unknown_tool');
    const info = computed(() => props.meta[name.value] || {});
    const tone = computed(() => info.value.tone || 'unknown');
    const toneVar = computed(() => TONE_VARS[tone.value] || TONE_VARS.unknown);
    const toneNote = computed(() => TONE_NOTES[tone.value] || '');
    const label = computed(() => info.value.label || '');
    const args = computed(() => props.event.args || {});
    const argEntries = computed(() => Object.entries(args.value));
    const status = computed(() => resultStatus(props.event.result));

    return { expanded, name, tone, toneVar, toneNote, label, argEntries, status, shortValue };
  },
  template: `
    <div class="tool-card" :style="{ '--tone': toneVar }">
      <button class="tool-card__head" type="button" :aria-expanded="String(expanded)" @click="expanded = !expanded">
        <span class="tool-card__dot"></span>
        <span class="tool-card__name">{{ name }}</span>
        <span v-if="label" class="tool-card__label">{{ label }}</span>
        <span class="tool-card__spacer"></span>
        <span v-if="toneNote" class="chip">{{ toneNote }}</span>
        <span class="status-badge" :class="'status-badge--' + status.kind">{{ status.label }}</span>
        <span class="round-label">{{ expanded ? '▾' : '▸' }}</span>
      </button>

      <div v-show="expanded" class="tool-card__body">
        <div>
          <div class="field-label">Input</div>
          <table v-if="argEntries.length" class="args-table">
            <tbody>
              <tr v-for="[key, value] in argEntries" :key="key">
                <td>{{ key }}</td>
                <td>{{ shortValue(value) }}</td>
              </tr>
            </tbody>
          </table>
          <div v-else class="args-empty">(không có tham số)</div>
        </div>

        <div>
          <div class="field-label">
            Kết quả
            <span v-if="status.kind === 'error'" class="status-badge status-badge--error">lỗi tool</span>
          </div>
          <json-view :value="event.result" :start-collapsed="true" />
        </div>
      </div>
    </div>
  `,
};

const TraceBlock = {
  components: { ToolCallCard },
  props: {
    rounds: { type: Array, default: () => [] },
    meta: { type: Object, default: () => ({}) },
    open: { type: Boolean, default: false },
  },
  setup(props) {
    const expanded = ref(props.open);
    const callCount = computed(() =>
      props.rounds.reduce((total, round) => total + ((round.tool_calls || []).length), 0)
    );
    const errorCount = computed(() =>
      props.rounds.reduce((total, round) => {
        const errors = (round.tool_results || []).filter((event) => resultStatus(event.result).kind === 'error');
        return total + errors.length;
      }, 0)
    );
    return { expanded, callCount, errorCount };
  },
  template: `
    <div v-if="rounds.length" class="trace">
      <button class="trace__head" type="button" :aria-expanded="String(expanded)" @click="expanded = !expanded">
        <span class="trace__title">Tool trace</span>
        <span class="trace__summary">
          <span>{{ rounds.length }} round · {{ callCount }} call</span>
          <span v-if="errorCount" class="status-badge status-badge--error">{{ errorCount }} lỗi</span>
        </span>
        <span class="round-label">{{ expanded ? '▾' : '▸' }}</span>
      </button>

      <div v-show="expanded" class="trace__body">
        <template v-for="(round, index) in rounds" :key="index">
          <div v-if="rounds.length > 1" class="round-label">Round {{ round.round || index + 1 }}</div>
          <tool-call-card
            v-for="(event, eventIndex) in (round.tool_results || [])"
            :key="index + '-' + eventIndex"
            :event="event"
            :meta="meta"
            :open="(round.tool_results || []).length === 1 && rounds.length === 1"
          />
          <div v-if="!(round.tool_results || []).length" class="args-empty">
            Round này không gọi tool — agent trả lời trực tiếp.
          </div>
        </template>
      </div>
    </div>
  `,
};

const AgentMessage = {
  components: { JsonView },
  props: {
    text: { default: '' },
    time: { type: String, default: '' },
    name: { type: String, default: 'Agent' },
  },
  setup(props) {
    const parsed = computed(() => parseAgentPayload(props.text));
    const showRaw = ref(false);
    const chips = computed(() => {
      const payload = parsed.value.payload;
      if (!payload) return [];
      const items = [];
      if (payload.intent) items.push({ key: 'intent', value: String(payload.intent) });
      if (payload.action) items.push({ key: 'action', value: String(payload.action) });
      const evidence = payload.evidence_ids;
      if (Array.isArray(evidence) && evidence.length) {
        items.push({ key: 'evidence', value: evidence.join(', ') });
      }
      return items;
    });
    return { parsed, chips, showRaw };
  },
  template: `
    <div class="msg msg--agent">
      <div class="msg__avatar msg__avatar--agent">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round">
          <rect x="7" y="7" width="10" height="10" rx="2.5" />
          <path d="M10 2.6v3M14 2.6v3M10 18.4v3M14 18.4v3M2.6 10h3M2.6 14h3M18.4 10h3M18.4 14h3" />
        </svg>
      </div>
      <div class="msg__col">
        <div class="msg__meta">
          <span class="msg__who">{{ name }}</span>
          <span v-if="time" class="msg__time">{{ time }}</span>
        </div>
        <div class="bubble bubble--agent">
          <div v-if="chips.length" class="agent-chips">
            <span v-for="chip in chips" :key="chip.key" class="chip">
              {{ chip.key }} <strong>{{ chip.value }}</strong>
            </span>
          </div>

          <div>{{ parsed.reply || '(agent không trả về nội dung)' }}</div>

          <div v-if="parsed.payload" style="margin-top:10px">
            <button class="btn btn--sm btn--ghost" type="button" @click="showRaw = !showRaw">
              {{ showRaw ? 'Ẩn JSON gốc' : 'Xem JSON gốc' }}
            </button>
            <div v-show="showRaw" style="margin-top:6px">
              <json-view :value="parsed.payload" />
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
};

/* ----------------------------------- app ---------------------------------- */

const app = createApp({
  components: { JsonView, ToolCallCard, TraceBlock, AgentMessage },
  setup() {
    const meta = ref(null);
    const session = ref(null);
    const turns = reactive([]);
    const draft = ref('');
    const sending = ref(false);
    const bootError = ref('');
    const sidebarOpen = ref(false);
    const traceOpen = ref(false);
    const toolQuery = ref('');
    const copiedKey = ref('');
    const panelOpen = reactive({ runtime: true, tools: true, prompts: true });
    const theme = ref('dark');
    const threadEl = ref(null);
    const composerEl = ref(null);

    const brand = computed(() => (meta.value && meta.value.ui && meta.value.ui.brand) || {
      short: 'AI', name: 'Agent Console', tagline: 'Prompt engineering & tool calling',
    });
    const toolMeta = computed(() => (meta.value && meta.value.ui && meta.value.ui.tool_meta) || {});
    const promptGroups = computed(() => (meta.value && meta.value.ui && meta.value.ui.prompt_groups) || []);
    const tools = computed(() => (meta.value && meta.value.tools) || []);

    const flatPrompts = computed(() => {
      const items = [];
      promptGroups.value.forEach((group) => (group.items || []).forEach((item) => items.push(item)));
      return items.slice(0, 4);
    });

    /** Lượt cuối đang chờ người dùng trả lời (clarify / xác nhận). */
    const pendingQuestion = computed(() => {
      for (let index = turns.length - 1; index >= 0; index -= 1) {
        const turn = turns[index];
        if (!turn.record) continue;
        if (turn.record.status !== 'waiting_for_user') return null;
        const events = turn.record.tool_events || [];
        for (let eventIndex = events.length - 1; eventIndex >= 0; eventIndex -= 1) {
          const result = events[eventIndex].result;
          if (result && result.awaiting_user) {
            const options = Array.isArray(result.options) ? result.options.filter(Boolean) : [];
            const type = result.response_type || 'text';
            const quick = options.length ? options : (type === 'yes_no' ? ['Có, xác nhận', 'Không'] : []);
            return { question: result.question || turn.record.assistant_text, quick };
          }
        }
        return { question: turn.record.assistant_text, quick: [] };
      }
      return null;
    });

    const runtimeState = computed(() => {
      if (bootError.value) return { dot: 'live-dot--down', label: 'Mất kết nối' };
      if (sending.value) return { dot: 'live-dot--busy', label: 'Đang chạy' };
      if (!session.value) return { dot: 'live-dot--busy', label: 'Đang khởi tạo' };
      return { dot: '', label: 'Sẵn sàng' };
    });

    const filteredTools = computed(() => {
      const needle = toolQuery.value.trim().toLowerCase();
      if (!needle) return tools.value;
      return tools.value.filter((tool) => {
        const label = (toolMeta.value[tool.name] || {}).label || '';
        const haystack = (tool.name + ' ' + label + ' ' + (tool.description || '')).toLowerCase();
        return haystack.indexOf(needle) !== -1;
      });
    });

    async function copyValue(key, value) {
      const ok = await copyText(String(value || ''));
      copiedKey.value = ok ? key : '';
      setTimeout(() => { copiedKey.value = ''; }, 1400);
    }

    function toneVarFor(name) {
      const info = toolMeta.value[name] || {};
      return TONE_VARS[info.tone] || TONE_VARS.unknown;
    }

    function toolLabel(name) {
      const info = toolMeta.value[name] || {};
      return info.label || '';
    }

    function requiredParams(tool) {
      const params = tool.parameters || {};
      const properties = params.properties || {};
      const required = params.required || [];
      return Object.keys(properties).map((key) => ({ key, required: required.indexOf(key) !== -1 }));
    }

    /** Hành động ghi dữ liệu đã thực sự chạy trong lượt này — hiện rõ để soi an toàn. */
    function writeActions(record) {
      if (!record) return [];
      return (record.tool_events || []).filter((event) => {
        const info = toolMeta.value[event.tool] || {};
        if (info.tone !== 'write') return false;
        return resultStatus(event.result).kind === 'ok';
      });
    }

    async function scrollToEnd() {
      await nextTick();
      const el = threadEl.value;
      if (el) el.scrollTop = el.scrollHeight;
    }

    function autoGrow() {
      const el = composerEl.value;
      if (!el) return;
      el.style.height = 'auto';
      el.style.height = Math.min(el.scrollHeight, 180) + 'px';
    }

    async function loadMeta() {
      meta.value = await api('/api/meta');
    }

    async function startSession() {
      const data = await api('/api/sessions', { method: 'POST' });
      session.value = data;
      if (data.meta) meta.value = data.meta;
      turns.splice(0, turns.length);
    }

    async function newSession() {
      if (sending.value) return;
      try {
        await startSession();
        draft.value = '';
        autoGrow();
      } catch (err) {
        bootError.value = String(err.message || err);
      }
    }

    async function send(text) {
      const message = (text === undefined ? draft.value : text).trim();
      if (!message || sending.value || !session.value) return;

      const turn = reactive({
        user: message,
        at: new Date().toISOString(),
        record: null,
        error: null,
        pending: true,
      });
      turns.push(turn);
      draft.value = '';
      autoGrow();
      sending.value = true;
      scrollToEnd();

      try {
        const data = await api('/api/sessions/' + session.value.session_id + '/messages', {
          method: 'POST',
          body: JSON.stringify({ message }),
        });
        turn.record = data.turn;
        session.value.transcript_path = data.transcript_path;
      } catch (err) {
        turn.error = String(err.message || err);
      } finally {
        turn.pending = false;
        sending.value = false;
        scrollToEnd();
      }
    }

    function onComposerKey(event) {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        send();
      }
    }

    function usePrompt(text) {
      draft.value = text;
      sidebarOpen.value = false;
      nextTick(() => {
        autoGrow();
        if (composerEl.value) composerEl.value.focus();
      });
    }

    async function downloadTranscript() {
      if (!session.value) return;
      try {
        const data = await api('/api/sessions/' + session.value.session_id);
        const blob = new Blob([formatJson(data)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = session.value.session_id + '.transcript.json';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      } catch (err) {
        bootError.value = String(err.message || err);
      }
    }

    function applyTheme(value) {
      theme.value = value;
      document.documentElement.setAttribute('data-theme', value);
      try {
        localStorage.setItem('novapc-theme', value);
      } catch (err) {
        /* private mode: bỏ qua */
      }
    }

    function toggleTheme() {
      applyTheme(theme.value === 'dark' ? 'light' : 'dark');
    }

    onMounted(async () => {
      let stored = null;
      try {
        stored = localStorage.getItem('novapc-theme');
      } catch (err) {
        stored = null;
      }
      applyTheme(stored === 'light' ? 'light' : 'dark');

      try {
        await loadMeta();
        await startSession();
      } catch (err) {
        bootError.value = String(err.message || err);
      }
    });

    return {
      meta, session, turns, draft, sending, bootError, sidebarOpen, traceOpen, theme,
      threadEl, composerEl, toolQuery, copiedKey, panelOpen,
      brand, toolMeta, promptGroups, tools, filteredTools, flatPrompts, pendingQuestion, runtimeState,
      toneVarFor, toolLabel, requiredParams, writeActions, formatTime, copyValue,
      send, newSession, onComposerKey, usePrompt, downloadTranscript, toggleTheme, autoGrow,
    };
  },
  template: `
    <div class="shell">
      <!-- ------------------------------ topbar ------------------------------ -->
      <header class="topbar">
        <div class="topbar-main">
          <button class="btn btn--icon btn--ghost sidebar-toggle" type="button"
                  @click="sidebarOpen = !sidebarOpen" aria-label="Mở panel">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <path d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          <div class="brand">
            <div class="brand-mark" :title="brand.name">
              <svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round">
                <rect x="4.5" y="6" width="23" height="16" rx="2.5" stroke-width="2.2" />
                <rect x="11" y="11.5" width="10" height="5" rx="1.2" fill="currentColor" stroke="none" />
                <path d="M16 22v4M11.5 26h9" stroke-width="2.2" />
              </svg>
            </div>
            <div class="brand-text">
              <div class="brand-name">{{ brand.name }}</div>
              <div class="brand-tagline">{{ brand.tagline }}</div>
            </div>
          </div>

          <div class="topbar-spacer"></div>

          <div class="status-cluster">
            <span class="status-cell" :title="bootError || 'Kết nối API'">
              <span class="live-dot" :class="runtimeState.dot"></span>
              <span>{{ runtimeState.label }}</span>
            </span>

            <span v-if="meta" class="status-cell status-cell--accent" :title="meta.artifact_version">
              <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round">
                <rect x="7" y="7" width="10" height="10" rx="2" />
                <path d="M10 2v3M14 2v3M10 19v3M14 19v3M2 10h3M2 14h3M19 10h3M19 14h3" />
              </svg>
              <strong>{{ meta.version }}</strong>
            </span>

            <span v-if="meta" class="status-cell status-cell--optional" :title="meta.provider + ' / ' + (meta.model || 'default')">
              {{ meta.provider }} <strong>{{ meta.model || 'default' }}</strong>
            </span>

            <span class="status-cell status-cell--optional">
              <strong>{{ turns.length }}</strong> lượt
            </span>
          </div>

          <span class="rule"></span>

          <div class="topbar-tools">
            <button class="btn btn--sm" type="button" :class="{ 'btn--on': traceOpen }"
                    :title="traceOpen ? 'Thu gọn toàn bộ trace' : 'Mở toàn bộ trace'"
                    @click="traceOpen = !traceOpen">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M4 17l5-5-5-5M12 17h8" />
              </svg>
              Trace
            </button>

            <button class="btn btn--icon" type="button" title="Tải transcript"
                    :disabled="!session || !turns.length" @click="downloadTranscript">
              <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 4v10m0 0 4-4m-4 4-4-4M5 19h14" />
              </svg>
            </button>

            <button class="btn btn--icon" type="button" title="Phiên mới" :disabled="sending" @click="newSession">
              <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                <path d="M12 5v14M5 12h14" />
              </svg>
            </button>

            <button class="btn btn--icon btn--ghost" type="button" @click="toggleTheme"
                    :aria-label="theme === 'dark' ? 'Chuyển giao diện sáng' : 'Chuyển giao diện tối'">
              <svg v-if="theme === 'dark'" viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round">
                <circle cx="12" cy="12" r="4" />
                <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
              </svg>
              <svg v-else viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round">
                <path d="M20 14.5A8 8 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5Z" />
              </svg>
            </button>
          </div>
        </div>

        <div class="substrip" v-if="meta">
          <span class="sub-item">
            <span class="sub-key">prompt</span>
            <b>{{ meta.system_prompt_name }}</b> {{ meta.prompt_hash.slice(0, 10) }}
          </span>
          <span class="sub-item">
            <span class="sub-key">tools</span>
            <b>{{ meta.tools_file_name }}</b> {{ tools.length }} tool · {{ meta.tools_hash.slice(0, 10) }}
          </span>
          <span class="sub-item">
            <span class="sub-key">loop</span>
            <b>{{ meta.max_tool_rounds }}</b> round · history <b>{{ meta.history_window }}</b>
          </span>
          <span class="spacer"></span>
          <span class="sub-item" v-if="session">
            <span class="sub-key">transcript</span>
            <b>{{ session.session_id }}</b>
          </span>
        </div>
      </header>

      <!-- ------------------------------ sidebar ----------------------------- -->
      <aside class="sidebar" :class="{ 'sidebar--open': sidebarOpen }">
        <!-- Runtime -->
        <section class="panel">
          <button class="panel-head" type="button" :aria-expanded="String(panelOpen.runtime)"
                  @click="panelOpen.runtime = !panelOpen.runtime">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                 class="chevron" :class="{ 'chevron--open': panelOpen.runtime }">
              <path d="M9 6l6 6-6 6" />
            </svg>
            <h2 class="panel-title">Runtime</h2>
            <span class="panel-head__spacer"></span>
            <span class="panel-count">{{ runtimeState.label }}</span>
          </button>

          <div class="panel-body" v-show="panelOpen.runtime">
            <div class="stat-grid">
              <div class="stat-tile stat-tile--accent">
                <div class="stat-tile__key">Version</div>
                <div class="stat-tile__val">{{ meta ? meta.version : '—' }}</div>
              </div>
              <div class="stat-tile">
                <div class="stat-tile__key">Tool</div>
                <div class="stat-tile__val">{{ tools.length }}</div>
              </div>
              <div class="stat-tile">
                <div class="stat-tile__key">Tool rounds</div>
                <div class="stat-tile__val">{{ meta ? meta.max_tool_rounds : '—' }}</div>
              </div>
              <div class="stat-tile">
                <div class="stat-tile__key">History</div>
                <div class="stat-tile__val">{{ meta ? meta.history_window : '—' }}</div>
              </div>
            </div>

            <div class="wire-row">
              <span class="wire-row__key">Model</span>
              <span class="wire-row__val" :title="meta ? meta.provider + ' / ' + (meta.model || 'default') : ''">
                {{ meta ? (meta.model || 'default') : '—' }}
              </span>
            </div>

            <button v-if="meta" class="wire-row" type="button" title="Copy prompt hash"
                    @click="copyValue('prompt', meta.prompt_hash)">
              <span class="wire-row__key">Prompt</span>
              <span class="wire-row__val">
                {{ copiedKey === 'prompt' ? 'đã copy' : meta.prompt_hash.slice(0, 14) }}
              </span>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round">
                <rect x="9" y="9" width="11" height="11" rx="2" />
                <path d="M5 15V5a2 2 0 0 1 2-2h8" />
              </svg>
            </button>

            <button v-if="meta" class="wire-row" type="button" title="Copy tools hash"
                    @click="copyValue('tools', meta.tools_hash)">
              <span class="wire-row__key">Tools</span>
              <span class="wire-row__val">
                {{ copiedKey === 'tools' ? 'đã copy' : meta.tools_hash.slice(0, 14) }}
              </span>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round">
                <rect x="9" y="9" width="11" height="11" rx="2" />
                <path d="M5 15V5a2 2 0 0 1 2-2h8" />
              </svg>
            </button>

            <button v-if="session" class="wire-row" type="button" title="Copy đường dẫn transcript"
                    @click="copyValue('transcript', session.transcript_path)">
              <span class="wire-row__key">Transcript</span>
              <span class="wire-row__val">
                {{ copiedKey === 'transcript' ? 'đã copy' : session.session_id }}
              </span>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round">
                <rect x="9" y="9" width="11" height="11" rx="2" />
                <path d="M5 15V5a2 2 0 0 1 2-2h8" />
              </svg>
            </button>
          </div>
        </section>

        <!-- Tool registry -->
        <section class="panel">
          <button class="panel-head" type="button" :aria-expanded="String(panelOpen.tools)"
                  @click="panelOpen.tools = !panelOpen.tools">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                 class="chevron" :class="{ 'chevron--open': panelOpen.tools }">
              <path d="M9 6l6 6-6 6" />
            </svg>
            <h2 class="panel-title">Tool registry</h2>
            <span class="panel-head__spacer"></span>
            <span class="panel-count">{{ filteredTools.length }}/{{ tools.length }}</span>
          </button>

          <div v-show="panelOpen.tools" class="panel-scroll">
            <div class="filter-sticky">
              <label class="filter-field">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                  <circle cx="11" cy="11" r="6.5" />
                  <path d="m16 16 4.5 4.5" />
                </svg>
                <input v-model="toolQuery" type="search" placeholder="Lọc theo tên hoặc mô tả…" />
              </label>
            </div>

            <div class="panel-body panel-body--flush">
              <div v-for="tool in filteredTools" :key="tool.name" class="tool-item"
                   :style="{ '--tone': toneVarFor(tool.name) }">
                <span class="tool-item__top">
                  <span class="tool-item__name">{{ tool.name }}</span>
                  <span v-if="toolLabel(tool.name)" class="tool-item__label">{{ toolLabel(tool.name) }}</span>
                </span>
                <span class="tool-item__desc" :title="tool.description">{{ tool.description || '(chưa có mô tả)' }}</span>
                <span class="tool-item__params">
                  <span v-for="param in requiredParams(tool)" :key="param.key"
                        class="param-chip" :class="{ 'param-chip--required': param.required }">
                    {{ param.key }}{{ param.required ? '*' : '' }}
                  </span>
                </span>
              </div>

              <div v-if="!tools.length" class="args-empty" style="padding:8px">Chưa nạp được tools.yaml.</div>
              <div v-else-if="!filteredTools.length" class="args-empty" style="padding:8px">
                Không có tool khớp “{{ toolQuery }}”.
              </div>
            </div>
          </div>

          <div class="panel-foot" v-show="panelOpen.tools">
            * = tham số bắt buộc · nguồn: {{ meta ? meta.tools_file_name : 'tools.yaml' }}
          </div>
        </section>

        <!-- Prompt gợi ý -->
        <section class="panel" v-if="promptGroups.length">
          <button class="panel-head" type="button" :aria-expanded="String(panelOpen.prompts)"
                  @click="panelOpen.prompts = !panelOpen.prompts">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                 class="chevron" :class="{ 'chevron--open': panelOpen.prompts }">
              <path d="M9 6l6 6-6 6" />
            </svg>
            <h2 class="panel-title">Câu hỏi mẫu</h2>
          </button>

          <div class="panel-body panel-scroll panel-scroll--sm" v-show="panelOpen.prompts">
            <div v-for="group in promptGroups" :key="group.label" class="prompt-group">
              <div class="prompt-group__label">{{ group.label }}</div>
              <button v-for="item in group.items" :key="item" class="prompt-btn" type="button" @click="usePrompt(item)">
                <span>{{ item }}</span>
              </button>
            </div>
          </div>
        </section>
      </aside>

      <div v-if="sidebarOpen" class="scrim" @click="sidebarOpen = false"></div>

      <!-- ------------------------------- main ------------------------------- -->
      <main class="main">
        <div class="thread" ref="threadEl">
          <div class="thread-inner">
            <div v-if="bootError" class="banner banner--error banner--flush">
              <div>
                <div class="banner__title">Không kết nối được API</div>
                <div class="banner__text">{{ bootError }}</div>
                <div class="banner__text" style="margin-top:6px">
                  Chạy lại server: <code>python api.py --provider openrouter --version v0</code>
                </div>
              </div>
            </div>

            <div v-if="!turns.length && !bootError" class="empty-state">
              <div class="empty-state__mark">
                <svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="4.5" y="6" width="23" height="16" rx="2.5" stroke-width="2.2" />
                  <rect x="11" y="11.5" width="10" height="5" rx="1.2" fill="currentColor" stroke="none" />
                  <path d="M16 22v4M11.5 26h9" stroke-width="2.2" />
                </svg>
              </div>
              <h1>{{ brand.name }}</h1>
              <p>{{ brand.tagline }}</p>
              <div class="empty-hints">
                <button v-for="item in flatPrompts" :key="item" class="prompt-btn" type="button" @click="usePrompt(item)">
                  {{ item }}
                </button>
              </div>
            </div>

            <div v-for="(turn, index) in turns" :key="index" class="turn">
              <div class="msg msg--user">
                <div class="msg__avatar msg__avatar--user">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round">
                    <circle cx="12" cy="8.5" r="3.6" />
                    <path d="M4.8 20a7.2 7.2 0 0 1 14.4 0" />
                  </svg>
                </div>
                <div class="msg__col">
                  <div class="msg__meta">
                    <span class="msg__time">{{ formatTime(turn.at) }}</span>
                    <span class="msg__who">Bạn</span>
                  </div>
                  <div class="bubble bubble--user">{{ turn.user }}</div>
                </div>
              </div>

              <div v-if="turn.pending" class="msg msg--agent">
                <div class="msg__avatar msg__avatar--agent">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round">
                    <rect x="7" y="7" width="10" height="10" rx="2.5" />
                    <path d="M10 2.6v3M14 2.6v3M10 18.4v3M14 18.4v3M2.6 10h3M2.6 14h3M18.4 10h3M18.4 14h3" />
                  </svg>
                </div>
                <div class="msg__col">
                  <div class="msg__meta">
                    <span class="msg__who">{{ brand.name }}</span>
                    <span class="msg__time">đang gọi tool…</span>
                  </div>
                  <div class="bubble bubble--agent">
                    <span class="typing"><span></span><span></span><span></span></span>
                  </div>
                </div>
              </div>

              <template v-else-if="turn.error">
                <div class="banner banner--error banner--flush">
                  <div>
                    <div class="banner__title">Lỗi gọi API</div>
                    <div class="banner__text">{{ turn.error }}</div>
                  </div>
                </div>
              </template>

              <template v-else-if="turn.record">
                <trace-block :rounds="turn.record.rounds || []" :meta="toolMeta" :open="traceOpen" />

                <div v-if="turn.record.status === 'provider_error'" class="banner banner--error">
                  <div>
                    <div class="banner__title">Provider error</div>
                    <div class="banner__text">{{ turn.record.error }}</div>
                  </div>
                </div>

                <div v-for="(event, eventIndex) in writeActions(turn.record)" :key="'w' + eventIndex"
                     class="banner banner--warn">
                  <div>
                    <div class="banner__title">Đã thực hiện hành động ghi dữ liệu</div>
                    <div class="banner__text">
                      <code>{{ event.tool }}</code> —
                      {{ event.result && event.result.order_id ? event.result.order_id : (event.result && event.result.ticket_id ? event.result.ticket_id : 'xem kết quả trong trace') }}
                    </div>
                  </div>
                </div>

                <agent-message v-if="turn.record.assistant_text"
                               :text="turn.record.assistant_text"
                               :name="brand.name"
                               :time="formatTime(turn.record.ended_at)" />

                <div v-if="turn.record.status === 'waiting_for_user'" class="banner banner--info">
                  <div style="flex:1">
                    <div class="banner__title">Agent đang chờ bạn trả lời</div>
                    <div class="banner__text">Trả lời để agent tiếp tục đúng ngữ cảnh.</div>
                    <div v-if="pendingQuestion && pendingQuestion.quick.length && index === turns.length - 1" class="quick-replies">
                      <button v-for="option in pendingQuestion.quick" :key="option" class="btn btn--sm" type="button"
                              :disabled="sending" @click="send(option)">
                        {{ option }}
                      </button>
                    </div>
                  </div>
                </div>

                <div class="turn-foot">
                  <span class="badge">{{ turn.record.status }}</span>
                  <span>{{ turn.record.latency_ms }} ms</span>
                  <span>{{ (turn.record.rounds || []).length }} round</span>
                  <span>{{ (turn.record.tool_events || []).length }} tool call</span>
                  <span class="spacer"></span>
                  <span>{{ meta ? meta.artifact_version : '' }}</span>
                </div>
              </template>
            </div>
          </div>
        </div>

        <!-- ----------------------------- composer ---------------------------- -->
        <div class="composer-wrap">
          <div class="composer">
            <textarea
              ref="composerEl"
              v-model="draft"
              rows="1"
              :disabled="sending || !session"
              placeholder="Hỏi về linh kiện, giá, hoặc yêu cầu đặt mua…"
              @keydown="onComposerKey"
              @input="autoGrow"></textarea>
            <button class="btn btn--primary" type="button" :disabled="sending || !draft.trim() || !session" @click="send()">
              {{ sending ? 'Đang chạy…' : 'Gửi' }}
            </button>
          </div>
          <div class="composer-foot">
            <span><kbd>Enter</kbd> gửi · <kbd>Shift</kbd>+<kbd>Enter</kbd> xuống dòng</span>
            <span class="spacer"></span>
            <span v-if="session">{{ session.transcript_path }}</span>
          </div>
        </div>
      </main>
    </div>
  `,
});

app.mount('#app');
