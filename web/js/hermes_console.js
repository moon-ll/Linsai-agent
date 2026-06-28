/**
 * hermes_console.js — hermes 控制台前端（cron 列表/启停/手动派活）
 * 零框架依赖，原生 JavaScript，复用 app.js 的 apiGet/apiPost/showToast。
 */

// P2-19: 模块级 reader 引用（供 closeHermesConsole 取消进行中的流）
let _hermesReader = null;
const HERMES_STREAM_TIMEOUT_MS = 120000;

// ============================================
// 面板打开/关闭
// ============================================
function openHermesConsole() {
  if (!document.getElementById('hermes-overlay')) return;
  openModal('hermes-overlay');
  loadHermesStatus();
  loadCronList();
}

function closeHermesConsole() {
  // P2-19: 关闭面板时取消进行中的 hermes 流，避免泄漏
  if (_hermesReader) {
    try { _hermesReader.cancel(); } catch (_) {}
    _hermesReader = null;
  }
  closeModal('hermes-overlay');
}

// ============================================
// 加载状态
// ============================================
async function loadHermesStatus() {
  const el = document.getElementById('hermes-status');
  if (!el) return;
  try {
    const data = await apiGet('/api/hermes/cron');
    const s = data.status || {};
    const parts = [];
    if (s.hermes_cli) parts.push('✓ CLI');
    if (s.linsai_profile) parts.push('✓ profile');
    if (s.gateway_status === 'running') parts.push('✓ 网关');
    parts.push(`${s.cron_jobs_count || 0} 任务`);
    el.textContent = parts.join(' | ');
    el.style.color = 'var(--text-secondary)';
  } catch (e) {
    el.textContent = '✗ 无法连接 hermes';
    el.style.color = 'var(--error-color)';
  }
}

// ============================================
// 加载 cron 列表
// ============================================
async function loadCronList() {
  const container = document.getElementById('hermes-cron-list');
  if (!container) return;
  container.innerHTML = '<p class="text-tertiary fs-085">加载中...</p>';

  try {
    const data = await apiGet('/api/hermes/cron');
    const jobs = data.jobs || [];
    if (!jobs.length) {
      container.innerHTML = '<p class="text-tertiary fs-085">无 cron 任务</p>';
      return;
    }

    let html = '';
    jobs.forEach(job => {
      const isActive = job.status === 'active';
      const statusBadge = isActive
        ? '<span class="text-success">● active</span>'
        : '<span class="text-tertiary">○ paused</span>';
      const lastIcon = job.last_status === 'ok' ? '✅' : (job.last_status ? '⚠️' : '○');

      html += `<div class="pad-8-10 m-6-0 bg-secondary br-6">
        <div style="display:flex;justify-content:space-between;align-items:start;gap:8px;">
          <div class="flex-1">
            <div class="fs-085 fw-500">${escapeHtml(job.name)}</div>
            <div class="fs-075 text-tertiary mt-2">
              ${statusBadge} | ⏰ ${escapeHtml(job.schedule || '?')} | ${lastIcon} ${escapeHtml(job.last_run ? job.last_run.slice(5,16) : '未运行')}
            </div>
          </div>
          <div style="display:flex;gap:4px;flex-shrink:0;">`;
      if (isActive) {
        html += `<button onclick="controlCron('${escapeAttr(job.id)}','pause')" class="pad-3-8 fs-075 cursor-pointer border-default br-4">暂停</button>`;
      } else {
        html += `<button onclick="controlCron('${escapeAttr(job.id)}','resume')" class="pad-3-8 fs-075 cursor-pointer border-default br-4">恢复</button>`;
      }
      html += `<button onclick="controlCron('${escapeAttr(job.id)}','run')" class="pad-3-8 fs-075 cursor-pointer border-default br-4 bg-accent text-white">触发</button>`;
      html += `</div></div></div>`;
    });
    container.innerHTML = html;
  } catch (e) {
    container.innerHTML = `<p class="text-error fs-085">加载失败: ${escapeHtml(e.message)}</p>`;
  }
}

