/**
 * projects.js — 项目总控中心前端（v3.1.0：5 tab 总览/任务/意见/执行/同步+NSFC+文献）
 * 零框架依赖，原生 JavaScript，复用 app.js 的 apiGet/apiPost/showToast/escapeHtml。
 */

const ProjectsState = { currentTab: 'overview' };  // v3.1.0 默认总览

function openProjectsManager() {
  const overlay = document.getElementById('projects-overlay');
  if (!overlay) return;
  overlay.style.display = 'flex';
  ProjectsState.currentTab = 'overview';
  document.querySelectorAll('.proj-tab-btn').forEach(btn => {
    btn.style.background = btn.dataset.tab === 'overview' ? 'var(--bg-active)' : 'transparent';
  });
  loadProjectsTab('overview');
}

function closeProjectsManager() {
  closeModal('projects-overlay');
}

function switchProjectsTab(tab) {
  ProjectsState.currentTab = tab;
  document.querySelectorAll('.proj-tab-btn').forEach(btn => {
    btn.style.background = btn.dataset.tab === tab ? 'var(--bg-active)' : 'transparent';
  });
  loadProjectsTab(tab);
}

async function loadProjectsTab(tab) {
  const body = document.getElementById('projects-body');
  if (!body) return;
  body.innerHTML = '<p class="state-loading state-loading pad-40">◐ 加载中…</p>';
  try {
    if (tab === 'overview') await renderOverviewTab(body);
    else if (tab === 'tasks') await renderTasksTab(body);
    else if (tab === 'opinions') await renderOpinionsTab(body);
    else if (tab === 'dispatches') await renderDispatchesTab(body);
    else if (tab === 'nsfc') await renderNsfcTree(body);
    else if (tab === 'papers') await renderPapersCards(body);
    else if (tab === 'sync') await renderSyncTab(body);
  } catch (e) {
    body.innerHTML = `<p class="state-error">加载失败: ${escapeHtml(e.message)}</p>`;
  }
}

// ============================================
// v3.1.0: 📊 总览 tab
// ============================================
async function renderOverviewTab(container) {
  try {
  const data = await apiGet('/api/projects/overview');
  const ts = data.task_stats || {};
  const ds = data.dispatch_stats || {};

  let html = '<h4 style="font-size:0.95rem;margin:0 0 12px;color:var(--text-primary);">📊 项目总览</h4>';

  // 4 张统计卡
  html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;margin-bottom:20px;">';
  // NSFC 进度卡
  html += `<div class="stat-card">
    <div class="meta-sm">🔬 NSFC 项目</div>
    <div class="stat-value-lg">${data.nsfc_available ? escapeHtml(data.nsfc_phase || '进行中') : '未启用'}</div>
    <div class="stat-sub">${data.nsfc_available ? 'state.md 已加载' : '无 hermes 项目'}</div>
  </div>`;
  // 任务卡
  const totalTasks = data.total_tasks || 0;
  html += `<div class="stat-card" style="--card-edge:var(--info-color);">
    <div class="meta-sm">📋 项目任务</div>
    <div class="stat-value-lg">${totalTasks} 个</div>
    <div class="stat-sub">○${ts.backlog||0} 待办 · ◐${ts.active||0} 进行 · ✓${ts.completed||0}</div>
  </div>`;
  // 意见卡
  html += `<div class="stat-card" style="--card-edge:var(--warning-color);">
    <div class="meta-sm">💭 项目意见</div>
    <div class="stat-value-lg">${ds.open_opinions||0} 待处理</div>
    <div class="stat-sub">共 ${ds.total_opinions||0} 条 · ${ds.fed_opinions||0} 已反馈</div>
  </div>`;
  // 执行卡
  html += `<div class="stat-card" style="--card-edge:var(--success-color);">
    <div class="meta-sm">⚡ hermes 执行</div>
    <div class="stat-value-lg">${ds.running_dispatches||0} 进行中</div>
    <div class="stat-sub">✓${ds.done_dispatches||0} 完成 · ✗${ds.failed_dispatches||0} 失败</div>
  </div>`;
  html += '</div>';

  // 快捷新建区
  html += '<div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:20px;">';
  html += '<button onclick="switchProjectsTab(\'tasks\')" style="padding:10px 16px;background:var(--accent-color);color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:0.85rem;">+ 新建项目任务</button>';
  html += '<button onclick="switchProjectsTab(\'opinions\')" style="padding:10px 16px;border:1px solid var(--accent-color);background:transparent;color:var(--accent-color);border-radius:6px;cursor:pointer;font-size:0.85rem;">💬 提出意见</button>';
  html += '<button onclick="switchProjectsTab(\'dispatches\')" class="btn-ghost-cancel-lg">⚡ 查看执行</button>';
  html += '</div>';

  // 任务分布表
  const byProj = data.task_by_project || {};
  const projKeys = Object.keys(byProj);
  if (projKeys.length) {
    html += '<div class="pad-12 bg-secondary br-6">';
    html += '<div class="label-sm-mb8">📁 任务按项目分布</div>';
    for (const p of projKeys) {
      const pct = totalTasks ? Math.round(byProj[p] / totalTasks * 100) : 0;
      html += `<div class="d-flex ai-center gap-8 m-4-0 fs-08">
        <span style="min-width:140px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${escapeHtml(p)}</span>
        <div style="flex:1;height:6px;background:var(--bg-tertiary);border-radius:3px;overflow:hidden;">
          <div style="width:${pct}%;height:100%;background:var(--accent-color);"></div>
        </div>
        <span style="min-width:30px;text-align:right;color:var(--text-tertiary);">${byProj[p]}</span>
      </div>`;
    }
    html += '</div>';
  }

  // 最近执行
  const recent = ds.recent_dispatches || [];
  if (recent.length) {
    html += '<div class="mt-16"><div class="label-sm-mb8">⚡ 最近执行</div>';
    for (const d of recent.slice(0, 5)) {
      const statusIcon = d.status === 'done' ? '✓' : d.status === 'failed' ? '✗' : d.status === 'timeout' ? '⏱' : '◐';
      const statusColor = d.status === 'done' ? 'var(--success-color)' : (d.status === 'failed' || d.status === 'timeout') ? 'var(--error-color)' : 'var(--warning-color)';
      html += `<div style="padding:6px 8px;font-size:0.78rem;border-left:2px solid ${statusColor};margin-bottom:4px;">
        ${statusIcon} <span style="color:${statusColor};font-weight:500;">[${d.status}]</span> ${escapeHtml((d.prompt||'').slice(0,60))}…
        <span class="text-tertiary ml-6">${escapeHtml(d.project||'通用')}</span>
      </div>`;
    }
    html += '</div>';
  }

  container.innerHTML = html;
  } catch (e) {
    console.warn('renderOverviewTab 失败:', e.message);
  }
}

