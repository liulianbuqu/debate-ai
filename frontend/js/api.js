/* ========================================
   API 通信层 - 封装所有后端接口调用
   ======================================== */

const API_BASE = '';

const api = {
    /**
     * 通用请求方法
     */
    async request(method, path, data = null) {
        const url = `${API_BASE}${path}`;
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
        };
        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }
        try {
            const res = await fetch(url, options);
            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || `请求失败 (${res.status})`);
            }
            return await res.json();
        } catch (err) {
            if (err.message.includes('Failed to fetch')) {
                throw new Error('无法连接到后端服务，请确保后端已启动');
            }
            throw err;
        }
    },

    // ========== 素材管理 ==========
    getMaterials(typeFilter = '') {
        const params = typeFilter ? `?type_filter=${encodeURIComponent(typeFilter)}` : '';
        return this.request('GET', `/api/materials/${params}`);
    },

    getMaterial(id) {
        return this.request('GET', `/api/materials/${id}`);
    },

    createMaterial(data) {
        return this.request('POST', '/api/materials/', data);
    },

    updateMaterial(id, data) {
        return this.request('PUT', `/api/materials/${id}`, data);
    },

    deleteMaterial(id) {
        return this.request('DELETE', `/api/materials/${id}`);
    },

    // ========== 稿件生成 ==========
    generateScript(data) {
        return this.request('POST', '/api/generation/', data);
    },

    getGenerationHistory(limit = 20) {
        return this.request('GET', `/api/generation/history?limit=${limit}`);
    },

    // ========== 辩手画像 ==========
    getProfile() {
        return this.request('GET', '/api/profile/');
    },

    updateProfile(data) {
        return this.request('PUT', '/api/profile/', data);
    },

    updateUnderstanding(data) {
        return this.request('POST', '/api/profile/understanding', data);
    },

    // ========== 反馈 ==========
    submitFeedback(data) {
        return this.request('POST', '/api/feedback/', data);
    },

    // ========== 设置 ==========
    testApiKey(data) {
        return this.request('POST', '/api/settings/test-key', data);
    },

    // ========== 健康检查 ==========
    healthCheck() {
        return this.request('GET', '/api/health');
    }
};
