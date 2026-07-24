/**
 * dashboard.js — v6.0 仪表盘首页
 * 打开就看到今日待处理项：文献/任务/决策/hermes状态
 */

// 渲染仪表盘
async function renderDashboard() {
  const container = document.getElementById('dashboard-page');
  if (!container) return;
  container.innerHTML = '<div style="text-align:center;padding:40px;color:var(--text-tertiary);">◐ 加载中…</div>';

  try {
    const data = await apiGet('/api/dashboard');

    // 林赛主动开场
    const hour = new Date().getHours();
    const greeting = hour < 6 ? '夜深了' : hour < 12 ? '早上好' : hour < 18 ? '下午好' : '晚上好';
    const totalPending = (data.papers.unseen || 0) + (data.tasks.active || 0) + (data.tasks.backlog || 0) + (data.decisions_total || 0);
    const greetingText = totalPending > 0
      ? `${greeting}。你有 <strong>${totalPending}</strong> 件事待处理。`
      : `${greeting}。目前没有待处理事项，一切就绪。`;

    let html = `<div class="dash-greeting">${greetingText}</div>`;

    // === 文献简报区 ===
    const p = data.papers;
    html += `<div class="dash-section">
      <div class="dash-section-header" onclick="switchToView('papers')">
        <span class="dash-section-icon">📄</span>
        <span class="dash-section-title">文献简报</span>
        <span class="dash-section-count">${p.unseen} 篇待处理${p.pushed ? ` · 📡 ${p.pushed} 篇已推送飞书` : ''}</span>
        <span class="dash-section-arrow">→</span>
      </div>`;

    // 文献预览卡片（前3篇）
    if (p.preview && p.preview.length) {
      html += '<div class="dash-cards">';
      for (const paper of p.preview) {
        html += `<div class="dash-card" onclick="openPaperDiscussion('${escapeAttr(paper.arxiv_id)}','${escapeAttr(paper.title)}')">
          <div class="dash-card-title">${escapeHtml(paper.title.slice(0, 50))}</div>
          <div class="dash-card-meta">${escapeHtml(paper.direction)}${paper.pushed ? ' · 📡已推送' : ''}</div>
        </div>`;
      }
      html += '</div>';
    }
    html += `<div class="dash-view-all" onclick="switchToView('papers')">查看全部 →</div>`;
    html += '</div>';

    // === 任务区 ===
    const t = data.tasks;
    html += `<div class="dash-section">
      <div class="dash-section-header" onclick="switchToView('hermes')">
        <span class="dash-section-icon">📋</span>
        <span class="dash-section-title">任务</span>
        <span class="dash-section-count">${t.active} 进行中 · ${t.backlog} 待办</span>
        <span class="dash-section-arrow">→</span>
      </div>`;

    if (t.preview && t.preview.length) {
      html += '<div class="dash-list">';
      for (const task of t.preview) {
        const statusIcon = task.status === 'active' ? '◐' : '○';
        const assigneeTag = task.assignee === 'hermes' ? '<span class="dash-tag dash-tag-hermes">hermes</span>' : '';
        html += `<div class="dash-list-item">
          <span>${statusIcon}</span>
          <span class="dash-list-title">${escapeHtml(task.title)}</span>
          ${assigneeTag}
        </div>`;
      }
      html += '</div>';
    } else {
      html += '<div class="dash-empty">暂无任务</div>';
    }
    html += `<div class="dash-view-all" onclick="switchToView('hermes')">查看全部 →</div>`;
    html += '</div>';

    // === NSFC 决策区 ===
    const decs = data.decisions || [];
    if (decs.length) {
      html += `<div class="dash-section">
        <div class="dash-section-header" onclick="switchToView('papers')">
          <span class="dash-section-icon">📌</span>
          <span class="dash-section-title">NSFC 待决策</span>
          <span class="dash-section-count">${data.decisions_total || decs.length} 项待拍板</span>
          <span class="dash-section-arrow">→</span>
        </div>
        <div class="dash-list">`;
      for (const dec of decs) {
        html += `<div class="dash-list-item dash-decision">
          <span class="dash-list-title">${escapeHtml(dec.title)}</span>
          ${dec.topic ? `<span class="dash-tag">${escapeHtml(dec.topic)}</span>` : ''}
          <button class="dash-btn dash-btn-approve" onclick="event.stopPropagation();quickDecide('${escapeAttr(dec.id)}','approve')">✓</button>
          <button class="dash-btn dash-btn-reject" onclick="event.stopPropagation();quickDecide('${escapeAttr(dec.id)}','reject')">✗</button>
        </div>`;
      }
      html += '</div></div>';
    }

    // === hermes 状态区 ===
    const h = data.hermes;
    html += `<div class="dash-section dash-section-compact">
      <div class="dash-section-header" onclick="switchToView('hermes')">
        <span class="dash-section-icon">📡</span>
        <span class="dash-section-title">hermes</span>
        <span class="dash-section-count">${h.available ? `${h.cron_active} 个定时任务运行中` : '⚠️ 未连接'}</span>
        <span class="dash-section-arrow">→</span>
      </div>`;
    if (h.jobs && h.jobs.length) {
      html += '<div class="dash-list dash-list-compact">';
      for (const job of h.jobs) {
        const ok = job.last_status === 'ok';
        html += `<div class="dash-list-item"><span class="${ok ? 'dash-dot-ok' : 'dash-dot-warn'}">●</span> ${escapeHtml(job.name)} <span class="dash-list-meta">${escapeHtml(job.schedule)}</span></div>`;
      }
      html += '</div>';
    }
    html += '</div>';

    container.innerHTML = html;
  } catch (e) {
    container.innerHTML = `<div style="color:var(--error-color);padding:20px;">加载失败: ${escapeHtml(e.message)}</div>`;
  }
}

// 快速决策（仪表盘上的✓/✗按钮）
async function quickDecide(pid, action) {
  const label = action === 'approve' ? '通过' : '否决';
  showToast(`◐ ${label}中…`, 'info');
  try {
    await apiPost(`/api/projects/nsfc/pending/${pid}`, { action, title: '' });
    showToast(`✓ 已${label}`, 'success');
    renderDashboard(); // 刷新
  } catch (e) {
    showToast(`✗ ${e.message}`, 'error');
  }
}

// 导航切换（仪表盘/知识库/hermes）
function switchToView(view) {
  const views = ['dashboard', 'kb', 'hermes'];
  views.forEach(v => {
    const el = document.getElementById(v + '-page');
    if (el) el.style.display = v === view ? 'flex' : 'none';
  });
  // 更新导航按钮样式
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.classList.toggle('nav-btn-active', btn.dataset.view === view);
  });
  // 切到知识库时不重新渲染（常驻）
  // 切到仪表盘时刷新数据
  if (view === 'dashboard') renderDashboard();
}

// 初始化仪表盘（页面加载时调用）
function initDashboard() {
  // 默认显示仪表盘
  switchToView('dashboard');
}
