#!/bin/bash
# 专用测试运行脚本 - 配置 pytest 环境变量并运行测试
#
# Usage:
#   ./run_tests.sh                          # 运行所有测试
#   ./run_tests.sh tests/e2e/               # 运行 E2E 测试
#   ./run_tests.sh --priority=P0            # 运行 P0 优先级测试
#   ./run_tests.sh --category=bike          # 运行指定分类的测试
#   ./run_tests.sh --product-id=fiido-d11   # 测试单个商品

set -e  # Exit on error

# 激活虚拟环境并清除 ROS 环境变量
if [ -f venv/bin/activate ]; then
    source venv/bin/activate
fi
unset PYTHONPATH

# 不设置 PYTEST_DISABLE_PLUGIN_AUTOLOAD，让 pytest 自动加载所有已安装的插件
# 包括 pytest-playwright, pytest-asyncio, pytest-cov 等

# 运行 pytest，传递所有参数
# -v: 详细输出
# --tb=short: 简短的错误追踪
# --color=yes: 彩色输出
pytest -v --tb=short --color=yes "$@"




