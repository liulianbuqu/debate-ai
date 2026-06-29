/* ========================================
   应用主入口 - 初始化 & 工具函数
   ======================================== */

/**
 * 应用初始化
 */
async function initApp() {
    // 恢复主题设置
    initTheme();

    // 尝试连接后端
    try {
        const health = await api.healthCheck();
        console.log('后端连接成功:', health.message);
    } catch (err) {
        console.warn('后端连接失败:', err.message);
        showToast('无法连接到后端服务，请确认后端已启动', 'error');
    }

    // 加载数据
    await Promise.all([
        loadMaterials(),
        loadProfile(),
        loadReferenceOptions()
    ]);
}

/**
 * 关闭模态框
 */
function closeModal(id) {
    document.getElementById(id).classList.remove('active');
}

// 点击遮罩层关闭模态框
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-overlay')) {
        e.target.classList.remove('active');
    }
});

/**
 * 显示 Toast 消息
 */
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/**
 * HTML 转义
 */
function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

/**
 * 格式化日期
 */
function formatDate(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;
}

// ========== 暗色模式 ==========

function initTheme() {
    const saved = localStorage.getItem('theme');
    if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.documentElement.setAttribute('data-theme', 'dark');
        document.getElementById('themeToggle').textContent = '☀️';
    } else {
        document.documentElement.setAttribute('data-theme', 'light');
        document.getElementById('themeToggle').textContent = '🌙';
    }
}

function toggleTheme() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    if (isDark) {
        document.documentElement.setAttribute('data-theme', 'light');
        localStorage.setItem('theme', 'light');
        document.getElementById('themeToggle').textContent = '🌙';
    } else {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
        document.getElementById('themeToggle').textContent = '☀️';
    }
}

// ========== 数据导出/导入 ==========

async function exportData() {
    try {
        const data = await api.request('GET', '/api/data/export');
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const date = new Date().toISOString().slice(0, 10);
        a.download = `debate-ai-backup-${date}.json`;
        a.click();
        URL.revokeObjectURL(url);
        showToast('数据导出成功 ✓', 'success');
    } catch (err) {
        showToast('导出失败: ' + err.message, 'error');
    }
}

async function importData(event) {
    const file = event.target.files[0];
    if (!file) return;

    try {
        const text = await file.text();
        const data = JSON.parse(text);

        if (!data.materials && !data.profiles && !data.generations) {
            showToast('无效的备份文件', 'error');
            return;
        }

        if (!confirm('导入将合并数据到当前数据库。确定继续？')) {
            event.target.value = '';
            return;
        }

        const result = await api.request('POST', '/api/data/import', data);
        showToast(result.message, 'success');
        // 刷新页面数据
        await Promise.all([
            loadMaterials(),
            loadProfile(),
            loadReferenceOptions()
        ]);
    } catch (err) {
        showToast('导入失败: ' + err.message, 'error');
    }
    event.target.value = '';
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', initApp);