// ============================================
// cron 控制
// ============================================
async function controlCron(jobId, action) {
  const labels = { pause: '暂停', resume: '恢复', run: '触发' };
  showToast(`◐ ${labels[action]}...`, 'info');
  try {
    const result = await apiPost(`/api/hermes/cron/${jobId}/${action}`, {});
    if (result.success) {
      showToast(result.message, 'success');
      loadCronList();
    } else {
      showToast(result.message || '操作失败', 'error');
    }
  } catch (e) {
    showToast(`✗ 操作失败: ${e.message}`, 'error');
  }
}

// ============================================
// 手动派活（hermes agent loop，流式）
// ============================================
function bindHermesRun() {
  const runBtn = document.getElementById('hermes-run');
  const promptInput = document.getElementById('hermes-prompt');
  const outputEl = document.getElementById('hermes-output');
  if (!runBtn || !promptInput) return;

  runBtn.addEventListener('click', async () => {
    const prompt = promptInput.value.trim();
    if (!prompt) {
      showToast('请输入任务', 'info');
      return;
    }

    runBtn.disabled = true;
    runBtn.textContent = '执行中...';
    if (outputEl) {
      outputEl.style.display = 'block';
      outputEl.textContent = '◐ hermes agent 正在工作...\n（agent loop 可能需要 30s-5min）';
    }

    let streamTimeoutId = null;
    let streamDone = false;
    try {
      const resp = await fetch('/api/hermes/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, timeout: 300 }),
      });

      // P2-19: HTTP 错误状态码检查
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        throw new Error(err.error || `HTTP ${resp.status}`);
      }

      const reader = resp.body.getReader();
      _hermesReader = reader;  // P2-19: 保存 reader 引用供关闭时取消
      const decoder = new TextDecoder();
      let buffer = '';
      let fullText = '';

      // P2-19: 120s 超时保护，避免无限等待
      streamTimeoutId = setTimeout(() => {
        if (!streamDone) {
          console.warn('[hermes] 流超时，强制结束');
          try { reader.cancel(); } catch (_) {}
          showToast('hermes 响应超时，请重试', 'error');
          if (outputEl) {
            outputEl.textContent = fullText + '\n\n⚠ 响应超时';
          }
        }
      }, HERMES_STREAM_TIMEOUT_MS);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop();
        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          const dataStr = line.slice(6).trim();
          if (dataStr === '[DONE]') continue;
          try {
            const evt = JSON.parse(dataStr);
            if (evt.type === 'token') {
              fullText += evt.content;
              if (outputEl) {
                outputEl.textContent = fullText;
                outputEl.scrollTop = outputEl.scrollHeight;
              }
            } else if (evt.type === 'done') {
              showToast(evt.success ? '✓ hermes 完成' : '⚠ 完成（可能有错误）', evt.success ? 'success' : 'info');
              // P1-5: hermes 完成后刷新知识库树
              if (typeof renderKbTree === 'function') {
                setTimeout(() => renderKbTree(), 500);
              }
            } else if (evt.type === 'error') {
              showToast(`✗ ${evt.message}`, 'error');
            }
          } catch {}
        }
      }
      streamDone = true;
    } catch (e) {
      showToast(`✗ 执行失败: ${e.message}`, 'error');
    } finally {
      if (streamTimeoutId) clearTimeout(streamTimeoutId);
      _hermesReader = null;
      runBtn.disabled = false;
      runBtn.textContent = '执行';
    }
  });
}

// ============================================
// 初始化绑定（由 app.js 调用）
// ============================================
function bindHermesEvents() {
  document.getElementById('toolbar-hermes')?.addEventListener('click', openHermesConsole);
  document.getElementById('hermes-close')?.addEventListener('click', closeHermesConsole);
  document.getElementById('hermes-overlay')?.addEventListener('click', e => {
    if (e.target === e.currentTarget) closeHermesConsole();
  });
  document.getElementById('hermes-refresh')?.addEventListener('click', () => {
    loadHermesStatus();
    loadCronList();
  });
  bindHermesRun();
}

// v3.5.1: 注册模块初始化
if (typeof ModuleLoader !== 'undefined') {
  ModuleLoader.register('hermes_console', () => {
    if (typeof bindHermesEvents === 'function') bindHermesEvents();
  });
}
