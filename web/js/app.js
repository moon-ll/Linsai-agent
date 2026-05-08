/**
 * LinSai-CoPilot Web 前端逻辑
 * 零框架依赖，原生 JavaScript
 */

// ============================================
// 全局状态
// ============================================
const State = {
  currentSessionId: null,
  currentMode: 'co-working',
  sessions: [],
  tasks: [],
  isStreaming: false,
  theme: localStorage.getItem('linsai-theme') || 'auto',
  autonomy: localStorage.getItem('linsai-autonomy') || 'suggest',
  viewingArchive: false,  // 是否正在查看历史会话
  sessionKeywords: {},    // 缓存会话关键词
};

const API_BASE = '';

// ============================================
// 主题管理
// ============================================
function applyTheme(theme) {
  const html = document.documentElement;
  if (theme === 'auto') {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    html.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
  } else {
    html.setAttribute('data-theme', theme);
  }
  State.theme = theme;
  localStorage.setItem('linsai-theme', theme);

  // 更新按钮图标
  const btn = document.getElementById('theme-toggle');
  btn.textContent = html.getAttribute('data-theme') === 'dark' ? '🌙' : '🔆';
}

function toggleTheme() {
  const html = document.documentElement;
  const current = html.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  applyTheme(next);
}

// ============================================
// 工具函数
// ============================================
function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function formatTime(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
}

function formatDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
}

/**
 * 轻量级 Markdown 渲染器
 * 支持：段落、粗体、斜体、代码块、行内代码、列表、引用、链接
 */
function renderMarkdown(text) {
  if (!text) return '';

  let html = escapeHtml(text);

  // 代码块
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) => {
    return `<pre><code>${escapeHtml(code.trim())}</code></pre>`;
  });

  // 行内代码
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

  // 粗体
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

  // 斜体
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');

  // 引用
  html = html.replace(/^&gt; (.+)$/gm, '<blockquote>$1</blockquote>');

  // 链接
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');

  // 无序列表
  html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
  html = html.replace(/(<li>.+<\/li>\n?)+/g, '<ul>$&</ul>');

  // 有序列表
  html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');

  // 段落（按空行分段）
  const paragraphs = html.split(/\n\n+/);
  html = paragraphs.map(p => {
    p = p.trim();
    if (!p) return '';
    if (p.startsWith('<') && !p.startsWith('<li>')) return p;
    return `<p>${p.replace(/\n/g, '<br>')}</p>`;
  }).join('');

  return html;
}

