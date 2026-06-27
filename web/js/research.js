/**
 * research.js — 课题指导模块前端（v3.5.0）
 * 零框架依赖，原生 JavaScript，复用 core.js 的 apiGet/apiPost/apiPut/apiDelete/
 * escapeHtml/renderMarkdown/showToast/openModal/closeModal/confirmModal/showModal。
 *
 * 用法：
 *   openResearchManager()        — 打开课题管理模态框（默认课题列表）
 *   closeResearchManager()       — 关闭模态框
 *   openProjectDetail(pid)       — 进入课题详情视图
 *
 * API 前缀：/api/research/
 */

const ResearchState = {
  currentProjectId: null,
  currentTab: 'list',   // list | detail
  detailTab: 'units',   // units | kb | memory | workflow
  kbLayer: 'all',
};

// 通用输入框/文本域样式（与 projects.js 保持一致的内联风格）
const _R_INP = 'width:100%;padding:8px;border:1px solid var(--border-color);border-radius:6px;background:var(--bg-primary);color:var(--text-primary);font-size:0.85rem;box-sizing:border-box;';
const _R_TA = _R_INP + 'resize:vertical;';

// ============================================
// 状态标签样式
// ============================================
function researchStatusStyle(status) {
  const map = {
    planning:  { label: '○ 规划中', color: 'var(--info-color)' },
    active:    { label: '◐ 进行中', color: 'var(--success-color)' },
    executing: { label: '⚡ 执行中', color: 'var(--warning-color)' },
    review:    { label: '🔍 待验收', color: '#c9a227' },
    completed: { label: '✓ 已完成', color: 'var(--text-tertiary)' },
    paused:    { label: '⏸ 已暂停', color: 'var(--text-tertiary)' },
  };
  return map[status] || { label: status || '未知', color: 'var(--text-tertiary)' };
}

function researchStatusBadge(status) {
  const s = researchStatusStyle(status);
  return `<span style="display:inline-block;padding:2px 8px;border-radius:10px;font-size:0.72rem;background:${s.color};color:#fff;white-space:nowrap;">${escapeHtml(s.label)}</span>`;
}

// ============================================
// 面板打开/关闭
// ============================================
function openResearchManager() {
  const overlay = document.getElementById('research-overlay');
  if (!overlay) return;
  overlay.style.display = 'flex';
  ResearchState.currentTab = 'list';
  ResearchState.currentProjectId = null;
  renderProjectList(document.getElementById('research-body'));
}

function closeResearchManager() {
  closeModal('research-overlay');
}

// ============================================
// 课题列表
// ============================================
async function renderProjectList(container) {
  if (!container) return;
  ResearchState.currentTab = 'list';
  container.innerHTML = '<p style="color:var(--text-tertiary);text-align:center;padding:40px;">◐ 加载中…</p>';
  try {
    const data = await apiGet('/api/research/projects');
    const projects = data.projects || [];
    let html = '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">';
    html += '<h4 style="font-size:0.95rem;margin:0;color:var(--text-primary);">🔬 课题列表</h4>';
    html += '<button id="research-create-btn" style="padding:6px 14px;background:var(--accent-color);color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:0.82rem;">+ 新建课题</button>';
    html += '</div>';
    if (!projects.length) {
      html += '<div style="text-align:center;padding:40px 20px;color:var(--text-tertiary);">';
      html += '<div style="font-size:2rem;margin-bottom:8px;">🔬</div>';
      html += '<p style="font-size:0.85rem;">暂无课题</p>';
      html += '<p style="font-size:0.78rem;margin-top:6px;">点击右上角「+ 新建课题」开始你的第一个研究课题</p>';
      html += '</div>';
    } else {
      html += '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px;">';
      for (const p of projects) {
        const st = researchStatusStyle(p.status);
        const unitCount = p.unit_count ?? p.units_count ?? '?';
        html += `<div class="research-card" tabindex="0" role="button" aria-label="打开课题 ${escapeHtml(p.name)}" onclick="openProjectDetail('${escapeHtml(p.project_id)}')" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();openProjectDetail('${escapeHtml(p.project_id)}')}" style="padding:14px;background:var(--bg-secondary);border-radius:8px;border:1px solid var(--border-color);border-left:3px solid ${st.color};cursor:pointer;transition:transform 0.15s;" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform=''">`;
        html += '<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;margin-bottom:6px;">';
        html += `<div style="font-size:0.9rem;font-weight:600;flex:1;color:var(--text-primary);">${escapeHtml(p.name)}</div>`;
        html += researchStatusBadge(p.status);
        html += '</div>';
        if (p.goal) {
          html += `<div style="font-size:0.78rem;color:var(--text-secondary);margin-bottom:8px;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;">${escapeHtml(p.goal)}</div>`;
        }
        html += '<div style="display:flex;gap:10px;font-size:0.72rem;color:var(--text-tertiary);">';
        if (p.phase) html += `<span>📍 ${escapeHtml(p.phase)}</span>`;
        html += `<span>📦 ${escapeHtml(String(unitCount))} 单元</span>`;
        html += '</div>';
        html += '</div>';
      }
      html += '</div>';
    }
    container.innerHTML = html;
    const createBtn = document.getElementById('research-create-btn');
    if (createBtn) createBtn.onclick = createProject;
  } catch (e) {
    container.innerHTML = `<p style="color:var(--error-color);">加载失败: ${escapeHtml(e.message)}</p>`;
  }
}

function createProject() {
  const html = `<div style="max-width:420px;">
    <h3 style="margin-bottom:12px;font-size:0.95rem;">🔬 新建课题</h3>
    <div style="display:flex;flex-direction:column;gap:10px;">
      <input type="text" id="rp-name" placeholder="课题名称（必填）" style="${_R_INP}">
      <textarea id="rp-goal" placeholder="课题目标（必填，你想达成什么）" rows="2" style="${_R_TA}"></textarea>
      <textarea id="rp-desc" placeholder="课题描述（可选，背景/范围/约束）" rows="3" style="${_R_TA}"></textarea>
      <div style="display:flex;gap:8px;">
        <button id="rp-confirm" style="flex:1;padding:8px;background:var(--accent-color);color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:0.85rem;">✓ 创建</button>
        <button id="rp-cancel" style="padding:8px 16px;border:1px solid var(--border-color);border-radius:6px;cursor:pointer;font-size:0.85rem;">取消</button>
      </div>
    </div>
  </div>`;
  showModal(html);
  document.getElementById('rp-cancel').onclick = () => closeModal('modal-overlay');
  document.getElementById('rp-confirm').onclick = async () => {
    const name = document.getElementById('rp-name').value.trim();
    const goal = document.getElementById('rp-goal').value.trim();
    const description = document.getElementById('rp-desc').value.trim();
    if (!name) { showToast('请填写课题名称', 'warning'); return; }
    if (!goal) { showToast('请填写课题目标', 'warning'); return; }
    const btn = document.getElementById('rp-confirm');
    btn.disabled = true; btn.textContent = '◐ 创建中…';
    try {
      await apiPost('/api/research/projects', { name, goal, description });
      showToast('✓ 课题已创建', 'success');
      closeModal('modal-overlay');
      renderProjectList(document.getElementById('research-body'));
    } catch (e) {
      showToast(`✗ 创建失败: ${e.message}`, 'error');
      btn.disabled = false; btn.textContent = '✓ 创建';
    }
  };
}

// ============================================
// 课题详情
// ============================================
function openProjectDetail(projectId) {
  ResearchState.currentProjectId = projectId;
  ResearchState.currentTab = 'detail';
  ResearchState.detailTab = 'units';
  renderProjectDetail(document.getElementById('research-body'));
}

