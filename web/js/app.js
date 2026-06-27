/**
 * app.js — 入口模块：事件绑定 + 初始化
 * 依赖：core.js, session.js, chat.js, task.js, settings.js, skill.js, kb.js, learning.js
 */

// ============================================
// 事件绑定
// ============================================
function bindEvents() {
  // 主题切换
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);

  // 设置面板
  document.getElementById('settings-toggle').addEventListener('click', () => {
    document.getElementById('settings-drawer').style.display = 'flex';
    document.getElementById('theme-select').value = State.theme;
    document.getElementById('autonomy-select').value = State.autonomy;
    loadLLMStatus();
    loadUsage();
    loadLearningConfig();
  });

  // 顶部 provider-badge 点击打开设置面板
  document.getElementById('provider-badge').addEventListener('click', () => {
    document.getElementById('settings-drawer').style.display = 'flex';
    document.getElementById('theme-select').value = State.theme;
    document.getElementById('autonomy-select').value = State.autonomy;
    loadLLMStatus();
    loadUsage();
    loadLearningConfig();
  });
  document.getElementById('close-settings').addEventListener('click', () => {
    document.getElementById('settings-drawer').style.display = 'none';
  });
  document.getElementById('settings-drawer').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) {
      e.currentTarget.style.display = 'none';
    }
  });

  // 关闭归档浏览视图
  document.getElementById('close-archive-view').addEventListener('click', () => {
    document.getElementById('chat-archive-header').style.display = 'none';
    document.querySelector('.input-area').style.display = 'block';
    State.viewingArchive = false;
    renderSessionList();
    if (State.currentSessionId) {
      switchSession(State.currentSessionId);
    }
  });

  // 关闭历史提示条
  document.getElementById('history-hint-close').addEventListener('click', () => {
    document.getElementById('history-hint').style.display = 'none';
  });

  // 主题选择
  document.getElementById('theme-select').addEventListener('change', (e) => {
    applyTheme(e.target.value);
  });

  // 自主级别选择
  document.getElementById('autonomy-select').addEventListener('change', (e) => {
    State.autonomy = e.target.value;
    localStorage.setItem('linsai-autonomy', e.target.value);
    showToast(`自主级别已设为: ${e.target.value}`);
  });

  // P0-10: 设置面板内备份按钮 — 真正触发备份
  document.getElementById('drawer-backup-btn').addEventListener('click', async () => {
    const btn = document.getElementById('drawer-backup-btn');
    if (btn) { btn.disabled = true; btn.textContent = '◐ 备份中…'; }
    try {
      const data = await apiPost('/api/backup', { action: 'create' }, 60000);
      if (data.success) {
        showToast(`✓ 备份成功: ${data.path} (${data.size_kb} KB)`, 'success', 5000);
      } else {
        showToast('✗ 备份失败', 'error');
      }
    } catch (e) {
      showToast('✗ 备份失败: ' + e.message, 'error');
    } finally {
      if (btn) { btn.disabled = false; btn.textContent = '💾 立即备份'; }
    }
  });

  // 加载 LLM 状态
  loadLLMStatus();

  // 新建会话
  document.getElementById('new-session-btn').addEventListener('click', () => {
    openModal('new-session-modal');
    document.getElementById('new-session-topic').focus();
  });
  document.getElementById('cancel-new-session').addEventListener('click', () => {
    closeModal('new-session-modal');
  });
  document.getElementById('confirm-new-session').addEventListener('click', () => {
    const topic = document.getElementById('new-session-topic').value.trim();
    const mode = document.getElementById('new-session-mode').value;
    if (!topic) {
      showToast('请输入会话主题', 'warning');
      return;
    }
    createNewSession(topic, mode);
    closeModal('new-session-modal');
    document.getElementById('new-session-topic').value = '';
  });
  document.getElementById('new-session-modal').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) {
      e.currentTarget.style.display = 'none';
    }
  });
  document.getElementById('new-session-topic').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      document.getElementById('confirm-new-session').click();
    }
  });

  // 会话搜索
  document.getElementById('session-search').addEventListener('input', renderSessionList);

  // 发送消息
  document.getElementById('send-btn').addEventListener('click', () => {
    const input = document.getElementById('message-input');
    sendMessage(input.value);
  });
  document.getElementById('message-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(e.target.value);
    }
  });

  // 输入时实时检测激活的技能
  let _skillDebounce = null;
  document.getElementById('message-input').addEventListener('input', (e) => {
    clearTimeout(_skillDebounce);
    _skillDebounce = setTimeout(() => {
      updateSkillBadge(e.target.value);
    }, 300);
  });

  // 快捷命令按钮
  document.querySelectorAll('.cmd-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const cmd = btn.dataset.cmd;
      const input = document.getElementById('message-input');
      if (cmd === '/mode') {
        showToast('模式切换请在新建会话时选择', 'warning');
      } else if (cmd === '/read') {
        input.value = '/read ';
        input.focus();
      } else if (cmd === '/agora') {
        selectedPersonas = [];
        renderPersonaGrid();
        openModal('agora-modal');
      } else if (cmd === '/summary') {
        sendMessage('/summary');
      }
    });
  });

  // Agora 弹窗
  document.getElementById('cancel-agora').addEventListener('click', () => {
    closeModal('agora-modal');
  });
  document.getElementById('confirm-agora').addEventListener('click', handleAgoraExport);
  document.getElementById('agora-modal').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) {
      e.currentTarget.style.display = 'none';
    }
  });

  // 编辑消息弹窗
  document.getElementById('cancel-edit-message').addEventListener('click', () => {
    closeModal('edit-message-modal');
    editingMsgId = null;
  });
  document.getElementById('confirm-edit-message').addEventListener('click', saveEditMessage);
  document.getElementById('edit-message-modal').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) {
      e.currentTarget.style.display = 'none';
      editingMsgId = null;
    }
  });

  // 文件上传
  const uploadZone = document.getElementById('upload-zone');
  const fileInput = document.getElementById('file-input');

  document.getElementById('upload-btn').addEventListener('click', () => {
    const zone = document.getElementById('upload-zone');
    if (zone.style.display === 'none' || !zone.style.display) {
      zone.style.display = 'block';
    } else {
      zone.style.display = 'none';
    }
  });

  fileInput.addEventListener('change', (e) => {
    uploadFiles(e.target.files);
    fileInput.value = '';
  });

  uploadZone.addEventListener('click', () => fileInput.click());

  uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('drag-over');
  });
  uploadZone.addEventListener('dragleave', () => {
    uploadZone.classList.remove('drag-over');
  });
  uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('drag-over');
    if (e.dataTransfer.files.length > 0) {
      uploadFiles(e.dataTransfer.files);
    }
  });

  // 移动端侧边栏切换
  document.getElementById('sidebar-toggle').addEventListener('click', () => {
    document.getElementById('left-sidebar').classList.toggle('open');
  });

  // P1-3: 移动端 kb/chat tab 切换
  document.querySelectorAll('.mobile-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      const target = tab.dataset.target;
      document.querySelectorAll('.mobile-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const kbMain = document.getElementById('kb-main');
      const chatSidebar = document.getElementById('chat-sidebar');
      if (target === 'kb-main') {
        kbMain?.classList.remove('mobile-hidden');
        chatSidebar?.classList.remove('mobile-visible');
      } else {
        kbMain?.classList.add('mobile-hidden');
        chatSidebar?.classList.add('mobile-visible');
      }
    });
  });

  // 归档按钮 → 打开历史搜索侧边栏
  document.getElementById('archived-btn').addEventListener('click', () => {
    document.getElementById('history-sidebar').style.display = 'flex';
  });

  // 顶部栏"查看历史记录"按钮 → 只读浏览当前会话
  document.getElementById('view-history-btn').addEventListener('click', () => {
    if (!State.currentSessionId) {
      showToast('请先选择一个会话', 'warning');
      return;
    }
    viewArchiveSession(State.currentSessionId);
  });

  // 关闭历史搜索
  document.getElementById('close-history').addEventListener('click', () => {
    document.getElementById('history-sidebar').style.display = 'none';
  });

  // 历史搜索
  document.getElementById('history-search-btn').addEventListener('click', searchHistory);
  document.getElementById('history-search-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') searchHistory();
  });

  // 底部按钮
  // P0-10: 底部备份按钮 — 真正触发备份
  document.getElementById('backup-btn').addEventListener('click', async () => {
    const btn = document.getElementById('backup-btn');
    if (btn) { btn.disabled = true; btn.textContent = '◐ 备份中…'; }
    try {
      const data = await apiPost('/api/backup', { action: 'create' }, 60000);
      if (data.success) {
        showToast(`✓ 备份成功: ${data.path} (${data.size_kb} KB)`, 'success', 5000);
      } else {
        showToast('✗ 备份失败', 'error');
      }
    } catch (e) {
      showToast('✗ 备份失败: ' + e.message, 'error');
    } finally {
      if (btn) { btn.disabled = false; btn.textContent = '💾 备份'; }
    }
  });
  document.getElementById('export-btn').addEventListener('click', async () => {
    if (!State.currentSessionId) {
      showToast('请先选择一个会话', 'info');
      return;
    }
    try {
      const [messages, sessions] = await Promise.all([
        apiGet(`/api/sessions/${State.currentSessionId}/messages`),
        apiGet('/api/sessions'),
      ]);
      const msgs = messages.messages || messages;
      const sess = sessions.find(s => s.session_id === State.currentSessionId) || {};
      const topic = sess.topic || State.currentSessionId;
      let md = `# ${topic}\n\n> 导出于 ${new Date().toLocaleString()}\n\n`;
      for (const m of msgs) {
        const role = m.role === 'user' ? '🧑 用户' : '🔬 林赛';
        md += `### ${role}\n\n${m.content || ''}\n\n---\n\n`;
      }
      const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = `${State.currentSessionId}.md`;
      a.click();
      URL.revokeObjectURL(a.href);
      showToast(`✓ 已导出 ${msgs.length} 条消息`, 'success');
    } catch (e) {
      showToast('✗ 导出失败: ' + e.message, 'error');
    }
  });

  // 监听系统主题变化
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (State.theme === 'auto') {
      applyTheme('auto');
    }
  });

  // 全局拖拽上传
  document.addEventListener('dragover', (e) => {
    if (e.dataTransfer.types.includes('Files')) {
      uploadZone.classList.add('drag-over');
    }
  });
  document.addEventListener('dragleave', (e) => {
    if (e.relatedTarget === null) {
      uploadZone.classList.remove('drag-over');
    }
  });
  document.addEventListener('drop', (e) => {
    uploadZone.classList.remove('drag-over');
  });

  // 工具栏 & 知识库管理器事件（跨模块绑定）
  bindKbManagerEvents();
}