// ============================================
// Toast 提醒
// ============================================
function showToast(message, type = 'success', duration = 3000) {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(30px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// ============================================
// API 请求
// ============================================
async function apiGet(path) {
  const res = await fetch(API_BASE + path);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

async function apiPost(path, body) {
  const res = await fetch(API_BASE + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `HTTP ${res.status}`);
  }
  return res.json();
}

// ============================================
// 会话管理
// ============================================
async function loadSessions() {
  try {
    State.sessions = await apiGet('/api/sessions');
    renderSessionList();
  } catch (e) {
    console.error('加载会话失败:', e);
    showToast('加载会话失败', 'error');
  }
}

function renderSessionList() {
  const container = document.getElementById('session-list');
  const search = document.getElementById('session-search').value.toLowerCase();

  let sessions = State.sessions;
  if (search) {
    sessions = sessions.filter(s =>
      (s.topic || '').toLowerCase().includes(search)
    );
  }

  container.innerHTML = sessions.map(s => {
    const kws = State.sessionKeywords[s.session_id] || [];
    const kwHtml = kws.length > 0
      ? `<div class="keyword-tags">${kws.slice(0, 4).map(k => `<span class="keyword-tag">${escapeHtml(k)}</span>`).join('')}</div>`
      : '';
    return `
    <div class="session-item ${s.session_id === State.currentSessionId && !State.viewingArchive ? 'active' : ''}"
         data-id="${escapeHtml(s.session_id)}">
      <div class="session-topic">${escapeHtml(s.topic || '未命名会话')}</div>
      <div class="session-meta">
        <span>${formatDate(s.last_active)}</span>
        <span>${s.message_count || 0} 条</span>
      </div>
      ${kwHtml}
    </div>
  `}).join('');

  // 绑定点击事件 — 点击会话列表 = 续接对话（不是只读浏览）
  container.querySelectorAll('.session-item').forEach(el => {
    el.addEventListener('click', () => {
      const sid = el.dataset.id;
      switchSession(sid);
    });
  });
}

async function switchSession(sessionId) {
  State.currentSessionId = sessionId;
  State.viewingArchive = false;
  renderSessionList();

  // 隐藏归档头部，显示输入区
  document.getElementById('chat-archive-header').style.display = 'none';
  document.querySelector('.input-area').style.display = 'block';

  // 隐藏欢迎页
  document.getElementById('welcome-screen').style.display = 'none';
  document.getElementById('messages').innerHTML = '';

  // 加载消息
  try {
    const data = await apiGet(`/api/sessions/${encodeURIComponent(sessionId)}/messages`);
    State.currentMode = data.mode || 'co-working';
    updateModeBadge(State.currentMode);

    if (data.messages && data.messages.length > 0) {
      data.messages.forEach(msg => {
        appendMessage(msg.role, msg.content, msg.timestamp, false, msg.msg_id);
      });
      scrollToBottom();
    } else {
      // 空会话显示欢迎语
      appendMessage('assistant', `你好，我是林赛。\n\n我们今天聊「${data.topic}」？先画个框图，说说你的整体思路。`, null, false);
    }

    updateStatus(`已加载: ${data.topic || sessionId}`);
  } catch (e) {
    console.error('加载消息失败:', e);
    showToast('加载消息失败', 'error');
  }

  // 加载任务
  loadTasks();
}

// ============================================
// 历史会话查看（只读模式）
// ============================================
async function viewArchiveSession(sessionId) {
  State.viewingArchive = true;
  renderSessionList();

  // 显示归档头部，隐藏输入区
  document.getElementById('chat-archive-header').style.display = 'flex';
  document.querySelector('.input-area').style.display = 'none';
  document.getElementById('welcome-screen').style.display = 'none';
  document.getElementById('messages').innerHTML = '';

  try {
    const data = await apiGet(`/api/sessions/${encodeURIComponent(sessionId)}/messages`);
    document.getElementById('archive-topic').textContent = data.topic || sessionId;
    document.getElementById('archive-meta').textContent = `${data.messages?.length || 0} 条消息 · ${data.mode || 'co-working'}`;

    if (data.messages && data.messages.length > 0) {
      data.messages.forEach(msg => {
        appendMessage(msg.role, msg.content, msg.timestamp, false, msg.msg_id);
      });
      scrollToBottom();
    } else {
      appendMessage('assistant', '（此会话暂无消息）', null, false);
    }

    updateStatus(`查看历史: ${data.topic || sessionId}`);
  } catch (e) {
    console.error('加载历史失败:', e);
    showToast('加载历史失败', 'error');
  }
}

function backToCurrentSession() {
  if (State.currentSessionId) {
    State.viewingArchive = false;
    switchSession(State.currentSessionId);
  }
}

// ============================================
// 历史搜索
// ============================================
async function searchHistory() {
  const input = document.getElementById('history-search-input');
  const query = input.value.trim();
  const container = document.getElementById('history-results');

  if (!query) {
    container.innerHTML = '<p class="empty">输入关键词搜索历史记录</p>';
    return;
  }

  container.innerHTML = '<p class="empty">◐ 搜索中…</p>';

  try {
    const data = await apiGet(`/api/history?q=${encodeURIComponent(query)}`);
    const results = data.results || [];

    if (results.length === 0) {
      container.innerHTML = '<p class="empty">未找到匹配记录</p>';
      return;
    }

    container.innerHTML = results.map(r => `
      <div class="history-result-item" data-session="${escapeHtml(r.session_id)}">
        <div class="result-topic">${escapeHtml(r.topic)}</div>
        <div class="result-preview">${escapeHtml(r.content_preview)}</div>
        <div class="result-meta">${r.role === 'user' ? '你' : '林赛'} · ${formatDate(r.timestamp)}</div>
      </div>
    `).join('');

    container.querySelectorAll('.history-result-item').forEach(el => {
      el.addEventListener('click', () => {
        const sid = el.dataset.session;
        viewArchiveSession(sid);
      });
    });
  } catch (e) {
    console.error('搜索失败:', e);
    container.innerHTML = '<p class="empty">搜索失败</p>';
  }
}

// ============================================
// 加载会话关键词
// ============================================
async function loadSessionKeywords() {
  for (const s of State.sessions) {
    try {
      const data = await apiGet(`/api/sessions/${encodeURIComponent(s.session_id)}/keywords`);
      State.sessionKeywords[s.session_id] = data.keywords || [];
    } catch (e) {
      State.sessionKeywords[s.session_id] = [];
    }
  }
  renderSessionList();
}

async function createNewSession(topic, mode) {
  try {
    const data = await apiPost('/api/sessions', { topic, mode });
    State.sessions.unshift(data);
    renderSessionList();
    switchSession(data.session_id);
    showToast('会话已创建');
  } catch (e) {
    console.error('创建会话失败:', e);
    showToast('创建会话失败', 'error');
  }
}

// ============================================
// 消息渲染
// ============================================
function appendMessage(role, content, timestamp, animate = true, msgId = null) {
  const container = document.getElementById('messages');
  const div = document.createElement('div');
  div.className = `message ${role}`;
  if (msgId) div.dataset.msgId = msgId;

  const avatar = role === 'user' ? '你' : '林';
  const time = timestamp ? formatTime(timestamp) : formatTime(new Date().toISOString());

  // 只有用户消息显示编辑/删除按钮
  const actions = role === 'user' && msgId ? `
    <div class="message-actions">
      <button class="msg-action-btn" data-action="edit">编辑</button>
      <button class="msg-action-btn" data-action="delete">删除</button>
    </div>
  ` : '';

  div.innerHTML = `
    <div class="message-avatar">${avatar}</div>
    <div>
      <div class="message-bubble">${renderMarkdown(content)}</div>
      ${actions}
      <div class="message-time">${time}</div>
    </div>
  `;

  if (!animate) {
    div.style.animation = 'none';
  }

  // 绑定操作按钮事件
  if (msgId) {
    div.querySelectorAll('.msg-action-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const action = btn.dataset.action;
        if (action === 'edit') openEditMessage(msgId, content);
        if (action === 'delete') deleteMessage(msgId);
      });
    });
  }

  container.appendChild(div);
  scrollToBottom();
  return div;
}