async function renderProjectDetail(container) {
  if (!container) return;
  const pid = ResearchState.currentProjectId;
  if (!pid) { renderProjectList(container); return; }
  container.innerHTML = '<p style="color:var(--text-tertiary);text-align:center;padding:40px;">◐ 加载中…</p>';
  try {
    const project = await apiGet(`/api/research/projects/${encodeURIComponent(pid)}`);
    let html = '<div style="margin-bottom:12px;">';
    html += '<div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;flex-wrap:wrap;">';
    html += `<button onclick="renderProjectList(document.getElementById('research-body'))" style="padding:4px 10px;border:1px solid var(--border-color);border-radius:6px;background:transparent;color:var(--text-secondary);cursor:pointer;font-size:0.8rem;">← 返回</button>`;
    html += `<h4 style="font-size:0.95rem;margin:0;flex:1;color:var(--text-primary);">${escapeHtml(project.name)}</h4>`;
    html += researchStatusBadge(project.status);
    html += `<button onclick="transitionProject('${escapeHtml(pid)}','${escapeHtml(project.status)}')" style="padding:4px 10px;border:1px solid var(--accent-color);border-radius:6px;background:transparent;color:var(--accent-color);cursor:pointer;font-size:0.78rem;">→ 流转</button>`;
    html += `<button onclick="deleteProject('${escapeHtml(pid)}')" style="padding:4px 10px;border:1px solid var(--error-color);border-radius:6px;background:transparent;color:var(--error-color);cursor:pointer;font-size:0.78rem;">✕ 删除</button>`;
    html += '</div>';
    if (project.goal) {
      html += `<div style="font-size:0.8rem;color:var(--text-secondary);margin-bottom:6px;">🎯 ${escapeHtml(project.goal)}</div>`;
    }
    if (project.description) {
      html += `<div style="font-size:0.78rem;color:var(--text-tertiary);margin-bottom:6px;">${escapeHtml(project.description)}</div>`;
    }
    html += '</div>';

    // tab 栏
    const tabs = [
      { key: 'units', label: '📦 单元' },
      { key: 'kb', label: '📚 知识库' },
      { key: 'memory', label: '🧠 记忆' },
      { key: 'workflow', label: '⚡ 工作流' },
    ];
    html += '<div style="display:flex;gap:6px;border-bottom:1px solid var(--border-color);margin-bottom:12px;flex-wrap:wrap;">';
    for (const t of tabs) {
      const active = ResearchState.detailTab === t.key;
      html += `<button class="research-tab-btn" data-tab="${t.key}" onclick="switchResearchDetailTab('${t.key}')" style="padding:6px 14px;border:none;border-bottom:2px solid ${active ? 'var(--accent-color)' : 'transparent'};background:transparent;color:${active ? 'var(--accent-color)' : 'var(--text-secondary)'};cursor:pointer;font-size:0.85rem;">${t.label}</button>`;
    }
    html += '</div>';
    html += '<div id="research-detail-tab"></div>';
    container.innerHTML = html;
    await loadResearchDetailTab();
  } catch (e) {
    container.innerHTML = `<p style="color:var(--error-color);">加载失败: ${escapeHtml(e.message)}</p>`;
  }
}

function switchResearchDetailTab(tab) {
  ResearchState.detailTab = tab;
  document.querySelectorAll('.research-tab-btn').forEach(btn => {
    const active = btn.dataset.tab === tab;
    btn.style.borderBottom = active ? '2px solid var(--accent-color)' : '2px solid transparent';
    btn.style.color = active ? 'var(--accent-color)' : 'var(--text-secondary)';
  });
  loadResearchDetailTab();
}

async function loadResearchDetailTab() {
  const tabContainer = document.getElementById('research-detail-tab');
  if (!tabContainer) return;
  const pid = ResearchState.currentProjectId;
  if (!pid) return;
  tabContainer.innerHTML = '<p style="color:var(--text-tertiary);text-align:center;padding:30px;">◐ 加载中…</p>';
  try {
    if (ResearchState.detailTab === 'units') await renderUnitsTab(tabContainer, pid);
    else if (ResearchState.detailTab === 'kb') await renderKbTab(tabContainer, pid);
    else if (ResearchState.detailTab === 'memory') await renderMemoryTab(tabContainer, pid);
    else if (ResearchState.detailTab === 'workflow') await renderWorkflowTab(tabContainer, pid);
  } catch (e) {
    tabContainer.innerHTML = `<p style="color:var(--error-color);">加载失败: ${escapeHtml(e.message)}</p>`;
  }
}

// ============================================
// 单元 tab（垂直时间线）
// ============================================
async function renderUnitsTab(container, pid) {
  const data = await apiGet(`/api/research/projects/${encodeURIComponent(pid)}/status`);
  const units = data.units || [];
  let html = '<div style="display:flex;gap:8px;margin-bottom:14px;flex-wrap:wrap;">';
  html += `<button onclick="addUnit('${escapeHtml(pid)}')" style="padding:6px 14px;background:var(--accent-color);color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:0.82rem;">+ 添加单元</button>`;
  html += `<button onclick="planUnits('${escapeHtml(pid)}')" style="padding:6px 14px;border:1px solid var(--accent-color);background:transparent;color:var(--accent-color);border-radius:6px;cursor:pointer;font-size:0.82rem;">📋 规划单元</button>`;
  html += '</div>';

  if (!units.length) {
    html += '<div style="text-align:center;padding:30px 20px;color:var(--text-tertiary);">';
    html += '<div style="font-size:1.6rem;margin-bottom:6px;">📦</div>';
    html += '<p style="font-size:0.82rem;">暂无研究单元</p>';
    html += '<p style="font-size:0.75rem;margin-top:4px;">添加单元开始拆解课题，或用「规划单元」批量生成</p>';
    html += '</div>';
    container.innerHTML = html;
    return;
  }

  // 垂直时间线：左侧竖线 + 圆点
  html += '<div style="position:relative;padding-left:26px;">';
  html += '<div style="position:absolute;left:7px;top:6px;bottom:6px;width:2px;background:var(--border-color);"></div>';
  units.forEach((u, idx) => {
    const st = researchStatusStyle(u.status);
    const seq = (u.sequence !== undefined && u.sequence !== null) ? u.sequence : (idx + 1);
    html += '<div style="position:relative;padding-bottom:16px;">';
    html += `<div style="position:absolute;left:-23px;top:4px;width:12px;height:12px;border-radius:50%;background:${st.color};border:2px solid var(--bg-primary);"></div>`;
    html += '<div style="padding:12px;background:var(--bg-secondary);border-radius:8px;border:1px solid var(--border-color);">';
    // 标题行
    html += '<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;margin-bottom:6px;">';
    html += `<div style="font-size:0.88rem;font-weight:600;color:var(--text-primary);"><span style="color:var(--text-tertiary);font-weight:400;">#${escapeHtml(String(seq))}</span> ${escapeHtml(u.title)}</div>`;
    html += researchStatusBadge(u.status);
    html += '</div>';

    // 验收标准勾选列表
    const acceptance = u.acceptance || u.acceptance_criteria || [];
    if (acceptance.length) {
      html += '<div style="margin:8px 0 6px;">';
      html += '<div style="font-size:0.75rem;color:var(--text-secondary);margin-bottom:4px;">✓ 验收标准</div>';
      acceptance.forEach(ac => {
        const acId = ac.id ?? ac.ac_id ?? '';
        const met = !!(ac.met);
        const text = ac.text ?? ac.title ?? ac.criterion ?? ac.summary ?? String(ac);
        if (acId) {
          html += `<label style="display:flex;align-items:flex-start;gap:6px;padding:3px 0;font-size:0.78rem;cursor:pointer;color:${met ? 'var(--text-tertiary)' : 'var(--text-primary)'};${met ? 'text-decoration:line-through;' : ''}">`;
          html += `<input type="checkbox" ${met ? 'checked' : ''} onchange="toggleAcceptance('${escapeHtml(pid)}','${escapeHtml(u.unit_id)}','${escapeHtml(String(acId))}',${met})" style="margin-top:2px;width:auto;">`;
          html += `<span>${escapeHtml(text)}</span></label>`;
        } else {
          html += `<div style="display:flex;align-items:flex-start;gap:6px;padding:3px 0;font-size:0.78rem;color:${met ? 'var(--text-tertiary)' : 'var(--text-primary)'};${met ? 'text-decoration:line-through;' : ''}">`;
          html += `<span style="color:${met ? 'var(--success-color)' : 'var(--text-tertiary)'};">${met ? '☑' : '☐'}</span><span>${escapeHtml(text)}</span></div>`;
        }
      });
      html += '</div>';
    }

    // 任务列表
    const tasks = u.tasks || [];
    if (tasks.length) {
      html += '<div style="margin-top:6px;">';
      html += '<div style="font-size:0.75rem;color:var(--text-secondary);margin-bottom:4px;">📋 任务</div>';
      for (const t of tasks) {
        const tDone = t.status === 'completed' || t.done;
        html += `<div style="font-size:0.76rem;padding:2px 0;color:${tDone ? 'var(--text-tertiary)' : 'var(--text-secondary)'};${tDone ? 'text-decoration:line-through;' : ''}">${tDone ? '☑' : '☐'} ${escapeHtml(t.title || t.name || '')}</div>`;
      }
      html += '</div>';
    }

    // 进度条
    if (u.progress !== undefined && u.progress !== null) {
      const pct = Math.round((u.progress || 0) * 100);
      html += `<div style="margin-top:8px;height:4px;background:var(--bg-tertiary);border-radius:2px;overflow:hidden;"><div style="width:${pct}%;height:100%;background:var(--success-color);"></div></div>`;
      html += `<div style="font-size:0.7rem;color:var(--text-tertiary);margin-top:3px;">进度 ${pct}%</div>`;
    }

    // 操作
    html += '<div style="display:flex;gap:6px;margin-top:8px;flex-wrap:wrap;">';
    html += `<button onclick="startExecution('${escapeHtml(pid)}','${escapeHtml(u.unit_id)}')" style="padding:3px 8px;border:1px solid var(--accent-color);border-radius:4px;background:transparent;color:var(--accent-color);cursor:pointer;font-size:0.72rem;">⚡ 执行</button>`;
    html += `<button onclick="reviewUnit('${escapeHtml(pid)}','${escapeHtml(u.unit_id)}')" style="padding:3px 8px;border:1px solid var(--warning-color);border-radius:4px;background:transparent;color:var(--warning-color);cursor:pointer;font-size:0.72rem;">🔍 验收</button>`;
    html += `<button onclick="completeUnit('${escapeHtml(pid)}','${escapeHtml(u.unit_id)}')" style="padding:3px 8px;border:1px solid var(--success-color);border-radius:4px;background:transparent;color:var(--success-color);cursor:pointer;font-size:0.72rem;">✓ 完成</button>`;
    html += `<button onclick="deleteUnit('${escapeHtml(pid)}','${escapeHtml(u.unit_id)}')" style="padding:3px 8px;border:1px solid var(--border-color);border-radius:4px;background:transparent;color:var(--text-tertiary);cursor:pointer;font-size:0.72rem;">✕</button>`;
    html += '</div>';
    html += '</div></div>';
  });
  html += '</div>';
  container.innerHTML = html;
}