// ============================================
// 跨模块事件绑定（工具栏、学习管理器、技能管理器、任务、@知识库）
// ============================================
function bindKbManagerEvents() {
  // P2-7: 工具栏按钮 active 态切换辅助
  function toggleToolbarActive(btnId, overlayId) {
    const btn = document.getElementById(btnId);
    const overlay = document.getElementById(overlayId);
    if (!btn || !overlay) return;
    const observer = new MutationObserver(() => {
      const isVisible = overlay.style.display !== 'none' && overlay.style.display !== '';
      btn.classList.toggle('active', isVisible);
    });
    observer.observe(overlay, { attributes: true, attributeFilter: ['style'] });
  }

  // 工具栏按钮
  document.getElementById('toolbar-kb')?.addEventListener('click', openKbManager);
  document.getElementById('toolbar-skills')?.addEventListener('click', openSkillManager);
  toggleToolbarActive('toolbar-skills', 'skill-manager-overlay');
  toggleToolbarActive('toolbar-learning', 'learning-manager-overlay');
  toggleToolbarActive('toolbar-projects', 'projects-overlay');
  toggleToolbarActive('toolbar-hermes', 'hermes-overlay');
  toggleToolbarActive('toolbar-research', 'research-overlay');
  document.getElementById('toolbar-tasks')?.addEventListener('click', () => {
    // P0-8: 修复窄屏失效 + 移除无效 flash
    const sidebar = document.getElementById('right-sidebar');
    if (!sidebar) {
      showToast('📋 任务面板在右侧栏', 'info');
      return;
    }
    // 窄屏展开侧栏
    if (window.innerWidth <= 768) {
      sidebar.classList.remove('collapsed');
      sidebar.style.display = 'flex';
    }
    // 高亮任务区域
    sidebar.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    const taskSection = sidebar.querySelector('.task-board') || sidebar;
    taskSection.style.transition = 'box-shadow 0.3s';
    taskSection.style.boxShadow = '0 0 0 2px var(--accent-color)';
    setTimeout(() => { taskSection.style.boxShadow = ''; }, 1500);
  });
  // P0-5: 统一用量统计，复用 loadUsage + 弹窗展示
  document.getElementById('toolbar-usage')?.addEventListener('click', async () => {
    try {
      const data = await apiGet('/api/usage');
      const today = data.today || data.daily || {};
      const total = data.total || {};
      const todayTokens = today.tokens || today.total_tokens || 0;
      const todayCost = today.cost || 0;
      const todayCalls = today.calls || today.messages || 0;
      const totalTokens = total.tokens || 0;
      const totalCost = total.cost || 0;
      showModal(`<div style="padding:16px;line-height:1.8;">
        <h3 style="margin-bottom:8px;">📊 Token 用量统计</h3>
        <hr style="border:none;border-top:1px solid var(--border-color);margin:8px 0;">
        <p><strong>今日</strong></p>
        <p>• 调用次数: ${todayCalls}</p>
        <p>• Token: ${todayTokens.toLocaleString()}</p>
        <p>• 费用: ¥${todayCost.toFixed(2)}</p>
        <hr style="border:none;border-top:1px solid var(--border-color);margin:8px 0;">
        <p><strong>累计</strong></p>
        <p>• Token: ${totalTokens.toLocaleString()}</p>
        <p>• 费用: ¥${totalCost.toFixed(2)}</p>
      </div>`);
    } catch (e) {
      showToast('加载用量失败', 'error');
    }
  });
  document.getElementById('toolbar-learning')?.addEventListener('click', openLearningManager);

  // 学习管理器
  document.getElementById('learning-manager-close')?.addEventListener('click', closeLearningManager);
  document.getElementById('learning-manager-overlay')?.addEventListener('click', (e) => {
    if (e.target === e.currentTarget) closeLearningManager();
  });
  document.getElementById('learning-trigger-btn')?.addEventListener('click', async () => {
    const btn = document.getElementById('learning-trigger-btn');
    if (btn) btn.disabled = true;
    showToast('🌱 启动自主学习周期...', 'info');
    try {
      const result = await apiPost('/api/learning/trigger', { sources: ['arxiv'], max_items: 1 });
      if (result.created && result.created.length > 0) {
        showToast(`✓ 学习完成，创建 ${result.created.length} 个 wiki`, 'success');
      } else if (result.failed && result.failed.length > 0) {
        showToast(`⚠ 学习失败: ${result.failed[0]}`, 'warning');
      } else {
        showToast('○ 未发现学习机会', 'info');
      }
      await renderLearningManager();
    } catch (e) {
      showToast('✗ 触发失败: ' + e.message, 'error');
    } finally {
      if (btn) btn.disabled = false;
    }
  });
  document.querySelectorAll('#learning-manager-overlay .kb-tab').forEach(tab => {
    tab.addEventListener('click', () => switchLearningTab(tab.dataset.tab));
  });

  // P0-2: 绑定学习配置保存按钮
  document.getElementById('save-learning-config')?.addEventListener('click', saveLearningConfig);

  // 项目面板 + hermes 控制台 + 课题指导
  if (typeof bindProjectsEvents === 'function') bindProjectsEvents();
  if (typeof bindHermesEvents === 'function') bindHermesEvents();
  if (typeof bindResearchEvents === 'function') bindResearchEvents();

  // 任务新建/删除
  document.getElementById('task-add-btn')?.addEventListener('click', () => {
    const form = document.getElementById('task-add-form');
    if (form) {
      form.style.display = form.style.display === 'none' ? 'block' : 'none';
      if (form.style.display === 'block') document.getElementById('task-add-title')?.focus();
    }
  });
  document.getElementById('task-add-confirm')?.addEventListener('click', () => {
    const title = document.getElementById('task-add-title')?.value.trim();
    const priority = document.getElementById('task-add-priority')?.value || 'medium';  // v3.1.0: 修复 priority 被丢弃
    if (title) createNewTask(title, '', priority);
    document.getElementById('task-add-title').value = '';
    document.getElementById('task-add-form').style.display = 'none';
  });
  document.getElementById('task-add-cancel')?.addEventListener('click', () => {
    document.getElementById('task-add-form').style.display = 'none';
  });
  document.getElementById('task-add-title')?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      const title = e.target.value.trim();
      const priority = document.getElementById('task-add-priority')?.value || 'medium';
      if (title) createNewTask(title, '', priority);
      document.getElementById('task-add-title').value = '';
      document.getElementById('task-add-form').style.display = 'none';
    }
  });

  // @知识库文件讨论
  document.getElementById('kb-context-btn')?.addEventListener('click', openKbFilePicker);
  document.getElementById('message-input')?.addEventListener('input', handleKbMention);
  document.getElementById('message-input')?.addEventListener('focus', ensureKbFileCache);

  // 技能管理器
  document.getElementById('skill-manager-close')?.addEventListener('click', closeSkillManager);
  document.getElementById('skill-manager-overlay')?.addEventListener('click', (e) => {
    if (e.target === e.currentTarget) closeSkillManager();
  });
  document.getElementById('skill-save-btn')?.addEventListener('click', saveSkillConfig);
  document.getElementById('skill-reset-btn')?.addEventListener('click', resetSkillConfig);
  document.getElementById('skill-search-input')?.addEventListener('input', filterSkillList);
  document.querySelectorAll('input[name="skill-mode"]').forEach(radio => {
    radio.addEventListener('change', (e) => onSkillModeChange(e.target.value));
  });
}

