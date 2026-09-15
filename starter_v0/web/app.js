const messages = document.querySelector('#messages');
const input = document.querySelector('#messageInput');
const form = document.querySelector('#chatForm');
const count = document.querySelector('#messageCount');
const themeToggle = document.querySelector('#themeToggle');

function setTheme(theme) {
  const isDark = theme === 'dark';
  document.documentElement.dataset.theme = isDark ? 'dark' : 'light';
  themeToggle.setAttribute('aria-pressed', String(isDark));
  themeToggle.setAttribute('aria-label', isDark ? 'Tắt dark mode' : 'Bật dark mode');
  localStorage.setItem('northstar-theme', theme);
}

setTheme(localStorage.getItem('northstar-theme') || 'light');
themeToggle.addEventListener('click', () => {
  setTheme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark');
});

function addMessage(text, type = 'user') {
  const row = document.createElement('div');
  row.className = `message-row ${type === 'user' ? 'user-row' : 'assistant-row'}`;
  const avatar = type === 'user' ? '<div class="message-avatar user-avatar">AL</div>' : '<div class="message-avatar">✦</div>';
  const author = type === 'user' ? 'Bạn' : 'Northstar Assistant';
  row.innerHTML = type === 'user'
    ? `<div class="message-content"><span class="message-author">${author}<time>now</time></span><div class="bubble user-bubble">${escapeHtml(text)}</div></div>${avatar}`
    : `${avatar}<div class="message-content"><span class="message-author">${author}<time>now</time></span><div class="bubble assistant-bubble">${text}</div></div>`;
  messages.appendChild(row);
  messages.scrollTop = messages.scrollHeight;
  count.textContent = String(Number(count.textContent) + 1);
}

function answerFor(text) {
  const lower = text.toLowerCase();
  if (lower.includes('vpn') || lower.includes('dịch vụ') || lower.includes('email') || lower.includes('wifi')) {
    return '<span class="success-dot"></span> Mình đã nhận yêu cầu. Ở bước tiếp theo, agent sẽ gọi tool phù hợp để kiểm tra trạng thái dịch vụ và trả lại kết quả có bằng chứng.<div class="result-grid"><div><small>STATUS</small><b class="green-text">Ready to check</b></div><div><small>VERSION</small><b>v0</b></div></div>Bạn có thể tiếp tục mô tả môi trường hoặc thiết bị liên quan nếu cần.';
  }
  if (lower.includes('laptop') || lower.includes('thiết bị') || lower.includes('lt-')) {
    return 'Mình có thể kiểm tra thiết bị cho bạn. Vui lòng cung cấp mã asset (ví dụ <b>LT-204</b>) và nhóm kiểm tra nếu bạn muốn tập trung vào network, VPN, security, hardware hoặc software.';
  }
  return 'Mình có thể hỗ trợ kiểm tra dịch vụ, chẩn đoán thiết bị, tìm hướng dẫn nội bộ hoặc tạo ticket. Bạn muốn bắt đầu với nội dung nào?';
}

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, (char) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[char]));
}

form.addEventListener('submit', (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  addMessage(text);
  input.value = '';
  window.setTimeout(() => addMessage(answerFor(text), 'assistant'), 450);
});

document.querySelectorAll('[data-prompt]').forEach((button) => {
  button.addEventListener('click', () => {
    input.value = button.dataset.prompt;
    input.focus();
  });
});

document.querySelectorAll('[data-collapsible] .tool-event-header').forEach((header) => {
  header.addEventListener('click', () => {
    const body = header.nextElementSibling;
    body.hidden = !body.hidden;
    header.querySelector('.chevron').textContent = body.hidden ? '›' : '⌄';
  });
});

document.querySelector('#newChatButton').addEventListener('click', () => {
  messages.innerHTML = '<div class="message-row assistant-row"><div class="message-avatar">✦</div><div class="message-content"><span class="message-author">Northstar Assistant <time>now</time></span><div class="bubble assistant-bubble">Cuộc hội thoại mới đã sẵn sàng. Bạn cần hỗ trợ điều gì?</div></div></div>';
  count.textContent = '1';
  input.focus();
});

document.querySelector('.close-tip').addEventListener('click', (event) => {
  event.currentTarget.closest('.tip-card').remove();
});

document.querySelectorAll('.nav-item[data-view]').forEach((item) => {
  item.addEventListener('click', () => {
    document.querySelectorAll('.nav-item[data-view]').forEach((nav) => nav.classList.remove('active'));
    item.classList.add('active');
  });
});