function addUnit(pid) {
  const html = `<div style="max-width:420px;">
    <h3 style="margin-bottom:12px;font-size:0.95rem;">📦 添加研究单元</h3>
    <div style="display:flex;flex-direction:column;gap:10px;">
      <input type="text" id="ru-title" placeholder="单元标题（必填）" style="${_R_INP}">
      <textarea id="ru-ac" placeholder="验收标准（每行一条，达标即完成）" rows="4" style="${_R_TA}"></textarea>
      <textarea id="ru-desc" placeholder="单元描述（可选）" rows="2" style="${_R_TA}"></textarea>
      <div style="display:flex;gap:8px;">
        <button id="ru-confirm" style="flex:1;padding:8px;background:var(--accent-color);color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:0.85rem;">✓ 创建</button>
        <button id="ru-cancel" style="padding:8px 16px;border:1px solid var(--border-color);border-radius:6px;cursor:pointer;font-size:0.85rem;">取消</button>
      </div>
    </div>
  </div>`;
  showModal(html);
  document.getElementById('ru-cancel').onclick = () => closeModal('modal-overlay');
  document.getElementById('ru-confirm').onclick = async () => {
    const title = document.getElementById('ru-title').value.trim();
    const acText = document.getElementById('ru-ac').value.trim();
    const description = document.getElementById('ru-desc').value.trim();
    if (!title) { showToast('请填写单元标题', 'warning'); return; }
    const acceptance_criteria = acText.split('\n').map(s => s.trim()).filter(Boolean);
    const btn = document.getElementById('ru-confirm');
    btn.disabled = true; btn.textContent = '◐ 创建中…';
    try {
      await apiPost(`/api/research/projects/${encodeURIComponent(pid)}/units`, { title, acceptance_criteria, description });
      showToast('✓ 单元已创建', 'success');
      closeModal('modal-overlay');
      loadResearchDetailTab();
    } catch (e) {
      showToast(`✗ 创建失败: ${e.message}`, 'error');
      btn.disabled = false; btn.textContent = '✓ 创建';
    }
  };
}

function planUnits(pid) {
  const html = `<div style="max-width:480px;">
    <h3 style="margin-bottom:10px;font-size:0.95rem;">📋 批量规划单元</h3>
    <p style="font-size:0.78rem;color:var(--text-secondary);margin-bottom:10px;">每行一个单元，格式：<code style="background:var(--bg-tertiary);padding:1px 4px;border-radius:3px;">标题 | 验收标准(分号分隔) | 描述</code></p>
    <textarea id="rpl-units" rows="6" placeholder="理论基础梳理 | 梳理HHG基本理论;建立数学模型 | 固体HHG三步模型推导&#10;实验方案设计 | 确定激光参数;完成光路图 | 中红外驱动光源搭建" style="${_R_TA}"></textarea>
    <div style="display:flex;gap:8px;margin-top:10px;">
      <button id="rpl-confirm" style="flex:1;padding:8px;background:var(--accent-color);color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:0.85rem;">✓ 规划</button>
      <button id="rpl-cancel" style="padding:8px 16px;border:1px solid var(--border-color);border-radius:6px;cursor:pointer;font-size:0.85rem;">取消</button>
    </div>
  </div>`;
  showModal(html);
  document.getElementById('rpl-cancel').onclick = () => closeModal('modal-overlay');
  document.getElementById('rpl-confirm').onclick = async () => {
    const text = document.getElementById('rpl-units').value.trim();
    const lines = text.split('\n').map(s => s.trim()).filter(Boolean);
    const unit_specs = lines.map(line => {
      const parts = line.split('|').map(s => s.trim());
      return {
        title: parts[0] || '',
        acceptance_criteria: (parts[1] || '').split(';').map(s => s.trim()).filter(Boolean),
        description: parts[2] || '',
        risks: [],
      };
    }).filter(s => s.title);
    if (!unit_specs.length) { showToast('请输入至少一个单元', 'warning'); return; }
    const btn = document.getElementById('rpl-confirm');
    btn.disabled = true; btn.textContent = '◐ 规划中…';
    try {
      const resp = await apiPost(`/api/research/projects/${encodeURIComponent(pid)}/workflow/plan`, { unit_specs });
      showToast(`✓ 已规划 ${resp.unit_ids ? resp.unit_ids.length : unit_specs.length} 个单元`, 'success');
      closeModal('modal-overlay');
      loadResearchDetailTab();
    } catch (e) {
      showToast(`✗ 规划失败: ${e.message}`, 'error');
      btn.disabled = false; btn.textContent = '✓ 规划';
    }
  };
}

function startExecution(pid, uid) {
  const html = `<div style="max-width:480px;">
    <h3 style="margin-bottom:10px;font-size:0.95rem;">⚡ 执行单元：添加任务分工</h3>
    <p style="font-size:0.78rem;color:var(--text-secondary);margin-bottom:10px;">每行一个任务，格式：<code style="background:var(--bg-tertiary);padding:1px 4px;border-radius:3px;">标题 | 执行者 | 描述 | 截止日期 | 优先级</code></p>
    <textarea id="re-tasks" rows="5" placeholder="推导HHG三步模型 | myself | 完成解析推导 | 2026-07-15 | high&#10;查阅相关文献 | hermes | arXiv 近三年固体HHG | 2026-07-10 | medium" style="${_R_TA}"></textarea>
    <div style="display:flex;gap:8px;margin-top:10px;">
      <button id="re-confirm" style="flex:1;padding:8px;background:var(--accent-color);color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:0.85rem;">✓ 开始执行</button>
      <button id="re-cancel" style="padding:8px 16px;border:1px solid var(--border-color);border-radius:6px;cursor:pointer;font-size:0.85rem;">取消</button>
    </div>
  </div>`;
  showModal(html);
  document.getElementById('re-cancel').onclick = () => closeModal('modal-overlay');
  document.getElementById('re-confirm').onclick = async () => {
    const text = document.getElementById('re-tasks').value.trim();
    const lines = text.split('\n').map(s => s.trim()).filter(Boolean);
    const task_specs = lines.map(line => {
      const parts = line.split('|').map(s => s.trim());
      return {
        title: parts[0] || '',
        assignee: parts[1] || 'myself',
        description: parts[2] || '',
        due_date: parts[3] || '',
        priority: parts[4] || 'medium',
      };
    }).filter(s => s.title);
    if (!task_specs.length) { showToast('请输入至少一个任务', 'warning'); return; }
    const btn = document.getElementById('re-confirm');
    btn.disabled = true; btn.textContent = '◐ 执行中…';
    try {
      await apiPost(`/api/research/projects/${encodeURIComponent(pid)}/workflow/execute`, { unit_id: uid, task_specs });
      showToast('✓ 任务已分配，单元进入执行', 'success');
      closeModal('modal-overlay');
      loadResearchDetailTab();
    } catch (e) {
      showToast(`✗ 执行失败: ${e.message}`, 'error');
      btn.disabled = false; btn.textContent = '✓ 开始执行';
    }
  };
}