// ============================================
// 初始化
// ============================================
async function init() {
  applyTheme(State.theme);

  try {
    const data = await apiGet('/api/version');
    document.getElementById('version-label').textContent = data.version;
  } catch (e) {
    console.error('获取版本失败:', e);
  }

  await loadSessions();
  loadSessionKeywords();
  await checkHeartbeat();
  loadReferences();
  loadUsage();
  loadLLMStatus();
  bindEvents();
  initKbMain();
  initChatSidebar();

  // P1-2: 自动选择第一个会话或显示欢迎页
  if (State.sessions.length > 0) {
    const active = State.sessions.find(s => s.status === 'active') || State.sessions[0];
    if (active && active.session_id) {
      switchSession(active.session_id);
    }
  } else {
    // 无会话时显示欢迎页
    const welcome = document.getElementById('welcome-screen');
    if (welcome) welcome.style.display = 'flex';
  }

  // v3.5.1: 模块加载器统一初始化
  if (typeof ModuleLoader !== 'undefined' && typeof ModuleLoader.init === 'function') {
    const result = ModuleLoader.init();
    if (result.fail > 0) {
      console.warn(`[ModuleLoader] ${result.fail}/${result.total} 个模块初始化失败`);
    }
  }
}

// 启动
document.addEventListener('DOMContentLoaded', init);