// ============================================
// v3.1.0: 📋 项目任务 tab（核心）
// ============================================
async function renderTasksTab(container) {
  try {
  // 并行加载任务列表 + 项目清单
  const [tasksData, projectsData] = await Promise.all([
    apiGet('/api/tasks'),
    apiGet('/api/projects/list'),
  ]);
  const tasks = Array.isArray(tasksData) ? tasksData : [];
  const projects = (projectsData.projects || []).map(p => p.name);
  window._projList = projects;  // 缓存供表单用

  let html = '';

  // 新建任务表单（折叠）
  html += `<details class="mb-16 border-accent br-8 overflow-hidden">
    <summary style="padding:10px 14px;cursor:pointer;font-weight:600;font-size:0.85rem;background:var(--bg-secondary);color:var(--accent-color);">+ 新建项目任务</summary>
    <div class="pad-14 d-flex fd-col gap-10">

      <!-- AI 辅助指派 -->
      <div style="background:var(--bg-tertiary);border-radius:8px;padding:10px;border:1px solid var(--border-color);">
        <div style="font-size:0.8rem;font-weight:600;color:var(--accent-color);margin-bottom:6px;">🤖 AI 辅助指派（只说目标，AI 补充细节）</div>
        <input type="text" id="ptask-ai-goal" placeholder="任务目标，如：调研MoS2圆偏振HHG的最新进展" class="field-input" style="margin-bottom:6px;">
        <input type="text" id="ptask-ai-req" placeholder="额外要求（可选），如：聚焦2024-2026年/需要对比表" class="field-input" style="margin-bottom:8px;">
        <button id="ptask-ai-gen" class="flex-1 pad-8 bg-accent text-white border-none br-6 cursor-pointer fs-085" style="width:100%;">🤖 AI 生成任务详情</button>
        <div id="ptask-ai-result" style="display:none;margin-top:8px;font-size:0.8rem;"></div>
      </div>

      <input type="text" id="ptask-title" placeholder="任务标题（必填）" class="field-input">
      <div class="d-flex gap-8 fw-wrap">
        <select id="ptask-project" class="field-select" style="flex:1;min-width:140px;">
          <option value="">（通用，无项目）</option>
          ${projects.map(p => `<option value="${escapeHtml(p)}">${escapeHtml(p)}</option>`).join('')}
        </select>
        <select id="ptask-priority" class="field-select">
          <option value="medium">中</option><option value="high">高</option><option value="urgent">紧急</option><option value="low">低</option>
        </select>
        <input type="date" id="ptask-due" class="field-select">
      </div>
      <textarea id="ptask-desc" placeholder="任务描述（可选）" rows="2" class="field-textarea"></textarea>
      <div style="display:flex;align-items:center;gap:16px;font-size:0.85rem;color:var(--text-secondary);">
        <span>执行者:</span>
        <label class="flex-ac-gap4"><input type="radio" name="ptask-assignee" value="myself" checked>我自己</label>
        <label class="flex-ac-gap4"><input type="radio" name="ptask-assignee" value="hermes">派 hermes 执行</label>
        <label class="flex-ac-gap4"><input type="radio" name="ptask-assignee" value="none">先不执行</label>
      </div>
      <div class="modal-btn-row">
        <button id="ptask-create" class="flex-1 pad-10 bg-accent text-white border-none br-6 cursor-pointer fs-085">✓ 创建任务</button>
        <button id="ptask-cancel" class="btn-ghost-cancel-lg">清空</button>
      </div>
    </div>
  </details>`;

  // 按项目分组渲染任务卡片
  const byProject = {};
  for (const t of tasks) {
    const p = t.project || '通用';
    if (!byProject[p]) byProject[p] = [];
    byProject[p].push(t);
  }
  const projNames = Object.keys(byProject).sort();
  if (!projNames.length) {
    html += '<p class="state-loading">暂无项目任务，点击上方「+ 新建项目任务」开始</p>';
  } else {
    for (const p of projNames) {
      html += `<details open class="mb-12 border-default br-6 overflow-hidden">
        <summary class="tab-item">
          📁 ${escapeHtml(p)} <span class="fw-normal-tertiary">(${byProject[p].length})</span>
        </summary>
        <div class="pad8-col-gap8">`;
      for (const t of byProject[p]) {
        html += renderProjectTaskCard(t);
      }
      html += '</div></details>';
    }
  }

  container.innerHTML = html;

  // 绑定新建按钮
  const createBtn = document.getElementById('ptask-create');
  if (createBtn) createBtn.onclick = createProjectTask;
  const cancelBtn = document.getElementById('ptask-cancel');
  if (cancelBtn) cancelBtn.onclick = () => {
    ['ptask-title','ptask-desc','ptask-ai-goal','ptask-ai-req'].forEach(id => { const el = document.getElementById(id); if (el) el.value = ''; });
    document.getElementById('ptask-ai-result').style.display = 'none';
  };
  // AI 辅助生成
  const aiBtn = document.getElementById('ptask-ai-gen');
  if (aiBtn) aiBtn.onclick = aiAssistTask;
  if (cancelBtn) cancelBtn.onclick = () => {
    ['ptask-title','ptask-desc'].forEach(id => { const el = document.getElementById(id); if (el) el.value = ''; });
    const projSel = document.getElementById('ptask-project'); if (projSel) projSel.value = '';
    const priSel = document.getElementById('ptask-priority'); if (priSel) priSel.value = 'medium';
  };
  } catch (e) {
    console.warn('renderTasksTab 失败:', e.message);
  }
}

// 渲染单个项目任务卡片
function renderProjectTaskCard(t) {
  const statusLabels = { backlog: '○ 待办', active: '◐ 进行中', completed: '✓ 已完成', paused: '⏸ 暂停' };
  const priColors = { urgent: 'var(--error-color)', high: 'var(--warning-color)', medium: 'var(--info-color)', low: 'var(--text-tertiary)' };
  const priColor = priColors[t.priority] || 'var(--text-tertiary)';
  const subDone = (t.subtasks || []).filter(s => s.done).length;
  const subTotal = (t.subtasks || []).length;
  const assigneeLabel = t.assignee === 'hermes' ? '⚡hermes' : t.assignee === 'none' ? '—' : '👤我';

  // 查是否有进行中的派活
  const hasRunning = t._runningDispatch;
  const dispatchBtn = hasRunning
    ? `<button onclick="viewTaskDispatch('${escapeAttr(t.task_id)}')" class="btn-xs btn-outline--warning-var">◐ 执行中</button>`
    : `<button onclick="dispatchTask('${escapeAttr(t.task_id)}','${escapeAttr(t.project||'')}')" class="btn-xs btn-outline--accent">⚡ 派hermes</button>`;

  return `<div style="padding:10px;background:var(--bg-tertiary);border-radius:6px;border-left:3px solid ${priColor};">
    <div class="d-flex jc-between ai-flex-start gap-8 mb-4">
      <div class="fs-085 fw-600 flex-1">${escapeHtml(t.title)}</div>
      <span class="fs-072 text-tertiary ws-nowrap">${statusLabels[t.status] || t.status}</span>
    </div>
    ${t.description ? `<div class="clamp-2">${escapeHtml(t.description)}</div>` : ''}
    <div class="d-flex ai-center gap-8 fs-072 text-tertiary mb-6">
      <span>${assigneeLabel}</span>
      ${t.due_date ? `<span>📅 ${escapeHtml(t.due_date)}</span>` : ''}
      ${subTotal ? `<span>◯ ${subDone}/${subTotal}</span>` : ''}
    </div>
    ${subTotal ? `<div style="height:3px;background:var(--bg-secondary);border-radius:2px;overflow:hidden;margin-bottom:6px;"><div style="width:${Math.round(subDone/subTotal*100)}%;height:100%;background:var(--success-color);"></div></div>` : ''}
    <div class="flex-gap6-wrap">
      ${t.status !== 'completed' ? `<button onclick="cycleTaskStatus('${escapeAttr(t.task_id)}','${escapeAttr(t.status)}')" class="btn-xs">→ 推进</button>` : ''}
      ${dispatchBtn}
    </div>
  </div>`;
}

