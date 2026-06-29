/* ========================================
   稿件生成模块 — 标签式素材选择
   ======================================== */

let currentGenerationId = null;
let currentGeneratedContent = '';
let currentGenType = '';
let currentGenTopic = '';
let currentGenPosition = '';

let allRefMaterials = [];
let refFilterType = '';
let refSearchQuery = '';
let selectedRefIds = new Set();

/* ========== 参考素材选择器 ========== */

async function loadReferenceOptions() {
    try {
        allRefMaterials = await api.getMaterials();
        refFilterType = document.getElementById('scriptType').value;
        renderRefSelector();
    } catch (err) { console.error(err); }
}

/** 当稿件类型改变时，自动切换筛选 */
document.addEventListener('DOMContentLoaded', () => {
    const typeSelect = document.getElementById('scriptType');
    if (typeSelect) {
        typeSelect.addEventListener('change', () => {
            refFilterType = typeSelect.value;
            renderRefSelector();
        });
    }
});

function renderRefSelector() {
    const list = document.getElementById('refList');
    const chips = document.getElementById('refChips');

    // 渲染已选标签
    const selectedItems = allRefMaterials.filter(m => selectedRefIds.has(m.id));
    chips.innerHTML = selectedItems.map(m => {
        const ctx = m.context || {};
        const label = ctx.debate_topic || m.title;
        return `<span class="ref-chip" data-id="${m.id}">
            <span class="ref-chip-type">${m.type}</span>
            <span>${escapeHtml(label)}</span>
            <span class="ref-chip-remove" onclick="removeRefMaterial('${m.id}')">×</span>
        </span>`;
    }).join('');

    // 如果没有选中的，显示提示
    if (!selectedItems.length) {
        chips.innerHTML = '<span class="ref-chip-hint">自动匹配同类素材（点选下方素材可手动指定）</span>';
    }

    // 过滤素材列表
    let filtered = allRefMaterials;
    // 按类型过滤
    if (refFilterType) {
        filtered = filtered.filter(m => m.type === refFilterType);
    }
    // 按搜索词过滤
    if (refSearchQuery) {
        const q = refSearchQuery.toLowerCase();
        filtered = filtered.filter(m => {
            const ctx = m.context || {};
            const topic = (ctx.debate_topic || '').toLowerCase();
            const title = m.title.toLowerCase();
            const content = m.content.slice(0, 100).toLowerCase();
            return topic.includes(q) || title.includes(q) || content.includes(q);
        });
    }
    // 最多显示 30 条
    filtered = filtered.slice(0, 30);

    if (!filtered.length) {
        list.innerHTML = '<div class="ref-empty">没有匹配的素材</div>';
        return;
    }

    list.innerHTML = filtered.map(m => {
        const ctx = m.context || {};
        const topic = ctx.debate_topic || '';
        const pos = ctx.position || '';
        const selected = selectedRefIds.has(m.id);
        return `<div class="ref-item ${selected ? 'selected' : ''}" onclick="toggleRefMaterial('${m.id}')">
            <div class="ref-item-check ${selected ? 'checked' : ''}">${selected ? '✓' : ''}</div>
            <span class="mat-type">${m.type}</span>
            ${pos ? `<span class="ref-item-pos">${pos}</span>` : ''}
            <span class="ref-item-title">${escapeHtml(topic || m.title)}</span>
        </div>`;
    }).join('');
}

function toggleRefMaterial(id) {
    if (selectedRefIds.has(id)) {
        selectedRefIds.delete(id);
    } else {
        selectedRefIds.add(id);
    }
    document.getElementById('referenceIds').value = Array.from(selectedRefIds).join(',');
    renderRefSelector();
}

function removeRefMaterial(id) {
    selectedRefIds.delete(id);
    document.getElementById('referenceIds').value = Array.from(selectedRefIds).join(',');
    renderRefSelector();
}

/** 搜索实时过滤 */
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('refSearch');
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            refSearchQuery = searchInput.value;
            renderRefSelector();
        });
    }
});

