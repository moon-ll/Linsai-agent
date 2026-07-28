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

// v6.7.7: hermes 工作台页面渲染（新风格）
async function initHermesWorkspace() {
  const container = document.getElementById('hermes-workspace-content');
  if (!container) return;

  container.innerHTML = `
    <div class="hw-header">
      <div>
        <div class="hw-title">⚡ hermes 工作台</div>
        <div class="hw-subtitle" id="hw-status">◐ 检查 hermes 状态中…</div>
      </div>
      <div class="hw-actions">
        <button class="hw-btn" id="hw-refresh">🔄 刷新</button>
      </div>
    </div>
    <div class="hw-grid">
      <div class="hw-panel hw-panel-cron">
        <div class="hw-panel-title">定时任务（cron）</div>
        <div id="hw-cron-list"><p class="hw-empty">◐ 加载中…</p></div>
      </div>
      <div class="hw-panel hw-panel-run">
        <div class="hw-panel-title">🤖 手动派活</div>
        <p class="hw-hint">输入任务目标，hermes 将用对应 profile 执行 agent loop。</p>
        <textarea id="hw-prompt" class="hw-textarea" rows="4" placeholder="例如：深读 arXiv 2403.15337，提炼三个创新点"></textarea>
        <button id="hw-run" class="hw-run-btn">执行</button>
        <div id="hw-output" class="hw-output" style="display:none;"></div>
      </div>
    </div>
  `;

  await loadHermesWorkspaceData();

  document.getElementById('hw-refresh')?.addEventListener('click', loadHermesWorkspaceData);
  document.getElementById('hw-run')?.addEventListener('click', runHermesTask);
}

async function loadHermesWorkspaceData() {
  // 状态栏
  const statusEl = document.getElementById('hw-status');
  try {
    const data = await apiGet('/api/hermes/cron');
    const s = data.status || {};
    const parts = [];
    if (s.hermes_cli) parts.push('✓ CLI');
    if (s.linsai_profile) parts.push('✓ profile');
    if (s.gateway_status === 'running') parts.push('✓ 网关');
    parts.push(`${s.cron_jobs_count || 0} 个 cron`);
    if (statusEl) statusEl.textContent = parts.join(' | ');
  } catch (e) {
    if (statusEl) statusEl.textContent = '✗ 无法连接 hermes';
  }

  // cron 列表
  const listEl = document.getElementById('hw-cron-list');
  if (!listEl) return;
  try {
    const data = await apiGet('/api/hermes/cron');
    const jobs = data.jobs || [];
    if (!jobs.length) {
      listEl.innerHTML = '<p class="hw-empty">无 cron 任务</p>';
      return;
    }
    listEl.innerHTML = jobs.map(j => {
      const isActive = j.status === 'active';
      const statusClass = isActive ? 'hw-status-active' : 'hw-status-paused';
      const statusText = isActive ? 'active' : 'paused';
      const lastIcon = j.last_status === 'ok' ? '✅' : (j.last_status ? '⚠️' : '○');
      const lastText = j.last_run ? formatDate(j.last_run) : '未运行';
      return `
        <div class="hw-cron-item">
          <div class="hw-cron-main">
            <div class="hw-cron-name">${escapeHtml(j.name)}</div>
            <div class="hw-cron-meta">
              <span class="hw-cron-status ${statusClass}">${statusText}</span>
              <span>⏰ ${escapeHtml(j.schedule || '?')}</span>
              <span>${lastIcon} ${lastText}</span>
            </div>
          </div>
          <div class="hw-cron-actions">
            ${isActive
              ? `<button class="hw-mini-btn" onclick="controlHermesCron('${escapeAttr(j.id)}','pause')">暂停</button>`
              : `<button class="hw-mini-btn" onclick="controlHermesCron('${escapeAttr(j.id)}','resume')">恢复</button>`}
            <button class="hw-mini-btn hw-mini-btn-primary" onclick="controlHermesCron('${escapeAttr(j.id)}','run')">触发</button>
          </div>
        </div>
      `;
    }).join('');
  } catch (e) {
    listEl.innerHTML = `<p class="hw-empty">加载失败: ${escapeHtml(e.message)}</p>`;
  }
}

async function runHermesTask() {
  const promptInput = document.getElementById('hw-prompt');
  const outputEl = document.getElementById('hw-output');
  const runBtn = document.getElementById('hw-run');
  const prompt = promptInput?.value.trim();
  if (!prompt) { showToast('请输入任务目标', 'warning'); return; }

  runBtn.disabled = true; runBtn.textContent = '执行中…';
  if (outputEl) { outputEl.style.display = 'block'; outputEl.textContent = '◐ hermes agent 执行中…'; }
  try {
    const resp = await fetch('/api/hermes/run', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, timeout: 300 }),
    });
    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let full = '';
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      for (const line of decoder.decode(value, { stream: true }).split('\n')) {
        if (line.startsWith('data: ')) {
          try { const evt = JSON.parse(line.slice(6)); if (evt.type === 'token') full += evt.content; } catch {}
        }
      }
      if (outputEl) { outputEl.textContent = full; outputEl.scrollTop = outputEl.scrollHeight; }
    }
    showToast('✓ 完成', 'success');
  } catch (e) { showToast('✗ ' + e.message, 'error'); }
  finally { runBtn.disabled = false; runBtn.textContent = '执行'; }
}

async function controlHermesCron(jobId, action) {
  try {
    const data = await apiPost(`/api/hermes/cron/${encodeURIComponent(jobId)}/${action}`, {});
    if (data.success) {
      showToast(`✓ 已${action === 'run' ? '触发' : (action === 'pause' ? '暂停' : '恢复')}`, 'success');
      loadHermesWorkspaceData();
    } else {
      showToast(data.error || '操作失败', 'error');
    }
  } catch (e) {
    showToast('操作失败: ' + e.message, 'error');
  }
}

// v3.5.1: 注册模块初始化
if (typeof ModuleLoader !== 'undefined') {
  ModuleLoader.register('hermes_console', () => {
    if (typeof bindHermesEvents === 'function') bindHermesEvents();
  });
}
