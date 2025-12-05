// 主JavaScript文件
// API基础URL
const API_BASE = '/api';

// 工具函数：显示Toast通知
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    const toastId = 'toast-' + Date.now();

    const bgColor = {
        'success': 'bg-success',
        'error': 'bg-danger',
        'warning': 'bg-warning',
        'info': 'bg-info'
    }[type] || 'bg-info';

    const icon = {
        'success': 'bi-check-circle',
        'error': 'bi-exclamation-circle',
        'warning': 'bi-exclamation-triangle',
        'info': 'bi-info-circle'
    }[type] || 'bi-info-circle';

    const toastHTML = `
        <div id="${toastId}" class="toast align-items-center text-white ${bgColor} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi ${icon}"></i> ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;

    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { autohide: true, delay: 3000 });
    toast.show();

    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

// 工具函数：格式化日期时间
function formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

// 工具函数：格式化持续时间
function formatDuration(seconds) {
    if (!seconds) return 'N/A';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    if (hours > 0) {
        return `${hours}时${minutes}分${secs}秒`;
    } else if (minutes > 0) {
        return `${minutes}分${secs}秒`;
    } else {
        return `${secs}秒`;
    }
}

// 工具函数：获取优先级标签
function getPriorityBadge(priority) {
    const badges = {
        'P0': '<span class="badge bg-danger" title="核心产品 - 整车/电动车">整车</span>',
        'P1': '<span class="badge bg-warning" title="电池/充电器/电机">重要配件</span>',
        'P2': '<span class="badge bg-info" title="其他配件">普通配件</span>'
    };
    return badges[priority] || '<span class="badge bg-secondary">未知</span>';
}

// 工具函数：获取状态徽章
function getStatusBadge(status) {
    const badges = {
        'passed': '<span class="badge bg-success">通过</span>',
        'failed': '<span class="badge bg-danger">失败</span>',
        'skipped': '<span class="badge bg-warning">跳过</span>',
        'running': '<span class="badge bg-primary">运行中</span>',
        'pending': '<span class="badge bg-secondary">待处理</span>'
    };
    return badges[status] || '<span class="badge bg-secondary">未知</span>';
}

// 工具函数：轮询任务状态
async function pollTaskStatus(taskId, onUpdate, onComplete) {
    const maxAttempts = 120; // 最多轮询10分钟（每5秒一次）
    let attempts = 0;

    const poll = async () => {
        try {
            const response = await fetch(`${API_BASE}/tests/status/${taskId}`);
            const data = await response.json();

            if (onUpdate) {
                onUpdate(data);
            }

            if (data.status === 'completed' || data.status === 'failed' || data.status === 'timeout' || data.status === 'error') {
                if (onComplete) {
                    onComplete(data);
                }
                return;
            }

            attempts++;
            if (attempts < maxAttempts) {
                setTimeout(poll, 5000); // 每5秒轮询一次
            } else {
                if (onComplete) {
                    onComplete({ status: 'timeout', error: '任务超时' });
                }
            }
        } catch (error) {
            console.error('轮询任务状态失败:', error);
            if (onComplete) {
                onComplete({ status: 'error', error: error.message });
            }
        }
    };

    poll();
}

// 工具函数：检查系统健康状态
async function checkSystemHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();

        const healthStatus = document.getElementById('health-status');
        if (healthStatus) {
            if (data.status === 'ok') {
                healthStatus.innerHTML = '<i class="bi bi-circle-fill text-success"></i> 系统正常';
            } else {
                healthStatus.innerHTML = '<i class="bi bi-circle-fill text-danger"></i> 系统异常';
            }
        }
    } catch (error) {
        console.error('健康检查失败:', error);
        const healthStatus = document.getElementById('health-status');
        if (healthStatus) {
            healthStatus.innerHTML = '<i class="bi bi-circle-fill text-warning"></i> 连接失败';
        }
    }
}

// 工具函数：显示加载动画
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="spinner-container">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">加载中...</span>
                </div>
            </div>
        `;
    }
}

// 工具函数：显示空状态
function showEmptyState(elementId, message, icon = 'inbox') {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="empty-state">
                <i class="bi bi-${icon}"></i>
                <p>${message}</p>
            </div>
        `;
    }
}

// 工具函数：显示错误信息
function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <i class="bi bi-exclamation-triangle"></i>
                ${message}
            </div>
        `;
    }
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', () => {
    // 检查系统健康状态
    checkSystemHealth();

    // 每30秒检查一次健康状态
    setInterval(checkSystemHealth, 30000);

    // 初始化所有tooltip
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(el => new bootstrap.Tooltip(el));

    // 初始化所有popover
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(el => new bootstrap.Popover(el));
});

// 导出工具函数供其他页面使用
window.utils = {
    showToast,
    formatDateTime,
    formatDuration,
    getPriorityBadge,
    getStatusBadge,
    pollTaskStatus,
    checkSystemHealth,
    showLoading,
    showEmptyState,
    showError
};
