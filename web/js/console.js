/**
 * console.js — v6.7.7 林赛控制台
 *
 * 统一操作界面：
 * - 全链路流水线可视化（输入 → drafts → optimizing → pending_review → archived → 输出）
 * - Agent / Profile 工作状态
 * - 告警与待处理 inbox
 * - 顶部快捷操作栏
 *
 * API:
 *   GET /api/console/flow
 *   GET /api/console/agents
 *   GET /api/console/alerts
 *   POST /api/console/action
 */

(function() {
  'use strict';

  const ConsoleState = {
    flow: null,
    agents: null,
    alerts: [],
    selectedStage: null,
  };

  const STAGE_ORDER = ['incoming', 'drafts', 'optimizing', 'pending_review', 'archived', 'output'];
  const STAGE_LABELS = {
    incoming: '输入端',
    drafts: '初稿',
    optimizing: '优化中',
    pending_review: '待校验',
    archived: '归档',
    output: '输出端',
  };
  const STAGE_ICONS = {
    incoming: '📥',
    drafts: '📝',
    optimizing: '🔄',
    pending_review: '🔍',
    archived: '📦',
    output: '📤',
  };

  // ============================================
  // 入口
  // ============================================

  function initConsole() {
    // 导航切换时刷新
    const btn = document.querySelector('.nav-btn[data-view="console"]');
    if (btn) btn.addEventListener('click', () => {
      switchToView('console');
      renderConsole();
      startPolling();
    });

    // 首次加载（如果默认是控制台）
    if (document.getElementById('console-page')?.style.display === 'flex') {
      renderConsole();
      startPolling();
    }
  }

  function startPolling() {
    PollService.register('console-flow', loadConsoleFlow, 30000);
    PollService.register('console-agents', loadConsoleAgents, 30000);
    PollService.register('console-alerts', loadConsoleAlerts, 30000);
  }

  function stopPolling() {
    PollService.unregister('console-flow');
    PollService.unregister('console-agents');
    PollService.unregister('console-alerts');
  }

  // ============================================
  // 数据加载
  // ============================================

  async function loadConsoleFlow() {
    try {
      const data = await apiGet('/api/console/flow');
      if (data.status === 'ok') {
        ConsoleState.flow = data.stages;
        renderFlow();
        if (ConsoleState.selectedStage) renderStageDetail(ConsoleState.selectedStage);
      }
    } catch (e) { console.error('console flow:', e); }
  }

  async function loadConsoleAgents() {
    try {
      const data = await apiGet('/api/console/agents');
      if (data.status === 'ok') {
        ConsoleState.agents = data;
        renderAgents();
      }
    } catch (e) { console.error('console agents:', e); }
  }

  async function loadConsoleAlerts() {
    try {
      const data = await apiGet('/api/console/alerts');
      if (data.status === 'ok') {
        ConsoleState.alerts = data.alerts || [];
        renderAlerts();
      }
    } catch (e) { console.error('console alerts:', e); }
  }

  // ============================================
  // 渲染：控制台主框架
  // ============================================

  function renderConsole() {
    const page = document.getElementById('console-page');
    if (!page) return;
    page.innerHTML = `
      <div class="console-toolbar">
        <button class="console-btn" data-action="orchestrate">🔄 手动编排</button>
        <button class="console-btn" data-action="repair">🔧 手动修复</button>
        <button class="console-btn" data-action="weekend_input">📥 周末输入</button>
        <button class="console-btn" data-action="weekend_output">📤 周末输出</button>
        <button class="console-btn" data-action="sync_kb">🔄 同步知识库</button>
        <span class="console-last-update" id="console-last-update">—</span>
      </div>
      <div class="console-grid">
        <div class="console-col console-col-left">
          <div class="console-section-title">全链路流水线</div>
          <div id="console-flow" class="console-flow"></div>
          <div id="console-stage-detail" class="console-stage-detail"></div>
        </div>
        <div class="console-col console-col-center">
          <div class="console-section-title">Agent 工作状态</div>
          <div id="console-agents" class="console-agents"></div>
          <div class="console-section-title" style="margin-top:16px;">当前 Cron 任务</div>
          <div id="console-cron-jobs" class="console-cron-jobs"></div>
        </div>
        <div class="console-col console-col-right">
          <div class="console-section-title">告警与待处理 <span id="console-alert-count" class="console-badge">0</span></div>
          <div id="console-alerts" class="console-alerts"></div>
        </div>
      </div>
    `;

    page.querySelectorAll('.console-btn').forEach(btn => {
      btn.addEventListener('click', () => runAction(btn.dataset.action));
    });

    loadConsoleFlow();
    loadConsoleAgents();
    loadConsoleAlerts();
  }

  // ============================================
  // 渲染：流水线
  // ============================================

  function renderFlow() {
    const container = document.getElementById('console-flow');
    if (!container || !ConsoleState.flow) return;

    let html = '';
    for (let i = 0; i < STAGE_ORDER.length; i++) {
      const key = STAGE_ORDER[i];
      const stage = ConsoleState.flow[key] || { count: 0, items: [], status: 'ok' };
      const active = ConsoleState.selectedStage === key ? 'console-stage-active' : '';
      const statusClass = stage.status === 'error' ? 'console-stage-error' : stage.status === 'warning' ? 'console-stage-warning' : 'console-stage-ok';
      html += `
        <div class="console-stage ${active} ${statusClass}" data-stage="${key}">
          <div class="console-stage-icon">${STAGE_ICONS[key]}</div>
          <div class="console-stage-label">${STAGE_LABELS[key]}</div>
          <div class="console-stage-count">${stage.count}</div>
          ${stage.items.length > 0 ? `<div class="console-stage-items">${stage.items.slice(0, 2).map(it => `<div class="console-stage-item">${escapeHtml(it.title || it.proposal_id || 'item')}</div>`).join('')}</div>` : ''}
        </div>
        ${i < STAGE_ORDER.length - 1 ? '<div class="console-flow-arrow">→</div>' : ''}
      `;
    }
    container.innerHTML = html;

    container.querySelectorAll('.console-stage').forEach(el => {
      el.addEventListener('click', () => {
        const key = el.dataset.stage;
        ConsoleState.selectedStage = ConsoleState.selectedStage === key ? null : key;
        renderFlow();
        renderStageDetail(key);
      });
    });
  }

  function renderStageDetail(key) {
    const container = document.getElementById('console-stage-detail');
    if (!container) return;
    const stage = ConsoleState.flow?.[key];
    if (!stage) { container.innerHTML = ''; return; }

    let html = `<div class="console-detail-header">${STAGE_ICONS[key]} ${STAGE_LABELS[key]} 详情</div>`;
    if (!stage.items || stage.items.length === 0) {
      html += '<div class="console-empty">该阶段暂无项目</div>';
    } else {
      html += '<div class="console-detail-list">';
      for (const it of stage.items) {
        const title = it.title || it.proposal_id || '未命名';
        html += `
          <div class="console-detail-item">
            <div class="console-detail-title">${escapeHtml(title)}</div>
            ${it.rounds !== undefined ? `<div class="console-detail-meta">轮次: ${it.rounds} · 分数: ${it.last_score != null ? it.last_score.toFixed(2) : '—'}</div>` : ''}
            ${it.generated_at ? `<div class="console-detail-meta">生成时间: ${formatDate(it.generated_at)}</div>` : ''}
          </div>
        `;
      }
      html += '</div>';
    }
    container.innerHTML = html;
  }

  // ============================================
  // 渲染：Agents
  // ============================================

  function renderAgents() {
    const container = document.getElementById('console-agents');
    if (!container || !ConsoleState.agents) return;

    const profiles = ConsoleState.agents.profiles || {};
    const profilesList = Object.entries(profiles);
    if (profilesList.length === 0) {
      container.innerHTML = '<div class="console-empty">暂无 agent 状态</div>';
      return;
    }

    let html = '<div class="console-agent-grid">';
    for (const [name, info] of profilesList) {
      const status = info.status || 'offline';
      const rate = info.success_rate_24h != null ? (info.success_rate_24h * 100).toFixed(0) + '%' : '—';
      html += `
        <div class="console-agent-card">
          <div class="console-agent-header">
            ${statusDot(status)}
            <span class="console-agent-name">${escapeHtml(name)}</span>
            <span class="console-agent-status ${statusColorClass(status)}">${escapeHtml(status)}</span>
          </div>
          <div class="console-agent-meta">24h 成功率: ${rate}</div>
          ${info.current_task ? `<div class="console-agent-task">◐ ${escapeHtml(info.current_task)}</div>` : ''}
          ${info.recent_error ? `<div class="console-agent-error" title="${escapeAttr(info.recent_error)}">${escapeHtml(info.recent_error.slice(0, 40))}</div>` : ''}
        </div>
      `;
    }
    html += '</div>';
    container.innerHTML = html;

    // cron jobs
    const cronContainer = document.getElementById('console-cron-jobs');
    if (cronContainer) {
      const jobs = ConsoleState.agents.cron_jobs || [];
      if (jobs.length === 0) {
        cronContainer.innerHTML = '<div class="console-empty">暂无运行中 cron</div>';
      } else {
        cronContainer.innerHTML = '<div class="console-cron-list">' + jobs.map(j => `
          <div class="console-cron-item">
            <span class="console-cron-name">${escapeHtml(j.name)}</span>
            <span class="console-cron-schedule">${escapeHtml(j.schedule)}</span>
            <span class="console-cron-last">${j.last_run ? formatDate(j.last_run) : '未运行'}</span>
          </div>
        `).join('') + '</div>';
      }
    }
  }

  // ============================================
  // 渲染：Alerts
  // ============================================

  function renderAlerts() {
    const container = document.getElementById('console-alerts');
    const countEl = document.getElementById('console-alert-count');
    if (!container) return;

    const alerts = ConsoleState.alerts || [];
    if (countEl) countEl.textContent = String(alerts.length);

    if (alerts.length === 0) {
      container.innerHTML = '<div class="console-empty">暂无告警或待处理项</div>';
      return;
    }

    container.innerHTML = '<div class="console-alert-list">' + alerts.map((a, idx) => {
      const levelClass = a.level === 'error' ? 'console-alert-error' : a.level === 'warning' ? 'console-alert-warning' : 'console-alert-info';
      let actions = '';
      if (a.action === 'clear_alert') {
        actions = `<button class="console-mini-btn" data-idx="${idx}" data-cmd="clear_alert" data-pid="${escapeAttr(a.proposal_id)}">清除告警</button>`;
      } else if (a.action === 'review') {
        actions = `<button class="console-mini-btn" data-idx="${idx}" data-cmd="review" data-pid="${escapeAttr(a.proposal_id)}">去审查</button>`;
      } else if (a.action === 'repair') {
        actions = `<button class="console-mini-btn" data-idx="${idx}" data-cmd="repair" data-pid="${escapeAttr(a.proposal_id)}">修复</button>`;
      } else if (a.action === 'review_idea') {
        actions = `<button class="console-mini-btn" data-idx="${idx}" data-cmd="review_idea" data-idea="${escapeAttr(a.idea_id)}">查看</button>`;
      } else if (a.action === 'retry_weekend') {
        actions = `<button class="console-mini-btn" data-idx="${idx}" data-cmd="retry_weekend" data-task="${escapeAttr(a.task_name)}">重试</button>`;
      }
      return `
        <div class="console-alert ${levelClass}">
          <div class="console-alert-message">${escapeHtml(a.message)}</div>
          ${a.reasons ? `<div class="console-alert-reasons">${a.reasons.map(r => `<div>· ${escapeHtml(r)}</div>`).join('')}</div>` : ''}
          <div class="console-alert-actions">${actions}</div>
        </div>
      `;
    }).join('') + '</div>';

    container.querySelectorAll('.console-mini-btn').forEach(btn => {
      btn.addEventListener('click', () => handleAlertAction(btn));
    });
  }

  async function handleAlertAction(btn) {
    const cmd = btn.dataset.cmd;
    try {
      if (cmd === 'clear_alert') {
        await apiPost('/api/console/action', { action: 'clear_alert', proposal_id: btn.dataset.pid });
        showToast('告警已清除');
      } else if (cmd === 'review') {
        openLifecycle();
        return;
      } else if (cmd === 'repair') {
        await runAction('repair');
        return;
      } else if (cmd === 'review_idea') {
        // 打开生命周期并切换到输入端视图
        openLifecycle();
        return;
      } else if (cmd === 'retry_weekend') {
        await runAction(`weekend_${btn.dataset.task}`);
        return;
      }
      loadConsoleAlerts();
    } catch (e) {
      showToast(`✗ ${e.message}`, 'error');
    }
  }

  // ============================================
  // 动作
  // ============================================

  async function runAction(action) {
    showToast(`◐ ${action} 执行中…`, 'info');
    try {
      const data = await apiPost('/api/console/action', { action });
      if (data.status === 'ok') {
        showToast(`✓ ${action} 已触发`, 'success');
        loadConsoleFlow();
        loadConsoleAgents();
        loadConsoleAlerts();
      } else {
        showToast(`✗ ${data.error || '未知错误'}`, 'error');
      }
    } catch (e) {
      showToast(`✗ ${e.message}`, 'error');
    }
  }

  // 注册到模块加载器
  if (typeof ModuleLoader !== 'undefined') {
    ModuleLoader.register('console', initConsole);
  } else {
    window.addEventListener('DOMContentLoaded', initConsole);
  }
})();