// AI 辅助任务指派：根据目标自动生成描述+hermes prompt
async function aiAssistTask() {
  const goal = document.getElementById('ptask-ai-goal')?.value.trim();
  if (!goal) { showToast('请输入任务目标', 'warning'); return; }
  const req = document.getElementById('ptask-ai-req')?.value.trim();
  const project = document.getElementById('ptask-project')?.value || '';

  const btn = document.getElementById('ptask-ai-gen');
  if (btn) { btn.disabled = true; btn.textContent = '◐ AI 生成中…'; }
  const resultDiv = document.getElementById('ptask-ai-result');
  if (resultDiv) { resultDiv.style.display = 'block'; resultDiv.innerHTML = '<span style="color:var(--text-tertiary);">◐ 林赛正在生成任务详情…</span>'; }

  try {
    const data = await apiPost('/api/tasks/ai-assist', { goal, requirements: req, project });
    if (data.error) { showToast('✗ ' + data.error, 'error'); return; }

    // 自动填充表单
    const titleEl = document.getElementById('ptask-title');
    if (titleEl && !titleEl.value) titleEl.value = goal.slice(0, 60);

    const descEl = document.getElementById('ptask-desc');
    if (descEl) {
      let desc = data.description || '';
      if (data.deliverables) desc += `\n📊 交付物：${data.deliverables}`;
      if (data.constraints) desc += `\n⚠️ 约束：${data.constraints}`;
      descEl.value = desc.trim();
    }

    // 优先级建议
    if (data.suggested_priority) {
      const prioEl = document.getElementById('ptask-priority');
      if (prioEl) prioEl.value = data.suggested_priority;
    }

    // hermes prompt 存入隐藏字段，创建任务时如果选 hermes 则使用
    window._aiHermesPrompt = data.hermes_prompt || '';

    // 显示生成结果摘要
    if (resultDiv) {
      let html = '<div style="border-top:1px solid var(--border-color);padding-top:6px;">';
      html += `<div style="margin-bottom:4px;">📝 ${escapeHtml(data.description || '').slice(0, 100)}</div>`;
      if (data.hermes_prompt) html += `<div style="color:var(--accent-color);font-size:0.75rem;margin-bottom:4px;">⚡ hermes指令已生成（${data.hermes_prompt.length}字）</div>`;
      html += '<div style="font-size:0.72rem;color:var(--text-tertiary);">✓ 已自动填充表单，可直接创建或修改后创建</div>';
      html += '</div>';
      resultDiv.innerHTML = html;
    }
    showToast('✓ AI 已生成任务详情并填充表单', 'success');
  } catch (e) {
    showToast('✗ AI 生成失败: ' + e.message, 'error');
    if (resultDiv) resultDiv.innerHTML = '<span style="color:var(--error-color);">生成失败</span>';
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = '🤖 AI 生成任务详情'; }
  }
}

// 创建项目任务
async function createProjectTask() {
  const title = document.getElementById('ptask-title')?.value.trim();
  if (!title) { showToast('请填写任务标题', 'warning'); return; }
  const project = document.getElementById('ptask-project')?.value || '';
  const priority = document.getElementById('ptask-priority')?.value || 'medium';
  const due_date = document.getElementById('ptask-due')?.value || '';
  const description = document.getElementById('ptask-desc')?.value.trim();
  const assignee = document.querySelector('input[name="ptask-assignee"]:checked')?.value || 'myself';

  const btn = document.getElementById('ptask-create');
  if (btn) { btn.disabled = true; btn.textContent = '◐ 创建中…'; }
  try {
    // 如果 AI 生成了 hermes_prompt 且选了 hermes 执行，用 AI 的 prompt
    const hermesPrompt = (assignee === 'hermes' && window._aiHermesPrompt) ? window._aiHermesPrompt : '';
    const resp = await apiPost('/api/tasks', { title, project, priority, due_date, description, assignee, hermes_prompt: hermesPrompt });
    window._aiHermesPrompt = '';  // 清除
    if (assignee === 'hermes' && resp.dispatch_id) {
      showToast(`✓ 任务已创建并派给 hermes（执行追踪 #${resp.dispatch_id.slice(-6)}）`, 'success');
      setTimeout(() => switchProjectsTab('dispatches'), 800);
    } else {
      showToast('✓ 任务已创建', 'success');
    }
    renderTasksTab(document.getElementById('projects-body'));
  } catch (e) {
    showToast(`✗ 创建失败: ${e.message}`, 'error');
    if (btn) { btn.disabled = false; btn.textContent = '✓ 创建任务'; }
  }
}

// 派任务给 hermes（卡片⚡按钮）
async function dispatchTask(taskId, project) {
  if (!await confirmModal('确定把这个任务派给 hermes 执行？（hermes 会在后台自主执行，可在执行追踪页查看结果）', '派发')) return;
  showToast('◐ 派发中…', 'info');
  try {
    const resp = await apiPost(`/api/tasks/${encodeURIComponent(taskId)}/dispatch`, { project });
    showToast(`✓ 已派给 hermes（追踪 #${resp.dispatch_id.slice(-6)}）`, 'success');
    setTimeout(() => switchProjectsTab('dispatches'), 600);
  } catch (e) {
    showToast(`✗ 派发失败: ${e.message}`, 'error');
  }
}

// 推进任务状态（backlog→active→completed），刷新项目面板视图（renderTasksTab）。
// 注意：task.js 的 updateTaskStatus 也调用 PUT /api/tasks/{id}，但它面向任务看板
// 侧栏（renderTaskBoard）并直接更新 State.tasks；二者后端调用相同但 UI/状态管理
// 不同，故保持独立未合并。
async function cycleTaskStatus(taskId, currentStatus) {
  const next = currentStatus === 'backlog' ? 'active' : 'completed';
  try {
    await apiPut(`/api/tasks/${encodeURIComponent(taskId)}`, { status: next });
    showToast(`✓ 已推进到「${next === 'active' ? '进行中' : '已完成'}」`, 'success');
    renderTasksTab(document.getElementById('projects-body'));
  } catch (e) {
    showToast(`✗ 推进失败: ${e.message}`, 'error');
  }
}