/* ========== 生成稿件 ========== */

async function generateScript() {
    const type = document.getElementById('scriptType').value;
    const topic = document.getElementById('topic').value.trim();
    const position = document.getElementById('position').value;
    const additional = document.getElementById('additionalInstructions').value.trim();

    if (!topic) { showToast('请输入辩题', 'error'); return; }

    const apiKey = localStorage.getItem('deepseek_api_key');
    if (!apiKey) { showToast('请先在设置中配置 API Key', 'error'); return; }

    const referenceIds = Array.from(selectedRefIds);
    currentGenType = type; currentGenTopic = topic; currentGenPosition = position;

    const resultDiv = document.getElementById('generationResult');
    const contentDiv = document.getElementById('resultContent');
    resultDiv.style.display = 'block';
    contentDiv.innerHTML = '<div class="loading"><div class="spinner"></div><span>AI 正在思考…</span></div>';

    const btn = document.getElementById('generateBtn');
    btn.textContent = '生成中…'; btn.disabled = true;

    try {
        const result = await api.generateScript({
            type, topic, position,
            reference_ids: referenceIds,
            additional_instructions: additional,
            api_key: apiKey
        });

        currentGenerationId = result.id;
        currentGeneratedContent = result.content;

        contentDiv.textContent = result.content;
        document.getElementById('resultMeta').innerHTML =
            `<strong>${result.type}稿</strong> · ${result.request_summary.topic} · ${result.request_summary.position}`;

        document.querySelectorAll('.star').forEach(s => s.classList.remove('active'));
        document.getElementById('feedbackComments').value = '';
        document.getElementById('wasUsed').checked = false;

        showToast('稿件生成完成', 'success');
    } catch (err) {
        contentDiv.innerHTML = `<div style="padding:20px;color:var(--text-secondary)">生成失败：${escapeHtml(err.message)}</div>`;
    } finally {
        btn.textContent = '生成稿件'; btn.disabled = false;
    }
}

async function saveResultAsMaterial() {
    if (!currentGeneratedContent) { showToast('没有可保存的内容', 'error'); return; }
    const ok = await quickSaveMaterial(currentGenType, currentGeneratedContent, currentGenTopic, currentGenPosition);
    if (ok) showToast('已保存到素材库', 'success');
}

function regenerateScript() { generateScript(); }

function copyResult() {
    if (!currentGeneratedContent) return;
    navigator.clipboard.writeText(currentGeneratedContent).then(
        () => showToast('已复制到剪贴板', 'success'),
        () => { const ta = document.createElement('textarea'); ta.value = currentGeneratedContent; document.body.appendChild(ta); ta.select(); document.execCommand('copy'); document.body.removeChild(ta); showToast('已复制到剪贴板', 'success'); }
    );
}

function clearResult() {
    document.getElementById('generationResult').style.display = 'none';
    currentGeneratedContent = ''; currentGenerationId = null;
}

async function submitFeedback() {
    if (!currentGenerationId) { showToast('没有可评价的稿件', 'error'); return; }
    const ratingEl = document.querySelector('.star.active');
    if (!ratingEl) { showToast('请先点击星星评分', 'error'); return; }
    try {
        await api.submitFeedback({
            generation_id: currentGenerationId,
            rating: parseInt(ratingEl.dataset.value),
            comments: document.getElementById('feedbackComments').value.trim(),
            was_used: document.getElementById('wasUsed').checked,
            modified_content: ''
        });
        showToast('反馈已提交', 'success');
    } catch (err) { showToast(err.message, 'error'); }
}

/* 星星评分 */
document.addEventListener('DOMContentLoaded', () => {
    const rating = document.getElementById('starRating');
    if (rating) {
        rating.addEventListener('click', (e) => {
            const star = e.target.closest('.star');
            if (!star) return;
            const value = parseInt(star.dataset.value);
            document.querySelectorAll('.star').forEach(s =>
                s.classList.toggle('active', parseInt(s.dataset.value) <= value)
            );
        });
    }
});
