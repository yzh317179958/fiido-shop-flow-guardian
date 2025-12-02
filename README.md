# Fiido Shop Flow Guardian

**通用电商自动化测试框架 - 基于 Playwright + AI 分析**

[![Version](https://img.shields.io/badge/version-v1.3.0-blue.svg)](https://github.com/yzh317179958/fiido-shop-flow-guardian/releases/tag/v1.3.0)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Test Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen.svg)]()
[![Daily Test](https://github.com/yzh317179958/fiido-shop-flow-guardian/actions/workflows/daily-test.yml/badge.svg)](https://github.com/yzh317179958/fiido-shop-flow-guardian/actions/workflows/daily-test.yml)
[![P0 Test](https://github.com/yzh317179958/fiido-shop-flow-guardian/actions/workflows/hourly-p0-test.yml/badge.svg)](https://github.com/yzh317179958/fiido-shop-flow-guardian/actions/workflows/hourly-p0-test.yml)

## 项目简介

为 Fiido 电商独立站（https://fiido.com）构建的通用化、可扩展的 E2E 自动化测试框架。

**当前版本**: v1.3.0 (Sprint 3 已完成)

**最后更新**: 2025-12-02

### 核心特性

- ✅ **通用化设计**: 仅需提供产品 URL，自动完成完整测试
- ✅ **自动发现**: 爬取网站结构，自动发现所有商品和分类
- ✅ **配置驱动**: 通过 JSON 配置文件控制测试范围和行为
- ✅ **一键扩展**: 新产品上线时，仅需更新配置或提供 URL
- ✅ **AI 智能分析**: 自动生成测试报告和失败分析 (支持 DeepSeek + Claude)
- ✅ **完整流程测试**: 商品页 → 购物车 → 结账完整 E2E 覆盖
- ⏳ **7x24 监控**: 全天候自动运行，即时发现问题 (Sprint 4 开发中)

### 项目进度

| Sprint | 主题 | 状态 | 版本 | 完成度 |
|--------|------|------|------|--------|
| Sprint 0 | 框架搭建 | ✅ 完成 | v1.0.0 | 100% |
| Sprint 1 | 产品爬虫 | ✅ 完成 | v1.1.0 | 100% |
| Sprint 2 | 通用测试框架 | ✅ 完成 | v1.2.0 | 100% |
| Sprint 3 | 购物流程 + AI 报告 | ✅ 完成 | v1.3.0 | 100% |
| **Sprint 4** | **CI/CD + 告警监控** | **🚀 进行中** | **v1.4.0** | **0%** |

**测试覆盖率**: 90%+ (单元测试 + 集成测试 + E2E 测试)

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
# 1. 发现所有商品（生成测试数据）
./run.sh python scripts/discover_products.py

# 2. 运行所有测试
./run_tests.sh

# 3. 运行 E2E 测试
./run_tests.sh tests/e2e/

# 4. 根据优先级过滤测试
./run_tests.sh --priority=P0        # 仅测试 P0 优先级商品
./run_tests.sh --priority=P1        # 仅测试 P1 优先级商品

# 5. 根据分类过滤测试
./run_tests.sh --category=bike      # 仅测试自行车类商品
./run_tests.sh --category=scooter   # 仅测试滑板车类商品

# 6. 测试单个商品
./run_tests.sh --product-id=fiido-d11

# 7. 指定商品数据文件
./run_tests.sh --product-file=data/demo_products.json

# 8. 生成 AI 智能报告 (DeepSeek 免费)
./run.sh python scripts/generate_universal_ai_report.py --provider deepseek

# 9. 仅生成摘要
./run.sh python scripts/generate_universal_ai_report.py --provider deepseek --summary-only
```

## AI 智能报告功能 ✨

### 快速开始 (3步，完全免费)

1. **获取 DeepSeek API Key**: 访问 https://platform.deepseek.com/ (支持国内手机号注册)
2. **配置环境变量**: 在 `.env` 文件中添加 `DEEPSEEK_API_KEY=sk-xxx`
3. **生成报告**: `./run.sh python scripts/generate_universal_ai_report.py --provider deepseek`

### AI 报告功能

- ✅ **自动分析**: 智能分析测试结果，识别失败模式
- 📊 **关键指标**: 通过率、失败分布、趋势统计
- 🔍 **失败分析**: 按优先级分类问题 (P0/P1/P2)
- 💡 **修复建议**: 提供具体的问题修复方案
- 📈 **趋势洞察**: 识别高失败率商品和共同问题

### 支持的 AI 提供商

| 提供商 | 费用 | 国内访问 | 注册难度 | 推荐度 |
|--------|------|----------|----------|--------|
| **DeepSeek** | ✅ 免费 | ✅ 快速 | ⭐ 简单 | ⭐⭐⭐⭐⭐ |
| Claude | 💰 付费 | ❌ 需代理 | ⭐⭐⭐ 困难 | ⭐⭐⭐ |

**推荐使用 DeepSeek**: 每天500万 tokens 免费额度，足够生成1000+次报告！

详细使用指南: [DeepSeek 快速开始](docs/quickstart-deepseek.md)

## CI/CD 自动化 🚀

### GitHub Actions 工作流

项目已集成 GitHub Actions 自动化测试，无需手动运行：

| 工作流 | 触发条件 | 测试范围 | 频率 |
|--------|---------|---------|------|
| **Daily Test** | 每日凌晨 2 点 (UTC) | 全量测试 | 每日 1 次 |
| **P0 Test** | 每小时（工作时间） | 核心商品测试 | 每小时 1 次 |
| **PR Test** | Pull Request | 单元+集成+烟雾测试 | PR 触发 |

### 自动化功能

- ✅ **定时测试**: 每日/每小时自动执行
- ✅ **测试报告**: 自动生成并上传到 Artifacts
- ✅ **AI 分析**: 自动生成智能报告
- ✅ **失败告警**: Slack/邮件通知（需配置）
- ✅ **PR 检查**: 代码质量门禁

### 配置 GitHub Secrets

在 GitHub 仓库的 Settings > Secrets and variables > Actions 中添加：

| Secret 名称 | 说明 | 是否必需 |
|------------|------|---------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | ✅ 必需（AI 报告） |
| `SLACK_WEBHOOK_URL` | Slack Webhook URL | ⏳ 可选（告警通知） |
| `SMTP_USER` | 邮箱用户名 | ⏳ 可选（邮件告警） |
| `SMTP_PASSWORD` | 邮箱密码 | ⏳ 可选（邮件告警） |

### 手动触发测试

在 GitHub Actions 页面可手动触发测试：

1. 访问 https://github.com/YOUR_USERNAME/fiido-shop-flow-guardian/actions
2. 选择工作流（Daily Test / P0 Test）
3. 点击 "Run workflow"
4. 选择测试范围并运行

### 查看测试报告

测试完成后，可在 Actions 页面下载报告：

1. 进入对应的 workflow run
2. 在 "Artifacts" 部分下载报告
3. 解压查看 HTML 报告和 AI 分析

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