async function reviewUnit(pid, uid) {
  showToast('◐ 正在验收…', 'info');
  try {
    const review = await apiPost(`/api/research/projects/${encodeURIComponent(pid)}/workflow/review`, { unit_id: uid });
    let html = `<div style="max-width:460px;">
      <h3 style="margin-bottom:10px;font-size:0.95rem;">🔍 验收结果</h3>`;
    const passed = review.passed ?? review.all_met ?? review.ready;
    const verdictColor = passed ? 'var(--success-color)' : 'var(--warning-color)';
    const verdictText = passed ? '✓ 全部达标，可完成' : '◐ 存在未达标项';
    html += `<div style="padding:10px;background:var(--bg-secondary);border-radius:6px;border-left:3px solid ${verdictColor};margin-bottom:10px;font-size:0.85rem;color:${verdictColor};font-weight:500;">${verdictText}</div>`;
    const acceptance = review.acceptance || review.criteria || [];
    if (acceptance.length) {
      html += '<div style="margin-bottom:10px;">';
      for (const ac of acceptance) {
        const met = !!(ac.met);
        const text = ac.text ?? ac.title ?? ac.criterion ?? ac.summary ?? String(ac);
        html += `<div style="font-size:0.78rem;padding:2px 0;color:${met ? 'var(--text-tertiary)' : 'var(--text-primary)'};${met ? 'text-decoration:line-through;' : ''}">${met ? '☑' : '☐'} ${escapeHtml(text)}</div>`;
      }
      html += '</div>';
    }
    if (review.summary) {
      html += `<div style="font-size:0.78rem;color:var(--text-secondary);margin-bottom:10px;white-space:pre-wrap;">${escapeHtml(review.summary)}</div>`;
    }
    if (review.issues && review.issues.length) {
      html += '<div style="font-size:0.78rem;color:var(--warning-color);margin-bottom:10px;">⚠ 待处理：<ul style="margin:4px 0 0 16px;">';
      for (const iss of review.issues) html += `<li>${escapeHtml(typeof iss === 'string' ? iss : (iss.text || iss.message || JSON.stringify(iss)))}</li>`;
      html += '</ul></div>';
    }
    html += `<button onclick="closeModal('modal-overlay')" style="width:100%;padding:8px;background:var(--accent-color);color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:0.85rem;">关闭</button></div>`;
    showModal(html);
    loadResearchDetailTab();
  } catch (e) {
    showToast(`✗ 验收失败: ${e.message}`, 'error');
  }
}

function completeUnit(pid, uid) {
  const html = `<div style="max-width:480px;">
    <h3 style="margin-bottom:10px;font-size:0.95rem;">✓ 完成单元</h3>
    <div style="display:flex;flex-direction:column;gap:10px;">
      <textarea id="rc-notes" placeholder="验收备注（可选，记录验收过程中的发现）" rows="3" style="${_R_TA}"></textarea>
      <textarea id="rc-report" placeholder="进展报告（可选，记录本单元成果、产出、下一步）" rows="5" style="${_R_TA}"></textarea>
      <div style="display:flex;gap:8px;">
        <button id="rc-confirm" style="flex:1;padding:8px;background:var(--success-color);color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:0.85rem;">✓ 确认完成</button>
        <button id="rc-cancel" style="padding:8px 16px;border:1px solid var(--border-color);border-radius:6px;cursor:pointer;font-size:0.85rem;">取消</button>
      </div>
    </div>
  </div>`;
  showModal(html);
  document.getElementById('rc-cancel').onclick = () => closeModal('modal-overlay');
  document.getElementById('rc-confirm').onclick = async () => {
    const review_notes = document.getElementById('rc-notes').value.trim();
    const report_content = document.getElementById('rc-report').value.trim();
    const btn = document.getElementById('rc-confirm');
    btn.disabled = true; btn.textContent = '◐ 完成中…';
    try {
      const resp = await apiPost(`/api/research/projects/${encodeURIComponent(pid)}/workflow/complete`, { unit_id: uid, review_notes, report_content });
      if (resp.all_done) {
        showToast('🎉 全部单元完成！课题可进入完成状态', 'success');
      } else {
        showToast(`✓ 单元已完成，下一单元：${resp.next_unit || ''}`, 'success');
      }
      closeModal('modal-overlay');
      loadResearchDetailTab();
    } catch (e) {
      showToast(`✗ 完成失败: ${e.message}`, 'error');
      btn.disabled = false; btn.textContent = '✓ 确认完成';
    }
  };
}

async function toggleAcceptance(pid, uid, acId, currentMet) {
  const wasMet = (currentMet === true || String(currentMet) === 'true');
  try {
    await apiPut(`/api/research/projects/${encodeURIComponent(pid)}/units/${encodeURIComponent(uid)}/acceptance/${encodeURIComponent(acId)}`, { met: !wasMet, notes: '' });
    showToast(!wasMet ? '✓ 已标记达标' : '○ 已取消达标', 'success');
    loadResearchDetailTab();
  } catch (e) {
    showToast(`✗ 操作失败: ${e.message}`, 'error');
  }
}

async function deleteUnit(pid, uid) {
  if (!await confirmModal('确定删除该研究单元？相关任务和验收记录将一并移除。', '删除')) return;
  showToast('◐ 删除中…', 'info');
  try {
    await apiDelete(`/api/research/projects/${encodeURIComponent(pid)}/units/${encodeURIComponent(uid)}`);
    showToast('✓ 单元已删除', 'success');
    loadResearchDetailTab();
  } catch (e) {
    showToast(`✗ 删除失败: ${e.message}`, 'error');
  }
}

// ============================================
// 知识库 tab（左侧文档列表 + 右侧预览）
// ============================================
async function renderKbTab(container, pid) {
  const layer = ResearchState.kbLayer;
  let html = '<div style="display:flex;gap:10px;margin-bottom:10px;flex-wrap:wrap;align-items:center;">';
  html += `<input type="text" id="rk-search" placeholder="🔍 搜索知识库…" style="flex:1;min-width:180px;padding:6px 10px;border:1px solid var(--border-color);border-radius:6px;background:var(--bg-primary);color:var(--text-primary);font-size:0.82rem;">`;
  html += `<button id="rk-search-btn" style="padding:6px 12px;border:1px solid var(--border-color);border-radius:6px;background:transparent;color:var(--text-secondary);cursor:pointer;font-size:0.82rem;">搜索</button>`;
  html += `<button onclick="addDocument('${escapeHtml(pid)}')" style="padding:6px 12px;background:var(--accent-color);color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:0.82rem;">+ 添加文档</button>`;
  html += '</div>';

  // 层级筛选
  const layers = [['all', '全部'], ['raw', 'raw'], ['parsed', 'parsed'], ['summary', 'summary']];
  html += '<div style="display:flex;gap:6px;margin-bottom:10px;flex-wrap:wrap;">';
  for (const [l, lbl] of layers) {
    const active = layer === l;
    html += `<button onclick="setKbLayer('${l}')" style="padding:3px 10px;border:1px solid ${active ? 'var(--accent-color)' : 'var(--border-color)'};border-radius:12px;background:${active ? 'var(--accent-color)' : 'transparent'};color:${active ? '#fff' : 'var(--text-secondary)'};cursor:pointer;font-size:0.75rem;">${escapeHtml(lbl)}</button>`;
  }
  html += '</div>';

  // 双栏：文档列表 + 内容预览
  html += '<div style="display:grid;grid-template-columns:240px 1fr;gap:10px;min-height:300px;">';
  html += '<div id="rk-doc-list" style="overflow-y:auto;max-height:55vh;"><p style="color:var(--text-tertiary);font-size:0.8rem;padding:10px;">◐ 加载中…</p></div>';
  html += '<div id="rk-doc-view" style="padding:10px;background:var(--bg-secondary);border-radius:6px;overflow-y:auto;max-height:55vh;"><p style="color:var(--text-tertiary);font-size:0.8rem;text-align:center;padding:30px;">← 选择左侧文档查看内容</p></div>';
  html += '</div>';
  container.innerHTML = html;

  const searchInput = document.getElementById('rk-search');
  const searchBtn = document.getElementById('rk-search-btn');
  if (searchBtn) searchBtn.onclick = () => searchKb(pid, searchInput.value.trim());
  if (searchInput) searchInput.addEventListener('keydown', e => { if (e.key === 'Enter') searchKb(pid, searchInput.value.trim()); });

  await loadKbDocList(pid);
}

