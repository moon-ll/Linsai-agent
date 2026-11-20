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
    profileModels: {},
    profileModelsLoading: false,
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
        updateLastUpdateTime();
      }
    } catch (e) { console.error('console flow:', e); }
  }

  function updateLastUpdateTime() {
    const el = document.getElementById('console-last-update');
    if (el) el.textContent = '更新于 ' + formatTime(new Date().toISOString());
  }

  async function loadConsoleAgents() {
    try {
      const data = await apiGet('/api/console/agents');
      if (data.status === 'ok') {
        ConsoleState.agents = data;
        renderAgents();
        loadProfileModels();
      }
    } catch (e) { console.error('console agents:', e); }
  }

  async function loadProfileModels() {
    if (ConsoleState.profileModelsLoading) return;
    const profiles = ConsoleState.agents?.profiles || {};
    const names = Object.keys(profiles);
    if (names.length === 0) return;
    ConsoleState.profileModelsLoading = true;
    for (const name of names) {
      if (ConsoleState.profileModels[name]) continue;
      try {
        const data = await apiGet(`/api/hermes/profiles/${encodeURIComponent(name)}/model`);
        if (data.status === 'ok') {
          ConsoleState.profileModels[name] = data;
        }
      } catch (e) { console.error(`profile model ${name}:`, e); }
    }
    ConsoleState.profileModelsLoading = false;
    renderAgents();
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
  // v6.9.0 R6: 待人工处理队列（验收/激活/负反馈 + 建议动作 + 等待时长）
  // ============================================

  const QUEUE_TYPE_LABELS = {
    review: '验收',
    activate: '激活',
    negative_feedback: '负反馈',
    strategy: '策略',
    parked: '平台冻结',
  };

  function formatQueueWait(hours) {
    if (hours == null) return '?';
    if (hours < 24) return `${Math.round(hours)}h`;
    return `${Math.round(hours / 24)}d`;
  }

  async function loadConsoleHumanQueue() {
    const container = document.getElementById('console-human-queue');
    if (!container) return;
    try {
      const data = await apiGet('/api/console/human-queue');
      if (data.status !== 'ok') return;
      const items = data.items || [];
      const countEl = document.getElementById('console-queue-count');
      if (countEl) countEl.textContent = String(items.length);

      if (items.length === 0) {
        container.innerHTML = '<div class="console-alert console-alert-info"><div class="console-alert-message">无待人工处理事项</div></div>';
        return;
      }

      container.innerHTML = items.map((item, idx) => {
        const typeLabel = QUEUE_TYPE_LABELS[item.type] || item.type;
        const verdictHint = item.can_adopt ? ' · 可一键采纳' : '';
        const actionBtn =
          item.type === 'review'
            ? `<button class="console-mini-btn" data-idx="${idx}" data-cmd="queue_review">去验收</button>`
            : item.type === 'activate'
              ? `<button class="console-mini-btn" data-idx="${idx}" data-cmd="queue_activate">去激活</button>`
              : '';
        return `
          <div class="console-alert ${item.escalate ? 'console-alert-error' : 'console-alert-warning'}">
            <div class="console-alert-header">
              <span class="console-alert-level">${typeLabel}</span>
              <span class="console-alert-time">等待 ${formatQueueWait(item.waiting_hours)}${item.escalate ? ' ⚠催办' : ''}</span>
            </div>
            <div class="console-alert-message">${escapeHtml(item.title || item.proposal_id)}</div>
            <div class="console-alert-reasons">
              <div>· 建议：${escapeHtml(item.suggested_action || '')}${escapeHtml(verdictHint)}</div>
            </div>
            <div class="console-alert-actions">${actionBtn}</div>
          </div>
        `;
      }).join('');

      container.querySelectorAll('.console-mini-btn').forEach(btn => {
        btn.addEventListener('click', () => handleQueueAction(btn, items));
      });
    } catch (e) { console.error('console human-queue:', e); }
  }

  async function handleQueueAction(btn, items) {
    const item = items[Number(btn.dataset.idx)];
    if (!item) return;
    if (btn.dataset.cmd === 'queue_review') {
      if (typeof window.lcReview === 'function') {
        window.lcReview(item.proposal_id);
      } else {
        openLifecycle();
      }
    } else if (btn.dataset.cmd === 'queue_activate') {
      openLifecycle();
    }
  }

  // ============================================
  // 渲染：控制台主框架
  // ============================================

  function renderConsole() {
    const page = document.getElementById('console-page');
    if (!page) return;
    page.innerHTML = `
      <div class="console-header">
        <div>
          <h2 class="console-title">🎛️ 控制台</h2>
          <div class="console-subtitle">全链路状态 · 告警 · Agent 工作负载</div>
        </div>
        <div class="console-toolbar">
          <button class="console-btn primary" data-action="orchestrate">🔄 手动编排</button>
          <button class="console-btn" data-action="repair">🔧 修复扫描</button>
          <button class="console-btn" data-action="sync_kb">🔄 同步知识库</button>
          <button class="console-btn" data-action="weekend_menu" id="console-weekend-btn">📅 周末任务 ▾</button>
          <button class="console-btn" data-action="orchestrator_panel" id="console-orch-btn" title="调度总控：profile 健康/失败模式/策略建议">📊 总控面板</button>
        </div>
      </div>
      <div class="console-weekend-menu" id="console-weekend-menu" style="display:none;">
        <button class="console-menu-item" data-action="weekend_input">📥 执行输入任务</button>
        <button class="console-menu-item" data-action="weekend_output">📤 执行输出任务</button>
        <button class="console-menu-item" data-action="weekend_reflection">📝 执行反思任务</button>
      </div>
      <div class="console-meta-bar">
        <span id="console-last-update">更新于 —</span>
        <button class="console-refresh-btn" id="console-refresh-btn">🔄 刷新</button>
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
          <div class="console-section-title">待人工处理 <span id="console-queue-count" class="console-badge">0</span></div>
          <div id="console-human-queue" class="console-alerts console-queue-list"></div>
          <div class="console-section-title console-queue-gap">调度策略 <span id="console-strategy-count" class="console-badge">0</span></div>
          <div id="console-strategy" class="console-alerts console-queue-list"></div>
          <div class="console-section-title console-queue-gap">告警与待处理 <span id="console-alert-count" class="console-badge">0</span></div>
          <div id="console-alerts" class="console-alerts"></div>
        </div>
      </div>
    `;

    page.querySelectorAll('.console-btn[data-action]').forEach(btn => {
      if (btn.dataset.action === 'weekend_menu') {
        btn.addEventListener('click', toggleWeekendMenu);
      } else {
        btn.addEventListener('click', () => runAction(btn.dataset.action));
      }
    });
    page.querySelectorAll('.console-menu-item').forEach(btn => {
      btn.addEventListener('click', () => {
        hideWeekendMenu();
        runAction(btn.dataset.action);
      });
    });
    document.getElementById('console-refresh-btn')?.addEventListener('click', () => {
      loadConsoleFlow();
      loadConsoleAgents();
      loadConsoleAlerts();
      loadConsoleHumanQueue();
      loadConsoleStrategy();
    });

    loadConsoleFlow();
    loadConsoleAgents();
    loadConsoleAlerts();
    loadConsoleHumanQueue();
    loadConsoleStrategy();
  }

  function toggleWeekendMenu() {
    const menu = document.getElementById('console-weekend-menu');
    if (!menu) return;
    menu.style.display = menu.style.display === 'none' ? 'flex' : 'none';
  }

  function hideWeekendMenu() {
    const menu = document.getElementById('console-weekend-menu');
    if (menu) menu.style.display = 'none';
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
        const pid = it.proposal_id || '';
        const ideaId = it.idea_id || '';
        const clickable = (key === 'optimizing' || key === 'pending_review') && pid;
        html += `
          <div class="console-detail-item ${clickable ? 'clickable' : ''}" data-pid="${escapeAttr(pid)}" data-idea="${escapeAttr(ideaId)}" data-stage="${escapeAttr(key)}">
            <div class="console-detail-title">${escapeHtml(title)}</div>
            ${it.rounds !== undefined ? `<div class="console-detail-meta">轮次: ${it.rounds} · 分数: ${it.last_score != null ? it.last_score.toFixed(2) : '—'}</div>` : ''}
            ${it.generated_at ? `<div class="console-detail-meta">生成时间: ${formatDate(it.generated_at)}</div>` : ''}
          </div>
        `;
      }
      html += '</div>';
    }
    container.innerHTML = html;

    container.querySelectorAll('.console-detail-item.clickable').forEach(el => {
      el.addEventListener('click', () => {
        const pid = el.dataset.pid;
        const stageKey = el.dataset.stage;
        if (stageKey === 'pending_review' && pid) {
          lcReview(pid);
        } else if (pid) {
          lcViewDetail(pid);
        }
      });
    });
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
      const modelHtml = renderProfileModelSelect(name);
      html += `
        <div class="console-agent-card" data-profile="${escapeAttr(name)}">
          <div class="console-agent-header">
            ${statusDot(status)}
            <span class="console-agent-name">${escapeHtml(name)}</span>
            <span class="console-agent-status ${statusColorClass(status)}">${escapeHtml(status)}</span>
          </div>
          <div class="console-agent-meta">24h 成功率: ${rate}</div>
          ${modelHtml}
          ${info.current_task ? `<div class="console-agent-task">◐ ${escapeHtml(info.current_task)}</div>` : ''}
          ${info.recent_error ? `<div class="console-agent-error" title="${escapeAttr(info.recent_error)}">${escapeHtml(info.recent_error.slice(0, 40))}</div>` : ''}
        </div>
      `;
    }
    html += '</div>';
    container.innerHTML = html;
    bindProfileModelSelects();

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

  function renderProfileModelSelect(name) {
    const cfg = ConsoleState.profileModels[name];
    if (!cfg) {
      return `<div class="console-agent-model"><label>主模型</label><select disabled><option>加载中…</option></select></div>`;
    }
    const currentKey = `${cfg.provider}|${cfg.model}`;
    const options = (cfg.options || []).map(opt => {
      const key = `${opt.provider}|${opt.model}`;
      return `<option value="${escapeAttr(key)}" ${key === currentKey ? 'selected' : ''}>${escapeHtml(opt.label)}</option>`;
    }).join('');
    return `
      <div class="console-agent-model">
        <label>主模型</label>
        <select data-profile="${escapeAttr(name)}">
          ${options}
        </select>
        <div class="console-agent-model-saved"></div>
      </div>
    `;
  }

  function bindProfileModelSelects() {
    document.querySelectorAll('.console-agent-model select[data-profile]').forEach(sel => {
      sel.addEventListener('change', async (e) => {
        const name = e.target.dataset.profile;
        const [provider, model] = e.target.value.split('|');
        const savedEl = e.target.parentElement.querySelector('.console-agent-model-saved');
        e.target.disabled = true;
        if (savedEl) savedEl.textContent = '保存中…';
        try {
          const result = await apiPost(`/api/hermes/profiles/${encodeURIComponent(name)}/model`, { provider, model });
          if (result.status === 'ok') {
            ConsoleState.profileModels[name] = { ...ConsoleState.profileModels[name], provider, model };
            if (savedEl) savedEl.textContent = '已保存';
            setTimeout(() => { if (savedEl) savedEl.textContent = ''; }, 2000);
          } else {
            throw new Error(result.error || '保存失败');
          }
        } catch (err) {
          console.error('save profile model:', err);
          if (savedEl) savedEl.textContent = '保存失败: ' + err.message;
          // 恢复选择
          const cfg = ConsoleState.profileModels[name];
          if (cfg) e.target.value = `${cfg.provider}|${cfg.model}`;
        } finally {
          e.target.disabled = false;
        }
      });
    });
  }

  // ============================================
  // 渲染：Alerts
  // ============================================

  function renderAlerts() {
    const container = document.getElementById('console-alerts');
    const countEl = document.getElementById('console-alert-count');
    if (!container) return;

    let alerts = ConsoleState.alerts || [];
    if (countEl) countEl.textContent = String(alerts.length);

    if (alerts.length === 0) {
      container.innerHTML = '<div class="console-empty">暂无告警或待处理项</div>';
      return;
    }

    // 按级别排序：error > warning > info
    const levelOrder = { error: 0, warning: 1, info: 2 };
    alerts = alerts.slice().sort((a, b) => (levelOrder[a.level] || 2) - (levelOrder[b.level] || 2));

    container.innerHTML = '<div class="console-alert-list">' + alerts.map((a, idx) => {
      const levelClass = a.level === 'error' ? 'console-alert-error' : a.level === 'warning' ? 'console-alert-warning' : 'console-alert-info';
      const levelLabel = a.level === 'error' ? '错误' : a.level === 'warning' ? '警告' : '提醒';
      let actions = '';
      if (a.action === 'clear_alert') {
        actions = `<button class="console-mini-btn" data-idx="${idx}" data-cmd="clear_alert" data-pid="${escapeAttr(a.proposal_id)}">清除</button>`;
      } else if (a.action === 'review') {
        actions = `<button class="console-mini-btn" data-idx="${idx}" data-cmd="review" data-pid="${escapeAttr(a.proposal_id)}">审核</button>`;
      } else if (a.action === 'repair') {
        actions = `<button class="console-mini-btn" data-idx="${idx}" data-cmd="repair" data-pid="${escapeAttr(a.proposal_id)}">修复</button>`;
      } else if (a.action === 'review_idea') {
        actions = `<button class="console-mini-btn" data-idx="${idx}" data-cmd="review_idea" data-idea="${escapeAttr(a.idea_id)}">查看</button>`;
      } else if (a.action === 'retry_weekend') {
        actions = `<button class="console-mini-btn" data-idx="${idx}" data-cmd="retry_weekend" data-task="${escapeAttr(a.task_name)}">重试</button>`;
      }
      return `
        <div class="console-alert ${levelClass}">
          <div class="console-alert-header">
            <span class="console-alert-level">${levelLabel}</span>
            <span class="console-alert-time">${a.time ? formatTime(a.time) : ''}</span>
          </div>
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

  // v6.9.58: 调度策略面板——当前值 vs 建议值 diff + 单项应用 + 历史记录
  // 背景：strategy_optimizer 建议 3 周 0 采纳（人工确认通道无界面），
  // human_queue 的 strategy 类事项也指向此处。
  async function loadConsoleStrategy() {
    const container = document.getElementById('console-strategy');
    if (!container) return;
    const countEl = document.getElementById('console-strategy-count');
    try {
      const [strats, log] = await Promise.all([
        apiGet('/api/orchestrator/strategies').catch(() => null),
        apiGet('/api/orchestrator/tuning-log').catch(() => null),
      ]);
      if (!strats) {
        container.innerHTML = '<div class="console-alert console-alert-info"><div class="console-alert-message">策略服务暂不可用</div></div>';
        return;
      }
      const current = strats.current || {};
      const suggested = strats.suggested || {};
      const changes = Object.keys(suggested)
        .filter(k => suggested[k] !== current[k])
        .map(k => ({ key: k, current: current[k], suggested: suggested[k] }));
      if (countEl) countEl.textContent = String(changes.length);

      let html = '';
      if (changes.length === 0) {
        html += '<div class="console-alert console-alert-info"><div class="console-alert-message">当前参数与建议一致，无需调整</div></div>';
      } else {
        for (const c of changes) {
          html += `
            <div class="console-alert console-alert-warning">
              <div class="console-alert-header">
                <span class="console-alert-level">${escapeHtml(c.key)}</span>
                <span class="console-alert-time">${escapeHtml(String(c.current))} → ${escapeHtml(String(c.suggested))}</span>
              </div>
              <div class="console-alert-message">建议调整（risk: ${escapeHtml(strats.risk || '?')}）</div>
              <div class="console-alert-actions">
                <button class="console-mini-btn" data-key="${escapeHtml(c.key)}" data-val="${escapeHtml(String(c.suggested))}" data-cmd="strategy_apply">应用</button>
              </div>
            </div>`;
        }
      }
      const history = (log && log.history) || [];
      if (history.length) {
        const last = history[0];
        html += `<div class="console-alert console-alert-info" style="margin-top:6px;">
          <div class="console-alert-message" style="font-size:0.75rem;">最近变更：${escapeHtml(last.at || '')} · ${escapeHtml(last.confirmed_by || '')} · ${Object.keys(last.new || {}).map(k => `${k}=${last.new[k]}`).join(', ')}</div>
        </div>`;
      }
      container.innerHTML = html;
      container.querySelectorAll('.console-mini-btn[data-cmd="strategy_apply"]').forEach(btn => {
        btn.addEventListener('click', async () => {
          const key = btn.dataset.key, val = btn.dataset.val;
          let parsed = val;
          if (val === 'true' || val === 'false') parsed = val === 'true';
          else if (!isNaN(Number(val)) && val !== '') parsed = Number(val);
          if (!confirm(`确认应用策略 ${key} = ${parsed}？（将写入 tuning-log，可审计）`)) return;
          btn.disabled = true;
          try {
            const r = await apiPost('/api/orchestrator/strategies/apply', { strategies: { [key]: parsed }, confirmed_by: 'human:console' });
            if (r.status === 'ok' || r.success) {
              showToast(`✓ 已应用 ${key} = ${parsed}`, 'success');
              loadConsoleStrategy();
            } else {
              showToast(`✗ ${r.error || '应用失败'}`, 'error');
            }
          } catch (e) {
            showToast(`✗ ${e.message}`, 'error');
          } finally { btn.disabled = false; }
        });
      });
    } catch (e) {
      console.error('console strategy:', e);
    }
  }

  async function runAction(action) {
    if (action === 'orchestrator_panel') {
      if (typeof Orchestrator !== 'undefined' && Orchestrator.open) {
        Orchestrator.open();
      } else {
        showToast('总控模块未加载', 'error');
      }
      return;
    }
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
