/**
 * task.js — 任务看板管理
 */

// ============================================
// 任务加载与渲染
// ============================================
async function loadTasks() {
  if (!State.currentSessionId) return;
  try {
    const data = await apiGet('/api/tasks');
    const all = Array.isArray(data) ? data : [];
    State.tasks = all.filter(t => !t.session_id || t.session_id === State.currentSessionId);
    renderTaskBoard();
  } catch (e) {
    console.error('加载任务失败:', e);
    State.tasks = [];
    renderTaskBoard();
  }
}

function renderTaskBoard() {
  const columns = {
    backlog: document.getElementById('task-backlog'),
    active: document.getElementById('task-active'),
    completed: document.getElementById('task-completed'),
  };

  Object.values(columns).forEach(col => {
    if (col) col.innerHTML = '';
  });

  const tasks = Array.isArray(State.tasks) ? State.tasks : [];
  tasks.forEach(task => {
    const col = columns[task.status];
    if (!col) return;

    const card = document.createElement('div');
    card.className = 'task-card';
    card.dataset.taskId = task.task_id;  // v3.1.0: 修复字段名（后端用 task_id）
    card.draggable = true;

    const priorityClass = task.priority === 'high' ? 'priority-high' : task.priority === 'low' ? 'priority-low' : '';
    const tags = (task.tags || []).map(t => `<span class="task-tag">${escapeHtml(t)}</span>`).join('');

    card.innerHTML = `
      <div class="task-card-title ${priorityClass}">${escapeHtml(task.title)}</div>
      ${task.description ? `<div class="task-card-desc">${escapeHtml(task.description)}</div>` : ''}
      ${tags ? `<div class="task-card-tags">${tags}</div>` : ''}
      <div class="task-card-meta">
        <span>${task.assignee === 'hermes' ? '⚡hermes' : task.assignee === 'none' ? '' : '👤我'}</span>
        ${task.due_date ? `<span>${formatDate(task.due_date)}</span>` : ''}
      </div>
    `;

    card.addEventListener('click', () => openTaskDetail(task.task_id));
    card.addEventListener('dragstart', (e) => {
      e.dataTransfer.setData('text/plain', task.task_id);
      card.classList.add('dragging');
    });
    card.addEventListener('dragend', () => card.classList.remove('dragging'));

    col.appendChild(card);
  });

  document.querySelectorAll('.task-column-body').forEach(col => {
    col.addEventListener('dragover', (e) => {
      e.preventDefault();
      col.classList.add('drag-over');
    });
    col.addEventListener('dragleave', () => col.classList.remove('drag-over'));
    col.addEventListener('drop', async (e) => {
      e.preventDefault();
      col.classList.remove('drag-over');
      const taskId = e.dataTransfer.getData('text/plain');
      const newStatus = col.parentElement.dataset.status;
      await updateTaskStatus(taskId, newStatus);
    });
  });
}

// 更新任务状态并刷新任务看板（task.js 侧栏视图）。
// 注意：projects.js 的 cycleTaskStatus 也调用 PUT /api/tasks/{id}，但它面向项目
// 面板视图（renderTasksTab）且含 backlog→active→completed 循环逻辑；二者后端调用
// 相同但 UI/状态管理不同，故保持独立未合并。
async function updateTaskStatus(taskId, newStatus) {
  try {
    await apiPut(`/api/tasks/${taskId}`, { status: newStatus });
    const task = State.tasks.find(t => t.task_id === taskId);
    if (task) task.status = newStatus;
    renderTaskBoard();
    showToast('任务状态已更新');
  } catch (e) {
    console.error('更新任务状态失败:', e);
    showToast('更新失败', 'error');
  }
}

async function createNewTask(title, description = '', priority = 'medium') {
  if (!State.currentSessionId) {
    showToast('请先选择一个会话', 'warning');
    return;
  }
  try {
    const task = await apiPost('/api/tasks', {
      session_id: State.currentSessionId,
      title,
      description,
      status: 'backlog',
      priority,
    });
    // P5-1: 防御性合并 — 确保 status/priority 等字段存在
    const fullTask = {
      task_id: task.task_id || '',
      title: task.title || title,
      description: task.description || description,
      status: task.status || 'backlog',
      priority: task.priority || priority,
      assignee: task.assignee || 'myself',
      progress: task.progress || 0,
      subtasks: task.subtasks || [],
      tags: task.tags || [],
      project: task.project || '',
      ...task,
    };
    State.tasks.push(fullTask);
    renderTaskBoard();
    showToast('任务已创建');
  } catch (e) {
    console.error('创建任务失败:', e);
    showToast('创建失败', 'error');
  }
}

async function openTaskDetail(taskId) {
  const task = State.tasks.find(t => t.task_id === taskId);
  if (!task) return;

  const statusLabels = { backlog: '待办', active: '进行中', completed: '已完成', paused: '暂停' };
  const priorityLabels = { urgent: '紧急', high: '高', medium: '中', low: '低' };
  const assigneeLabels = { myself: '我自己', hermes: 'hermes 执行', none: '未分配' };

  const html = `
    <div class="task-detail">
      <h3>${escapeHtml(task.title)}</h3>
      <p>${escapeHtml(task.description || '无描述')}</p>
      <div class="task-detail-meta">
        <div>状态: ${escapeHtml(statusLabels[task.status] || task.status)}</div>
        <div>优先级: ${escapeHtml(priorityLabels[task.priority] || '中')}</div>
        <div>执行者: ${escapeHtml(assigneeLabels[task.assignee] || task.assignee || '未分配')}</div>
        ${task.project ? `<div>项目: ${escapeHtml(task.project)}</div>` : ''}
        ${task.due_date ? `<div>截止: ${formatDate(task.due_date)}</div>` : ''}
      </div>
      <div class="task-detail-actions">
        <button onclick="deleteTask('${task.task_id}')" class="btn-danger">删除任务</button>
      </div>
    </div>
  `;
  showModal(html);
}

async function deleteTask(taskId) {
  if (!await confirmModal('确定删除此任务？')) return;
  try {
    await apiDelete(`/api/tasks/${taskId}`);
    State.tasks = State.tasks.filter(t => t.task_id !== taskId);
    renderTaskBoard();
    closeModal('modal-overlay');
    showToast('任务已删除');
  } catch (e) {
    console.error('删除任务失败:', e);
    showToast('删除失败', 'error');
  }
}

// v3.5.1: 注册模块初始化
// task.js 无独立 bind 函数，事件绑定在 app.js bindKbManagerEvents() 中完成
if (typeof ModuleLoader !== 'undefined') {
  ModuleLoader.register('task', () => {
    // 任务模块事件绑定由 app.js 统一处理，此处保留接口供未来迁移
  });
}
