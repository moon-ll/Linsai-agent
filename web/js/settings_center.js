/**
 * settings_center.js — v6.7.7 设置中心
 *
 * 分类管理关键配置：
 * - pipeline      链路配置
 * - templates     内容/模板配置
 * - agents        Agent / Profile 配置
 * - tasks         任务配置
 * - learning      学习配置
 * - autonomy      自主级别配置
 * - kb_output     知识库 / 输出配置
 *
 * API:
 *   GET  /api/settings/categories
 *   GET  /api/settings/:category
 *   POST /api/settings/:category
 *   POST /api/settings/:category/preview
 */

(function() {
  'use strict';

  const SettingsState = {
    categories: [],
    current: 'pipeline',
    data: {},
    original: {},
    unsaved: false,
  };

  // 每个分类的编辑器配置
  const EDITORS = {
    pipeline: {
      fields: [
        { key: 'max_rounds', label: '最大优化轮数', type: 'number', min: 1, max: 100 },
        { key: 'score_threshold', label: '默认达标分数', type: 'number', min: 0, max: 1, step: 0.01 },
        { key: 'no_improvement_limit', label: '连续无提升轮数上限', type: 'number', min: 1, max: 20 },
        { key: 'stagger_seconds', label: '课题间错峰间隔（秒）', type: 'number', min: 0, max: 600 },
      ],
      groups: [
        {
          title: '维度短板阈值',
          description: '低于该分数视为该维度存在短板',
          prefix: 'dimension_floor',
          fields: [
            { key: 'innovation', label: '创新性', type: 'number', min: 0, max: 1, step: 0.01 },
            { key: 'feasibility', label: '可行性', type: 'number', min: 0, max: 1, step: 0.01 },
            { key: 'rigor', label: '严谨性', type: 'number', min: 0, max: 1, step: 0.01 },
            { key: 'completeness', label: '完整性', type: 'number', min: 0, max: 1, step: 0.01 },
          ],
        },
      ],
    },
    templates: {
      description: 'NSFC 三类项目质量标准、撰写模板与评审清单。',
      customRender: true,
    },
    rules: {
      description: '人工反馈意见标准、问题类型、严重级别与整理 prompt。',
      customRender: true,
    },
    agents: {
      fields: [
        { key: 'strategy', label: '路由策略', type: 'select', options: [{value:'priority',label:'优先级'},{value:'round_robin',label:'轮询'}] },
        { key: 'timeout', label: '默认超时（秒）', type: 'number', min: 10, max: 600 },
        { key: 'retry', label: '失败重试次数', type: 'number', min: 0, max: 5 },
      ],
      description: 'Provider 列表请在 memory/llm-config.json 中编辑，或对话让 agent 修改。',
    },
    tasks: {
      fields: [
        { key: 'default_assignee', label: '默认负责人', type: 'text' },
        { key: 'default_priority', label: '默认优先级', type: 'select', options: [{value:'low',label:'低'},{value:'medium',label:'中'},{value:'high',label:'高'}] },
        { key: 'auto_dispatch_hermes', label: '自动派活给 hermes', type: 'checkbox' },
      ],
    },
    learning: {
      fields: [
        { key: 'auto_enabled', label: '启用自主学习', type: 'checkbox' },
        { key: 'strategy', label: '学习策略', type: 'select', options: [{value:'conservative',label:'保守'},{value:'balanced',label:'平衡'},{value:'aggressive',label:'积极'}] },
        { key: 'daily_quota', label: '每日配额', type: 'number', min: 0, max: 50 },
        { key: 'cost_limit_daily', label: '每日成本上限', type: 'number', min: 0, max: 100, step: 0.1 },
        { key: 'max_daily_papers', label: '每日最大论文数', type: 'number', min: 0, max: 100 },
        { key: 'min_quality_score', label: '最低质量分', type: 'number', min: 0, max: 1, step: 0.05 },
      ],
    },
    autonomy: {
      fields: [
        { key: 'level', label: '自主级别', type: 'select', options: [{value:'observe',label:'观察'},{value:'suggest',label:'建议'},{value:'act',label:'执行'}] },
        { key: 'frequency', label: '提醒频率', type: 'select', options: [{value:'low',label:'低'},{value:'normal',label:'正常'},{value:'high',label:'高'}] },
      ],
    },
    kb_output: {
      fields: [
        { key: 'derived_ttl_days', label: 'derived 内容过期天数', type: 'number', min: 1, max: 365 },
      ],
      description: '可靠来源类型与归档萃取字段请在配置文件中编辑，或对话让 agent 修改。',
    },
  };

  // ============================================
  // 入口
  // ============================================

  function initSettingsCenter() {
    const navBtn = document.querySelector('.nav-btn[data-view="settings"]');
    if (navBtn) navBtn.addEventListener('click', () => {
      switchToView('settings');
      renderSettingsCenter();
    });
  }

  // ============================================
  // 渲染
  // ============================================

  async function renderSettingsCenter() {
    const page = document.getElementById('settings-page');
    if (!page) return;
    page.innerHTML = '<div style="padding:40px;text-align:center;color:var(--text-tertiary);">加载设置中心...</div>';

    try {
      const cats = await apiGet('/api/settings/categories');
      SettingsState.categories = cats.categories || [];
      await loadCategory(SettingsState.current);
      paintSettingsCenter();
    } catch (e) {
      page.innerHTML = `<div style="padding:40px;color:var(--error-color);">加载失败: ${escapeHtml(e.message)}</div>`;
    }
  }

  async function loadCategory(key) {
    const data = await apiGet(`/api/settings/${key}`);
    SettingsState.current = key;
    SettingsState.data = data.data || {};
    SettingsState.original = JSON.parse(JSON.stringify(data.data || {}));
    SettingsState.unsaved = false;
  }

  function paintSettingsCenter() {
    const page = document.getElementById('settings-page');
    if (!page) return;

    page.innerHTML = `
      <div class="settings-layout">
        <aside class="settings-menu">
          ${SettingsState.categories.map(c => `
            <div class="settings-menu-item ${c.key === SettingsState.current ? 'active' : ''}" data-category="${escapeAttr(c.key)}">
              <div class="settings-menu-label">${escapeHtml(c.label)}</div>
              <div class="settings-menu-desc">${escapeHtml(c.description)}</div>
            </div>
          `).join('')}
        </aside>
        <main class="settings-main">
          <div class="settings-header">
            <h2>${escapeHtml(currentLabel())}</h2>
            <div class="settings-actions">
              <button id="settings-preview-btn" class="btn-secondary">预览变更</button>
              <button id="settings-save-btn" class="btn-primary">保存</button>
            </div>
          </div>
          <div id="settings-form" class="settings-form"></div>
          <div id="settings-preview" class="settings-preview" style="display:none;"></div>
        </main>
      </div>
    `;

    renderForm();

    page.querySelectorAll('.settings-menu-item').forEach(el => {
      el.addEventListener('click', async () => {
        if (SettingsState.unsaved && !(await confirmModal('有未保存变更，确定切换？'))) return;
        await loadCategory(el.dataset.category);
        paintSettingsCenter();
      });
    });

    document.getElementById('settings-save-btn').addEventListener('click', saveCurrent);
    document.getElementById('settings-preview-btn').addEventListener('click', previewCurrent);
  }

  function currentLabel() {
    const cat = SettingsState.categories.find(c => c.key === SettingsState.current);
    return cat ? cat.label : SettingsState.current;
  }

  function renderForm() {
    const container = document.getElementById('settings-form');
    if (!container) return;
    const cfg = EDITORS[SettingsState.current];

    if (cfg?.customRender) {
      container.innerHTML = renderCustom(SettingsState.current);
      bindCustom(SettingsState.current);
      return;
    }

    let html = '';
    if (cfg?.description) {
      html += `<div class="settings-desc">${escapeHtml(cfg.description)}</div>`;
    }

    if (cfg?.fields) {
      html += '<div class="settings-fields">' + cfg.fields.map(f => renderField(f, SettingsState.data)).join('') + '</div>';
    }

    if (cfg?.groups) {
      for (const g of cfg.groups) {
        html += `<div class="settings-group"><div class="settings-group-title">${escapeHtml(g.title)}</div>`;
        if (g.description) html += `<div class="settings-group-desc">${escapeHtml(g.description)}</div>`;
        html += '<div class="settings-fields">';
        for (const f of g.fields) {
          const fullKey = g.prefix ? `${g.prefix}.${f.key}` : f.key;
          html += renderField({ ...f, key: fullKey }, SettingsState.data);
        }
        html += '</div></div>';
      }
    }

    container.innerHTML = html;
    bindFormChanges();
  }

  function renderField(field, data) {
    const value = getNested(data, field.key);
    const id = `stg-${field.key.replace(/\./g, '-')}`;
    let inputHtml = '';
    if (field.type === 'select') {
      inputHtml = `<select id="${id}" class="settings-input" data-key="${escapeAttr(field.key)}">
        ${field.options.map(opt => `<option value="${escapeAttr(opt.value)}" ${value === opt.value ? 'selected' : ''}>${escapeHtml(opt.label)}</option>`).join('')}
      </select>`;
    } else if (field.type === 'checkbox') {
      inputHtml = `<label class="settings-checkbox"><input type="checkbox" id="${id}" data-key="${escapeAttr(field.key)}" ${value ? 'checked' : ''}> 启用</label>`;
    } else if (field.type === 'number') {
      inputHtml = `<input type="number" id="${id}" class="settings-input" data-key="${escapeAttr(field.key)}" value="${value != null ? value : ''}" min="${field.min ?? ''}" max="${field.max ?? ''}" step="${field.step ?? ''}">`;
    } else {
      inputHtml = `<input type="text" id="${id}" class="settings-input" data-key="${escapeAttr(field.key)}" value="${value != null ? escapeAttr(value) : ''}">`;
    }
    return `
      <div class="settings-field">
        <label class="settings-field-label" for="${id}">${escapeHtml(field.label)}</label>
        ${inputHtml}
      </div>
    `;
  }

  function bindFormChanges() {
    const container = document.getElementById('settings-form');
    if (!container) return;
    container.querySelectorAll('[data-key]').forEach(el => {
      el.addEventListener('change', () => {
        const key = el.dataset.key;
        let val;
        if (el.type === 'checkbox') val = el.checked;
        else if (el.type === 'number') val = el.value === '' ? null : (el.step && el.step.includes('.') ? parseFloat(el.value) : parseInt(el.value));
        else val = el.value;
        setNested(SettingsState.data, key, val);
        SettingsState.unsaved = true;
        document.getElementById('settings-preview').style.display = 'none';
      });
    });
  }

  // ============================================
  // 自定义渲染：templates / rules
  // ============================================

  function renderCustom(category) {
    if (category === 'templates') return renderTemplatesEditor();
    if (category === 'rules') return renderRulesEditor();
    return '<div class="settings-desc">该分类暂不支持可视化编辑，请通过对话让 agent 修改。</div>';
  }

  function bindCustom(category) {
    if (category === 'templates') bindTemplatesEditor();
    else if (category === 'rules') bindRulesEditor();
  }

  // ---------- templates ----------

  const TEMPLATE_TABS = ['基础参数', '撰写要求', '评审清单'];
  let tplActiveTab = '基础参数';

  function renderTemplatesEditor() {
    const types = SettingsState.data.project_types || {};
    let html = '<div class="settings-desc">可调整各项目类型的分数阈值、页数限制、撰写风格与评审清单。</div>';
    html += '<div class="settings-template-list">';
    for (const [key, info] of Object.entries(types)) {
      html += `
        <div class="settings-template-card" data-type="${escapeAttr(key)}">
          <div class="settings-template-title">${escapeHtml(info.name_cn || key)} <span class="text-tertiary fs-072">(${escapeHtml(key)})</span></div>
          <div class="settings-template-tabs">
            ${TEMPLATE_TABS.map(t => `<button class="settings-template-tab ${t === tplActiveTab ? 'active' : ''}" data-tab="${escapeAttr(t)}" data-type="${escapeAttr(key)}">${escapeHtml(t)}</button>`).join('')}
          </div>
          <div class="settings-template-body" data-type="${escapeAttr(key)}">
            ${renderTemplateTabContent(key, info)}
          </div>
        </div>
      `;
    }
    html += '</div>';
    return html;
  }

  function renderTemplateTabContent(typeKey, info) {
    if (tplActiveTab === '基础参数') {
      return `
        <div class="settings-fields">
          <div class="settings-field"><label>资助上限（万元）</label><input type="number" class="settings-input stg-tpl-num" data-type="${escapeAttr(typeKey)}" data-field="funding_max_wan" value="${info.funding_max_wan != null ? info.funding_max_wan : ''}"></div>
          <div class="settings-field"><label>执行年限（年）</label><input type="number" class="settings-input stg-tpl-num" data-type="${escapeAttr(typeKey)}" data-field="duration_years" value="${info.duration_years != null ? info.duration_years : ''}"></div>
          <div class="settings-field"><label>页数限制</label><input type="number" class="settings-input stg-tpl-num" data-type="${escapeAttr(typeKey)}" data-field="page_limit" value="${info.page_limit != null ? info.page_limit : ''}"></div>
          <div class="settings-field"><label>达标分数</label><input type="number" class="settings-input stg-tpl-num" data-type="${escapeAttr(typeKey)}" data-field="min_overall_score" value="${info.quality_threshold?.min_overall_score ?? ''}" min="0" max="1" step="0.01"></div>
          <div class="settings-field"><label>允许 high 问题数</label><input type="number" class="settings-input stg-tpl-num" data-type="${escapeAttr(typeKey)}" data-field="max_high_issues" value="${info.quality_threshold?.max_high_issues ?? ''}" min="0"></div>
          <div class="settings-field"><label>允许 medium 问题数</label><input type="number" class="settings-input stg-tpl-num" data-type="${escapeAttr(typeKey)}" data-field="max_medium_issues" value="${info.quality_threshold?.max_medium_issues ?? ''}" min="0"></div>
          <div class="settings-field" style="grid-column:1/-1;"><label>核心要求</label><textarea class="settings-textarea stg-tpl-text" data-type="${escapeAttr(typeKey)}" data-field="core_requirement" rows="2">${escapeHtml(info.core_requirement || '')}</textarea></div>
          <div class="settings-field" style="grid-column:1/-1;"><label>结构要求</label><textarea class="settings-textarea stg-tpl-text" data-type="${escapeAttr(typeKey)}" data-field="structure" rows="2">${escapeHtml(info.structure || '')}</textarea></div>
        </div>
      `;
    }
    if (tplActiveTab === '撰写要求') {
      const style = info.writing_style || {};
      let html = '<div class="settings-fields">';
      for (const section of ['立项依据', '研究内容', '研究方案', '特色创新', '年度研究计划', '预期研究成果']) {
        html += `<div class="settings-field" style="grid-column:1/-1;"><label>${escapeHtml(section)}</label><textarea class="settings-textarea stg-tpl-style" data-type="${escapeAttr(typeKey)}" data-section="${escapeAttr(section)}" rows="2">${escapeHtml(style[section] || '')}</textarea></div>`;
      }
      html += '</div>';
      return html;
    }
    if (tplActiveTab === '评审清单') {
      const checklist = info.review_checklist || [];
      let html = `<div class="settings-checklist" data-type="${escapeAttr(typeKey)}">`;
      checklist.forEach((item, idx) => {
        html += `
          <div class="settings-checklist-item">
            <span class="settings-checklist-num">${idx + 1}.</span>
            <input type="text" class="settings-input stg-tpl-checklist" data-type="${escapeAttr(typeKey)}" data-idx="${idx}" value="${escapeAttr(item)}">
            <button class="btn-text stg-tpl-checklist-del" data-type="${escapeAttr(typeKey)}" data-idx="${idx}">✕</button>
          </div>`;
      });
      html += `<button class="btn-text stg-tpl-checklist-add" data-type="${escapeAttr(typeKey)}">+ 添加评审项</button>`;
      html += '</div>';
      return html;
    }
    return '';
  }

  function bindTemplatesEditor() {
    const container = document.getElementById('settings-form');
    if (!container) return;

    // 标签切换
    container.querySelectorAll('.settings-template-tab').forEach(btn => {
      btn.addEventListener('click', () => {
        tplActiveTab = btn.dataset.tab;
        paintSettingsCenter();
      });
    });

    // 数值 / 文本字段
    container.querySelectorAll('.stg-tpl-num, .stg-tpl-text').forEach(el => {
      el.addEventListener('change', () => {
        const type = el.dataset.type;
        const field = el.dataset.field;
        let val;
        if (el.type === 'number') {
          val = el.value === '' ? null : (el.step && el.step.includes('.') ? parseFloat(el.value) : parseInt(el.value));
        } else {
          val = el.value;
        }
        ensurePath(SettingsState.data, ['project_types', type]);
        if (['min_overall_score', 'max_high_issues', 'max_medium_issues'].includes(field)) {
          ensurePath(SettingsState.data, ['project_types', type, 'quality_threshold']);
          SettingsState.data.project_types[type].quality_threshold[field] = val;
        } else {
          SettingsState.data.project_types[type][field] = val;
        }
        SettingsState.unsaved = true;
      });
    });

    // 撰写风格
    container.querySelectorAll('.stg-tpl-style').forEach(el => {
      el.addEventListener('change', () => {
        const type = el.dataset.type;
        const section = el.dataset.section;
        ensurePath(SettingsState.data, ['project_types', type, 'writing_style']);
        SettingsState.data.project_types[type].writing_style[section] = el.value;
        SettingsState.unsaved = true;
      });
    });

    // 评审清单
    container.querySelectorAll('.stg-tpl-checklist').forEach(el => {
      el.addEventListener('change', () => {
        const type = el.dataset.type;
        const idx = parseInt(el.dataset.idx);
        ensurePath(SettingsState.data, ['project_types', type, 'review_checklist'], []);
        SettingsState.data.project_types[type].review_checklist[idx] = el.value;
        SettingsState.unsaved = true;
      });
    });
    container.querySelectorAll('.stg-tpl-checklist-del').forEach(btn => {
      btn.addEventListener('click', () => {
        const type = btn.dataset.type;
        const idx = parseInt(btn.dataset.idx);
        ensurePath(SettingsState.data, ['project_types', type, 'review_checklist'], []);
        SettingsState.data.project_types[type].review_checklist.splice(idx, 1);
        SettingsState.unsaved = true;
        paintSettingsCenter();
      });
    });
    container.querySelectorAll('.stg-tpl-checklist-add').forEach(btn => {
      btn.addEventListener('click', () => {
        const type = btn.dataset.type;
        ensurePath(SettingsState.data, ['project_types', type, 'review_checklist'], []);
        SettingsState.data.project_types[type].review_checklist.push('');
        SettingsState.unsaved = true;
        paintSettingsCenter();
      });
    });
  }

  // ---------- rules ----------

  function renderRulesEditor() {
    let html = '<div class="settings-desc">编辑人工反馈标准。可直接修改 JSON 文本，保存前会校验格式。</div>';
    html += '<textarea id="stg-rules-json" class="settings-json-editor" rows="28">' + escapeHtml(JSON.stringify(SettingsState.data, null, 2)) + '</textarea>';
    html += '<div id="stg-rules-error" class="text-error mt-8" style="display:none;"></div>';
    return html;
  }

  function bindRulesEditor() {
    const container = document.getElementById('settings-form');
    if (!container) return;
    const textarea = document.getElementById('stg-rules-json');
    const errorEl = document.getElementById('stg-rules-error');
    if (!textarea) return;

    const apply = () => {
      try {
        const parsed = JSON.parse(textarea.value);
        SettingsState.data = parsed;
        SettingsState.unsaved = true;
        errorEl.style.display = 'none';
        errorEl.textContent = '';
      } catch (e) {
        errorEl.style.display = 'block';
        errorEl.textContent = 'JSON 格式错误：' + e.message;
      }
    };
    textarea.addEventListener('change', apply);
    textarea.addEventListener('input', apply);
  }

  // ---------- helpers ----------

  function ensurePath(obj, path, defaultValue) {
    let cur = obj;
    for (let i = 0; i < path.length - 1; i++) {
      const k = path[i];
      if (!cur[k] || typeof cur[k] !== 'object') cur[k] = {};
      cur = cur[k];
    }
    const last = path[path.length - 1];
    if (cur[last] === undefined && defaultValue !== undefined) cur[last] = defaultValue;
  }

  // ============================================
  // 保存 / 预览
  // ============================================

  async function saveCurrent() {
    const btn = document.getElementById('settings-save-btn');
    btn.disabled = true; btn.textContent = '保存中…';
    try {
      await apiPost(`/api/settings/${SettingsState.current}`, SettingsState.data);
      SettingsState.original = JSON.parse(JSON.stringify(SettingsState.data));
      SettingsState.unsaved = false;
      showToast('配置已保存');
      document.getElementById('settings-preview').style.display = 'none';
    } catch (e) {
      showToast(`✗ ${e.message}`, 'error');
    } finally {
      btn.disabled = false; btn.textContent = '保存';
    }
  }

  async function previewCurrent() {
    const previewEl = document.getElementById('settings-preview');
    previewEl.style.display = 'block';
    previewEl.innerHTML = '<div>计算差异...</div>';
    try {
      const data = await apiPost(`/api/settings/${SettingsState.current}/preview`, SettingsState.data);
      const diff = data.diff || [];
      if (diff.length === 0) {
        previewEl.innerHTML = '<div class="settings-preview-empty">无变更</div>';
      } else {
        previewEl.innerHTML = '<div class="settings-preview-title">即将变更的字段</div>' + diff.map(d => `
          <div class="settings-preview-row">
            <div class="settings-preview-key">${escapeHtml(d.key)}</div>
            <div class="settings-preview-old">旧: ${escapeHtml(JSON.stringify(d.old))}</div>
            <div class="settings-preview-new">新: ${escapeHtml(JSON.stringify(d.new))}</div>
          </div>
        `).join('');
      }
    } catch (e) {
      previewEl.innerHTML = `<div class="text-error">预览失败: ${escapeHtml(e.message)}</div>`;
    }
  }

  // ============================================
  // 工具
  // ============================================

  function getNested(obj, key) {
    return key.split('.').reduce((o, k) => (o && typeof o === 'object') ? o[k] : undefined, obj);
  }

  function setNested(obj, key, value) {
    const parts = key.split('.');
    let cur = obj;
    for (let i = 0; i < parts.length - 1; i++) {
      if (!cur[parts[i]] || typeof cur[parts[i]] !== 'object') cur[parts[i]] = {};
      cur = cur[parts[i]];
    }
    cur[parts[parts.length - 1]] = value;
  }

  if (typeof ModuleLoader !== 'undefined') {
    ModuleLoader.register('settings_center', initSettingsCenter);
  } else {
    window.addEventListener('DOMContentLoaded', initSettingsCenter);
  }
})();
