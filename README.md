# Fiido Shop Flow Guardian

**通用电商自动化测试框架 - 基于 Playwright + AI 分析**

## 项目简介

为 Fiido 电商独立站（https://fiido.com）构建的通用化、可扩展的 E2E 自动化测试框架。

### 核心特性

- **通用化设计**: 仅需提供产品 URL，自动完成完整测试
- **自动发现**: 爬取网站结构，自动发现所有商品和分类
- **配置驱动**: 通过 JSON 配置文件控制测试范围和行为
- **一键扩展**: 新产品上线时，仅需更新配置或提供 URL
- **AI 智能分析**: 自动生成测试报告和失败分析
- **7x24 监控**: 全天候自动运行，即时发现问题

## 快速开始

### 环境要求

- Python 3.11+
- Ubuntu 22.04 / macOS / Windows 10+
- 4GB+ RAM（推荐 8GB）

### 安装

```bash
# 1. 克隆项目
git clone <repository>
cd fiido-shop-flow-guardian

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate    # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 安装 Playwright 浏览器
playwright install chromium
```

### 使用示例

```bash
# 发现所有商品
python scripts/discover_products.py

# 运行测试
pytest tests/test_all_products.py -v

# 生成 AI 报告
export CLAUDE_API_KEY="your-key"
python scripts/generate_ai_report.py
```

## 项目结构

```
fiido-shop-flow-guardian/
├── core/                   # 核心框架
│   ├── crawler.py         # 产品爬虫
│   ├── models.py          # 数据模型
│   └── selector_manager.py # 选择器管理
├── pages/                  # 页面对象
│   ├── product_page.py
│   ├── cart_page.py
│   └── checkout_page.py
├── tests/                  # 测试套件
│   ├── unit/              # 单元测试
│   ├── integration/       # 集成测试
│   └── e2e/               # 端到端测试
├── config/                 # 配置文件
├── data/                   # 数据存储
├── scripts/                # 工具脚本
├── screenshots/            # 测试截图
└── reports/                # 测试报告
```

## 开发指南

请参考以下文档：

- [开发规范与要求](./claude.md)
- [完整开发指南](./development-lifecycle-guide.md)
- [方案说明文档](./coze/购物流程AI自动化检测方案_Fiido独立站.md)

## 开发方法

本项目采用**渐进式增量开发**方法：

1. **小步开发**: 每次只完成一个小功能
2. **测试优先**: 开发后立即测试
3. **零破坏**: 不破坏已有功能
4. **扩展式**: 通过扩展而非修改实现新功能

## 许可证

Copyright © 2025 Fiido Technical Team
