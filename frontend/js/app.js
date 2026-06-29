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

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', initApp);