function setKbLayer(layer) {
  ResearchState.kbLayer = layer;
  loadKbDocList(ResearchState.currentProjectId);
}

async function loadKbDocList(pid) {
  const listEl = document.getElementById('rk-doc-list');
  if (!listEl) return;
  listEl.innerHTML = '<p style="color:var(--text-tertiary);font-size:0.8rem;padding:10px;">◐ 加载中…</p>';
  try {
    const layerParam = ResearchState.kbLayer === 'all' ? '' : `&layer=${encodeURIComponent(ResearchState.kbLayer)}`;
    const data = await apiGet(`/api/research/projects/${encodeURIComponent(pid)}/kb/documents?${layerParam}`);
    const docs = data.documents || [];
    if (!docs.length) {
      listEl.innerHTML = '<p style="color:var(--text-tertiary);font-size:0.78rem;padding:10px;text-align:center;">暂无文档</p>';
      return;
    }
    const layerColors = { raw: 'var(--text-tertiary)', parsed: 'var(--info-color)', summary: 'var(--success-color)' };
    let html = '<div style="display:flex;flex-direction:column;gap:4px;">';
    for (const d of docs) {
      const lc = layerColors[d.layer] || 'var(--text-tertiary)';
      const tags = (d.tags || []).slice(0, 3).map(t => `<span style="font-size:0.65rem;color:var(--text-tertiary);background:var(--bg-tertiary);padding:1px 5px;border-radius:8px;">${escapeHtml(t)}</span>`).join(' ');
      html += `<div tabindex="0" role="button" aria-label="查看文档 ${escapeHtml(d.title || d.path)}" onclick="viewDocument('${escapeHtml(pid)}','${escapeHtml(d.path)}')" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();viewDocument('${escapeHtml(pid)}','${escapeHtml(d.path)}')}" style="padding:8px;background:var(--bg-tertiary);border-radius:6px;cursor:pointer;border:1px solid transparent;" onmouseover="this.style.borderColor='var(--accent-color)'" onmouseout="this.style.borderColor='transparent'">`;
      html += `<div style="font-size:0.8rem;font-weight:500;color:var(--text-primary);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${escapeHtml(d.title || d.path)}</div>`;
      html += '<div style="display:flex;align-items:center;gap:6px;margin-top:3px;">';
      html += `<span style="font-size:0.65rem;padding:1px 6px;border-radius:8px;background:${lc};color:#fff;">${escapeHtml(d.layer || '')}</span>`;
      if (d.type) html += `<span style="font-size:0.65rem;color:var(--text-tertiary);">${escapeHtml(d.type)}</span>`;
      html += '</div>';
      if (tags) html += `<div style="margin-top:3px;display:flex;gap:3px;flex-wrap:wrap;">${tags}</div>`;
      html += '</div>';
    }
    html += '</div>';
    listEl.innerHTML = html;
  } catch (e) {
    listEl.innerHTML = `<p style="color:var(--error-color);font-size:0.78rem;padding:10px;">加载失败: ${escapeHtml(e.message)}</p>`;
  }
}

async function searchKb(pid, query) {
  const listEl = document.getElementById('rk-doc-list');
  if (!query) { loadKbDocList(pid); return; }
  if (listEl) listEl.innerHTML = '<p style="color:var(--text-tertiary);font-size:0.8rem;padding:10px;">◐ 搜索中…</p>';
  try {
    const data = await apiGet(`/api/research/projects/${encodeURIComponent(pid)}/kb/search?q=${encodeURIComponent(query)}`);
    const results = data.results || [];
    if (!results.length) {
      if (listEl) listEl.innerHTML = '<p style="color:var(--text-tertiary);font-size:0.78rem;padding:10px;text-align:center;">未找到匹配文档</p>';
      return;
    }
    let html = '<div style="display:flex;flex-direction:column;gap:4px;">';
    for (const r of results) {
      html += `<div tabindex="0" role="button" aria-label="查看文档 ${escapeHtml(r.title)}" onclick="viewDocument('${escapeHtml(pid)}','${escapeHtml(r.path)}')" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();viewDocument('${escapeHtml(pid)}','${escapeHtml(r.path)}')}" style="padding:8px;background:var(--bg-tertiary);border-radius:6px;cursor:pointer;border:1px solid transparent;" onmouseover="this.style.borderColor='var(--accent-color)'" onmouseout="this.style.borderColor='transparent'">`;
      html += `<div style="font-size:0.8rem;font-weight:500;color:var(--text-primary);">${escapeHtml(r.title)}</div>`;
      html += `<div style="font-size:0.65rem;color:var(--text-tertiary);margin-top:2px;">${escapeHtml(r.layer || '')}${r.score !== undefined ? ' · ' + Math.round(r.score * 100) + '%' : ''}</div>`;
      if (r.snippet) html += `<div style="font-size:0.72rem;color:var(--text-secondary);margin-top:3px;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;">${escapeHtml(r.snippet)}</div>`;
      html += '</div>';
    }
    html += '</div>';
    if (listEl) listEl.innerHTML = html;
  } catch (e) {
    if (listEl) listEl.innerHTML = `<p style="color:var(--error-color);font-size:0.78rem;padding:10px;">搜索失败: ${escapeHtml(e.message)}</p>`;
  }
}

async function viewDocument(pid, docPath) {
  const viewEl = document.getElementById('rk-doc-view');
  if (!viewEl) return;
  viewEl.innerHTML = '<p style="color:var(--text-tertiary);font-size:0.8rem;text-align:center;padding:30px;">◐ 加载中…</p>';
  try {
    const data = await apiGet(`/api/research/projects/${encodeURIComponent(pid)}/kb/doc/${encodeURIComponent(docPath)}`);
    let html = `<div style="font-size:0.82rem;font-weight:600;margin-bottom:6px;color:var(--text-primary);">${escapeHtml(data.path || docPath)}</div>`;
    const fm = data.frontmatter || {};
    const fmKeys = Object.keys(fm);
    if (fmKeys.length) {
      html += '<div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px;font-size:0.7rem;">';
      for (const k of fmKeys) {
        html += `<span style="color:var(--text-tertiary);">${escapeHtml(k)}: <span style="color:var(--text-secondary);">${escapeHtml(String(fm[k]))}</span></span>`;
      }
      html += '</div>';
    }
    html += `<div style="font-size:0.82rem;line-height:1.6;color:var(--text-primary);">${renderMarkdown(data.content || '')}</div>`;
    viewEl.innerHTML = html;
  } catch (e) {
    viewEl.innerHTML = `<p style="color:var(--error-color);font-size:0.8rem;">加载失败: ${escapeHtml(e.message)}</p>`;
  }
}

