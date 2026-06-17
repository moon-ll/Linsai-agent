/**
 * hermes_console.js — hermes 控制台前端（cron 列表/启停/手动派活）
 * 零框架依赖，原生 JavaScript，复用 app.js 的 apiGet/apiPost/showToast。
 */

// ============================================
// 面板打开/关闭
// ============================================
function openHermesConsole() {
  const overlay = document.getElementById('hermes-overlay');
  if (!overlay) return;
  overlay.style.display = 'flex';
  loadHermesStatus();
  loadCronList();
}

function closeHermesConsole() {
  const overlay = document.getElementById('hermes-overlay');
  if (overlay) overlay.style.display = 'none';
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
  container.innerHTML = '<p style="color:var(--text-tertiary);font-size:0.85rem;">加载中...</p>';

  try {
    const data = await apiGet('/api/hermes/cron');
    const jobs = data.jobs || [];
    if (!jobs.length) {
      container.innerHTML = '<p style="color:var(--text-tertiary);font-size:0.85rem;">无 cron 任务</p>';
      return;
    }

    let html = '';
    jobs.forEach(job => {
      const isActive = job.status === 'active';
      const statusBadge = isActive
        ? '<span style="color:var(--success-color);">● active</span>'
        : '<span style="color:var(--text-tertiary);">○ paused</span>';
      const lastIcon = job.last_status === 'ok' ? '✅' : (job.last_status ? '⚠️' : '○');

      html += `<div style="padding:8px 10px;margin:6px 0;background:var(--bg-secondary);border-radius:6px;">
        <div style="display:flex;justify-content:space-between;align-items:start;gap:8px;">
          <div style="flex:1;">
            <div style="font-size:0.85rem;font-weight:500;">${escapeHtml(job.name)}</div>
            <div style="font-size:0.75rem;color:var(--text-tertiary);margin-top:2px;">
              ${statusBadge} | ⏰ ${escapeHtml(job.schedule || '?')} | ${lastIcon} ${escapeHtml(job.last_run ? job.last_run.slice(5,16) : '未运行')}
            </div>
          </div>
          <div style="display:flex;gap:4px;flex-shrink:0;">`;
      if (isActive) {
        html += `<button onclick="controlCron('${job.id}','pause')" style="padding:3px 8px;font-size:0.75rem;cursor:pointer;border:1px solid var(--border-color);border-radius:4px;">暂停</button>`;
      } else {
        html += `<button onclick="controlCron('${job.id}','resume')" style="padding:3px 8px;font-size:0.75rem;cursor:pointer;border:1px solid var(--border-color);border-radius:4px;">恢复</button>`;
      }
      html += `<button onclick="controlCron('${job.id}','run')" style="padding:3px 8px;font-size:0.75rem;cursor:pointer;border:1px solid var(--border-color);border-radius:4px;background:var(--accent-color);color:#fff;">触发</button>`;
      html += `</div></div></div>`;
    });
    container.innerHTML = html;
  } catch (e) {
    container.innerHTML = `<p style="color:var(--error-color);font-size:0.85rem;">加载失败: ${escapeHtml(e.message)}</p>`;
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

    try {
      const resp = await fetch('/api/hermes/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, timeout: 300 }),
      });
      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let fullText = '';

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
            } else if (evt.type === 'error') {
              showToast(`✗ ${evt.message}`, 'error');
            }
          } catch {}
        }
      }
    } catch (e) {
      showToast(`✗ 执行失败: ${e.message}`, 'error');
    } finally {
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