// 查看任务的派活输出
async function viewTaskDispatch(taskId) {
  try {
  switchProjectsTab('dispatches');
  // dispatches 页会加载全部，这里可加高亮，简化处理直接跳转
  } catch (e) {
    console.warn('viewTaskDispatch 失败:', e.message);
  }
}

// ============================================
// v3.1.0: 💭 项目意见 tab
// ============================================
async function renderOpinionsTab(container) {
  try {
  const [opinionsData, projectsData] = await Promise.all([
    apiGet('/api/projects/opinions'),
    apiGet('/api/projects/list'),
  ]);
  const opinions = opinionsData.opinions || [];
  const projects = (projectsData.projects || []).map(p => p.name);

  let html = '<div style="display:grid;grid-template-columns:1fr 1.4fr;gap:16px;">';

  // 左：输入区
  html += '<div>';
  html += '<h4 class="h3-sm">💬 提出项目意见</h4>';
  html += `<select id="op-project" style="width:100%;padding:8px;margin-bottom:8px;border:1px solid var(--border-color);border-radius:6px;background:var(--bg-primary);color:var(--text-primary);font-size:0.85rem;box-sizing:border-box;">
    <option value="">（通用，无项目）</option>
    ${projects.map(p => `<option value="${escapeHtml(p)}">${escapeHtml(p)}</option>`).join('')}
  </select>`;
  html += '<textarea id="op-content" placeholder="写下你对项目的意见、建议、想法…（必填）" rows="6" style="width:100%;padding:8px;margin-bottom:8px;border:1px solid var(--border-color);border-radius:6px;background:var(--bg-primary);color:var(--text-primary);font-size:0.85rem;box-sizing:border-box;resize:vertical;"></textarea>';
  html += '<label class="d-flex ai-center gap-6 fs-08 text-secondary mb-10 cursor-pointer"><input type="checkbox" id="op-feed-hermes" checked class="w-auto"> 同时反馈给 hermes（异步，不阻塞）</label>';
  html += '<button id="op-submit" class="w-100 pad-10 bg-accent text-white border-none br-6 cursor-pointer fs-085">✓ 提交意见</button>';
  html += '</div>';

  // 右：意见列表
  html += '<div>';
  html += `<h4 class="h3-sm">📜 意见记录（${opinions.length}）</h4>`;
  if (!opinions.length) {
    html += '<p style="color:var(--text-tertiary);font-size:0.82rem;padding:20px 0;text-align:center;">暂无意见</p>';
  } else {
    html += '<div style="display:flex;flex-direction:column;gap:8px;max-height:60vh;overflow-y:auto;">';
    for (const o of opinions) {
      const statusBadge = o.status === 'resolved'
        ? '<span class="text-success">✓ 已解决</span>'
        : '<span class="text-warning">○ 待处理</span>';
      const fedBadge = o.fed_to_hermes ? '<span class="text-info">⚡已反馈</span>' : '';
      html += `<div style="padding:10px;background:var(--bg-secondary);border-radius:6px;border-left:3px solid ${o.status === 'resolved' ? 'var(--success-color)' : 'var(--warning-color)'};">
        <div class="d-flex jc-between mb-4 fs-072">
          <span class="text-tertiary">📁 ${escapeHtml(o.project || '通用')} · ${escapeHtml((o.created_at||'').slice(0,10))}</span>
          <span>${statusBadge} ${fedBadge}</span>
        </div>
        <div class="fs-082 text-primary mb-6 ws-pre-wrap">${escapeHtml(o.content)}</div>
        <div class="flex-gap6">
          ${o.status !== 'resolved' ? `<button onclick="resolveOpinion('${escapeAttr(o.id)}')" class="btn-xs btn-outline--success">✓ 标记解决</button>` : ''}
          <button onclick="discussOpinion('${escapeAttr(o.id)}','${escapeAttr((o.content||'').slice(0,80))}')" class="btn-xs">🗨️ 转讨论</button>
        </div>
      </div>`;
    }
    html += '</div>';
  }
  html += '</div>';

  html += '</div>';
  container.innerHTML = html;

  const submitBtn = document.getElementById('op-submit');
  if (submitBtn) submitBtn.onclick = submitOpinion;
  } catch (e) {
    console.warn('renderOpinionsTab 失败:', e.message);
  }
}

async function submitOpinion() {
  const project = document.getElementById('op-project')?.value || '';
  const content = document.getElementById('op-content')?.value.trim();
  const feed_hermes = document.getElementById('op-feed-hermes')?.checked;
  if (!content) { showToast('请填写意见内容', 'warning'); return; }
  const btn = document.getElementById('op-submit');
  if (btn) { btn.disabled = true; btn.textContent = '◐ 提交中…'; }
  try {
    await apiPost('/api/projects/opinions', { project, content, feed_hermes });
    showToast(feed_hermes ? '✓ 意见已提交并反馈 hermes' : '✓ 意见已提交', 'success');
    renderOpinionsTab(document.getElementById('projects-body'));
  } catch (e) {
    showToast(`✗ 提交失败: ${e.message}`, 'error');
    if (btn) { btn.disabled = false; btn.textContent = '✓ 提交意见'; }
  }
}

async function resolveOpinion(opId) {
  try {
    await apiPut(`/api/projects/opinions/${encodeURIComponent(opId)}/resolve`, {});
    showToast('✓ 已标记解决', 'success');
    renderOpinionsTab(document.getElementById('projects-body'));
  } catch (e) {
    showToast(`✗ 操作失败: ${e.message}`, 'error');
  }
}

// 意见转讨论（填入聊天框）
function discussOpinion(opId, contentSnippet) {
  closeProjectsManager();
  const input = document.getElementById('message-input');
  if (input) {
    input.value = `💭 关于项目意见「${contentSnippet}」，我想和林赛讨论：`;
    input.focus();
  }
  showToast('💬 已填入聊天框，补充你的问题后发送', 'info');
}

