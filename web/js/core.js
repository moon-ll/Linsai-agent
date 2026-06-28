/**
 * core.js — 全局状态、常量、工具函数、API 请求、模态框、Toast、主题
 * 所有模块的基础依赖，必须最先加载
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
  viewingArchive: false,
  sessionKeywords: {},
  currentReader: null,  // P1-10: SSE reader 引用，切换会话时取消
};

const API_BASE = '';

// ============================================
// 阶段标签与图标常量
// ============================================
const STAGE_LABELS_FULL = { seedling: '🌱 幼苗', growing: '🌿 成长中', mature: '🌳 成熟', archived: '📦 归档' };
const STAGE_ICONS = { seedling: '🌱', growing: '🌿', mature: '🌳', archived: '📦' };

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

  const btn = document.getElementById('theme-toggle');
  if (btn) btn.textContent = html.getAttribute('data-theme') === 'dark' ? '🌙' : '🔆';
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
  if (str === null || str === undefined) return '';
  if (typeof str !== 'string') str = String(str);
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// 安全转义函数：用于 HTML 属性值（特别是 onclick/onkeydown 等事件处理器内的参数）
// 相比 escapeHtml，额外转义单引号(')和双引号(")，防止属性闭合或 JS 字符串逃逸注入
function escapeAttr(s) {
  if (s == null) return '';
  return String(s).replace(/&/g,'&amp;').replace(/'/g,'&#39;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// P3-1: 通用 debounce 函数，供各模块复用（替代手动 timer 管理）
function debounce(fn, ms = 300) {
  let timer = null;
  return function(...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), ms);
  };
}

function formatTime(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return isNaN(d.getTime()) ? '' : d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
}

function formatDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return isNaN(d.getTime()) ? '' : d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
}

function renderMarkdown(text) {
  if (!text) return '';
  let html = escapeHtml(text);

  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) => {
    return `<pre><code>${escapeHtml(code.trim())}</code></pre>`;
  });
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
  html = html.replace(/^&gt; (.+)$/gm, '<blockquote>$1</blockquote>');
  // 标题（须在转义后匹配，# 不受 escapeHtml 影响；先 ### 再 ## 再 # 避免误匹配）
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (match, text, url) => {
    // P1-13: 链接协议白名单，防止 javascript: XSS
    const safeUrl = url.trim();
    if (/^(https?:|mailto:|\/|#)/i.test(safeUrl)) {
      return `<a href="${safeUrl}" target="_blank" rel="noopener noreferrer">${text}</a>`;
    }
    return `<span title="不支持的链接协议">${text}</span>`;
  });
  html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
  html = html.replace(/(<li>.+<\/li>\n?)+/g, '<ul>$&</ul>');
  html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');

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
  if (!container) { console.warn('toast-container not found:', message); return; }
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

async function apiPost(path, body, timeoutMs) {
  // P2-16: 支持可选超时
  const controller = timeoutMs ? new AbortController() : null;
  const timer = timeoutMs ? setTimeout(() => controller.abort(), timeoutMs) : null;
  try {
    const res = await fetch(API_BASE + path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: controller?.signal,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || `HTTP ${res.status}`);
    }
    return res.json();
  } catch (e) {
    if (e.name === 'AbortError') throw new Error('请求超时');
    throw e;
  } finally {
    if (timer) clearTimeout(timer);
  }
}

async function apiPut(path, body) {
  const res = await fetch(API_BASE + path, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `HTTP ${res.status}`);
  }
  return res.json();
}

// apiDelete 辅助
async function apiDelete(path) {
  const resp = await fetch(API_BASE + path, { method: 'DELETE' });
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  return resp.json();
}

// ============================================
// 模态框
// ============================================
function openModal(id) { const el = document.getElementById(id); if (el) el.style.display = 'flex'; }
function closeModal(id) { const el = document.getElementById(id); if (el) el.style.display = 'none'; }

// P0-9: Promise 版 confirm，替代原生 confirm()
function confirmModal(message, confirmText = '确定', cancelText = '取消') {
  return new Promise(resolve => {
    showModal(`<div class="mw-360 ta-center">
      <p class="m-16-0 fs-09">${escapeHtml(message)}</p>
      <div class="d-flex gap-8 jc-center">
        <button id="cm-confirm-btn" style="padding:6px 20px;background:var(--error-color);color:#fff;border:none;border-radius:6px;cursor:pointer;">${escapeHtml(confirmText)}</button>
        <button id="cm-cancel-btn" class="pad-6-20 border-default br-6 cursor-pointer">${escapeHtml(cancelText)}</button>
      </div>
    </div>`);
    document.getElementById('cm-cancel-btn').onclick = () => { closeModal('modal-overlay'); resolve(false); };
    document.getElementById('cm-confirm-btn').onclick = () => { closeModal('modal-overlay'); resolve(true); };
  });
}

// P0-9: Promise 版 prompt，替代原生 prompt()
function promptModal(message, placeholder = '') {
  return new Promise(resolve => {
    showModal(`<div class="mw-360 ta-center">
      <p class="m-16-0 fs-09">${escapeHtml(message)}</p>
      <input id="pm-input" type="text" placeholder="${escapeHtml(placeholder)}" class="w-100 pad-8 border-default br-6 mb-12 bg-secondary text-primary" />
      <div class="d-flex gap-8 jc-center">
        <button id="pm-confirm-btn" class="pad-6-20 bg-accent text-white border-none br-6 cursor-pointer">确定</button>
        <button id="pm-cancel-btn" class="pad-6-20 border-default br-6 cursor-pointer">取消</button>
      </div>
    </div>`);
    const input = document.getElementById('pm-input');
    input.focus();
    input.addEventListener('keydown', e => { if (e.key === 'Enter') { closeModal('modal-overlay'); resolve(input.value); } });
    document.getElementById('pm-cancel-btn').onclick = () => { closeModal('modal-overlay'); resolve(null); };
    document.getElementById('pm-confirm-btn').onclick = () => { closeModal('modal-overlay'); resolve(input.value); };
  });
}

function showModal(htmlContent) {
  let overlay = document.getElementById('modal-overlay');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.id = 'modal-overlay';
    overlay.className = 'modal-overlay';
    overlay.innerHTML = '<div class="modal" id="modal-content"></div>';
    document.body.appendChild(overlay);
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) closeModal('modal-overlay');
    });
  }
  const html = (typeof htmlContent === 'string') ? htmlContent : String(htmlContent || '');
  document.getElementById('modal-content').innerHTML = html;
  overlay.style.display = 'flex';
  // P2-11: focus trap — 聚焦到模态框内第一个可交互元素
  setTimeout(() => {
    const focusable = overlay.querySelector('button, input, textarea, select, a[href]');
    if (focusable) focusable.focus();
  }, 50);
}

// P2-11: ESC 关闭模态框
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    // 关闭通用 modal-overlay
    const modalOverlay = document.getElementById('modal-overlay');
    if (modalOverlay && modalOverlay.style.display !== 'none') {
      closeModal('modal-overlay');
      return;
    }
    // 关闭其他 overlay（new-session-modal, agora-modal, edit-message-modal 等）
    const overlays = document.querySelectorAll('[id$="-overlay"], [id$="-modal"]');
    for (const ov of overlays) {
      if (ov.style.display !== 'none' && ov.style.display !== '') {
        ov.style.display = 'none';
        return;
      }
    }
    // 关闭设置抽屉
    const settingsDrawer = document.getElementById('settings-drawer');
    if (settingsDrawer && settingsDrawer.style.display === 'flex') {
      settingsDrawer.style.display = 'none';
      return;
    }
    // 关闭历史侧边栏
    const historySidebar = document.getElementById('history-sidebar');
    if (historySidebar && historySidebar.style.display === 'flex') {
      historySidebar.style.display = 'none';
      return;
    }
  }
});

// P2-14: 全局断网检测
let _offlineBanner = null;
window.addEventListener('offline', () => {
  if (!_offlineBanner) {
    _offlineBanner = document.createElement('div');
    _offlineBanner.style.cssText = 'position:fixed;top:0;left:0;right:0;background:var(--error-color);color:#fff;text-align:center;padding:6px;font-size:0.82rem;z-index:10000;';
    _offlineBanner.textContent = '⚠ 网络已断开，部分功能不可用';
    document.body.appendChild(_offlineBanner);
  }
  _offlineBanner.style.display = 'block';
});
window.addEventListener('online', () => {
  if (_offlineBanner) {
    _offlineBanner.style.display = 'none';
  }
  showToast('✓ 网络已恢复', 'success');
});

// ============================================
// v3.5.1: 极简模块加载器
// 每个模块通过 Loader.register 注册初始化函数，app.js 统一调用 Loader.init()
// ============================================
const ModuleLoader = {
  _modules: [],
  register(name, initFn) {
    this._modules.push({ name, initFn });
  },
  init() {
    let ok = 0, fail = 0;
    this._modules.forEach(m => {
      try {
        if (typeof m.initFn === 'function') m.initFn();
        ok++;
      } catch (e) {
        console.warn(`[ModuleLoader] ${m.name} 初始化失败:`, e);
        fail++;
      }
    });
    return { ok, fail, total: this._modules.length };
  }
};