function scrollToBottom() {
  const container = document.getElementById('messages');
  container.scrollTop = container.scrollHeight;
}

// ============================================
// SSE 流式发送消息
// ============================================
async function sendMessage(content) {
  if (!State.currentSessionId) {
    showToast('请先创建或选择一个会话', 'warning');
    return;
  }
  if (State.isStreaming) {
    showToast('林赛正在回复，请稍候', 'warning');
    return;
  }
  if (!content.trim()) return;

  // 显示用户消息
  appendMessage('user', content);
  document.getElementById('message-input').value = '';

  // 显示打字指示器
  State.isStreaming = true;
  document.getElementById('typing-indicator').style.display = 'flex';
  updateStatus('林赛正在思考…');

  // 创建林赛消息占位
  const assistantDiv = appendMessage('assistant', '', null, true);
  const bubble = assistantDiv.querySelector('.message-bubble');
  bubble.innerHTML = ''; // 清空，准备流式填充

  // 超时保护：120 秒后强制重置
  const STREAM_TIMEOUT_MS = 120000;
  let streamTimeoutId = null;

  try {
    const res = await fetch(API_BASE + `/api/sessions/${encodeURIComponent(State.currentSessionId)}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content, mode: State.currentMode }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || `HTTP ${res.status}`);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let fullText = '';
    let streamDone = false;

    // 设置超时
    streamTimeoutId = setTimeout(() => {
      if (!streamDone) {
        console.warn('[SSE] 流超时，强制结束');
        try { reader.cancel(); } catch (_) {}
        State.isStreaming = false;
        document.getElementById('typing-indicator').style.display = 'none';
        updateStatus('响应超时');
        showToast('林赛响应超时，请重试', 'error');
      }
    }, STREAM_TIMEOUT_MS);

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        const dataStr = line.slice(6);
        if (dataStr === '[DONE]') continue;

        try {
          const data = JSON.parse(dataStr);
          if (data.type === 'token') {
            fullText += data.content;
            bubble.innerHTML = renderMarkdown(fullText);
            scrollToBottom();
          } else if (data.type === 'done') {
            streamDone = true;
            break; // 收到 done 立即退出，不等待连接关闭
          } else if (data.type === 'error') {
            throw new Error(data.message);
          }
        } catch (e) {
          if (e.message && e.message !== 'Unexpected end of JSON input') {
            console.warn('[SSE] 解析异常:', e.message);
          }
        }
      }

      if (streamDone) break;
    }

    // 最终渲染确保 Markdown 完整解析
    bubble.innerHTML = renderMarkdown(fullText);
    updateStatus('就绪');

    // 刷新会话列表（更新消息数）
    loadSessions();

  } catch (e) {
    console.error('发送消息失败:', e);
    bubble.innerHTML = `<p style="color:var(--error-color)">✗ 发送失败: ${escapeHtml(e.message)}</p>`;
    updateStatus('发送失败');
  } finally {
    if (streamTimeoutId) clearTimeout(streamTimeoutId);
    State.isStreaming = false;
    document.getElementById('typing-indicator').style.display = 'none';
    console.log('[SSE] 流已结束，状态已重置');
  }
}

// ============================================
// 文件上传
// ============================================
async function uploadFiles(files) {
  if (!files || files.length === 0) return;

  const progressBar = document.getElementById('upload-progress');
  const progressFill = document.getElementById('progress-fill');
  const progressText = document.getElementById('progress-text');
  progressBar.style.display = 'flex';

  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    const pct = Math.round(((i) / files.length) * 100);
    progressFill.style.width = pct + '%';
    progressText.textContent = pct + '%';

    try {
      const isText = file.type.startsWith('text/') || file.name.endsWith('.md') || file.name.endsWith('.txt');
      let content, isBase64;

      if (isText) {
        content = await file.text();
        isBase64 = false;
      } else {
        const arrayBuffer = await file.arrayBuffer();
        const bytes = new Uint8Array(arrayBuffer);
        let binary = '';
        for (let b of bytes) binary += String.fromCharCode(b);
        content = btoa(binary);
        isBase64 = true;
      }

      const category = file.name.match(/\.(pdf|doc|docx)$/i) ? 'papers' : 'notes';
      const result = await apiPost('/api/upload', {
        filename: file.name,
        content,
        category,
        is_base64: isBase64,
      });

      if (result.success) {
        showToast(`已上传: ${result.filename}`);
        // 在对话中插入文件引用
        if (State.currentSessionId) {
          const card = `
📎 **文件已上传**\n\n` +
            `- 名称: ${result.filename}\n` +
            `- 位置: ${result.path}\n` +
            (result.preview ? `- 预览: ${result.preview.substring(0, 80)}…\n` : '') +
            `\n使用 \`/read ${result.path}\` 读取全文。`;
          appendMessage('assistant', card, null, true);
        }
        loadReferences();
      } else {
        showToast(`上传失败: ${result.error}`, 'error');
      }
    } catch (e) {
      console.error('上传失败:', e);
      showToast(`上传失败: ${e.message}`, 'error');
    }
  }

  progressFill.style.width = '100%';
  progressText.textContent = '100%';
  setTimeout(() => {
    progressBar.style.display = 'none';
    progressFill.style.width = '0%';
  }, 800);
}

