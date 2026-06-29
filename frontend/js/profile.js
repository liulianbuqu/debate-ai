/* ========================================
   辩手画像模块 — 纯本地 API Key 版
   ======================================== */

let understandingEditOpen = false;

async function loadProfile() {
    try {
        const profile = await api.getProfile();
        renderUnderstanding(profile.debate_understanding);
        renderStyleProfile(profile.style_profile);
        renderProfileStatus(profile);
        return profile;
    } catch (err) { return null; }
}

function renderUnderstanding(understanding) {
    const container = document.getElementById('understandingDisplay');
    if (!understanding || Object.values(understanding).every(v => !v)) {
        container.innerHTML = '<div class="empty-state" style="padding:16px 12px;font-size:13px">写下你的辩论理念<br>让 AI 不只是模仿「形」，更理解「神」<br><button class="btn btn-secondary" style="padding:5px 12px;font-size:12px;margin-top:8px" onclick="toggleUnderstandingEdit()">去填写</button></div>';
        return;
    }
    const labels = { '辩论观': '辩论观', '胜负观': '胜负观', '对辩题的理解方法论': '方法论', '对质询的理解': '质询观', '对陈词的理解': '陈词观', '对自由辩的理解': '自由辩观' };
    let html = '';
    for (const [key, value] of Object.entries(understanding)) {
        if (value && value.trim()) {
            html += `<div class="understanding-item">
                <span class="u-key">${labels[key] || key}</span>
                <div class="u-value">${escapeHtml(value.slice(0, 120))}${value.length > 120 ? '…' : ''}</div>
            </div>`;
        }
    }
    container.innerHTML = html || '<div class="empty-state" style="padding:16px 12px;font-size:13px">尚未填写</div>';
}

async function toggleUnderstandingEdit() {
    const display = document.getElementById('understandingDisplay');
    const editor = document.getElementById('understandingEditor');
    if (!understandingEditOpen) {
        try {
            const profile = await api.getProfile();
            const u = profile.debate_understanding || {};
            ['辩论观', '胜负观', '对辩题的理解方法论', '对质询的理解', '对陈词的理解', '对自由辩的理解'].forEach(f => {
                const el = document.getElementById(`u_${f}`);
                if (el) el.value = u[f] || '';
            });
        } catch (e) {}
        display.style.display = 'none';
        editor.style.display = 'block';
        understandingEditOpen = true;
    } else {
        display.style.display = 'block';
        editor.style.display = 'none';
        understandingEditOpen = false;
    }
}

async function saveInlineUnderstanding() {
    const fields = ['辩论观', '胜负观', '对辩题的理解方法论', '对质询的理解', '对陈词的理解', '对自由辩的理解'];
    const data = {};
    fields.forEach(f => {
        const el = document.getElementById(`u_${f}`);
        if (el && el.value.trim()) data[f] = el.value.trim();
    });
    try {
        await api.updateUnderstanding(data);
        toggleUnderstandingEdit();
        showToast('辩论理解已更新', 'success');
        loadProfile();
    } catch (err) { showToast(err.message, 'error'); }
}

function renderStyleProfile(styleProfile) {
    const container = document.getElementById('styleProfile');
    const count = styleProfile['累计分析'] || 0;
    if (count === 0) {
        container.innerHTML = '<div class="empty-state" style="padding:16px 12px;font-size:13px">上传素材后自动建立风格画像</div>';
        return;
    }

    // 素材类型分布
    const typeDist = styleProfile['素材类型分布'] || {};
    const typeStr = Object.entries(typeDist)
        .map(([t, n]) => `${t} ${n}篇`)
        .join(' · ');

    // 按素材类型聚合的分析
    const perType = styleProfile['素材分析'] || {};

    let html = '';

    // 顶部概览
    html += `<div style="font-size:12px;color:var(--text-tertiary);margin-bottom:12px;line-height:1.6">已分析 ${count} 篇素材：${typeStr}</div>`;

    // 逐类型展示
    const typeOrder = ['立论', '质询', '陈词', '结辩', '自由辩'];
    for (const t of typeOrder) {
        if (!perType[t]) continue;
        const a = perType[t];
        // 类型标题
        html += `<div style="margin-bottom:12px;padding:10px;background:var(--surface);border-radius:var(--radius-sm);border:1px solid var(--border-light)">`;
        html += `<div style="font-size:12px;font-weight:600;color:var(--accent);margin-bottom:6px;letter-spacing:0.03em">${t}稿</div>`;

        // 整体评价
        if (a['整体评价']) {
            html += `<div style="font-size:13px;line-height:1.7;color:var(--text-secondary);margin-bottom:6px">${escapeHtml(a['整体评价'])}</div>`;
        }

        // 各维度
        const dimLabels = { '语言风格': '语言风格', '论证方式': '论证方式', '结构特点': '结构特点', '修辞手法': '修辞手法' };
        for (const [dk, dl] of Object.entries(dimLabels)) {
            if (a[dk]) {
                html += `<div style="font-size:12px;line-height:1.6;margin-bottom:2px">
                    <strong style="color:var(--text)">${dl}</strong>
                    <span style="color:var(--text-secondary)">${escapeHtml(a[dk])}</span>
                </div>`;
            }
        }
        html += `</div>`;
    }

    container.innerHTML = html;
}

function renderProfileStatus(profile) {
    const badge = document.getElementById('profileStatus');
    const count = profile.update_count || 0;
    if (count === 0) { badge.textContent = '待完善'; badge.style.background = '#fef3c7'; badge.style.color = '#92400e'; }
    else if (count < 5) { badge.textContent = `成长中 (${count})`; badge.style.background = '#dbeafe'; badge.style.color = '#1e40af'; }
    else { badge.textContent = `已成熟 (${count})`; badge.style.background = '#dcfce7'; badge.style.color = '#166534'; }
    document.getElementById('statUpdates').textContent = count;
}

/* ========== 设置 / API Key ========== */

function showSettings() {
    document.getElementById('apiKey').value = localStorage.getItem('deepseek_api_key') || '';
    document.getElementById('apiUrl').value = localStorage.getItem('deepseek_api_url') || '';
    document.getElementById('modelSelect').value = localStorage.getItem('deepseek_model') || 'deepseek-chat';
    document.getElementById('settingsModal').classList.add('active');
}

async function saveSettings() {
    const apiKey = document.getElementById('apiKey').value.trim();
    const apiUrl = document.getElementById('apiUrl').value.trim();
    const model = document.getElementById('modelSelect').value;

    if (!apiKey) { showToast('请输入 API Key', 'error'); return; }

    // 保存到本地
    localStorage.setItem('deepseek_api_key', apiKey);
    if (apiUrl) localStorage.setItem('deepseek_api_url', apiUrl);
    localStorage.setItem('deepseek_model', model);

    // 测试 API Key
    const testBtn = document.querySelector('#settingsModal .btn-primary');
    const origText = testBtn.textContent;
    testBtn.textContent = '测试中…';
    testBtn.disabled = true;

    try {
        const result = await api.testApiKey({ api_key: apiKey, api_url: apiUrl || undefined });
        if (result.success) {
            closeModal('settingsModal');
            showToast('API Key 可用 ✓ 设置已保存', 'success');
        } else {
            showToast('API Key 无效: ' + result.message, 'error');
        }
    } catch (err) {
        showToast('测试失败: ' + err.message, 'error');
    } finally {
        testBtn.textContent = origText;
        testBtn.disabled = false;
    }
}
