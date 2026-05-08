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

  container.innerHTML = sessions.map(s => `
    <div class="session-item ${s.session_id === State.currentSessionId ? 'active' : ''}"
         data-id="${escapeHtml(s.session_id)}">
      <div class="session-topic">${escapeHtml(s.topic || '未命名会话')}</div>
      <div class="session-meta">
        <span>${formatDate(s.last_active)}</span>
        <span>${s.message_count || 0} 条</span>
      </div>
    </div>
  `).join('');

  // 绑定点击事件
  container.querySelectorAll('.session-item').forEach(el => {
    el.addEventListener('click', () => {
      const sid = el.dataset.id;
      switchSession(sid);
    });
  });
}

async function switchSession(sessionId) {
  State.currentSessionId = sessionId;
  renderSessionList();

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
        appendMessage(msg.role, msg.content, msg.timestamp, false);
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
function appendMessage(role, content, timestamp, animate = true) {
  const container = document.getElementById('messages');
  const div = document.createElement('div');
  div.className = `message ${role}`;

  const avatar = role === 'user' ? '你' : '林';
  const time = timestamp ? formatTime(timestamp) : formatTime(new Date().toISOString());

  div.innerHTML = `
    <div class="message-avatar">${avatar}</div>
    <div>
      <div class="message-bubble">${renderMarkdown(content)}</div>
      <div class="message-time">${time}</div>
    </div>
  `;

  if (!animate) {
    div.style.animation = 'none';
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
          } else if (data.type === 'error') {
            throw new Error(data.message);
          }
        } catch (e) {
          // 忽略解析失败的行
        }
      }
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
    State.isStreaming = false;
    document.getElementById('typing-indicator').style.display = 'none';
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
        input.value = '/agora ';
        input.focus();
      } else if (cmd === '/summary') {
        sendMessage('/summary');
      }
    });
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

  // 归档按钮
  document.getElementById('archived-btn').addEventListener('click', () => {
    showToast('归档功能请使用终端: python3 scripts/copilot_engine.py --archive <ID>', 'warning', 5000);
  });

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

  // 检查主动提醒
  await checkHeartbeat();

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