// ============================================
// v3.1.0: ⚡ 执行追踪 tab
// ============================================
async function renderDispatchesTab(container) {
  const data = await apiGet('/api/projects/dispatches?limit=50');
  const dispatches = data.dispatches || [];

  let html = '<div class="d-flex jc-between ai-center mb-12">';
  html += '<h4 class="fs-09 m-0 text-primary">⚡ hermes 执行追踪</h4>';
  html += '<button onclick="renderDispatchesTab(document.getElementById(\'projects-body\'))" class="btn-outline">🔄 刷新</button>';
  html += '</div>';

  if (!dispatches.length) {
    html += '<div class="state-empty">';
    html += '<div class="fs-2 mb-8">⚡</div>';
    html += '<p class="fs-085">暂无派活记录</p>';
    html += '<p class="fs-078 mt-6">在「📋 项目任务」创建任务时选「派 hermes」，或点任务卡片的 ⚡ 按钮</p>';
    html += '</div>';
    container.innerHTML = html;
    return;
  }

  html += '<div class="col-gap8">';
  for (const d of dispatches) {
    const statusMap = {
      running: { icon: '◐', label: '执行中', color: 'var(--warning-color)' },
      done: { icon: '✓', label: '完成', color: 'var(--success-color)' },
      failed: { icon: '✗', label: '失败', color: 'var(--error-color)' },
      timeout: { icon: '⏱', label: '超时', color: 'var(--error-color)' },
    };
    const st = statusMap[d.status] || statusMap.running;
    const sourceLabel = d.source === 'create' ? '创建即派' : d.source === 'opinion' ? '意见派发' : '手动派发';
    const duration = d.finished_at && d.started_at ? `· 耗时 ${calcDuration(d.started_at, d.finished_at)}` : '';

    html += `<div style="padding:12px;background:var(--bg-secondary);border-radius:8px;border-left:3px solid ${st.color};">
      <div class="d-flex jc-between ai-flex-start gap-8 mb-6">
        <div class="flex-1">
          <div class="fs-085 fw-500">${st.icon} <span style="color:${st.color};">[${st.label}]</span> ${escapeHtml((d.prompt||'').slice(0,70))}${(d.prompt||'').length > 70 ? '…' : ''}</div>
          <div class="fs-072 text-tertiary mt-3">📁 ${escapeHtml(d.project||'通用')} · ${sourceLabel} · ${escapeHtml((d.started_at||'').slice(0,16).replace('T',' '))} ${duration}</div>
        </div>
      </div>`;
    if (d.output_snippet && d.status !== 'running') {
      html += `<details class="mt-6"><summary class="cursor-pointer fs-072 text-accent">查看输出</summary>
        <pre style="margin-top:6px;padding:8px;background:var(--bg-tertiary);border-radius:4px;font-size:0.72rem;max-height:240px;overflow-y:auto;white-space:pre-wrap;word-break:break-word;">${escapeHtml(d.output_snippet)}</pre>
      </details>`;
    }
    if (d.status === 'running') {
      html += '<div class="fs-072 text-tertiary mt-4">◐ hermes 正在后台执行…点击上方「🔄 刷新」查看结果</div>';
    }
    html += '</div>';
  }
  html += '</div>';
  container.innerHTML = html;
}

function calcDuration(start, end) {
  try {
    const s = new Date(start.replace('Z','')).getTime();
    const e = new Date(end.replace('Z','')).getTime();
    const sec = Math.round((e - s) / 1000);
    if (sec < 60) return `${sec}s`;
    if (sec < 3600) return `${Math.round(sec/60)}m`;
    return `${(sec/3600).toFixed(1)}h`;
  } catch (e) { return '?'; }
}

// ============================================
// NSFC 三区面板（v2.9.2：课题产物 + 调研资料 + 待决策项）
// ============================================
async function renderNsfcTree(container) {
  try {
  const [topics, refs, pending] = await Promise.all([
    apiGet('/api/projects/nsfc/topics'),
    apiGet('/api/projects/nsfc/references'),
    apiGet('/api/projects/nsfc/pending'),
  ]);

  let html = '';

  // === 区域 1：课题产物（卡片网格）===
  const progressColors = { mature: 'var(--success-color)', growing: 'var(--info-color)', seedling: 'var(--warning-color)', empty: 'var(--text-tertiary)' };
  const progressLabels = { mature: '🌳 成熟', growing: '🌿 成长中', seedling: '🌱 起步', empty: '○ 空' };

  html += '<h4 class="h3-xs">📋 课题产物（点击展开浏览文档）</h4>';
  html += '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px;margin-bottom:20px;">';
  for (const t of (topics.topics || [])) {
    const color = progressColors[t.progress] || 'inherit';
    html += `<details class="border-default br-8 overflow-hidden bg-secondary">
      <summary style="padding:8px 10px;cursor:pointer;font-size:0.82rem;font-weight:600;user-select:none;">
        <span style="color:${color};">${t.topic}</span> ${escapeHtml(t.name)}
        <div class="fs-072 fw-400 text-tertiary mt-2">
          ${progressLabels[t.progress]} · ${t.total_kb}KB · 📚${t.references_count}
        </div>
      </summary>
      <div style="padding:6px 8px;border-top:1px solid var(--border-color);">`;
    if (t.notes && t.notes.length) {
      html += '<div class="fs-072 text-secondary mb-4">📄 立项依据：</div>';
      for (const n of t.notes) {
        html += `<div style="font-size:0.75rem;padding:2px 0;color:var(--text-secondary);">
          ${escapeHtml(n.name).replace(/\.md$/,'')} <span class="text-tertiary">(${n.size_kb}KB, ${n.modified})</span>
        </div>`;
      }
    } else {
      html += '<div class="meta-sm">无文档</div>';
    }
    html += `<div class="fs-072 mt-4 text-tertiary">📚 ${t.references_count} 篇参考 · 🧠 ${t.decisions_count} 条决策</div>`;
    html += `</div></details>`;
  }
  html += '</div>';

  // === 区域 2：调研资料（折叠列表）===
  html += '<details class="mb-16 border-default br-6 overflow-hidden">';
  html += '<summary class="tab-item">📚 调研资料</summary>';
  html += '<div style="padding:8px 12px;">';
  // references
  if (refs.references && refs.references.length) {
    html += `<div class="fs-08 mb-4">参考文献笔记（${refs.references.length}）：</div>`;
    for (const r of refs.references.slice(0, 10)) {
      html += `<div class="subhead-sm">📄 ${escapeHtml(r.name)} <span class="text-tertiary">${r.size_kb}KB</span></div>`;
    }
    if (refs.references.length > 10) html += `<div class="fs-072 text-tertiary">... 共 ${refs.references.length} 篇</div>`;
  }
  // knowledge_base
  const kb = refs.knowledge_base || {};
  for (const [type, items] of Object.entries(kb)) {
    if (items && items.length) {
      html += `<div class="subhead">${type}（${items.length}）：</div>`;
      for (const it of items) {
        html += `<div class="subhead-sm">📝 ${escapeHtml(it.name)} <span class="text-tertiary">${it.size_kb}KB</span></div>`;
      }
    }
  }
  // briefs
  if (refs.briefs && refs.briefs.length) {
    html += `<div class="subhead">每日简报（${refs.briefs.length}）：</div>`;
    for (const b of refs.briefs.slice(0, 5)) {
      html += `<div class="subhead-sm">📊 ${escapeHtml(b.date)} <span class="text-tertiary">${b.size_kb}KB</span></div>`;
    }
  }
  html += '</div></details>';

  // === 区域 3：待决策项（卡片）===
  const pendItems = pending.pending || [];
  html += `<h4 class="h3-xs">📌 待决策项（${pendItems.length}）</h4>`;
  if (!pendItems.length) {
    html += '<p class="text-tertiary fs-082 pad-8">暂无待决策项 🎉</p>';
  } else {
    html += '<div class="col-gap8">';
    for (const p of pendItems) {
      html += `<div style="padding:10px;background:var(--bg-secondary);border-radius:8px;border-left:3px solid var(--warning-color);">
        <div class="fs-085 fw-500 mb-4">📌 ${escapeHtml(p.title)}</div>
        <div class="meta-sm-mb">${p.related_topic ? '课题 '+p.related_topic+' · ' : ''}来源 ${escapeHtml(p.source)}</div>
        <div class="flex-gap6">
          <button onclick="nsfcDecide('${escapeAttr(p.id)}','approve','${escapeAttr(p.title)}')" class="btn-outline-5 btn-outline--success">✓ 通过</button>
          <button onclick="nsfcDecide('${escapeAttr(p.id)}','reject','${escapeAttr(p.title)}')" class="btn-outline-5 btn-outline--tertiary">✗ 否决</button>
          <button onclick="nsfcDiscuss('${escapeAttr(p.id)}','${escapeAttr(p.title)}','${escapeAttr(p.related_topic)}')" class="btn-filled-5">💬 讨论</button>
        </div>
      </div>`;
    }
    html += '</div>';
  }

  html += `<div id="nsfc-file-viewer" class="mt-12 d-none"></div>`;
  container.innerHTML = html;
  } catch (e) {
    console.warn('renderNsfcTree 失败:', e.message);
  }
}

