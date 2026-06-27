/**
 * settings.js — LLM 状态、用量统计、学习配置、心跳检测、状态栏更新、历史提示
 */

// ============================================
// 心跳检测 & 状态更新 (P0-6: 用 status-text 替代不存在的 status-dot)
// v3.4: 消费 reminders，展示林赛主动提醒
// ============================================
let _heartbeatTimer = null;
let _lastProactiveMsgs = [];

async function checkHeartbeat() {
  try {
    const data = await apiGet('/api/heartbeat');
    updateStatus('就绪');
    // v3.4: 消费主动提醒消息
    const msgs = data.proactive_messages || [];
    if (msgs.length > 0) {
      _showProactiveReminders(msgs);
    }
    _lastProactiveMsgs = msgs;
    // 设置 30 秒后再次检测
    if (_heartbeatTimer) clearTimeout(_heartbeatTimer);
    _heartbeatTimer = setTimeout(checkHeartbeat, 30000);
  } catch (e) {
    updateStatus('⚠️ 连接异常');
    if (_heartbeatTimer) clearTimeout(_heartbeatTimer);
    _heartbeatTimer = setTimeout(checkHeartbeat, 60000);
  }
}

// v3.4: 在聊天区顶部展示林赛的主动提醒
function _showProactiveReminders(msgs) {
  let banner = document.getElementById('proactive-banner');
  if (!banner) {
    banner = document.createElement('div');
    banner.id = 'proactive-banner';
    banner.style.cssText = 'padding:8px 14px;margin:0 0 8px 0;background:var(--bg-tertiary);border-left:3px solid var(--accent-color);border-radius:6px;font-size:0.85rem;display:none;';
    const chatArea = document.getElementById('chat-messages') || document.querySelector('.chat-area');
    if (chatArea) {
      chatArea.parentElement.insertBefore(banner, chatArea);
    }
  }
  // 去重：只显示新消息
  const newMsgs = msgs.filter(m => !_lastProactiveMsgs.some(o => o.message === m.message));
  if (newMsgs.length === 0) return;
  const lines = newMsgs.map(m => {
    const icon = m.severity === 'high' ? '⚠️' : m.severity === 'medium' ? '📌' : '💡';
    return `${icon} ${escapeHtml(m.message)}`;
  }).join('<br>');
  banner.innerHTML = `<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;">
    <div>${lines}</div>
    <span onclick="document.getElementById('proactive-banner').style.display='none'" style="cursor:pointer;color:var(--text-tertiary);font-size:1.1rem;flex-shrink:0;">✕</span>
  </div>`;
  banner.style.display = 'block';
}

// v3.4: 会话首次加载时注入开场白（主动提醒 + 林赛问候）
async function injectProactiveOpening() {
  try {
    const data = await apiGet('/api/heartbeat');
    const msgs = data.proactive_messages || [];
    if (msgs.length === 0) return;
    // 在消息区插入一条林赛主动消息
    const chatArea = document.getElementById('chat-messages');
    if (!chatArea) return;
    const existing = chatArea.querySelector('.proactive-opening');
    if (existing) return; // 避免重复
    const lines = msgs.map(m => {
      const icon = m.severity === 'high' ? '⚠️' : m.severity === 'medium' ? '📌' : '💡';
      return `${icon} ${m.message}`;
    }).join('\n\n');
    const bubble = document.createElement('div');
    bubble.className = 'message assistant proactive-opening';
    bubble.style.cssText = 'opacity:0.85;margin-bottom:12px;';
    bubble.innerHTML = `<div class="message-avatar">🔬</div>
      <div class="message-bubble" style="background:var(--bg-tertiary);border:1px solid var(--border-color);">
        <p style="font-size:0.82rem;color:var(--text-secondary);margin-bottom:4px;">林赛主动提醒</p>
        ${lines.split('\n\n').map(l => `<p style="margin:4px 0;">${escapeHtml(l)}</p>`).join('')}
      </div>`;
    chatArea.insertBefore(bubble, chatArea.firstChild);
  } catch (e) { /* 静默 */ }
}

// P0-7: 补全所有模式映射
function updateModeBadge(mode) {
  const badge = document.getElementById('mode-badge');
  if (!badge) return;
  const labels = {
    'co-working': '并肩工作',
    'deep-talk': '深度对话',
    'quick-check': '快速验证',
    'autonomous': '自主',
    'review': '审阅',
  };
  badge.textContent = labels[mode] || mode;
  badge.className = 'mode-badge ' + (mode || 'co-working');
}

function updateStatus(text) {
  const el = document.getElementById('status-text');
  if (el) el.textContent = text;
}

