#!/bin/bash
# 项目通用脚本 - 自动处理 Python 环境

# 激活虚拟环境并清除 ROS 环境变量
source venv/bin/activate
unset PYTHONPATH

# 运行传入的命令
"$@"