// NSFC 决策（通过/否决）
async function nsfcDecide(pid, action, title) {
  const labels = { approve: '通过', reject: '否决' };
  showToast(`◐ ${labels[action]}: ${title.slice(0,30)}...`, 'info');
  try {
    await apiPost(`/api/projects/nsfc/pending/${pid}`, { action, title });
    showToast(`✓ 已${labels[action]}，已反馈 hermes`, 'success');
    loadProjectsTab('nsfc');  // 刷新
  } catch (e) {
    showToast(`✗ 操作失败: ${e.message}`, 'error');
  }
}

// NSFC 讨论（注入上下文 → 聊天框）
async function nsfcDiscuss(pid, title, topic) {
  try {
    const resp = await apiPost(`/api/projects/nsfc/pending/${pid}`, { action: 'discuss', title, related_topic: topic });
    closeProjectsManager();
    // 加载该课题的知识库上下文
    window._kbSelectedFiles = [];
    window._discussContext = { pid, title, topic, context_files: resp.context_files || [] };
    // 注入 references 内容
    for (const fp of (resp.context_files || []).slice(0, 3)) {
      try {
        const data = await apiGet(`/api/knowledge/file-content?path=${encodeURIComponent('references/' + fp)}`);
        if (data.content) window._kbSelectedFiles.push({ path: 'references/' + fp, title: fp });
      } catch (e) {}
    }
    // 填入聊天框
    const input = document.getElementById('message-input');
    if (input) {
      input.value = `📌 关于待决策项「${title}」（课题${topic}），基于知识库讨论：`;
      input.focus();
    }
    // 显示讨论工具栏（总结按钮）
    showDiscussBar(pid, title);
    showToast(`💬 已加载课题${topic}的知识库，开始讨论`, 'info');
  } catch (e) {
    showToast(`✗ 启动讨论失败: ${e.message}`, 'error');
  }
}

// 讨论工具栏（显示"总结讨论"按钮）
function showDiscussBar(pid, title) {
  let bar = document.getElementById('discuss-bar');
  if (!bar) {
    bar = document.createElement('div');
    bar.id = 'discuss-bar';
    bar.style.cssText = 'position:sticky;top:0;background:var(--bg-secondary);border:1px solid var(--accent-color);border-radius:6px;padding:6px 10px;margin-bottom:6px;display:flex;align-items:center;gap:8px;font-size:0.82rem;z-index:10;';
    document.querySelector('#messages')?.prepend(bar);
  }
  bar.innerHTML = `<span class="text-accent">💬 正在讨论：${escapeHtml(title.slice(0,40))}</span>
    <button id="discuss-summarize-btn" style="margin-left:auto;padding:4px 12px;background:var(--accent-color);color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:0.78rem;">📝 总结讨论</button>
    <button id="discuss-cancel-btn" class="btn-outline">取消</button>`;
  bar.style.display = 'flex';
  document.getElementById('discuss-summarize-btn').onclick = () => summarizeDiscussion(pid, title);
  document.getElementById('discuss-cancel-btn').onclick = () => { bar.style.display = 'none'; window._discussContext = null; };
}

// 总结讨论 → 写 discussions + 反馈 hermes
async function summarizeDiscussion(pid, title) {
  const input = document.getElementById('message-input');
  showToast('◐ 林赛正在总结讨论...', 'info');
  // 让林赛总结当前会话
  input.value = `请总结我们刚才关于「${title}」的讨论，给出结论和下一步建议（3-5句话）。`;
  // 标记这是总结请求
  window._discussSummaryPending = { pid, title, topic: window._discussContext?.topic || '' };
  // 触发展示"提交总结"按钮（在林赛回复后）
  setTimeout(() => {
    const bar = document.getElementById('discuss-bar');
    if (bar) {
      bar.innerHTML = `<span class="text-accent">⏳ 等待林赛总结...收到后点击提交</span>
        <button id="submit-summary-btn" style="margin-left:auto;padding:4px 12px;background:var(--success-color);color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:0.78rem;">✓ 提交总结到 discussions</button>
        <button id="discuss-cancel-btn" class="btn-outline">取消</button>`;
      document.getElementById('submit-summary-btn').onclick = submitDiscussionSummary;
      document.getElementById('discuss-cancel-btn').onclick = () => { bar.style.display = 'none'; };
    }
  }, 100);
}

// 提交讨论总结到后端
async function submitDiscussionSummary() {
  // 获取林赛最后一条回复
  const msgs = document.querySelectorAll('.message.assistant');
  const lastMsg = msgs[msgs.length - 1];
  const summary = lastMsg ? lastMsg.textContent.trim().slice(0, 1000) : '';
  if (!summary) { showToast('未找到林赛的总结回复', 'error'); return; }

  const ctx = window._discussSummaryPending || {};
  showToast('◐ 提交总结并反馈 hermes...', 'info');
  try {
    await apiPost('/api/projects/nsfc/discuss-summary', {
      pending_id: ctx.pid || '',
      title: ctx.title || '',
      topic: ctx.topic || '',
      summary,
    });
    showToast('✓ 讨论总结已写入 discussions 并反馈 hermes', 'success');
    document.getElementById('discuss-bar').style.display = 'none';
    window._discussContext = null;
    window._discussSummaryPending = null;
  } catch (e) {
    showToast(`✗ 提交失败: ${e.message}`, 'error');
  }
}

