#!/usr/bin/env python3
"""
Fiido 测试工作台 Web 应用

提供简单易用的 UI 界面，非技术人员可以通过浏览器使用测试系统。
"""

from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
import threading

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
CORS(app)  # 允许跨域访问

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / "reports"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# 当前运行的任务
running_tasks = {}


def run_command(command, task_id=None):
    """
    执行命令并返回结果（支持实时输出捕获）

    Args:
        command: 要执行的命令列表
        task_id: 任务 ID（用于后台任务）

    Returns:
        命令执行结果
    """
    try:
        # 启动进程，实时捕获输出
        process = subprocess.Popen(
            command,
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        stdout_lines = []
        stderr_lines = []

        # 如果有task_id，初始化日志存储
        if task_id:
            running_tasks[task_id]['logs'] = []
            running_tasks[task_id]['progress'] = {
                'current': 0,
                'total': 0,
                'message': '正在初始化...'
            }

        # 实时读取输出
        import select
        import time

        timeout = 600  # 10分钟超时
        start_time = time.time()

        while True:
            # 检查超时
            if time.time() - start_time > timeout:
                process.kill()
                raise subprocess.TimeoutExpired(command, timeout)

            # 检查进程是否结束
            if process.poll() is not None:
                # 读取剩余输出
                remaining_stdout = process.stdout.read()
                remaining_stderr = process.stderr.read()
                if remaining_stdout:
                    stdout_lines.append(remaining_stdout)
                    if task_id:
                        # 🔧 修复: 解析剩余日志中的每一行
                        for remaining_line in remaining_stdout.splitlines():
                            running_tasks[task_id]['logs'].append(remaining_line)
                            parse_progress_line(remaining_line, task_id)
                if remaining_stderr:
                    stderr_lines.append(remaining_stderr)
                break

            # 读取stdout
            line = process.stdout.readline()
            if line:
                stdout_lines.append(line)
                if task_id:
                    running_tasks[task_id]['logs'].append(line.rstrip())
                    # 解析进度信息
                    parse_progress_line(line, task_id)

            time.sleep(0.1)

        returncode = process.returncode
        stdout = ''.join(stdout_lines)
        stderr = ''.join(stderr_lines)

        output = {
            'success': returncode == 0,
            'stdout': stdout,
            'stderr': stderr,
            'returncode': returncode
        }

        if task_id:
            running_tasks[task_id].update({
                'status': 'completed' if returncode == 0 else 'failed',
                'result': output,
                'completed_at': datetime.now().isoformat()
            })

        return output

    except subprocess.TimeoutExpired:
        error = {'success': False, 'error': '命令执行超时'}
        if task_id:
            running_tasks[task_id].update({
                'status': 'timeout',
                'result': error,
                'completed_at': datetime.now().isoformat()
            })
        return error
    except Exception as e:
        error = {'success': False, 'error': str(e)}
        if task_id:
            running_tasks[task_id].update({
                'status': 'error',
                'result': error,
                'completed_at': datetime.now().isoformat()
            })
        return error


def parse_progress_line(line, task_id):
    """解析日志行，提取进度信息

    Args:
        line: 日志行
        task_id: 任务ID
    """
    import re

    # 解析测试步骤: [步骤 1] 页面访问
    match = re.search(r'\[步骤\s+(\d+)\]\s+(.+)', line)
    if match:
        step_number = int(match.group(1))
        step_name = match.group(2).strip()

        # 记录测试步骤
        if 'test_steps' not in running_tasks[task_id]:
            running_tasks[task_id]['test_steps'] = []

        # 检查是否已存在该步骤
        existing_step = None
        for step in running_tasks[task_id]['test_steps']:
            if step['number'] == step_number:
                existing_step = step
                break

        if not existing_step:
            running_tasks[task_id]['test_steps'].append({
                'number': step_number,
                'name': step_name,
                'status': 'running'
            })
        return

    # 解析步骤说明
    match = re.search(r'说明:\s*(.+)', line)
    if match and 'test_steps' in running_tasks[task_id]:
        description = match.group(1).strip()
        steps = running_tasks[task_id]['test_steps']
        if steps:
            steps[-1]['description'] = description
        return

    # 解析步骤结果: ✓ 结果: xxx
    match = re.search(r'[✓✗⊘]\s*结果:\s*(.+?)(?:\s*\(耗时:\s*([\d.]+)s\))?$', line)
    if match and 'test_steps' in running_tasks[task_id]:
        result = match.group(1).strip()
        duration = match.group(2)

        steps = running_tasks[task_id]['test_steps']
        if steps:
            step = steps[-1]
            step['result'] = result
            if duration:
                step['duration'] = float(duration)

            # 根据符号判断状态
            if '✓' in line:
                step['status'] = 'passed'
            elif '✗' in line:
                step['status'] = 'failed'
            elif '⊘' in line:
                step['status'] = 'skipped'
        return

    # 解析错误信息
    match = re.search(r'错误:\s*(.+)', line)
    if match and 'test_steps' in running_tasks[task_id]:
        error = match.group(1).strip()
        steps = running_tasks[task_id]['test_steps']
        if steps:
            steps[-1]['error'] = error
        return

    # 🔧 新增: 解析问题详情 (📋 问题详情 后面的各行)
    # 解析场景
    match = re.search(r'场景:\s*(.+)', line)
    if match and 'test_steps' in running_tasks[task_id]:
        scenario = match.group(1).strip()
        steps = running_tasks[task_id]['test_steps']
        if steps:
            if 'issue_details' not in steps[-1]:
                steps[-1]['issue_details'] = {}
            steps[-1]['issue_details']['scenario'] = scenario
        return

    # 解析操作
    match = re.search(r'操作:\s*(.+)', line)
    if match and 'test_steps' in running_tasks[task_id]:
        operation = match.group(1).strip()
        steps = running_tasks[task_id]['test_steps']
        if steps:
            if 'issue_details' not in steps[-1]:
                steps[-1]['issue_details'] = {}
            steps[-1]['issue_details']['operation'] = operation
        return

    # 解析问题
    match = re.search(r'问题:\s*(.+)', line)
    if match and 'test_steps' in running_tasks[task_id]:
        problem = match.group(1).strip()
        steps = running_tasks[task_id]['test_steps']
        if steps:
            if 'issue_details' not in steps[-1]:
                steps[-1]['issue_details'] = {}
            steps[-1]['issue_details']['problem'] = problem
        return

    # 解析根因
    match = re.search(r'根因:\s*(.+)', line)
    if match and 'test_steps' in running_tasks[task_id]:
        root_cause = match.group(1).strip()
        steps = running_tasks[task_id]['test_steps']
        if steps:
            if 'issue_details' not in steps[-1]:
                steps[-1]['issue_details'] = {}
            steps[-1]['issue_details']['root_cause'] = root_cause
        return

    # 解析JS错误
    match = re.search(r'JS错误:\s*(.+)', line)
    if match and 'test_steps' in running_tasks[task_id]:
        js_error = match.group(1).strip()
        steps = running_tasks[task_id]['test_steps']
        if steps:
            if 'issue_details' not in steps[-1]:
                steps[-1]['issue_details'] = {}
            if 'js_errors' not in steps[-1]['issue_details']:
                steps[-1]['issue_details']['js_errors'] = []
            steps[-1]['issue_details']['js_errors'].append(js_error)
        return

    # 解析 "[1/10] Processing collection: xxx" (商品发现)
    match = re.search(r'\[(\d+)/(\d+)\]\s+Processing collection:\s+(.+)', line)
    if match:
        current = int(match.group(1))
        total = int(match.group(2))
        collection = match.group(3).strip()
        running_tasks[task_id]['progress'] = {
            'current': current,
            'total': total,
            'message': f'正在处理分类 {current}/{total}: {collection}'
        }
        return

    # 解析 "Found X products in xxx"
    match = re.search(r'Found (\d+) products in (.+)', line)
    if match:
        count = match.group(1)
        collection = match.group(2).strip()
        current_progress = running_tasks[task_id].get('progress', {})
        current_progress['message'] = f'在 {collection} 中发现 {count} 个商品'
        return

    # 解析 "Discovering all collections..."
    if 'Discovering all collections' in line:
        running_tasks[task_id]['progress']['message'] = '正在发现所有商品分类...'
        return

    # 解析 "Found X collections"
    match = re.search(r'Found (\d+) collections', line)
    if match:
        count = match.group(1)
        running_tasks[task_id]['progress']['message'] = f'发现了 {count} 个商品分类'
        running_tasks[task_id]['progress']['total'] = int(count)
        return

    # 解析统计信息
    if '扫描分类数:' in line:
        match = re.search(r'扫描分类数:\s*(\d+)', line)
        if match and task_id in running_tasks:
            running_tasks[task_id]['stats'] = {'collections': int(match.group(1))}

    if '商品总数:' in line:
        match = re.search(r'商品总数:\s*(\d+)', line)
        if match and task_id in running_tasks:
            if 'stats' not in running_tasks[task_id]:
                running_tasks[task_id]['stats'] = {}
            running_tasks[task_id]['stats']['total_products'] = int(match.group(1))

    if '新增商品:' in line:
        match = re.search(r'新增商品:\s*(\d+)', line)
        if match and task_id in running_tasks:
            if 'stats' not in running_tasks[task_id]:
                running_tasks[task_id]['stats'] = {}
            running_tasks[task_id]['stats']['new_products'] = int(match.group(1))

    if '执行耗时:' in line:
        match = re.search(r'执行耗时:\s*([\d.]+)\s*秒', line)
        if match and task_id in running_tasks:
            if 'stats' not in running_tasks[task_id]:
                running_tasks[task_id]['stats'] = {}
            running_tasks[task_id]['stats']['duration'] = float(match.group(1))


@app.route('/')
def index():
    """首页 - 工作台"""
    return render_template('index.html')


@app.route('/products')
def products():
    """商品管理页面"""
    return render_template('products.html')


@app.route('/tests')
def tests():
    """测试执行页面"""
    return render_template('tests.html')


@app.route('/reports')
def reports():
    """报告中心页面"""
    return render_template('reports.html')


@app.route('/api/health')
def health():
    """健康检查"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})


@app.route('/api/products/discover', methods=['POST'])
def discover_products():
    """发现商品"""
    task_id = f"discover_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    running_tasks[task_id] = {
        'status': 'running',
        'started_at': datetime.now().isoformat()
    }

    # 后台执行
    def run_discovery():
        command = ['./run.sh', 'python3', 'scripts/discover_products.py']
        run_command(command, task_id)

    thread = threading.Thread(target=run_discovery)
    thread.start()

    return jsonify({'task_id': task_id, 'status': 'started'})


@app.route('/api/products/list')
def list_products():
    """获取商品列表"""
    products_file = DATA_DIR / 'products.json'

    if not products_file.exists():
        return jsonify({'products': [], 'total': 0, 'metadata': {}})

    try:
        with open(products_file) as f:
            data = json.load(f)

        # 处理新格式：{metadata: {...}, products: [...]}
        if isinstance(data, dict) and 'products' in data:
            products = data['products']
            metadata = data.get('metadata', {})
        else:
            # 兼容旧格式：直接是数组
            products = data if isinstance(data, list) else []
            metadata = {}

        return jsonify({
            'products': products,
            'total': len(products),
            'metadata': metadata
        })
    except Exception as e:
        logger.error(f"Failed to load products: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/tests/run', methods=['POST'])
def run_tests():
    """运行测试"""
    data = request.json or {}
    test_mode = data.get('test_mode', 'quick')  # quick 或 full

    # 构建测试命令
    # 如果是单个商品测试，使用专用脚本
    if data.get('product_id'):
        command = [
            './run.sh',
            'python3',
            'scripts/run_product_test.py',
            '--product-id', data['product_id'],
            '--mode', test_mode
        ]
    else:
        # 使用批量测试脚本
        command = [
            './run.sh',
            'python3',
            'scripts/batch_test_products.py',
            '--mode', test_mode
        ]

        # 添加过滤参数
        if data.get('priority'):
            command.extend(['--priority', data['priority']])

        if data.get('category'):
            command.extend(['--category', data['category']])

    task_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    running_tasks[task_id] = {
        'status': 'running',
        'started_at': datetime.now().isoformat(),
        'params': data,
        'test_steps': [],  # 存储测试步骤
        'test_mode': test_mode  # 记录测试模式
    }

    # 后台执行
    def run_test():
        run_command(command, task_id)

    thread = threading.Thread(target=run_test)
    thread.start()

    return jsonify({'task_id': task_id, 'status': 'started'})


@app.route('/api/tests/status/<task_id>')
def test_status(task_id):
    """查询测试状态"""
    if task_id not in running_tasks:
        return jsonify({'error': 'Task not found'}), 404

    return jsonify(running_tasks[task_id])


@app.route('/api/reports/list')
def list_reports():
    """获取报告列表"""
    reports = []

    # 查找所有测试报告
    for report_dir in REPORTS_DIR.glob('test_*'):
        if report_dir.is_dir():
            result_file = report_dir / 'test_results.json'
            if result_file.exists():
                try:
                    with open(result_file) as f:
                        data = json.load(f)

                    reports.append({
                        'id': report_dir.name,
                        'timestamp': data.get('timestamp', ''),
                        'summary': data.get('summary', {}),
                        'path': str(report_dir.relative_to(PROJECT_ROOT))
                    })
                except:
                    pass

    # 按时间倒序排序
    reports.sort(key=lambda x: x['timestamp'], reverse=True)

    return jsonify({'reports': reports, 'total': len(reports)})


@app.route('/api/reports/latest')
def latest_report():
    """获取最新报告"""
    result_file = REPORTS_DIR / 'test_results.json'

    if not result_file.exists():
        return jsonify({'error': 'No reports found'}), 404

    try:
        with open(result_file) as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/reports/ai/generate', methods=['POST'])
def generate_ai_report():
    """生成 AI 报告"""
    data = request.json or {}
    provider = data.get('provider', 'deepseek')

    command = [
        './run.sh',
        'python3',
        'scripts/generate_universal_ai_report.py',
        '--provider', provider
    ]

    if data.get('summary_only'):
        command.append('--summary-only')

    task_id = f"ai_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    running_tasks[task_id] = {
        'status': 'running',
        'started_at': datetime.now().isoformat()
    }

    # 后台执行
    def run_ai():
        run_command(command, task_id)

    thread = threading.Thread(target=run_ai)
    thread.start()

    return jsonify({'task_id': task_id, 'status': 'started'})


@app.route('/api/changes/detect', methods=['POST'])
def detect_changes():
    """检测商品变更"""
    command = [
        './run.sh',
        'python3',
        'scripts/detect_product_changes.py',
        '--save-history'
    ]

    task_id = f"changes_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    running_tasks[task_id] = {
        'status': 'running',
        'started_at': datetime.now().isoformat()
    }

    # 后台执行
    def run_detect():
        run_command(command, task_id)

    thread = threading.Thread(target=run_detect)
    thread.start()

    return jsonify({'task_id': task_id, 'status': 'started'})


@app.route('/api/changes/latest')
def latest_changes():
    """获取最新变更"""
    changes_file = DATA_DIR / 'product_changes.json'

    if not changes_file.exists():
        return jsonify({'error': 'No changes detected yet'}), 404

    try:
        with open(changes_file) as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/trends/analyze', methods=['POST'])
def analyze_trends():
    """分析历史趋势"""
    data = request.json or {}
    days = data.get('days', 30)

    command = [
        './run.sh',
        'python3',
        'scripts/analyze_trends.py',
        '--days', str(days)
    ]

    task_id = f"trends_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    running_tasks[task_id] = {
        'status': 'running',
        'started_at': datetime.now().isoformat()
    }

    # 后台执行
    def run_trends():
        run_command(command, task_id)

    thread = threading.Thread(target=run_trends)
    thread.start()

    return jsonify({'task_id': task_id, 'status': 'started'})


@app.route('/api/trends/latest')
def latest_trends():
    """获取最新趋势分析"""
    trends_file = REPORTS_DIR / 'trend_analysis.json'

    if not trends_file.exists():
        return jsonify({'error': 'No trend analysis found'}), 404

    try:
        with open(trends_file) as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/dashboard/generate', methods=['POST'])
def generate_dashboard():
    """生成质量看板"""
    command = [
        './run.sh',
        'python3',
        'scripts/generate_dashboard.py'
    ]

    result = run_command(command)

    if result['success']:
        return jsonify({'status': 'success', 'url': '/dashboard'})
    else:
        return jsonify({'error': result.get('stderr', 'Unknown error')}), 500


@app.route('/dashboard')
def view_dashboard():
    """查看质量看板"""
    dashboard_file = REPORTS_DIR / 'dashboard.html'

    if not dashboard_file.exists():
        return "Dashboard not generated yet. Please generate it first.", 404

    return send_file(dashboard_file)


@app.route('/api/health/check')
def health_check():
    """系统健康检查"""
    health_file = REPORTS_DIR / 'test_health.json'

    if not health_file.exists():
        # 运行健康检查
        command = ['./run.sh', 'python3', 'scripts/check_test_health.py']
        run_command(command)

    if health_file.exists():
        try:
            with open(health_file) as f:
                data = json.load(f)
            return jsonify(data)
        except:
            pass

    return jsonify({'status': 'UNKNOWN'})


@app.route('/api/config')
def get_config():
    """获取系统配置"""
    return jsonify({
        'project_name': 'Fiido Shop Flow Guardian',
        'version': 'v1.4.0',
        'data_dir': str(DATA_DIR.relative_to(PROJECT_ROOT)),
        'reports_dir': str(REPORTS_DIR.relative_to(PROJECT_ROOT))
    })


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Fiido 测试工作台启动中...")
    print("=" * 60)
    print(f"📁 项目目录: {PROJECT_ROOT}")
    print(f"📊 数据目录: {DATA_DIR}")
    print(f"📈 报告目录: {REPORTS_DIR}")
    print("=" * 60)
    print("✅ 服务已启动！")
    print("🌐 访问地址: http://localhost:5000")
    print("=" * 60)

    # 开发模式启动
    app.run(host='0.0.0.0', port=5000, debug=True)
