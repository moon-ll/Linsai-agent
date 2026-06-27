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
  body.innerHTML = '<p style="color:var(--text-tertiary);text-align:center;padding:40px;">◐ 加载中…</p>';
  try {
    if (tab === 'overview') await renderOverviewTab(body);
    else if (tab === 'tasks') await renderTasksTab(body);
    else if (tab === 'opinions') await renderOpinionsTab(body);
    else if (tab === 'dispatches') await renderDispatchesTab(body);
    else if (tab === 'nsfc') await renderNsfcTree(body);
    else if (tab === 'papers') await renderPapersCards(body);
    else if (tab === 'sync') await renderSyncTab(body);
  } catch (e) {
    body.innerHTML = `<p style="color:var(--error-color);">加载失败: ${escapeHtml(e.message)}</p>`;
  }
}

// ============================================
// v3.1.0: 📊 总览 tab
// ============================================
async function renderOverviewTab(container) {
  const data = await apiGet('/api/projects/overview');
  const ts = data.task_stats || {};
  const ds = data.dispatch_stats || {};

  let html = '<h4 style="font-size:0.95rem;margin:0 0 12px;color:var(--text-primary);">📊 项目总览</h4>';

  // 4 张统计卡
  html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;margin-bottom:20px;">';
  // NSFC 进度卡
  html += `<div style="padding:14px;background:var(--bg-secondary);border-radius:8px;border-left:3px solid var(--accent-color);">
    <div style="font-size:0.75rem;color:var(--text-tertiary);">🔬 NSFC 项目</div>
    <div style="font-size:1.1rem;font-weight:600;margin-top:4px;">${data.nsfc_available ? escapeHtml(data.nsfc_phase || '进行中') : '未启用'}</div>
    <div style="font-size:0.72rem;color:var(--text-tertiary);margin-top:2px;">${data.nsfc_available ? 'state.md 已加载' : '无 hermes 项目'}</div>
  </div>`;
  // 任务卡
  const totalTasks = data.total_tasks || 0;
  html += `<div style="padding:14px;background:var(--bg-secondary);border-radius:8px;border-left:3px solid var(--info-color);">
    <div style="font-size:0.75rem;color:var(--text-tertiary);">📋 项目任务</div>
    <div style="font-size:1.1rem;font-weight:600;margin-top:4px;">${totalTasks} 个</div>
    <div style="font-size:0.72rem;color:var(--text-tertiary);margin-top:2px;">○${ts.backlog||0} 待办 · ◐${ts.active||0} 进行 · ✓${ts.completed||0}</div>
  </div>`;
  // 意见卡
  html += `<div style="padding:14px;background:var(--bg-secondary);border-radius:8px;border-left:3px solid var(--warning-color);">
    <div style="font-size:0.75rem;color:var(--text-tertiary);">💭 项目意见</div>
    <div style="font-size:1.1rem;font-weight:600;margin-top:4px;">${ds.open_opinions||0} 待处理</div>
    <div style="font-size:0.72rem;color:var(--text-tertiary);margin-top:2px;">共 ${ds.total_opinions||0} 条 · ${ds.fed_opinions||0} 已反馈</div>
  </div>`;
  // 执行卡
  html += `<div style="padding:14px;background:var(--bg-secondary);border-radius:8px;border-left:3px solid var(--success-color);">
    <div style="font-size:0.75rem;color:var(--text-tertiary);">⚡ hermes 执行</div>
    <div style="font-size:1.1rem;font-weight:600;margin-top:4px;">${ds.running_dispatches||0} 进行中</div>
    <div style="font-size:0.72rem;color:var(--text-tertiary);margin-top:2px;">✓${ds.done_dispatches||0} 完成 · ✗${ds.failed_dispatches||0} 失败</div>
  </div>`;
  html += '</div>';

  // 快捷新建区
  html += '<div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:20px;">';
  html += '<button onclick="switchProjectsTab(\'tasks\')" style="padding:10px 16px;background:var(--accent-color);color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:0.85rem;">+ 新建项目任务</button>';
  html += '<button onclick="switchProjectsTab(\'opinions\')" style="padding:10px 16px;border:1px solid var(--accent-color);background:transparent;color:var(--accent-color);border-radius:6px;cursor:pointer;font-size:0.85rem;">💬 提出意见</button>';
  html += '<button onclick="switchProjectsTab(\'dispatches\')" style="padding:10px 16px;border:1px solid var(--border-color);background:transparent;color:var(--text-secondary);border-radius:6px;cursor:pointer;font-size:0.85rem;">⚡ 查看执行</button>';
  html += '</div>';

  // 任务分布表
  const byProj = data.task_by_project || {};
  const projKeys = Object.keys(byProj);
  if (projKeys.length) {
    html += '<div style="padding:12px;background:var(--bg-secondary);border-radius:6px;">';
    html += '<div style="font-size:0.8rem;color:var(--text-secondary);margin-bottom:8px;">📁 任务按项目分布</div>';
    for (const p of projKeys) {
      const pct = totalTasks ? Math.round(byProj[p] / totalTasks * 100) : 0;
      html += `<div style="display:flex;align-items:center;gap:8px;margin:4px 0;font-size:0.8rem;">
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
    html += '<div style="margin-top:16px;"><div style="font-size:0.8rem;color:var(--text-secondary);margin-bottom:8px;">⚡ 最近执行</div>';
    for (const d of recent.slice(0, 5)) {
      const statusIcon = d.status === 'done' ? '✓' : d.status === 'failed' ? '✗' : d.status === 'timeout' ? '⏱' : '◐';
      const statusColor = d.status === 'done' ? 'var(--success-color)' : (d.status === 'failed' || d.status === 'timeout') ? 'var(--error-color)' : 'var(--warning-color)';
      html += `<div style="padding:6px 8px;font-size:0.78rem;border-left:2px solid ${statusColor};margin-bottom:4px;">
        ${statusIcon} <span style="color:${statusColor};font-weight:500;">[${d.status}]</span> ${escapeHtml((d.prompt||'').slice(0,60))}…
        <span style="color:var(--text-tertiary);margin-left:6px;">${escapeHtml(d.project||'通用')}</span>
      </div>`;
    }
    html += '</div>';
  }

  container.innerHTML = html;
}

// ============================================
// v3.1.0: 📋 项目任务 tab（核心）
// ============================================
async function renderTasksTab(container) {
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
  html += `<details style="margin-bottom:16px;border:1px solid var(--accent-color);border-radius:8px;overflow:hidden;">
    <summary style="padding:10px 14px;cursor:pointer;font-weight:600;font-size:0.85rem;background:var(--bg-secondary);color:var(--accent-color);">+ 新建项目任务</summary>
    <div style="padding:14px;display:flex;flex-direction:column;gap:10px;">
      <input type="text" id="ptask-title" placeholder="任务标题（必填）" style="width:100%;padding:8px;border:1px solid var(--border-color);border-radius:6px;background:var(--bg-primary);color:var(--text-primary);font-size:0.85rem;box-sizing:border-box;">
      <div style="display:flex;gap:8px;flex-wrap:wrap;">
        <select id="ptask-project" style="flex:1;min-width:140px;padding:8px;border:1px solid var(--border-color);border-radius:6px;background:var(--bg-primary);color:var(--text-primary);font-size:0.85rem;">
          <option value="">（通用，无项目）</option>
          ${projects.map(p => `<option value="${escapeHtml(p)}">${escapeHtml(p)}</option>`).join('')}
        </select>
        <select id="ptask-priority" style="padding:8px;border:1px solid var(--border-color);border-radius:6px;background:var(--bg-primary);color:var(--text-primary);font-size:0.85rem;">
          <option value="medium">中</option><option value="high">高</option><option value="urgent">紧急</option><option value="low">低</option>
        </select>
        <input type="date" id="ptask-due" style="padding:8px;border:1px solid var(--border-color);border-radius:6px;background:var(--bg-primary);color:var(--text-primary);font-size:0.85rem;">
      </div>
      <textarea id="ptask-desc" placeholder="任务描述（可选）" rows="2" style="width:100%;padding:8px;border:1px solid var(--border-color);border-radius:6px;background:var(--bg-primary);color:var(--text-primary);font-size:0.85rem;box-sizing:border-box;resize:vertical;"></textarea>
      <div style="display:flex;align-items:center;gap:16px;font-size:0.85rem;color:var(--text-secondary);">
        <span>执行者:</span>
        <label style="display:flex;align-items:center;gap:4px;cursor:pointer;"><input type="radio" name="ptask-assignee" value="myself" checked>我自己</label>
        <label style="display:flex;align-items:center;gap:4px;cursor:pointer;"><input type="radio" name="ptask-assignee" value="hermes">派 hermes 执行</label>
        <label style="display:flex;align-items:center;gap:4px;cursor:pointer;"><input type="radio" name="ptask-assignee" value="none">先不执行</label>
      </div>
      <div style="display:flex;gap:8px;">
        <button id="ptask-create" style="flex:1;padding:10px;background:var(--accent-color);color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:0.85rem;">✓ 创建任务</button>
        <button id="ptask-cancel" style="padding:10px 16px;border:1px solid var(--border-color);background:transparent;color:var(--text-secondary);border-radius:6px;cursor:pointer;font-size:0.85rem;">清空</button>
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
    html += '<p style="color:var(--text-tertiary);text-align:center;padding:30px;">暂无项目任务，点击上方「+ 新建项目任务」开始</p>';
  } else {
    for (const p of projNames) {
      html += `<details open style="margin-bottom:12px;border:1px solid var(--border-color);border-radius:6px;overflow:hidden;">
        <summary style="padding:8px 12px;cursor:pointer;font-weight:600;font-size:0.85rem;background:var(--bg-secondary);">
          📁 ${escapeHtml(p)} <span style="font-weight:400;color:var(--text-tertiary);">(${byProject[p].length})</span>
        </summary>
        <div style="padding:8px;display:flex;flex-direction:column;gap:8px;">`;
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
    ['ptask-title','ptask-desc'].forEach(id => { const el = document.getElementById(id); if (el) el.value = ''; });
    const projSel = document.getElementById('ptask-project'); if (projSel) projSel.value = '';
    const priSel = document.getElementById('ptask-priority'); if (priSel) priSel.value = 'medium';
  };
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
    ? `<button onclick="viewTaskDispatch('${escapeHtml(t.task_id)}')" style="padding:3px 8px;border:1px solid var(--warning-color);border-radius:4px;background:transparent;color:var(--warning-color);cursor:pointer;font-size:0.72rem;">◐ 执行中</button>`
    : `<button onclick="dispatchTask('${escapeHtml(t.task_id)}','${escapeHtml(t.project||'')}')" style="padding:3px 8px;border:1px solid var(--accent-color);border-radius:4px;background:transparent;color:var(--accent-color);cursor:pointer;font-size:0.72rem;">⚡ 派hermes</button>`;

  return `<div style="padding:10px;background:var(--bg-tertiary);border-radius:6px;border-left:3px solid ${priColor};">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;margin-bottom:4px;">
      <div style="font-size:0.85rem;font-weight:600;flex:1;">${escapeHtml(t.title)}</div>
      <span style="font-size:0.72rem;color:var(--text-tertiary);white-space:nowrap;">${statusLabels[t.status] || t.status}</span>
    </div>
    ${t.description ? `<div style="font-size:0.78rem;color:var(--text-secondary);margin-bottom:6px;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;">${escapeHtml(t.description)}</div>` : ''}
    <div style="display:flex;align-items:center;gap:8px;font-size:0.72rem;color:var(--text-tertiary);margin-bottom:6px;">
      <span>${assigneeLabel}</span>
      ${t.due_date ? `<span>📅 ${escapeHtml(t.due_date)}</span>` : ''}
      ${subTotal ? `<span>◯ ${subDone}/${subTotal}</span>` : ''}
    </div>
    ${subTotal ? `<div style="height:3px;background:var(--bg-secondary);border-radius:2px;overflow:hidden;margin-bottom:6px;"><div style="width:${Math.round(subDone/subTotal*100)}%;height:100%;background:var(--success-color);"></div></div>` : ''}
    <div style="display:flex;gap:6px;flex-wrap:wrap;">
      ${t.status !== 'completed' ? `<button onclick="cycleTaskStatus('${escapeHtml(t.task_id)}','${escapeHtml(t.status)}')" style="padding:3px 8px;border:1px solid var(--border-color);border-radius:4px;background:transparent;color:var(--text-secondary);cursor:pointer;font-size:0.72rem;">→ 推进</button>` : ''}
      ${dispatchBtn}
    </div>
  </div>`;
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
    const resp = await apiPost('/api/tasks', { title, project, priority, due_date, description, assignee });
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
  switchProjectsTab('dispatches');
  // dispatches 页会加载全部，这里可加高亮，简化处理直接跳转
}

// ============================================
// v3.1.0: 💭 项目意见 tab
// ============================================
async function renderOpinionsTab(container) {
  const [opinionsData, projectsData] = await Promise.all([
    apiGet('/api/projects/opinions'),
    apiGet('/api/projects/list'),
  ]);
  const opinions = opinionsData.opinions || [];
  const projects = (projectsData.projects || []).map(p => p.name);

  let html = '<div style="display:grid;grid-template-columns:1fr 1.4fr;gap:16px;">';

  // 左：输入区
  html += '<div>';
  html += '<h4 style="font-size:0.9rem;margin:0 0 10px;color:var(--text-primary);">💬 提出项目意见</h4>';
  html += `<select id="op-project" style="width:100%;padding:8px;margin-bottom:8px;border:1px solid var(--border-color);border-radius:6px;background:var(--bg-primary);color:var(--text-primary);font-size:0.85rem;box-sizing:border-box;">
    <option value="">（通用，无项目）</option>
    ${projects.map(p => `<option value="${escapeHtml(p)}">${escapeHtml(p)}</option>`).join('')}
  </select>`;
  html += '<textarea id="op-content" placeholder="写下你对项目的意见、建议、想法…（必填）" rows="6" style="width:100%;padding:8px;margin-bottom:8px;border:1px solid var(--border-color);border-radius:6px;background:var(--bg-primary);color:var(--text-primary);font-size:0.85rem;box-sizing:border-box;resize:vertical;"></textarea>';
  html += '<label style="display:flex;align-items:center;gap:6px;font-size:0.8rem;color:var(--text-secondary);margin-bottom:10px;cursor:pointer;"><input type="checkbox" id="op-feed-hermes" checked style="width:auto;"> 同时反馈给 hermes（异步，不阻塞）</label>';
  html += '<button id="op-submit" style="width:100%;padding:10px;background:var(--accent-color);color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:0.85rem;">✓ 提交意见</button>';
  html += '</div>';

  // 右：意见列表
  html += '<div>';
  html += `<h4 style="font-size:0.9rem;margin:0 0 10px;color:var(--text-primary);">📜 意见记录（${opinions.length}）</h4>`;
  if (!opinions.length) {
    html += '<p style="color:var(--text-tertiary);font-size:0.82rem;padding:20px 0;text-align:center;">暂无意见</p>';
  } else {
    html += '<div style="display:flex;flex-direction:column;gap:8px;max-height:60vh;overflow-y:auto;">';
    for (const o of opinions) {
      const statusBadge = o.status === 'resolved'
        ? '<span style="color:var(--success-color);">✓ 已解决</span>'
        : '<span style="color:var(--warning-color);">○ 待处理</span>';
      const fedBadge = o.fed_to_hermes ? '<span style="color:var(--info-color);">⚡已反馈</span>' : '';
      html += `<div style="padding:10px;background:var(--bg-secondary);border-radius:6px;border-left:3px solid ${o.status === 'resolved' ? 'var(--success-color)' : 'var(--warning-color)'};">
        <div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:0.72rem;">
          <span style="color:var(--text-tertiary);">📁 ${escapeHtml(o.project || '通用')} · ${escapeHtml((o.created_at||'').slice(0,10))}</span>
          <span>${statusBadge} ${fedBadge}</span>
        </div>
        <div style="font-size:0.82rem;color:var(--text-primary);margin-bottom:6px;white-space:pre-wrap;">${escapeHtml(o.content)}</div>
        <div style="display:flex;gap:6px;">
          ${o.status !== 'resolved' ? `<button onclick="resolveOpinion('${escapeHtml(o.id)}')" style="padding:3px 8px;border:1px solid var(--success-color);border-radius:4px;background:transparent;color:var(--success-color);cursor:pointer;font-size:0.72rem;">✓ 标记解决</button>` : ''}
          <button onclick="discussOpinion('${escapeHtml(o.id)}','${escapeHtml((o.content||'').replace(/'/g,'')).slice(0,80)}')" style="padding:3px 8px;border:1px solid var(--border-color);border-radius:4px;background:transparent;color:var(--text-secondary);cursor:pointer;font-size:0.72rem;">🗨️ 转讨论</button>
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

  let html = '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">';
  html += '<h4 style="font-size:0.9rem;margin:0;color:var(--text-primary);">⚡ hermes 执行追踪</h4>';
  html += '<button onclick="renderDispatchesTab(document.getElementById(\'projects-body\'))" style="padding:4px 10px;border:1px solid var(--border-color);border-radius:4px;background:transparent;color:var(--text-secondary);cursor:pointer;font-size:0.78rem;">🔄 刷新</button>';
  html += '</div>';

  if (!dispatches.length) {
    html += '<div style="text-align:center;padding:40px 20px;color:var(--text-tertiary);">';
    html += '<div style="font-size:2rem;margin-bottom:8px;">⚡</div>';
    html += '<p style="font-size:0.85rem;">暂无派活记录</p>';
    html += '<p style="font-size:0.78rem;margin-top:6px;">在「📋 项目任务」创建任务时选「派 hermes」，或点任务卡片的 ⚡ 按钮</p>';
    html += '</div>';
    container.innerHTML = html;
    return;
  }

  html += '<div style="display:flex;flex-direction:column;gap:8px;">';
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
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;margin-bottom:6px;">
        <div style="flex:1;">
          <div style="font-size:0.85rem;font-weight:500;">${st.icon} <span style="color:${st.color};">[${st.label}]</span> ${escapeHtml((d.prompt||'').slice(0,70))}${(d.prompt||'').length > 70 ? '…' : ''}</div>
          <div style="font-size:0.72rem;color:var(--text-tertiary);margin-top:3px;">📁 ${escapeHtml(d.project||'通用')} · ${sourceLabel} · ${escapeHtml((d.started_at||'').slice(0,16).replace('T',' '))} ${duration}</div>
        </div>
      </div>`;
    if (d.output_snippet && d.status !== 'running') {
      html += `<details style="margin-top:6px;"><summary style="cursor:pointer;font-size:0.72rem;color:var(--accent-color);">查看输出</summary>
        <pre style="margin-top:6px;padding:8px;background:var(--bg-tertiary);border-radius:4px;font-size:0.72rem;max-height:240px;overflow-y:auto;white-space:pre-wrap;word-break:break-word;">${escapeHtml(d.output_snippet)}</pre>
      </details>`;
    }
    if (d.status === 'running') {
      html += '<div style="font-size:0.72rem;color:var(--text-tertiary);margin-top:4px;">◐ hermes 正在后台执行…点击上方「🔄 刷新」查看结果</div>';
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
  const [topics, refs, pending] = await Promise.all([
    apiGet('/api/projects/nsfc/topics'),
    apiGet('/api/projects/nsfc/references'),
    apiGet('/api/projects/nsfc/pending'),
  ]);

  let html = '';

  // === 区域 1：课题产物（卡片网格）===
  const progressColors = { mature: 'var(--success-color)', growing: 'var(--info-color)', seedling: 'var(--warning-color)', empty: 'var(--text-tertiary)' };
  const progressLabels = { mature: '🌳 成熟', growing: '🌿 成长中', seedling: '🌱 起步', empty: '○ 空' };

  html += '<h4 style="font-size:0.9rem;margin:0 0 8px;color:var(--text-primary);">📋 课题产物（点击展开浏览文档）</h4>';
  html += '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px;margin-bottom:20px;">';
  for (const t of (topics.topics || [])) {
    const color = progressColors[t.progress] || 'inherit';
    html += `<details style="border:1px solid var(--border-color);border-radius:8px;overflow:hidden;background:var(--bg-secondary);">
      <summary style="padding:8px 10px;cursor:pointer;font-size:0.82rem;font-weight:600;user-select:none;">
        <span style="color:${color};">${t.topic}</span> ${escapeHtml(t.name)}
        <div style="font-size:0.72rem;font-weight:400;color:var(--text-tertiary);margin-top:2px;">
          ${progressLabels[t.progress]} · ${t.total_kb}KB · 📚${t.references_count}
        </div>
      </summary>
      <div style="padding:6px 8px;border-top:1px solid var(--border-color);">`;
    if (t.notes && t.notes.length) {
      html += '<div style="font-size:0.72rem;color:var(--text-secondary);margin-bottom:4px;">📄 立项依据：</div>';
      for (const n of t.notes) {
        html += `<div style="font-size:0.75rem;padding:2px 0;color:var(--text-secondary);">
          ${escapeHtml(n.name).replace(/\.md$/,'')} <span style="color:var(--text-tertiary);">(${n.size_kb}KB, ${n.modified})</span>
        </div>`;
      }
    } else {
      html += '<div style="font-size:0.75rem;color:var(--text-tertiary);">无文档</div>';
    }
    html += `<div style="font-size:0.72rem;margin-top:4px;color:var(--text-tertiary);">📚 ${t.references_count} 篇参考 · 🧠 ${t.decisions_count} 条决策</div>`;
    html += `</div></details>`;
  }
  html += '</div>';

  // === 区域 2：调研资料（折叠列表）===
  html += '<details style="margin-bottom:16px;border:1px solid var(--border-color);border-radius:6px;overflow:hidden;">';
  html += '<summary style="padding:8px 12px;cursor:pointer;font-weight:600;font-size:0.85rem;background:var(--bg-secondary);">📚 调研资料</summary>';
  html += '<div style="padding:8px 12px;">';
  // references
  if (refs.references && refs.references.length) {
    html += `<div style="font-size:0.8rem;margin-bottom:4px;">参考文献笔记（${refs.references.length}）：</div>`;
    for (const r of refs.references.slice(0, 10)) {
      html += `<div style="font-size:0.75rem;padding:2px 0;">📄 ${escapeHtml(r.name)} <span style="color:var(--text-tertiary);">${r.size_kb}KB</span></div>`;
    }
    if (refs.references.length > 10) html += `<div style="font-size:0.72rem;color:var(--text-tertiary);">... 共 ${refs.references.length} 篇</div>`;
  }
  // knowledge_base
  const kb = refs.knowledge_base || {};
  for (const [type, items] of Object.entries(kb)) {
    if (items && items.length) {
      html += `<div style="font-size:0.8rem;margin:6px 0 4px;">${type}（${items.length}）：</div>`;
      for (const it of items) {
        html += `<div style="font-size:0.75rem;padding:2px 0;">📝 ${escapeHtml(it.name)} <span style="color:var(--text-tertiary);">${it.size_kb}KB</span></div>`;
      }
    }
  }
  // briefs
  if (refs.briefs && refs.briefs.length) {
    html += `<div style="font-size:0.8rem;margin:6px 0 4px;">每日简报（${refs.briefs.length}）：</div>`;
    for (const b of refs.briefs.slice(0, 5)) {
      html += `<div style="font-size:0.75rem;padding:2px 0;">📊 ${escapeHtml(b.date)} <span style="color:var(--text-tertiary);">${b.size_kb}KB</span></div>`;
    }
  }
  html += '</div></details>';

  // === 区域 3：待决策项（卡片）===
  const pendItems = pending.pending || [];
  html += `<h4 style="font-size:0.9rem;margin:0 0 8px;color:var(--text-primary);">📌 待决策项（${pendItems.length}）</h4>`;
  if (!pendItems.length) {
    html += '<p style="color:var(--text-tertiary);font-size:0.82rem;padding:8px;">暂无待决策项 🎉</p>';
  } else {
    html += '<div style="display:flex;flex-direction:column;gap:8px;">';
    for (const p of pendItems) {
      html += `<div style="padding:10px;background:var(--bg-secondary);border-radius:8px;border-left:3px solid var(--warning-color);">
        <div style="font-size:0.85rem;font-weight:500;margin-bottom:4px;">📌 ${escapeHtml(p.title)}</div>
        <div style="font-size:0.72rem;color:var(--text-tertiary);margin-bottom:6px;">${p.related_topic ? '课题 '+p.related_topic+' · ' : ''}来源 ${escapeHtml(p.source)}</div>
        <div style="display:flex;gap:6px;">
          <button onclick="nsfcDecide('${escapeHtml(p.id)}','approve','${escapeHtml(p.title).replace(/'/g,'')}')" style="padding:4px 10px;border:1px solid var(--success-color);border-radius:5px;background:transparent;color:var(--success-color);cursor:pointer;font-size:0.78rem;">✓ 通过</button>
          <button onclick="nsfcDecide('${escapeHtml(p.id)}','reject','${escapeHtml(p.title).replace(/'/g,'')}')" style="padding:4px 10px;border:1px solid var(--border-color);border-radius:5px;background:transparent;color:var(--text-tertiary);cursor:pointer;font-size:0.78rem;">✗ 否决</button>
          <button onclick="nsfcDiscuss('${escapeHtml(p.id)}','${escapeHtml(p.title).replace(/'/g,'')}','${escapeHtml(p.related_topic)}')" style="padding:4px 10px;border:1px solid var(--accent-color);border-radius:5px;background:var(--accent-color);color:#fff;cursor:pointer;font-size:0.78rem;">💬 讨论</button>
        </div>
      </div>`;
    }
    html += '</div>';
  }

  html += `<div id="nsfc-file-viewer" style="margin-top:12px;display:none;"></div>`;
  container.innerHTML = html;
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
  bar.innerHTML = `<span style="color:var(--accent-color);">💬 正在讨论：${escapeHtml(title.slice(0,40))}</span>
    <button id="discuss-summarize-btn" style="margin-left:auto;padding:4px 12px;background:var(--accent-color);color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:0.78rem;">📝 总结讨论</button>
    <button id="discuss-cancel-btn" style="padding:4px 10px;border:1px solid var(--border-color);border-radius:4px;cursor:pointer;font-size:0.78rem;">取消</button>`;
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
      bar.innerHTML = `<span style="color:var(--accent-color);">⏳ 等待林赛总结...收到后点击提交</span>
        <button id="submit-summary-btn" style="margin-left:auto;padding:4px 12px;background:var(--success-color);color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:0.78rem;">✓ 提交总结到 discussions</button>
        <button id="discuss-cancel-btn" style="padding:4px 10px;border:1px solid var(--border-color);border-radius:4px;cursor:pointer;font-size:0.78rem;">取消</button>`;
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
  const pool = await apiGet('/api/projects/papers/pool');
  const byStatus = pool.by_status || {};

  let html = `<div style="margin-bottom:12px;padding:8px 12px;background:var(--bg-secondary);border-radius:6px;font-size:0.8rem;color:var(--text-secondary);">
    📊 候选池：<strong style="color:var(--info-color)">${byStatus.unseen||0}</strong> 未看 ·
    <strong style="color:var(--warning-color)">${byStatus.viewed||0}</strong> 已看未讨论 ·
    <strong style="color:var(--success-color)">${byStatus.archived||0}</strong> 已归档
    <span style="margin-left:8px;color:var(--text-tertiary);">(共 ${pool.total} 篇，累积保留)</span>
    <span style="margin-left:8px;color:var(--text-tertiary);">| 📚 沉淀后可在知识库浏览</span>
  </div>`;

  // 按状态分组
  const groups = [
    {status: 'unseen', label: '🔔 未看（待你决定）', color: 'var(--info-color)', defaultOpen: true},
    {status: 'viewed', label: '📖 已看未讨论（感兴趣/待深读，讨论后归档）', color: 'var(--warning-color)', defaultOpen: false},
    {status: 'archived', label: '✅ 已归档（深度阅读+讨论后的知识沉淀）', color: 'var(--success-color)', defaultOpen: false},
  ];

  const papers = pool.papers || [];
  for (const g of groups) {
    const groupPapers = papers.filter(p => p.status === g.status);
    if (!groupPapers.length) continue;
    const openAttr = g.defaultOpen ? 'open' : '';
    html += `<details ${openAttr} style="margin-bottom:10px;border:1px solid var(--border-color);border-radius:6px;overflow:hidden;">
      <summary style="padding:8px 12px;cursor:pointer;font-weight:600;font-size:0.85rem;background:var(--bg-secondary);color:${g.color};">
        ${g.label} <span style="font-weight:400;color:var(--text-tertiary);">(${groupPapers.length})</span>
      </summary>
      <div style="padding:8px;display:flex;flex-direction:column;gap:8px;">`;

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
      html += `<div style="display:flex;justify-content:space-between;margin-bottom:4px;">${lifecycleLabelHtml}</div>`;
      html += `<div style="font-size:0.85rem;font-weight:600;line-height:1.4;margin-bottom:3px;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;">${escapeHtml(p.title)}</div>`;
      html += `<div style="font-size:0.72rem;color:var(--text-tertiary);margin-bottom:6px;">${escapeHtml(p.authors)} · ${escapeHtml(p.direction)} · ${scorePct}%</div>`;
      if (p.tldr) {
        html += `<div style="font-size:0.78rem;color:var(--text-secondary);margin-bottom:6px;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;">${escapeHtml(p.tldr)}</div>`;
      }
      html += `<div style="display:flex;gap:6px;flex-wrap:wrap;">`;

      if (g.status === 'unseen') {
        html += `<button onclick="paperFeedback('${escapeHtml(p.arxiv_id)}','interested',this)" style="padding:4px 10px;border:1px solid var(--success-color);border-radius:5px;background:transparent;color:var(--success-color);cursor:pointer;font-size:0.78rem;">👍 感兴趣</button>`;
        html += `<button onclick="paperFeedback('${escapeHtml(p.arxiv_id)}','later',this)" style="padding:4px 10px;border:1px solid var(--border-color);border-radius:5px;background:transparent;color:var(--warning-color);cursor:pointer;font-size:0.78rem;">⏰ 稍后</button>`;
        html += `<button onclick="paperFeedback('${escapeHtml(p.arxiv_id)}','skip',this)" style="padding:4px 10px;border:1px solid var(--border-color);border-radius:5px;background:transparent;color:var(--text-tertiary);cursor:pointer;font-size:0.78rem;">👎 跳过</button>`;
        html += `<button onclick="discussPaper('${escapeHtml(p.arxiv_id)}','${escapeHtml(p.title).replace(/'/g,"")}')" style="padding:4px 10px;border:1px solid var(--accent-color);border-radius:5px;background:var(--accent-color);color:#fff;cursor:pointer;font-size:0.78rem;">💬 讨论</button>`;
      } else if (g.status === 'viewed') {
        // 已看未讨论：主要操作是讨论，讨论完可归档
        html += `<button onclick="discussPaper('${escapeHtml(p.arxiv_id)}','${escapeHtml(p.title).replace(/'/g,"")}')" style="padding:4px 10px;border:1px solid var(--accent-color);border-radius:5px;background:var(--accent-color);color:#fff;cursor:pointer;font-size:0.78rem;">💬 讨论</button>`;
        html += `<button onclick="paperFeedback('${escapeHtml(p.arxiv_id)}','discuss_done',this)" style="padding:4px 10px;border:1px solid var(--success-color);border-radius:5px;background:transparent;color:var(--success-color);cursor:pointer;font-size:0.78rem;">📥 归档沉淀</button>`;
      } else {
        html += `<span style="font-size:0.75rem;color:var(--success-color);padding:4px 8px;">✓ 已深度沉淀</span>`;
      }
      html += `</div></div>`;
    }
    html += `</div></details>`;
  }

  if (!papers.length) {
    html = '<p style="color:var(--text-tertiary);text-align:center;padding:40px;">候选池为空</p>';
  }
  container.innerHTML = html;
}

// 讨论某篇文献（跳到聊天框 + 注入上下文）
async function discussPaper(arxivId, title) {
  closeProjectsManager();
  showToast(`💬 正在加载 ${title.slice(0,30)}... 到讨论`, 'info');
  // 把文献信息注入聊天输入框，用户可补充问题后发送
  const input = document.getElementById('message-input');
  if (input) {
    input.value = `基于 arXiv:${arxivId}（${title}）的内容，`;
    input.focus();
    input.setSelectionRange(input.value.length, input.value.length);
  }
  // 异步加载该论文的 raw 内容到 KB 上下文（通过 @机制）
  try {
    const resp = await apiGet(`/api/knowledge/search?q=${arxivId}`);
    if (resp.results && resp.results.length) {
      window._pendingKbContext = resp.results.slice(0, 2);  // 暂存，发送时注入
    }
  } catch (e) { /* 静默 */ }
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

  let html = `<div style="max-width:500px;">
    <h3 style="margin-bottom:8px;">📚 知识库生长建议</h3>
    <p style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:12px;">已归档 <strong>${escapeHtml(suggestion.title)}</strong>，以下内容可提取为知识库笔记：</p>`;

  // concept 建议
  if (concepts.length) {
    html += '<div style="margin-bottom:10px;"><div style="font-size:0.8rem;font-weight:600;margin-bottom:4px;">概念笔记：</div>';
    concepts.slice(0, 6).forEach((c, i) => {
      const checked = c.existing ? '' : 'checked';
      const tag = c.existing ? `<span style="color:var(--info-color);font-size:0.72rem;">→ 连接已有「${escapeHtml(c.existing_title)}」</span>` : '<span style="color:var(--success-color);font-size:0.72rem;">新建</span>';
      html += `<label style="display:flex;align-items:center;gap:6px;padding:3px 0;font-size:0.82rem;">
        <input type="checkbox" id="grow-c-${i}" ${checked} ${c.existing ? '' : ''}> 
        <span>${escapeHtml(c.name)}</span> ${tag}
      </label>`;
    });
    html += '</div>';
  }

  // relation 建议
  if (relations.length) {
    html += '<div style="margin-bottom:10px;"><div style="font-size:0.8rem;font-weight:600;margin-bottom:4px;">图谱关联：</div>';
    relations.slice(0, 4).forEach((rel, i) => {
      html += `<label style="display:flex;align-items:center;gap:6px;padding:2px 0;font-size:0.8rem;">
        <input type="checkbox" id="grow-r-${i}" checked> 
        <span>${escapeHtml(rel.from)} → ${escapeHtml(rel.to)}</span>
      </label>`;
    });
    html += '</div>';
  }

  html += `<div style="display:flex;gap:8px;margin-top:12px;">
    <button id="grow-confirm-btn" style="flex:1;padding:8px;background:var(--accent-color);color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:0.85rem;">✓ 确认生成</button>
    <button id="grow-skip-btn" style="padding:8px 16px;border:1px solid var(--border-color);border-radius:6px;cursor:pointer;font-size:0.85rem;">跳过</button>
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
  let html = '<div style="margin-bottom:16px;">';
  html += `<div style="font-size:0.8rem;color:var(--text-secondary);margin-bottom:8px;">同步状态</div>`;
  html += `<div style="padding:10px;background:var(--bg-secondary);border-radius:6px;">
    <div style="font-size:0.85rem;">已同步会话: <strong>${status.synced_sessions_count}</strong></div>
    <div style="font-size:0.85rem;margin-top:4px;">已同步文献: <strong>${status.synced_papers_count}</strong></div>
    <div style="font-size:0.78rem;color:var(--text-tertiary);margin-top:4px;">上次同步: ${escapeHtml(status.last_sync || '从未')}</div>
  </div>`;
  html += `<button id="sync-run-btn" style="margin-top:10px;padding:8px 16px;background:var(--accent-color);color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:0.85rem;">🔄 立即同步</button>`;
  html += '</div>';
  if (status.history && status.history.length) {
    html += '<div><div style="font-size:0.8rem;color:var(--text-secondary);margin-bottom:6px;">同步历史</div>';
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