// ============================================
// 文献候选池（v2.9.1：三状态分组 + 持久化）
// ============================================
async function renderPapersCards(container) {
  try {
  const pool = await apiGet('/api/projects/papers/pool');
  const byStatus = pool.by_status || {};
  const unseenCount = (byStatus.unseen||0) + (byStatus.pushed||0) + (byStatus.candidate||0) + (byStatus.interested||0);
  const pushedCount = byStatus.pushed || 0;

  let html = `<div style="margin-bottom:12px;padding:8px 12px;background:var(--bg-secondary);border-radius:6px;font-size:0.8rem;color:var(--text-secondary);">
    📊 候选池：<strong class="text-info">${unseenCount}</strong> 未看 ·
    <strong class="text-warning">${byStatus.viewed||0}</strong> 已看未讨论 ·
    <strong class="text-success">${byStatus.archived||0}</strong> 已归档${pushedCount > 0 ? ` · <span class="text-info">📡 ${pushedCount} 篇已推送飞书</span>` : ''}
    <span class="ml-8-tertiary">(共 ${pool.total} 篇，累积保留)</span>
    <span class="ml-8-tertiary">| 📚 沉淀后可在知识库浏览</span>
  </div>`;

  // 按状态分组（pushed/candidate/interested 归入未看，因为都是还没处理的新论文）
  const UNSEEN_STATUSES = ['unseen', 'pushed', 'candidate', 'interested'];
  const groups = [
    {status: 'unseen', label: '🔔 未看（待你决定）', color: 'var(--info-color)', defaultOpen: true},
    {status: 'viewed', label: '📖 已看未讨论（感兴趣/待深读，讨论后归档）', color: 'var(--warning-color)', defaultOpen: false},
    {status: 'archived', label: '✅ 已归档（深度阅读+讨论后的知识沉淀）', color: 'var(--success-color)', defaultOpen: false},
  ];

  const papers = pool.papers || [];
  for (const g of groups) {
    const groupPapers = g.status === 'unseen'
      ? papers.filter(p => UNSEEN_STATUSES.includes(p.status))
      : papers.filter(p => p.status === g.status);
    if (!groupPapers.length) continue;
    const openAttr = g.defaultOpen ? 'open' : '';
    html += `<details ${openAttr} class="mb-10 border-default br-6 overflow-hidden">
      <summary style="padding:8px 12px;cursor:pointer;font-weight:600;font-size:0.85rem;background:var(--bg-secondary);color:${g.color};">
        ${g.label} <span class="fw-normal-tertiary">(${groupPapers.length})</span>
      </summary>
      <div class="pad8-col-gap8">`;

    for (const p of groupPapers) {
      const scorePct = Math.round((p.score || 0) * 100);
      // P2-2: 文献生命周期进度条
      const lifecycleSteps = ['unseen', 'viewed', 'archived'];
      const currentStep = lifecycleSteps.indexOf(g.status);
      const lifecycleHtml = lifecycleSteps.map((step, i) => {
        const isActive = i <= currentStep;
        const colors = { unseen: 'var(--info-color)', viewed: 'var(--warning-color)', archived: 'var(--success-color)' };
        return `<span style="flex:1;height:3px;border-radius:2px;background:${isActive ? colors[step] : 'var(--bg-tertiary)'};"></span>`;
      }).join('<span style="width:2px;"></span>');
      const lifecycleLabels = ['未看', '感兴趣', '已沉淀'];
      const lifecycleLabelHtml = lifecycleLabels.map((label, i) => {
        const isActive = i <= currentStep;
        return `<span style="font-size:0.65rem;color:${isActive ? 'var(--text-secondary)' : 'var(--text-tertiary)'};">${label}</span>`;
      }).join('<span style="width:2px;"></span>');

      html += `<div class="paper-card" id="card-${escapeHtml(p.arxiv_id)}" style="padding:10px;background:var(--bg-tertiary);border-radius:6px;border:1px solid var(--border-color);transition:opacity 0.3s;">`;
      // P2-2: 生命周期进度条
      html += `<div style="display:flex;align-items:center;gap:2px;margin-bottom:6px;">${lifecycleHtml}</div>`;
      html += `<div class="d-flex jc-between mb-4">${lifecycleLabelHtml}</div>`;
      html += `<div style="font-size:0.85rem;font-weight:600;line-height:1.4;margin-bottom:3px;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;">${escapeHtml(p.title)}</div>`;
      html += `<div class="meta-sm-mb">${escapeHtml(p.authors)} · ${escapeHtml(p.direction)} · ${scorePct}%${p.pushed_to_feishu ? ' · <span style="color:var(--info-color);">📡已推送飞书</span>' : ''}${p.unified_status && p.unified_status !== p.status ? ' · <span style="color:var(--accent-color);">'+escapeHtml(p.unified_status)+'</span>' : ''}</div>`;
      if (p.tldr) {
        html += `<div class="clamp-2">${escapeHtml(p.tldr)}</div>`;
      }
      html += `<div class="flex-gap6-wrap">`;

      if (g.status === 'unseen') {
        html += `<button onclick="paperFeedback('${escapeAttr(p.arxiv_id)}','interested',this)" class="btn-outline-5 btn-outline--success">👍 感兴趣</button>`;
        html += `<button onclick="paperFeedback('${escapeAttr(p.arxiv_id)}','later',this)" style="padding:4px 10px;border:1px solid var(--border-color);border-radius:5px;background:transparent;color:var(--warning-color);cursor:pointer;font-size:0.78rem;">⏰ 稍后</button>`;
        html += `<button onclick="paperFeedback('${escapeAttr(p.arxiv_id)}','skip',this)" class="btn-outline-5 btn-outline--tertiary">👎 跳过</button>`;
        html += `<button onclick="discussPaper('${escapeAttr(p.arxiv_id)}','${escapeAttr(p.title)}')" class="btn-filled-5">💬 讨论</button>`;
      } else if (g.status === 'viewed') {
        // 已看未讨论：主要操作是讨论，讨论完可归档
        html += `<button onclick="discussPaper('${escapeAttr(p.arxiv_id)}','${escapeAttr(p.title)}')" class="btn-filled-5">💬 讨论</button>`;
        html += `<button onclick="paperFeedback('${escapeAttr(p.arxiv_id)}','discuss_done',this)" class="btn-outline-5 btn-outline--success">📥 归档沉淀</button>`;
      } else {
        html += `<span class="fs-075 text-success pad-4-8">✓ 已深度沉淀</span>`;
      }
      html += `</div></div>`;
    }
    html += `</div></details>`;
  }

  if (!papers.length) {
    html = '<p class="state-loading state-loading pad-40">候选池为空</p>';
  }
  container.innerHTML = html;
  } catch (e) {
    console.warn('renderPapersCards 失败:', e.message);
  }
}

// 讨论某篇文献（跳到聊天框 + 注入上下文）
async function discussPaper(arxivId, title) {
  // v4.1: 打开独立讨论弹窗（不再填入侧栏聊天）
  closeProjectsManager();
  openPaperDiscussion(arxivId, title);
}

// 文献反馈处理
async function paperFeedback(arxivId, action, btn) {
  const card = btn.closest('.paper-card');
  if (action === 'interested') {
    btn.textContent = '◐ 处理中…'; btn.disabled = true;
  }
  try {
    const resp = await apiPost('/api/projects/papers/feedback', { arxiv_id: arxivId, action });
    const r = resp.result || {};

    if (action === 'interested') {
      showToast('👍 已标记感兴趣，移入"已看未讨论"，待深度讨论后归档', 'success');
    } else if (action === 'discuss_done') {
      let msg = `✓ 已归档沉淀: ${r.archived || '已存在'}`;
      if (r.has_analysis) msg += ' + 深度解析已导入';
      showToast(msg, 'success');
      // 展示 wiki 建议确认
      if (r.wiki_suggestion && r.wiki_suggestion.available) {
        showWikiGrowConfirm(r.wiki_suggestion);
      }
    } else if (action === 'archive') {
      showToast(`✓ 已归档: ${r.archived || '已存在'}`, 'success');
    } else if (action === 'skip') {
      showToast('👎 已记录偏好', 'info');
    } else if (action === 'later') {
      showToast('⏰ 已标记稍后', 'info');
    }

    // 刷新候选池（状态流转，不删除）
    if (card) card.style.opacity = '0.4';
    setTimeout(() => loadProjectsTab('papers'), 600);
  } catch (e) {
    showToast(`✗ 操作失败: ${e.message}`, 'error');
    if (action === 'interested') { btn.textContent = '👍 感兴趣'; btn.disabled = false; }
  }
}

