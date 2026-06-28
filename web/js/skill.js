/**
 * skill.js — 技能管理（技能列表、配置、筛选）
 */

let _skillConfigCache = null;
let _allSkillsCache = [];

// ============================================
// 技能徽章
// ============================================
function updateSkillBadge() {
  const badge = document.getElementById('skill-badge');
  if (!badge) return;
  const mode = State.currentMode || 'co-working';
  const labels = { 'co-working': '协作', 'autonomous': '自主', 'review': '审阅' };
  badge.textContent = labels[mode] || mode;
}

// ============================================
// 技能管理面板
// ============================================
async function openSkillManager() {
  openModal('skill-manager-overlay');
  await loadSkillList();
}

function closeSkillManager() {
  closeModal('skill-manager-overlay');
}

async function loadSkillList() {
  const container = document.getElementById('skill-list-content');
  if (!container) return;
  container.innerHTML = '<p class="empty">◐ 加载中…</p>';

  try {
    const data = await apiGet('/api/skills');
    _allSkillsCache = data.skills || [];
    _skillConfigCache = data.config || {};
    renderSkillList();
    updateSkillCount();
  } catch (e) {
    console.error('加载技能失败:', e);
    container.innerHTML = '<p class="empty">加载失败</p>';
  }
}

function renderSkillList() {
  const container = document.getElementById('skill-list-content');
  if (!container) return;
  const filter = document.getElementById('skill-search-input')?.value.toLowerCase() || '';
  const mode = State.currentMode || 'co-working';
  const modeConfig = (_skillConfigCache && _skillConfigCache[mode]) || { enabled: [], disabled: [] };

  let skills = _allSkillsCache;
  if (filter) {
    skills = skills.filter(s => {
      const name = (s && typeof s.name === 'string') ? s.name : '';
      const desc = (s && typeof s.description === 'string') ? s.description : '';
      return name.toLowerCase().includes(filter) || desc.toLowerCase().includes(filter);
    });
  }

  container.innerHTML = skills.map(s => {
    const name = (s && typeof s.name === 'string') ? s.name : '';
    const desc = (s && typeof s.description === 'string') ? s.description : '';
    const enabled = modeConfig.enabled?.includes(name);
    return `
      <div class="skill-item ${enabled ? 'enabled' : ''}" data-name="${escapeHtml(name)}">
        <div class="skill-info">
          <div class="skill-name">${escapeHtml(name)}</div>
          <div class="skill-desc">${escapeHtml(desc)}</div>
        </div>
        <label class="switch">
          <input type="checkbox" ${enabled ? 'checked' : ''} data-skill="${escapeHtml(name)}">
          <span class="slider"></span>
        </label>
      </div>
    `;
  }).join('');

  container.querySelectorAll('input[type="checkbox"]').forEach(cb => {
    cb.addEventListener('change', () => {
      const name = cb.dataset.skill;
      const item = cb.closest('.skill-item');
      if (cb.checked) {
        item.classList.add('enabled');
        if (!modeConfig.enabled.includes(name)) modeConfig.enabled.push(name);
        modeConfig.disabled = modeConfig.disabled.filter(n => n !== name);
      } else {
        item.classList.remove('enabled');
        modeConfig.enabled = modeConfig.enabled.filter(n => n !== name);
        if (!modeConfig.disabled.includes(name)) modeConfig.disabled.push(name);
      }
      updateSkillCount();
    });
  });
}

function updateSkillCount() {
  const mode = State.currentMode || 'co-working';
  const modeConfig = (_skillConfigCache && _skillConfigCache[mode]) || { enabled: [] };
  const count = modeConfig.enabled?.length || 0;
  const el = document.getElementById('skill-active-count');
  if (el) el.textContent = `${count} 个技能已启用`;
}

function filterSkillList() {
  renderSkillList();
}

function onSkillModeChange(mode) {
  State.currentMode = mode;
  updateModeBadge(mode);
  updateSkillBadge();
  renderSkillList();
  updateSkillCount();
}

async function saveSkillConfig() {
  try {
    await apiPost('/api/skills/config', _skillConfigCache);
    showToast('技能配置已保存');
    closeSkillManager();
  } catch (e) {
    console.error('保存技能配置失败:', e);
    showToast('保存失败', 'error');
  }
}

async function resetSkillConfig() {
  if (!await confirmModal('确定重置所有技能配置？')) return;
  _skillConfigCache = {};
  renderSkillList();
  updateSkillCount();
  showToast('配置已重置（需保存生效）');
}

// v3.5.1: 注册模块初始化
// skill.js 无独立 bind 函数，事件绑定在 app.js bindKbManagerEvents() 中完成
if (typeof ModuleLoader !== 'undefined') {
  ModuleLoader.register('skill', () => {
    // 技能模块事件绑定由 app.js 统一处理，此处保留接口供未来迁移
  });
}
