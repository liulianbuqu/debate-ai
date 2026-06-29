/* ========================================
   素材管理模块 — 异步分析状态版
   ======================================== */

let currentFilter = '';
let allMaterials = [];
let viewingMaterialId = null;

async function loadMaterials() {
    try {
        allMaterials = await api.getMaterials(currentFilter);
        renderMaterialList();
        updateStats();
    } catch (err) { showToast(err.message, 'error'); }
}

function renderMaterialList() {
    const container = document.getElementById('materialList');
    if (!allMaterials.length) {
        container.innerHTML = '<div class="empty-state">暂无素材<br>点击「+ 新增」上传你的稿件</div>';
        return;
    }
    container.innerHTML = allMaterials.map(m => {
        const ctx = m.context || {};
        const topic = ctx.debate_topic || '';
        const pos = ctx.position || '';
        const isAnalyzing = m.analysis_status === 'pending';
        const isFailed = m.analysis_status === 'failed';
        const isAiDone = m.analysis_status === 'ai_done';
        return `<div class="material-item" onclick="viewMaterial('${m.id}')">
            <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px">
                <span class="mat-type">${m.type}</span>
                ${pos ? `<span style="font-size:11px;color:var(--text-tertiary)">${pos}</span>` : ''}
                ${isAiDone ? `<span style="font-size:10px;color:var(--accent);background:var(--accent-subtle);padding:1px 6px;border-radius:3px">AI 增强</span>` : ''}
            </div>
            ${topic ? `<div class="mat-title">${escapeHtml(topic)}</div>` : `<div class="mat-title">${escapeHtml(m.content.slice(0, 40))}</div>`}
            <div class="mat-preview">${escapeHtml(m.content.slice(0, 80))}</div>
            <div class="mat-date">${formatDate(m.created_at)}</div>
        </div>`;
    }).join('');
}

function filterMaterials(el, type) {
    document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
    el.classList.add('active');
    currentFilter = type;
    loadMaterials();
}

function showAddMaterial(type) {
    document.getElementById('addMaterialModal').classList.add('active');
    document.getElementById('newMaterialContent').value = '';
    document.getElementById('newMaterialTopic').value = '';
    document.getElementById('newMaterialRound').value = '';
    document.getElementById('newMaterialPosition').value = '';
    document.getElementById('newMaterialType').value = type || '立论';
}

async function saveMaterial() {
    const type = document.getElementById('newMaterialType').value;
    const topic = document.getElementById('newMaterialTopic').value.trim();
    const position = document.getElementById('newMaterialPosition').value;
    const round = document.getElementById('newMaterialRound').value.trim();
    const content = document.getElementById('newMaterialContent').value.trim();

    if (!content) { showToast('请输入稿件全文', 'error'); return; }

    const title = topic || `${type}稿`;
    const context = {};
    if (topic) context.debate_topic = topic;
    if (position) context.position = position;
    if (round) context.round = round;

    const btn = document.getElementById('saveMaterialBtn');
    btn.disabled = true; btn.textContent = '保存中…';

    try {
        // 立即返回，分析在后台
        const result = await api.createMaterial({ type, title, content, tags: [], context });
        closeModal('addMaterialModal');
        showToast('素材已保存（AI 正在分析风格…）', 'success');

        // 立即刷新列表（分析已同步完成）
        loadMaterials();
        loadProfile();
    } catch (err) {
        showToast(err.message, 'error');
    } finally {
        btn.disabled = false; btn.textContent = '保存素材';
    }
}

/** 外部调用：快速保存生成的内容为素材 */
async function quickSaveMaterial(type, content, topic, position) {
    const context = {};
    if (topic) context.debate_topic = topic;
    if (position) context.position = position;
    const title = topic || `${type}稿`;
    try {
        await api.createMaterial({ type, title, content, tags: [], context });
        loadMaterials(); loadProfile();
        return true;
    } catch (err) { return false; }
}

async function viewMaterial(id) {
    viewingMaterialId = id;
    try {
        const mat = await api.getMaterial(id);
        const ctx = mat.context || {};
        document.getElementById('viewMaterialTitle').textContent =
            `${mat.type}稿${ctx.debate_topic ? ' · ' + ctx.debate_topic : ''}`;
        document.getElementById('viewMaterialMeta').innerHTML =
            `<strong>${mat.type}</strong>` +
            (ctx.position ? ' · ' + ctx.position : '') +
            (ctx.debate_topic ? ' · 「' + ctx.debate_topic + '」' : '') +
            (ctx.round ? ' · ' + ctx.round : '') +
            `<br><span style="color:var(--text-tertiary)">${formatDate(mat.created_at)}</span>` +
            (mat.analysis_status === 'ai_done' ? '<br><span style="color:var(--accent)">✓ 已完成 AI 增强分析</span>' : '');

        // 显示重新分析按钮
        document.getElementById('reanalyzeBtn').style.display = 'inline-flex';

        document.getElementById('viewMaterialContent').textContent = mat.content;

        const analysisDiv = document.getElementById('analysisContent');
        const features = mat.extracted_features;

        if (features && features['整体评价']) {
            const dimLabels = { '语言风格': '语言风格', '论证方式': '论证方式', '结构特点': '结构特点', '修辞手法': '修辞手法', '篇幅说明': '篇幅说明' };
            const sections = ['整体评价', '语言风格', '论证方式', '结构特点', '修辞手法', '篇幅说明'];
            analysisDiv.innerHTML = sections
                .filter(k => features[k])
                .map(k => {
                    const label = k === '整体评价' ? '' : dimLabels[k];
                    const text = features[k];
                    if (k === '整体评价') return `<div style="font-size:14px;line-height:1.8;color:var(--text);margin-bottom:16px">${escapeHtml(text)}</div>`;
                    return `<div style="margin-bottom:10px;font-size:13px;line-height:1.7">
                        <strong style="color:var(--accent);display:block;margin-bottom:2px;font-size:12px">${label}</strong>
                        <span style="color:var(--text-secondary)">${escapeHtml(text)}</span>
                    </div>`;
                }).join('');
        } else {
            analysisDiv.innerHTML = '<div class="empty-state" style="padding:12px">暂无可用的风格分析数据</div>';
        }
        document.getElementById('viewMaterialModal').classList.add('active');
    } catch (err) { showToast(err.message, 'error'); }
}

async function reanalyzeMaterial() {
    if (!viewingMaterialId) return;
    try {
        const result = await api.request('POST', `/api/materials/${viewingMaterialId}/reanalyze`);
        showToast(result.message || '分析已完成', 'success');
        closeModal('viewMaterialModal');
        // 立即刷新素材列表，看到最新状态
        await loadMaterials();
    } catch (err) { showToast(err.message, 'error'); }
}

async function deleteCurrentMaterial() {
    if (!viewingMaterialId) return;
    if (!confirm('确定删除此素材？')) return;
    try {
        await api.deleteMaterial(viewingMaterialId);
        closeModal('viewMaterialModal');
        showToast('素材已删除', 'success');
        loadMaterials(); loadProfile();
    } catch (err) { showToast(err.message, 'error'); }
}

async function updateStats() {
    try {
        const materials = await api.getMaterials();
        document.getElementById('statMaterials').textContent = materials.length || 0;
        const history = await api.getGenerationHistory(999);
        document.getElementById('statGenerations').textContent = history.length || 0;
    } catch (e) {}
}