function addDocument(pid) {
  const html = `<div style="max-width:460px;">
    <h3 style="margin-bottom:12px;font-size:0.95rem;">📄 添加知识库文档</h3>
    <div style="display:flex;flex-direction:column;gap:10px;">
      <input type="text" id="rkd-title" placeholder="文档标题（必填）" style="${_R_INP}">
      <div style="display:flex;gap:8px;">
        <select id="rkd-layer" style="flex:1;padding:8px;border:1px solid var(--border-color);border-radius:6px;background:var(--bg-primary);color:var(--text-primary);font-size:0.85rem;">
          <option value="raw">raw（原始）</option>
          <option value="parsed" selected>parsed（解析）</option>
          <option value="summary">summary（摘要）</option>
        </select>
        <select id="rkd-type" style="flex:1;padding:8px;border:1px solid var(--border-color);border-radius:6px;background:var(--bg-primary);color:var(--text-primary);font-size:0.85rem;">
          <option value="note">note</option>
          <option value="paper">paper</option>
          <option value="data">data</option>
          <option value="report">report</option>
        </select>
      </div>
      <input type="text" id="rkd-tags" placeholder="标签（逗号分隔，如：HHG,实验,推导）" style="${_R_INP}">
      <textarea id="rkd-content" placeholder="文档内容（支持 Markdown）" rows="6" style="${_R_TA}"></textarea>
      <div style="display:flex;gap:8px;">
        <button id="rkd-confirm" style="flex:1;padding:8px;background:var(--accent-color);color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:0.85rem;">✓ 添加</button>
        <button id="rkd-cancel" style="padding:8px 16px;border:1px solid var(--border-color);border-radius:6px;cursor:pointer;font-size:0.85rem;">取消</button>
      </div>
    </div>
  </div>`;
  showModal(html);
  document.getElementById('rkd-cancel').onclick = () => closeModal('modal-overlay');
  document.getElementById('rkd-confirm').onclick = async () => {
    const title = document.getElementById('rkd-title').value.trim();
    const layer = document.getElementById('rkd-layer').value;
    const doc_type = document.getElementById('rkd-type').value;
    const content = document.getElementById('rkd-content').value;
    const tags = document.getElementById('rkd-tags').value.split(',').map(s => s.trim()).filter(Boolean);
    if (!title) { showToast('请填写文档标题', 'warning'); return; }
    const btn = document.getElementById('rkd-confirm');
    btn.disabled = true; btn.textContent = '◐ 添加中…';
    try {
      await apiPost(`/api/research/projects/${encodeURIComponent(pid)}/kb/documents`, { layer, doc_type, title, content, tags });
      showToast('✓ 文档已添加', 'success');
      closeModal('modal-overlay');
      loadKbDocList(pid);
    } catch (e) {
      showToast(`✗ 添加失败: ${e.message}`, 'error');
      btn.disabled = false; btn.textContent = '✓ 添加';
    }
  };
}

// ============================================
// 记忆 tab（统计 + 可编辑记忆文件 + 片段 + 决策）
// ============================================
async function renderMemoryTab(container, pid) {
  container.innerHTML = '<p style="color:var(--text-tertiary);text-align:center;padding:30px;">◐ 加载中…</p>';
  try {
    const [stats, fileData, snippetsData] = await Promise.all([
      apiGet(`/api/research/projects/${encodeURIComponent(pid)}/memory/stats`),
      apiGet(`/api/research/projects/${encodeURIComponent(pid)}/memory/file`),
      apiGet(`/api/research/projects/${encodeURIComponent(pid)}/memory/snippets`),
    ]);

    // 统计卡
    const cards = [
      { label: '对话片段', val: stats.conversation_count ?? 0, color: 'var(--info-color)' },
      { label: '记忆片段', val: stats.snippet_count ?? 0, color: 'var(--accent-color)' },
      { label: '决策记录', val: stats.decision_count ?? 0, color: 'var(--success-color)' },
      { label: '风险项', val: stats.risk_count ?? 0, color: 'var(--warning-color)' },
    ];
    let html = '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:8px;margin-bottom:14px;">';
    for (const c of cards) {
      html += `<div style="padding:10px;background:var(--bg-secondary);border-radius:6px;border-left:3px solid ${c.color};"><div style="font-size:0.7rem;color:var(--text-tertiary);">${c.label}</div><div style="font-size:1.05rem;font-weight:600;margin-top:2px;">${escapeHtml(String(c.val))}</div></div>`;
    }
    html += '</div>';

    // PROJECT-MEMORY.md 可编辑
    html += '<div style="margin-bottom:14px;">';
    html += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;"><span style="font-size:0.82rem;font-weight:600;color:var(--text-primary);">📝 PROJECT-MEMORY.md</span>';
    html += '<div style="display:flex;gap:6px;">';
    html += '<button id="rm-edit" style="padding:3px 10px;border:1px solid var(--accent-color);border-radius:4px;background:transparent;color:var(--accent-color);cursor:pointer;font-size:0.75rem;">✎ 编辑</button>';
    html += '<button id="rm-save" style="display:none;padding:3px 10px;background:var(--success-color);color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:0.75rem;">✓ 保存</button>';
    html += '</div></div>';
    html += `<textarea id="rm-memory" readonly style="width:100%;height:180px;padding:8px;border:1px solid var(--border-color);border-radius:6px;background:var(--bg-secondary);color:var(--text-primary);font-size:0.78rem;font-family:monospace;box-sizing:border-box;resize:vertical;">${escapeHtml(fileData.content || '')}</textarea>`;
    html += '</div>';

    // 记忆片段
    const snippets = snippetsData.snippets || [];
    html += `<div style="margin-bottom:14px;"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;"><span style="font-size:0.82rem;font-weight:600;color:var(--text-primary);">🧩 记忆片段（${snippets.length}）</span><button onclick="addSnippet('${escapeHtml(pid)}')" style="padding:3px 10px;border:1px solid var(--accent-color);border-radius:4px;background:transparent;color:var(--accent-color);cursor:pointer;font-size:0.75rem;">+ 添加</button></div>`;
    if (snippets.length) {
      html += '<div style="display:flex;flex-direction:column;gap:6px;max-height:200px;overflow-y:auto;">';
      for (const s of snippets) {
        const impColor = s.importance === 'critical' ? 'var(--error-color)' : s.importance === 'high' ? 'var(--warning-color)' : 'var(--text-tertiary)';
        html += `<div style="padding:8px;background:var(--bg-secondary);border-radius:6px;border-left:3px solid var(--accent-color);"><div style="font-size:0.78rem;color:var(--text-primary);">${escapeHtml(s.summary || s.content || '')}</div><div style="font-size:0.7rem;color:var(--text-tertiary);margin-top:3px;">${escapeHtml(s.trigger || '')} · ${escapeHtml(s.source || '')}${s.importance ? ` · <span style="color:${impColor};">★${escapeHtml(String(s.importance))}</span>` : ''}</div></div>`;
      }
      html += '</div>';
    } else {
      html += '<p style="color:var(--text-tertiary);font-size:0.78rem;padding:8px;">暂无记忆片段</p>';
    }
    html += '</div>';

    // 决策记录
    html += `<div><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;"><span style="font-size:0.82rem;font-weight:600;color:var(--text-primary);">📌 决策记录</span><button onclick="addDecision('${escapeHtml(pid)}')" style="padding:3px 10px;border:1px solid var(--success-color);border-radius:4px;background:transparent;color:var(--success-color);cursor:pointer;font-size:0.75rem;">+ 添加</button></div>`;
    html += `<p style="color:var(--text-tertiary);font-size:0.78rem;padding:8px;">决策记录写入 PROJECT-MEMORY.md（共 ${escapeHtml(String(stats.decision_count ?? 0))} 条），可在上方编辑器查看与编辑</p>`;
    html += '</div>';

    container.innerHTML = html;

    // 绑定编辑/保存
    const editBtn = document.getElementById('rm-edit');
    const saveBtn = document.getElementById('rm-save');
    const ta = document.getElementById('rm-memory');
    if (editBtn) editBtn.onclick = () => {
      ta.readOnly = false;
      ta.focus();
      editBtn.style.display = 'none';
      saveBtn.style.display = 'inline-block';
    };
    if (saveBtn) saveBtn.onclick = () => editMemoryFile(pid);
  } catch (e) {
    container.innerHTML = `<p style="color:var(--error-color);">加载失败: ${escapeHtml(e.message)}</p>`;
  }
}

