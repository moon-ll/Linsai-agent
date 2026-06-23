/**
 * settings.js — LLM 状态、用量统计、学习配置、心跳检测、状态栏更新、历史提示
 */

// ============================================
// 心跳检测 & 状态更新
// ============================================
async function checkHeartbeat() {
  try {
    const data = await apiGet('/api/heartbeat');
    const dot = document.getElementById('status-dot');
    if (dot) {
      dot.className = 'status-dot online';
    }
  } catch (e) {
    const dot = document.getElementById('status-dot');
    if (dot) dot.className = 'status-dot offline';
  }
}

function updateModeBadge(mode) {
  const badge = document.getElementById('mode-badge');
  if (!badge) return;
  const labels = {
    'co-working': '协作',
    'autonomous': '自主',
    'review': '审阅',
  };
  badge.textContent = labels[mode] || mode;
  badge.className = 'mode-badge ' + mode;
}

function updateStatus(text) {
  const el = document.getElementById('status-text');
  if (el) el.textContent = text;
}

// ============================================
// LLM 状态管理
// ============================================
async function loadLLMStatus() {
  try {
    const data = await apiGet('/api/llm-status');
    const providerEl = document.getElementById('llm-provider');
    const modelEl = document.getElementById('llm-model');
    const activeName = data.active_provider || data.provider || 'unknown';
    const providers = data.providers || [];
    const active = providers.find(p => p.name === activeName);
    const model = active?.model || data.model || '';
    if (providerEl) providerEl.textContent = activeName;
    if (modelEl) modelEl.textContent = model || 'default';
  } catch (e) {
    console.error('加载LLM状态失败:', e);
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
// 用量统计
// ============================================
async function loadUsage() {
  try {
    const data = await apiGet('/api/usage');
    const el = document.getElementById('usage-info');
    if (!el) return;

    const today = data.today || {};
    const total = data.total || {};

    el.innerHTML = `
      <div class="usage-section">
        <h4>今日</h4>
        <div class="usage-stats">
          <div class="usage-stat">
            <span class="usage-label">消息</span>
            <span class="usage-value">${today.messages || 0}</span>
          </div>
          <div class="usage-stat">
            <span class="usage-label">Token</span>
            <span class="usage-value">${(today.tokens || 0).toLocaleString()}</span>
          </div>
          <div class="usage-stat">
            <span class="usage-label">费用</span>
            <span class="usage-value">¥${(today.cost || 0).toFixed(2)}</span>
          </div>
        </div>
      </div>
      <div class="usage-section">
        <h4>累计</h4>
        <div class="usage-stats">
          <div class="usage-stat">
            <span class="usage-label">消息</span>
            <span class="usage-value">${total.messages || 0}</span>
          </div>
          <div class="usage-stat">
            <span class="usage-label">Token</span>
            <span class="usage-value">${(total.tokens || 0).toLocaleString()}</span>
          </div>
          <div class="usage-stat">
            <span class="usage-label">费用</span>
            <span class="usage-value">¥${(total.cost || 0).toFixed(2)}</span>
          </div>
        </div>
      </div>
    `;
  } catch (e) {
    console.error('加载用量失败:', e);
  }
}

// ============================================
// 学习配置
// ============================================
async function loadLearningConfig() {
  try {
    const data = await apiGet('/api/learning/config');
    const cb = document.getElementById('learning-enabled');
    if (cb) cb.checked = data.enabled !== false;
    const autoCb = document.getElementById('learning-auto-review');
    if (autoCb) autoCb.checked = data.auto_review !== false;
    const intervalEl = document.getElementById('learning-interval');
    if (intervalEl) intervalEl.value = data.review_interval || 7;
  } catch (e) {
    console.error('加载学习配置失败:', e);
  }
}

async function saveLearningConfig() {
  const config = {
    enabled: document.getElementById('learning-enabled')?.checked !== false,
    auto_review: document.getElementById('learning-auto-review')?.checked !== false,
    review_interval: parseInt(document.getElementById('learning-interval')?.value || '7'),
  };

  try {
    await apiPost('/api/learning/config', config);
    showToast('学习配置已保存');
  } catch (e) {
    console.error('保存学习配置失败:', e);
    showToast('保存失败', 'error');
  }
}