// wiki 笔记生成确认弹窗
function showWikiGrowConfirm(suggestion) {
  const concepts = suggestion.concepts || [];
  const methods = suggestion.methods || [];
  const relations = suggestion.relations || [];
  if (!concepts.length && !methods.length && !relations.length) {
    return;  // 无建议，不弹窗
  }

  let html = `<div class="mw-500">
    <h3 class="mb-8">📚 知识库生长建议</h3>
    <p class="fs-085 text-secondary mb-12">已归档 <strong>${escapeHtml(suggestion.title)}</strong>，以下内容可提取为知识库笔记：</p>`;

  // concept 建议
  if (concepts.length) {
    html += '<div class="mb-10"><div class="label-bold-mb4">概念笔记：</div>';
    concepts.slice(0, 6).forEach((c, i) => {
      const checked = c.existing ? '' : 'checked';
      const tag = c.existing ? `<span class="text-info fs-072">→ 连接已有「${escapeHtml(c.existing_title)}」</span>` : '<span class="text-success fs-072">新建</span>';
      html += `<label style="display:flex;align-items:center;gap:6px;padding:3px 0;font-size:0.82rem;">
        <input type="checkbox" id="grow-c-${i}" ${checked} ${c.existing ? '' : ''}> 
        <span>${escapeHtml(c.name)}</span> ${tag}
      </label>`;
    });
    html += '</div>';
  }

  // relation 建议
  if (relations.length) {
    html += '<div class="mb-10"><div class="label-bold-mb4">图谱关联：</div>';
    relations.slice(0, 4).forEach((rel, i) => {
      html += `<label style="display:flex;align-items:center;gap:6px;padding:2px 0;font-size:0.8rem;">
        <input type="checkbox" id="grow-r-${i}" checked> 
        <span>${escapeHtml(rel.from)} → ${escapeHtml(rel.to)}</span>
      </label>`;
    });
    html += '</div>';
  }

  html += `<div class="d-flex gap-8 mt-12">
    <button id="grow-confirm-btn" class="btn-confirm">✓ 确认生成</button>
    <button id="grow-skip-btn" class="btn-ghost-cancel">跳过</button>
  </div></div>`;

  showModal(html);

  // 绑定按钮
  setTimeout(() => {
    const confirmBtn = document.getElementById('grow-confirm-btn');
    const skipBtn = document.getElementById('grow-skip-btn');
    if (skipBtn) skipBtn.onclick = closeModal;
    if (confirmBtn) confirmBtn.onclick = async () => {
      const confirmed = { concepts: [], relations: [], project: suggestion.project };
      concepts.forEach((c, i) => {
        const cb = document.getElementById(`grow-c-${i}`);
        if (cb && cb.checked) confirmed.concepts.push({ name: c.name, generate: true, type: 'concepts' });
      });
      relations.forEach((rel, i) => {
        const cb = document.getElementById(`grow-r-${i}`);
        if (cb && cb.checked) confirmed.relations.push({ from: rel.from, to: rel.to, confirm: true });
      });
      confirmBtn.textContent = '◐ 生成中…'; confirmBtn.disabled = true;
      try {
        const result = await apiPost('/api/knowledge/grow', { arxiv_id: suggestion.arxiv_id, confirmed });
        showToast(`✓ 生成 ${result.generated_concepts.length} 篇笔记 + ${result.generated_relations.length} 条关联`, 'success');
        closeModal('modal-overlay');
      } catch (e) {
        showToast(`✗ 生成失败: ${e.message}`, 'error');
        confirmBtn.textContent = '✓ 确认生成'; confirmBtn.disabled = false;
      }
    };
  }, 100);
}

// ============================================
// 多端同步（沿用现有）
// ============================================
async function renderSyncTab(container) {
  const status = await apiGet('/api/sync/status');
  let html = '<div class="mb-16">';
  html += `<div class="label-sm-mb8">同步状态</div>`;
  html += `<div class="pad-10 bg-secondary br-6">
    <div class="fs-085">已同步会话: <strong>${status.synced_sessions_count}</strong></div>
    <div class="fs-085 mt-4">已同步文献: <strong>${status.synced_papers_count}</strong></div>
    <div class="fs-078 text-tertiary mt-4">上次同步: ${escapeHtml(status.last_sync || '从未')}</div>
  </div>`;
  html += `<button id="sync-run-btn" class="mt-10 pad-8-16 bg-accent text-white border-none br-6 cursor-pointer fs-085">🔄 立即同步</button>`;
  html += '</div>';
  if (status.history && status.history.length) {
    html += '<div><div class="fs-08 text-secondary mb-6">同步历史</div>';
    status.history.forEach(h => {
      html += `<div style="padding:4px 0;font-size:0.78rem;color:var(--text-tertiary);">${h.timestamp.slice(0,16)} | 会话+${h.new_sessions} 文献+${h.new_papers}</div>`;
    });
    html += '</div>';
  }
  container.innerHTML = html;
  const syncBtn = document.getElementById('sync-run-btn');
  if (syncBtn) syncBtn.addEventListener('click', async () => {
    syncBtn.disabled = true; syncBtn.textContent = '同步中…';
    try {
      const result = await apiPost('/api/sync/run', {});
      showToast(`✓ 同步完成：会话 +${result.result.new_sessions}，文献 +${result.result.new_papers}`, 'success');
      renderSyncTab(container);
    } catch (e) { showToast(`✗ 同步失败: ${e.message}`, 'error'); }
    finally { syncBtn.disabled = false; syncBtn.textContent = '🔄 立即同步'; }
  });
}

// ============================================
// 初始化
// ============================================
function bindProjectsEvents() {
  document.getElementById('toolbar-projects')?.addEventListener('click', openProjectsManager);
  document.getElementById('projects-close')?.addEventListener('click', closeProjectsManager);
  document.getElementById('projects-overlay')?.addEventListener('click', e => {
    if (e.target === e.currentTarget) closeProjectsManager();
  });
  document.querySelectorAll('.proj-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => switchProjectsTab(btn.dataset.tab));
  });
  document.getElementById('proj-refresh')?.addEventListener('click', () => loadProjectsTab(ProjectsState.currentTab));
}

// v3.5.1: 注册模块初始化
if (typeof ModuleLoader !== 'undefined') {
  ModuleLoader.register('projects', () => {
    if (typeof bindProjectsEvents === 'function') bindProjectsEvents();
  });
}
