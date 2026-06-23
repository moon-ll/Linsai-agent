/**
 * learning.js — 学习管理器（学习日志、待审队列、统计面板）
 */

const LearningManager = { activeTab: 'learning-log' };

function openLearningManager() {
  if (!document.getElementById('learning-manager-overlay')) return;
  openModal('learning-manager-overlay');
  LearningManager.activeTab = 'learning-log';
  document.querySelectorAll('#learning-manager-overlay .kb-tab').forEach(t => {
    t.classList.toggle('active', t.dataset.tab === 'learning-log');
  });
  document.querySelectorAll('#learning-manager-overlay .kb-panel').forEach(p => {
    p.classList.toggle('active', p.id === 'kb-panel-learning-log');
  });
  renderLearningManager();
}

function closeLearningManager() {
  closeModal('learning-manager-overlay');
}

async function renderLearningManager() {
  const tab = LearningManager.activeTab;
  if (tab === 'learning-log') await loadLearningLog();
  else if (tab === 'learning-review') await loadLearningReview();
  else if (tab === 'learning-stats') await loadLearningStats();
}

function switchLearningTab(tab) {
  LearningManager.activeTab = tab;
  document.querySelectorAll('#learning-manager-overlay .kb-tab').forEach(t => {
    t.classList.toggle('active', t.dataset.tab === tab);
  });
  document.querySelectorAll('#learning-manager-overlay .kb-panel').forEach(p => {
    p.classList.toggle('active', p.id === `kb-panel-${tab}`);
  });
  renderLearningManager();
}

async function loadLearningLog() {
  const el = document.getElementById('learning-log-content');
  if (!el) return;
  el.innerHTML = '<span style="color:var(--text-tertiary);">◐ 加载中…</span>';
  try {
    const data = await apiGet('/api/learning/log');
    const log = (data && data.log) || [];
    if (!log.length) {
      el.innerHTML = '<p style="color:var(--text-tertiary);text-align:center;padding:20px;">暂无学习记录</p>';
      return;
    }
    el.innerHTML = log.slice(-20).reverse().map(item => {
      const time = (item.timestamp || item.time || '').slice(0, 16);
      const action = escapeHtml(item.action || item.type || '学习');
      const target = escapeHtml(item.target || item.title || item.concept || '');
      const status = item.success === false ? '⚠️' : '✓';
      return `<div style="padding:6px 0;border-bottom:1px solid var(--border-color);font-size:0.85rem;">
        ${status} <span style="color:var(--text-tertiary);">${time}</span> ${action} → <strong>${target}</strong>
      </div>`;
    }).join('');
  } catch (e) {
    el.innerHTML = `<p style="color:var(--error-color);">加载失败: ${escapeHtml(e.message)}</p>`;
  }
}

async function loadLearningReview() {
  const el = document.getElementById('learning-review-content');
  if (!el) return;
  el.innerHTML = '<span style="color:var(--text-tertiary);">◐ 加载中…</span>';
  try {
    const data = await apiGet('/api/learning/queue');
    const queue = (data && (data.queue || data.items)) || [];
    if (!queue.length) {
      el.innerHTML = '<p style="color:var(--text-tertiary);text-align:center;padding:20px;">无待审内容</p>';
      return;
    }
    el.innerHTML = queue.map(item => {
      const title = escapeHtml(item.title || item.concept || '未知');
      const stage = escapeHtml(item.growth_stage || '');
      return `<div style="padding:8px;margin:4px 0;background:var(--bg-secondary);border-radius:6px;">
        <div style="font-size:0.88rem;font-weight:500;">${title}</div>
        <div style="font-size:0.75rem;color:var(--text-tertiary);">${stage}</div>
      </div>`;
    }).join('');
  } catch (e) {
    el.innerHTML = `<p style="color:var(--error-color);">加载失败: ${escapeHtml(e.message)}</p>`;
  }
}

async function loadLearningStats() {
  const el = document.getElementById('learning-stats-content');
  if (!el) return;
  el.innerHTML = '<span style="color:var(--text-tertiary);">◐ 加载中…</span>';
  try {
    const data = await apiGet('/api/learning/status');
    const stats = data || {};
    let html = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">';
    const fields = [
      ['自动学习', stats.auto_enabled ? '✓ 开启' : '○ 关闭'],
      ['总学习数', stats.total_learned || 0],
      ['今日学习', stats.today_count || 0],
      ['待审', stats.pending_count || 0],
      ['本月成本', `${stats.cost_monthly || 0}`],
      ['策略', escapeHtml(stats.strategy || 'balanced')],
    ];
    fields.forEach(([k, v]) => {
      html += `<div style="padding:10px;background:var(--bg-secondary);border-radius:6px;">
        <div style="font-size:0.75rem;color:var(--text-tertiary);">${escapeHtml(k)}</div>
        <div style="font-size:1.1rem;font-weight:600;margin-top:4px;">${v}</div>
      </div>`;
    });
    html += '</div>';
    el.innerHTML = html;
  } catch (e) {
    el.innerHTML = `<p style="color:var(--error-color);">加载失败: ${escapeHtml(e.message)}</p>`;
  }
}