// ============================================
// LLM 状态管理 (P0-4: 同时更新顶栏 provider-badge)
// ============================================
async function loadLLMStatus() {
  try {
    const data = await apiGet('/api/llm-status');
    const activeName = data.active_provider || data.provider || 'unknown';
    const providers = data.providers || [];
    const active = providers.find(p => p.name === activeName);
    const model = active?.model || data.model || '';

    // 更新设置面板
    const llmStatusEl = document.getElementById('llm-status');
    if (llmStatusEl) {
      llmStatusEl.innerHTML = `Provider: <strong>${escapeHtml(activeName)}</strong>${model ? ` · Model: ${escapeHtml(model)}` : ''}`;
    }

    // P0-4: 更新顶栏 provider-badge
    const badge = document.getElementById('provider-badge');
    if (badge) {
      badge.textContent = activeName;
      badge.title = `当前模型: ${model || activeName}`;
    }
  } catch (e) {
    console.error('加载LLM状态失败:', e);
    const llmStatusEl = document.getElementById('llm-status');
    if (llmStatusEl) llmStatusEl.textContent = '⚠️ LLM 未配置';
    const badge = document.getElementById('provider-badge');
    if (badge) badge.textContent = '未配置';
  }
}

async function switchProvider(provider) {
  try {
    await apiPost('/api/llm-provider', { provider });
    showToast(`已切换到 ${provider}`);
    loadLLMStatus();
  } catch (e) {
    console.error('切换失败:', e);
    showToast('切换失败', 'error');
  }
}

// ============================================
// 历史消息提示
// ============================================
function showHistoryHint(count) {
  const hint = document.getElementById('history-hint');
  if (!hint) return;
  hint.textContent = `📜 本会话已有 ${count} 条消息，向上滚动查看历史`;
  hint.style.display = 'block';
  setTimeout(() => {
    hint.style.opacity = '0';
    hint.style.transition = 'opacity 1s';
    setTimeout(() => {
      hint.style.display = 'none';
      hint.style.opacity = '1';
    }, 1000);
  }, 4000);
}

// ============================================
// 用量统计 (P0-5: 统一 API 契约，更新 usage-status)
// ============================================
async function loadUsage() {
  try {
    const data = await apiGet('/api/usage');
    const el = document.getElementById('usage-status');
    if (!el) return;

    // 兼容两种 API 返回结构
    const today = data.today || data.daily || {};
    const total = data.total || {};
    const todayTokens = today.tokens || today.total_tokens || 0;
    const todayCost = today.cost || 0;
    const todayCalls = today.calls || today.messages || 0;
    const totalTokens = total.tokens || 0;
    const totalCost = total.cost || 0;

    el.innerHTML = `
      <div style="display:flex;gap:12px;flex-wrap:wrap;">
        <span>今日: <strong>${todayCalls}</strong> 次 · <strong>${todayTokens.toLocaleString()}</strong> tokens · ¥<strong>${todayCost.toFixed(2)}</strong></span>
      </div>
      <div style="font-size:0.78rem;color:var(--text-tertiary);margin-top:4px;">
        累计: ${totalTokens.toLocaleString()} tokens · ¥${totalCost.toFixed(2)}
      </div>
    `;
  } catch (e) {
    console.error('加载用量失败:', e);
    const el = document.getElementById('usage-status');
    if (el) el.textContent = '暂无用量数据';
  }
}

// ============================================
// 学习配置 (P0-2: 对接 HTML 现有 id)
// ============================================
async function loadLearningConfig() {
  try {
    const data = await apiGet('/api/learning/config');
    const autoCb = document.getElementById('learning-auto-enabled');
    if (autoCb) autoCb.checked = data.enabled !== false;
    const strategyEl = document.getElementById('learning-strategy');
    if (strategyEl) strategyEl.value = data.strategy || 'balanced';
    const arxivCb = document.getElementById('learning-source-arxiv');
    if (arxivCb) arxivCb.checked = (data.sources || []).includes('arxiv');
    const webCb = document.getElementById('learning-source-web');
    if (webCb) webCb.checked = (data.sources || []).includes('web');
    const rawCb = document.getElementById('learning-source-raw');
    if (rawCb) rawCb.checked = (data.sources || []).includes('raw');
    const quotaEl = document.getElementById('learning-daily-quota');
    if (quotaEl) quotaEl.value = data.daily_quota || 1;
    const costEl = document.getElementById('learning-cost-limit');
    if (costEl) costEl.value = data.cost_limit || 0.5;
  } catch (e) {
    console.error('加载学习配置失败:', e);
  }
}

async function saveLearningConfig() {
  const sources = [];
  if (document.getElementById('learning-source-arxiv')?.checked) sources.push('arxiv');
  if (document.getElementById('learning-source-web')?.checked) sources.push('web');
  if (document.getElementById('learning-source-raw')?.checked) sources.push('raw');

  const config = {
    enabled: document.getElementById('learning-auto-enabled')?.checked !== false,
    strategy: document.getElementById('learning-strategy')?.value || 'balanced',
    sources,
    daily_quota: parseInt(document.getElementById('learning-daily-quota')?.value || '1'),
    cost_limit: parseFloat(document.getElementById('learning-cost-limit')?.value || '0.5'),
  };

  const statusEl = document.getElementById('learning-config-status');
  try {
    if (statusEl) statusEl.textContent = '保存中…';
    await apiPost('/api/learning/config', config);
    showToast('学习配置已保存');
    if (statusEl) statusEl.textContent = '✓ 已保存';
  } catch (e) {
    console.error('保存学习配置失败:', e);
    showToast('保存失败', 'error');
    if (statusEl) statusEl.textContent = '✗ 保存失败';
  }
}