// ============================================
// 文献列表
// ============================================
async function loadReferences() {
  try {
    const refs = await apiGet('/api/references');
    renderReferenceList(refs);
  } catch (e) {
    console.error('加载文献失败:', e);
  }
}

function renderReferenceList(refs) {
  const container = document.getElementById('reference-list');
  if (!refs || refs.length === 0) {
    container.innerHTML = '<p class="empty">暂无引用</p>';
    return;
  }
  container.innerHTML = refs.slice(0, 10).map(r => `
    <div class="reference-item" data-path="${escapeHtml(r.path || '')}">
      📄 ${escapeHtml(r.title || r.filename || '未命名')}
    </div>
  `).join('');

  container.querySelectorAll('.reference-item').forEach(el => {
    el.addEventListener('click', () => {
      const path = el.dataset.path;
      if (path) {
        const input = document.getElementById('message-input');
        input.value = `/read ${path}`;
        input.focus();
      }
    });
  });
}

// ============================================
// Agora 导出
// ============================================
const AGORA_PERSONAS = [
  '费曼', '狄拉克', '爱因斯坦', '玻尔', '海森堡',
  '薛定谔', '泡利', '冯·诺依曼', '居里夫人', '普朗克',
  '玻尔兹曼', '麦克斯韦', '高斯', '欧拉', '希尔伯特',
  '诺特', '杨振宁', '李政道', '盖尔曼', '费米',
];

let selectedPersonas = [];