async function editMemoryFile(pid) {
  const ta = document.getElementById('rm-memory');
  if (!ta) return;
  const content = ta.value;
  const saveBtn = document.getElementById('rm-save');
  if (saveBtn) { saveBtn.disabled = true; saveBtn.textContent = '◐ 保存中…'; }
  try {
    await apiPut(`/api/research/projects/${encodeURIComponent(pid)}/memory/file`, { content });
    showToast('✓ 记忆文件已保存', 'success');
    ta.readOnly = true;
    if (saveBtn) { saveBtn.style.display = 'none'; saveBtn.disabled = false; saveBtn.textContent = '✓ 保存'; }
    const editBtn = document.getElementById('rm-edit');
    if (editBtn) editBtn.style.display = 'inline-block';
  } catch (e) {
    showToast(`✗ 保存失败: ${e.message}`, 'error');
    if (saveBtn) { saveBtn.disabled = false; saveBtn.textContent = '✓ 保存'; }
  }
}

function addSnippet(pid) {
  const html = `<div style="max-width:420px;">
    <h3 style="margin-bottom:12px;font-size:0.95rem;">🧩 添加记忆片段</h3>
    <div style="display:flex;flex-direction:column;gap:10px;">
      <input type="text" id="rs-trigger" placeholder="触发词（如：HHG实验参数）" style="${_R_INP}">
      <textarea id="rs-summary" placeholder="摘要（必填，记录这条记忆的内容）" rows="3" style="${_R_TA}"></textarea>
      <input type="text" id="rs-source" placeholder="来源（如：20260620-会议 / 会话记录）" style="${_R_INP}">
      <select id="rs-importance" style="padding:8px;border:1px solid var(--border-color);border-radius:6px;background:var(--bg-primary);color:var(--text-primary);font-size:0.85rem;">
        <option value="normal">普通</option>
        <option value="high">重要</option>
        <option value="critical">关键</option>
      </select>
      <div style="display:flex;gap:8px;">
        <button id="rs-confirm" style="flex:1;padding:8px;background:var(--accent-color);color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:0.85rem;">✓ 添加</button>
        <button id="rs-cancel" style="padding:8px 16px;border:1px solid var(--border-color);border-radius:6px;cursor:pointer;font-size:0.85rem;">取消</button>
      </div>
    </div>
  </div>`;
  showModal(html);
  document.getElementById('rs-cancel').onclick = () => closeModal('modal-overlay');
  document.getElementById('rs-confirm').onclick = async () => {
    const trigger = document.getElementById('rs-trigger').value.trim();
    const summary = document.getElementById('rs-summary').value.trim();
    const source = document.getElementById('rs-source').value.trim();
    const importance = document.getElementById('rs-importance').value;
    if (!summary) { showToast('请填写摘要', 'warning'); return; }
    const btn = document.getElementById('rs-confirm');
    btn.disabled = true; btn.textContent = '◐ 添加中…';
    try {
      await apiPost(`/api/research/projects/${encodeURIComponent(pid)}/memory/snippets`, { trigger, summary, source, importance });
      showToast('✓ 记忆片段已添加', 'success');
      closeModal('modal-overlay');
      loadResearchDetailTab();
    } catch (e) {
      showToast(`✗ 添加失败: ${e.message}`, 'error');
      btn.disabled = false; btn.textContent = '✓ 添加';
    }
  };
}

function addDecision(pid) {
  const html = `<div style="max-width:420px;">
    <h3 style="margin-bottom:12px;font-size:0.95rem;">📌 添加决策记录</h3>
    <div style="display:flex;flex-direction:column;gap:10px;">
      <input type="text" id="rdc-title" placeholder="决策标题（必填，如：采用中红外驱动光源）" style="${_R_INP}">
      <textarea id="rdc-rationale" placeholder="决策理由（必填，为什么这么决定）" rows="3" style="${_R_TA}"></textarea>
      <div style="display:flex;gap:8px;">
        <button id="rdc-confirm" style="flex:1;padding:8px;background:var(--success-color);color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:0.85rem;">✓ 添加</button>
        <button id="rdc-cancel" style="padding:8px 16px;border:1px solid var(--border-color);border-radius:6px;cursor:pointer;font-size:0.85rem;">取消</button>
      </div>
    </div>
  </div>`;
  showModal(html);
  document.getElementById('rdc-cancel').onclick = () => closeModal('modal-overlay');
  document.getElementById('rdc-confirm').onclick = async () => {
    const title = document.getElementById('rdc-title').value.trim();
    const rationale = document.getElementById('rdc-rationale').value.trim();
    if (!title || !rationale) { showToast('请填写标题和理由', 'warning'); return; }
    const btn = document.getElementById('rdc-confirm');
    btn.disabled = true; btn.textContent = '◐ 添加中…';
    try {
      await apiPost(`/api/research/projects/${encodeURIComponent(pid)}/memory/decisions`, { title, rationale });
      showToast('✓ 决策已记录', 'success');
      closeModal('modal-overlay');
      loadResearchDetailTab();
    } catch (e) {
      showToast(`✗ 添加失败: ${e.message}`, 'error');
      btn.disabled = false; btn.textContent = '✓ 添加';
    }
  };
}

// ============================================
// 工作流 tab（状态 + 操作 + 单元进度）
// ============================================
async function renderWorkflowTab(container, pid) {
  container.innerHTML = '<p style="color:var(--text-tertiary);text-align:center;padding:30px;">◐ 加载中…</p>';
  try {
    const data = await apiGet(`/api/research/projects/${encodeURIComponent(pid)}/status`);
    const project = data.project || {};
    const units = data.units || [];
    const stats = data.stats || {};

    // 统计卡
    const scards = [
      { label: '总单元', val: stats.total_units ?? 0, color: 'var(--info-color)' },
      { label: '已完成', val: stats.completed_units ?? 0, color: 'var(--success-color)' },
      { label: '总任务', val: stats.total_tasks ?? 0, color: 'var(--accent-color)' },
    ];
    let html = '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:8px;margin-bottom:14px;">';
    for (const c of scards) {
      html += `<div style="padding:10px;background:var(--bg-secondary);border-radius:6px;border-left:3px solid ${c.color};"><div style="font-size:0.7rem;color:var(--text-tertiary);">${c.label}</div><div style="font-size:1.05rem;font-weight:600;margin-top:2px;">${escapeHtml(String(c.val))}</div></div>`;
    }
    html += '</div>';

    // 当前单元
    const currentUnit = units.find(u => u.status === 'executing') || units.find(u => u.status === 'active') || units.find(u => u.status !== 'completed') || null;
    if (currentUnit) {
      const st = researchStatusStyle(currentUnit.status);
      html += `<div style="padding:12px;background:var(--bg-secondary);border-radius:8px;border-left:3px solid ${st.color};margin-bottom:14px;">`;
      html += '<div style="font-size:0.72rem;color:var(--text-tertiary);margin-bottom:4px;">▶ 当前单元</div>';
      html += `<div style="font-size:0.9rem;font-weight:600;color:var(--text-primary);">${escapeHtml(currentUnit.title)} ${researchStatusBadge(currentUnit.status)}</div>`;
      if (currentUnit.progress !== undefined && currentUnit.progress !== null) {
        const pct = Math.round((currentUnit.progress || 0) * 100);
        html += `<div style="margin-top:6px;height:5px;background:var(--bg-tertiary);border-radius:3px;overflow:hidden;"><div style="width:${pct}%;height:100%;background:var(--success-color);"></div></div>`;
        html += `<div style="font-size:0.72rem;color:var(--text-tertiary);margin-top:3px;">进度 ${pct}%</div>`;
      }
      html += '</div>';
    } else if (units.length) {
      html += '<div style="padding:12px;background:var(--bg-secondary);border-radius:8px;border-left:3px solid var(--success-color);margin-bottom:14px;font-size:0.85rem;color:var(--success-color);">🎉 所有单元已完成，可生成课题总结</div>';
    }

    // 工作流操作按钮
    html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:8px;margin-bottom:12px;">';
    html += `<button onclick="planUnits('${escapeHtml(pid)}')" style="padding:10px;border:1px solid var(--info-color);border-radius:6px;background:transparent;color:var(--info-color);cursor:pointer;font-size:0.82rem;text-align:center;">📋 规划单元<br><span style="font-size:0.7rem;color:var(--text-tertiary);">批量拆解课题</span></button>`;
    html += `<button onclick="workflowExecutePick('${escapeHtml(pid)}')" style="padding:10px;border:1px solid var(--accent-color);border-radius:6px;background:transparent;color:var(--accent-color);cursor:pointer;font-size:0.82rem;text-align:center;">⚡ 执行单元<br><span style="font-size:0.7rem;color:var(--text-tertiary);">分配任务分工</span></button>`;
    html += `<button onclick="workflowReviewPick('${escapeHtml(pid)}')" style="padding:10px;border:1px solid var(--warning-color);border-radius:6px;background:transparent;color:var(--warning-color);cursor:pointer;font-size:0.82rem;text-align:center;">🔍 验收单元<br><span style="font-size:0.7rem;color:var(--text-tertiary);">检查达标情况</span></button>`;
    html += `<button onclick="workflowCompletePick('${escapeHtml(pid)}')" style="padding:10px;border:1px solid var(--success-color);border-radius:6px;background:transparent;color:var(--success-color);cursor:pointer;font-size:0.82rem;text-align:center;">✓ 完成单元<br><span style="font-size:0.7rem;color:var(--text-tertiary);">归档并推进</span></button>`;
    html += '</div>';

    // 生成总结
    html += `<button onclick="generateSummary('${escapeHtml(pid)}')" style="width:100%;padding:10px;background:var(--bg-secondary);border:1px solid var(--border-color);border-radius:6px;color:var(--text-primary);cursor:pointer;font-size:0.82rem;">📝 生成课题总结报告</button>`;

    // 单元进度列表
    if (units.length) {
      html += '<div style="margin-top:14px;"><div style="font-size:0.8rem;color:var(--text-secondary);margin-bottom:6px;">📦 单元进度</div>';
      for (const u of units) {
        const st = researchStatusStyle(u.status);
        html += `<div style="display:flex;align-items:center;gap:8px;padding:4px 0;font-size:0.78rem;"><span style="color:${st.color};">●</span><span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--text-primary);">${escapeHtml(u.title)}</span>${researchStatusBadge(u.status)}</div>`;
      }
      html += '</div>';
    }

    // 项目状态提示
    if (project.status) {
      const pst = researchStatusStyle(project.status);
      html += `<div style="margin-top:12px;font-size:0.75rem;color:var(--text-tertiary);text-align:center;">课题状态：${escapeHtml(pst.label)}</div>`;
    }

    container.innerHTML = html;
  } catch (e) {
    container.innerHTML = `<p style="color:var(--error-color);">加载失败: ${escapeHtml(e.message)}</p>`;
  }
}