function renderPersonaGrid() {
  const grid = document.getElementById('persona-grid');
  grid.innerHTML = AGORA_PERSONAS.map(p => `
    <div class="persona-item" data-name="${escapeHtml(p)}">${escapeHtml(p)}</div>
  `).join('');

  grid.querySelectorAll('.persona-item').forEach(el => {
    el.addEventListener('click', () => {
      const name = el.dataset.name;
      if (el.classList.contains('selected')) {
        el.classList.remove('selected');
        selectedPersonas = selectedPersonas.filter(x => x !== name);
      } else {
        el.classList.add('selected');
        selectedPersonas.push(name);
      }
    });
  });
}

async function handleAgoraExport() {
  if (!State.currentSessionId) {
    showToast('请先选择一个会话', 'warning');
    return;
  }
  if (selectedPersonas.length === 0) {
    showToast('请至少选择一位历史人物', 'warning');
    return;
  }

  try {
    document.getElementById('confirm-agora').textContent = '导出中…';
    const data = await apiPost('/api/agora', {
      session_id: State.currentSessionId,
      topic: '',
      personas: selectedPersonas,
    });
    showToast(`Agora 导出成功: ${data.path}`);
    document.getElementById('agora-modal').style.display = 'none';
  } catch (e) {
    console.error('Agora 导出失败:', e);
    showToast(`导出失败: ${e.message}`, 'error');
  } finally {
    document.getElementById('confirm-agora').textContent = '导出';
  }
}

// ============================================
// 消息编辑/删除
// ============================================
let editingMsgId = null;

function openEditMessage(msgId, content) {
  editingMsgId = msgId;
  document.getElementById('edit-message-content').value = content;
  document.getElementById('edit-message-modal').style.display = 'flex';
}

async function saveEditMessage() {
  if (!editingMsgId || !State.currentSessionId) return;
  const newContent = document.getElementById('edit-message-content').value.trim();
  if (!newContent) {
    showToast('内容不能为空', 'warning');
    return;
  }

  try {
    await fetch(`${API_BASE}/api/sessions/${encodeURIComponent(State.currentSessionId)}/messages/${editingMsgId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: newContent }),
    });

    // 更新 DOM
    const msgDiv = document.querySelector(`.message[data-msg-id="${editingMsgId}"]`);
    if (msgDiv) {
      msgDiv.querySelector('.message-bubble').innerHTML = renderMarkdown(newContent);
      // 更新编辑按钮的 content 引用
      const editBtn = msgDiv.querySelector('[data-action="edit"]');
      if (editBtn) {
        editBtn.replaceWith(editBtn.cloneNode(true));
        msgDiv.querySelector('[data-action="edit"]').addEventListener('click', (e) => {
          e.stopPropagation();
          openEditMessage(editingMsgId, newContent);
        });
      }
    }

    showToast('消息已更新');
    document.getElementById('edit-message-modal').style.display = 'none';
    editingMsgId = null;
  } catch (e) {
    console.error('编辑失败:', e);
    showToast('编辑失败', 'error');
  }
}

async function deleteMessage(msgId) {
  if (!confirm('确定删除这条消息？')) return;
  if (!State.currentSessionId) return;

  try {
    await fetch(`${API_BASE}/api/sessions/${encodeURIComponent(State.currentSessionId)}/messages/${msgId}`, {
      method: 'DELETE',
    });

    const msgDiv = document.querySelector(`.message[data-msg-id="${msgId}"]`);
    if (msgDiv) msgDiv.remove();
    showToast('消息已删除');
  } catch (e) {
    console.error('删除失败:', e);
    showToast('删除失败', 'error');
  }
}

// ============================================
// 任务面板
// ============================================
async function loadTasks() {
  try {
    State.tasks = await apiGet('/api/tasks');
    renderTaskList();
  } catch (e) {
    console.error('加载任务失败:', e);
  }
}

function renderTaskList() {
  const container = document.getElementById('task-list');
  if (!State.tasks || State.tasks.length === 0) {
    container.innerHTML = '<p class="empty">暂无任务</p>';
    return;
  }

  container.innerHTML = State.tasks.slice(0, 8).map(t => {
    const statusClass = t.status === 'active' ? 'status-active' :
                        t.status === 'completed' ? 'status-completed' :
                        t.due_date && new Date(t.due_date) < new Date() ? 'status-overdue' : '';
    return `
      <div class="task-item ${statusClass}">
        <div class="task-title">${escapeHtml(t.title || '未命名')}</div>
        <div class="task-meta">
          ${t.due_date ? formatDate(t.due_date) : '无截止日期'}
          · ${t.priority || '普通'}
        </div>
      </div>
    `;
  }).join('');
}

// ============================================
// 主动提醒
// ============================================
async function checkHeartbeat() {
  try {
    const data = await apiGet('/api/heartbeat');
    if (data.reminders && data.reminders.length > 0) {
      data.reminders.forEach(r => showToast(r, 'warning', 6000));
    }
  } catch (e) {
    // 静默失败
  }
}

// ============================================
// UI 更新
// ============================================
function updateModeBadge(mode) {
  const map = {
    'co-working': '并肩工作',
    'deep-talk': '深度对话',
    'quick-check': '快速验证',
  };
  document.getElementById('mode-badge').textContent = map[mode] || mode;
}

function updateStatus(text) {
  document.getElementById('status-text').textContent = text;
}

// ============================================
// 事件绑定
// ============================================
function bindEvents() {
  // 主题切换
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);

  // 设置面板
  document.getElementById('settings-toggle').addEventListener('click', () => {
    document.getElementById('settings-drawer').style.display = 'flex';
    document.getElementById('theme-select').value = State.theme;
    document.getElementById('autonomy-select').value = State.autonomy;
  });
  document.getElementById('close-settings').addEventListener('click', () => {
    document.getElementById('settings-drawer').style.display = 'none';
  });
  document.getElementById('settings-drawer').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) {
      e.currentTarget.style.display = 'none';
    }
  });

  // 主题选择
  document.getElementById('theme-select').addEventListener('change', (e) => {
    applyTheme(e.target.value);
  });

  // 自主级别选择
  document.getElementById('autonomy-select').addEventListener('change', (e) => {
    State.autonomy = e.target.value;
    localStorage.setItem('linsai-autonomy', e.target.value);
    showToast(`自主级别已设为: ${e.target.value}`);
  });

  // 设置面板内备份按钮
  document.getElementById('drawer-backup-btn').addEventListener('click', () => {
    showToast('请在终端运行: python3 scripts/backup_manager.py', 'warning', 5000);
  });

  // 新建会话
  document.getElementById('new-session-btn').addEventListener('click', () => {
    document.getElementById('new-session-modal').style.display = 'flex';
    document.getElementById('new-session-topic').focus();
  });
  document.getElementById('cancel-new-session').addEventListener('click', () => {
    document.getElementById('new-session-modal').style.display = 'none';
  });
  document.getElementById('confirm-new-session').addEventListener('click', () => {
    const topic = document.getElementById('new-session-topic').value.trim();
    const mode = document.getElementById('new-session-mode').value;
    if (!topic) {
      showToast('请输入会话主题', 'warning');
      return;
    }
    createNewSession(topic, mode);
    document.getElementById('new-session-modal').style.display = 'none';
    document.getElementById('new-session-topic').value = '';
  });
  document.getElementById('new-session-modal').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) {
      e.currentTarget.style.display = 'none';
    }
  });
  document.getElementById('new-session-topic').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      document.getElementById('confirm-new-session').click();
    }
  });

  // 会话搜索
  document.getElementById('session-search').addEventListener('input', renderSessionList);

  // 发送消息
  document.getElementById('send-btn').addEventListener('click', () => {
    const input = document.getElementById('message-input');
    sendMessage(input.value);
  });
  document.getElementById('message-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(e.target.value);
    }
  });

  // 快捷命令按钮
  document.querySelectorAll('.cmd-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const cmd = btn.dataset.cmd;
      const input = document.getElementById('message-input');
      if (cmd === '/mode') {
        showToast('模式切换请在新建会话时选择', 'warning');
      } else if (cmd === '/read') {
        input.value = '/read ';
        input.focus();
      } else if (cmd === '/agora') {
        selectedPersonas = [];
        renderPersonaGrid();
        document.getElementById('agora-modal').style.display = 'flex';
      } else if (cmd === '/summary') {
        sendMessage('/summary');
      }
    });
  });

  // Agora 弹窗
  document.getElementById('cancel-agora').addEventListener('click', () => {
    document.getElementById('agora-modal').style.display = 'none';
  });
  document.getElementById('confirm-agora').addEventListener('click', handleAgoraExport);
  document.getElementById('agora-modal').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) {
      e.currentTarget.style.display = 'none';
    }
  });

  // 编辑消息弹窗
  document.getElementById('cancel-edit-message').addEventListener('click', () => {
    document.getElementById('edit-message-modal').style.display = 'none';
    editingMsgId = null;
  });
  document.getElementById('confirm-edit-message').addEventListener('click', saveEditMessage);
  document.getElementById('edit-message-modal').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) {
      e.currentTarget.style.display = 'none';
      editingMsgId = null;
    }
  });

  // 文件上传
  const uploadZone = document.getElementById('upload-zone');
  const fileInput = document.getElementById('file-input');

  document.getElementById('upload-btn').addEventListener('click', () => {
    fileInput.click();
  });

  fileInput.addEventListener('change', (e) => {
    uploadFiles(e.target.files);
    fileInput.value = ''; // 重置，允许重复选择同一文件
  });

  uploadZone.addEventListener('click', () => fileInput.click());

  uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('drag-over');
  });
  uploadZone.addEventListener('dragleave', () => {
    uploadZone.classList.remove('drag-over');
  });
  uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('drag-over');
    if (e.dataTransfer.files.length > 0) {
      uploadFiles(e.dataTransfer.files);
    }
  });

  // 快速开始按钮
  document.querySelectorAll('.quick-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const topic = btn.dataset.topic;
      createNewSession(topic, 'co-working');
    });
  });

  // 移动端侧边栏切换
  document.getElementById('sidebar-toggle').addEventListener('click', () => {
    document.getElementById('left-sidebar').classList.toggle('open');
  });

  // 归档按钮 → 打开历史搜索侧边栏
  document.getElementById('archived-btn').addEventListener('click', () => {
    document.getElementById('history-sidebar').style.display = 'flex';
  });

  // 顶部栏"查看历史记录"按钮 → 只读浏览当前会话
  document.getElementById('view-history-btn').addEventListener('click', () => {
    if (!State.currentSessionId) {
      showToast('请先选择一个会话', 'warning');
      return;
    }
    viewArchiveSession(State.currentSessionId);
  });

  // 关闭历史搜索
  document.getElementById('close-history').addEventListener('click', () => {
    document.getElementById('history-sidebar').style.display = 'none';
  });

  // 历史搜索
  document.getElementById('history-search-btn').addEventListener('click', searchHistory);
  document.getElementById('history-search-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') searchHistory();
  });

  // 返回当前会话
  document.getElementById('back-to-current').addEventListener('click', backToCurrentSession);

  // 底部按钮
  document.getElementById('backup-btn').addEventListener('click', () => {
    showToast('请在终端运行: python3 scripts/backup_manager.py', 'warning', 5000);
  });
  document.getElementById('export-btn').addEventListener('click', () => {
    showToast('导出功能开发中', 'warning');
  });

  // 监听系统主题变化
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (State.theme === 'auto') {
      applyTheme('auto');
    }
  });

  // 全局拖拽上传（拖拽到页面任意位置）
  document.addEventListener('dragover', (e) => {
    if (e.dataTransfer.types.includes('Files')) {
      uploadZone.classList.add('drag-over');
    }
  });
  document.addEventListener('dragleave', (e) => {
    if (e.relatedTarget === null) {
      uploadZone.classList.remove('drag-over');
    }
  });
  document.addEventListener('drop', (e) => {
    uploadZone.classList.remove('drag-over');
  });
}

// ============================================
// 初始化
// ============================================
async function init() {
  // 应用主题
  applyTheme(State.theme);

  // 加载版本
  try {
    const data = await apiGet('/api/version');
    document.getElementById('version-label').textContent = data.version;
  } catch (e) {
    console.error('获取版本失败:', e);
  }

  // 加载会话
  await loadSessions();

  // 加载会话关键词（异步，不阻塞）
  loadSessionKeywords();

  // 检查主动提醒
  await checkHeartbeat();

  // 加载文献
  loadReferences();

  // 绑定事件
  bindEvents();

  // 检查是否有活跃会话，有则自动选中最新
  if (State.sessions.length > 0) {
    const active = State.sessions.find(s => s.status === 'active') || State.sessions[0];
    // 不自动切换，让用户选择
  }

  console.log('✓ LinSai Web 界面已就绪');
}

// 启动
document.addEventListener('DOMContentLoaded', init);