// 工作流：选择单元执行/验收/完成
function pickUnit(pid, title) {
  return new Promise(async resolve => {
    let units = [];
    try {
      const data = await apiGet(`/api/research/projects/${encodeURIComponent(pid)}/units`);
      units = data.units || [];
    } catch (e) { /* ignore */ }
    if (!units.length) { showToast('暂无可选单元', 'warning'); resolve(null); return; }
    let html = `<div style="max-width:380px;"><h3 style="margin-bottom:10px;font-size:0.9rem;">${escapeHtml(title)}</h3><div style="display:flex;flex-direction:column;gap:6px;">`;
    units.forEach((u, i) => {
      const st = researchStatusStyle(u.status);
      html += `<button id="pu-${i}" style="padding:8px;text-align:left;background:var(--bg-secondary);border:1px solid var(--border-color);border-radius:6px;cursor:pointer;font-size:0.82rem;color:var(--text-primary);">${escapeHtml(u.title)} <span style="font-size:0.7rem;color:${st.color};">(${st.label})</span></button>`;
    });
    html += `</div><button id="pu-cancel" style="margin-top:8px;width:100%;padding:6px;border:1px solid var(--border-color);border-radius:6px;cursor:pointer;font-size:0.82rem;">取消</button></div>`;
    showModal(html);
    document.getElementById('pu-cancel').onclick = () => { closeModal('modal-overlay'); resolve(null); };
    units.forEach((u, i) => {
      const btn = document.getElementById(`pu-${i}`);
      if (btn) btn.onclick = () => { closeModal('modal-overlay'); resolve(u.unit_id); };
    });
  });
}

async function workflowExecutePick(pid) {
  const uid = await pickUnit(pid, '选择要执行的单元');
  if (uid) startExecution(pid, uid);
}

async function workflowReviewPick(pid) {
  const uid = await pickUnit(pid, '选择要验收的单元');
  if (uid) reviewUnit(pid, uid);
}

async function workflowCompletePick(pid) {
  const uid = await pickUnit(pid, '选择要完成的单元');
  if (uid) completeUnit(pid, uid);
}

async function generateSummary(pid) {
  if (!await confirmModal('生成课题总结报告？将汇总各单元成果写入知识库。', '生成')) return;
  showToast('◐ 正在生成总结报告…', 'info');
  try {
    const resp = await apiPost(`/api/research/projects/${encodeURIComponent(pid)}/workflow/summary`, {});
    showToast(`✓ 总结报告已生成${resp.path ? '：' + resp.path : ''}`, 'success');
  } catch (e) {
    showToast(`✗ 生成失败: ${e.message}`, 'error');
  }
}

// ============================================
// 课题级操作：删除 / 状态流转
// ============================================
async function deleteProject(pid) {
  if (!await confirmModal('确定删除该课题？所有单元、任务、记忆和知识库文档将一并删除，且不可恢复。', '删除课题')) return;
  showToast('◐ 删除中…', 'info');
  try {
    await apiDelete(`/api/research/projects/${encodeURIComponent(pid)}`);
    showToast('✓ 课题已删除', 'success');
    renderProjectList(document.getElementById('research-body'));
  } catch (e) {
    showToast(`✗ 删除失败: ${e.message}`, 'error');
  }
}

function transitionProject(pid, currentStatus) {
  const transitions = {
    planning:  ['active'],
    active:    ['executing', 'paused'],
    executing: ['review', 'active'],
    review:    ['completed', 'active'],
    completed: ['active'],
    paused:    ['active'],
  };
  const options = transitions[currentStatus] || ['planning', 'active', 'executing', 'review', 'completed', 'paused'];
  let html = `<div style="max-width:340px;"><h3 style="margin-bottom:10px;font-size:0.9rem;">→ 课题状态流转</h3><div style="display:flex;flex-direction:column;gap:6px;">`;
  for (const s of options) {
    const st = researchStatusStyle(s);
    html += `<button onclick="doTransitionProject('${escapeHtml(pid)}','${escapeHtml(s)}')" style="padding:8px;background:var(--bg-secondary);border:1px solid var(--border-color);border-radius:6px;cursor:pointer;font-size:0.82rem;text-align:left;color:var(--text-primary);"><span style="color:${st.color};">●</span> ${escapeHtml(st.label)}</button>`;
  }
  html += `</div><button id="tp-cancel" style="margin-top:8px;width:100%;padding:6px;border:1px solid var(--border-color);border-radius:6px;cursor:pointer;font-size:0.82rem;">取消</button></div>`;
  showModal(html);
  document.getElementById('tp-cancel').onclick = () => closeModal('modal-overlay');
}

async function doTransitionProject(pid, status) {
  closeModal('modal-overlay');
  try {
    await apiPut(`/api/research/projects/${encodeURIComponent(pid)}/transition`, { status });
    showToast(`✓ 课题已流转到「${researchStatusStyle(status).label}」`, 'success');
    renderProjectDetail(document.getElementById('research-body'));
  } catch (e) {
    showToast(`✗ 流转失败: ${e.message}`, 'error');
  }
}

// ============================================
// 初始化绑定（由 app.js 调用）
// ============================================
function bindResearchEvents() {
  document.getElementById('toolbar-research')?.addEventListener('click', openResearchManager);
  document.getElementById('research-close')?.addEventListener('click', closeResearchManager);
  document.getElementById('research-overlay')?.addEventListener('click', e => {
    if (e.target === e.currentTarget) closeResearchManager();
  });
}

// v3.5.1: 注册模块初始化
if (typeof ModuleLoader !== 'undefined') {
  ModuleLoader.register('research', () => {
    if (typeof bindResearchEvents === 'function') bindResearchEvents();
  });
}
