# Shop Flow Guardian

**通用电商自动化测试框架 - 基于 Playwright + AI 分析**

[![Version](https://img.shields.io/badge/version-v2.0.1-blue.svg)](https://github.com/yzh317179958/fiido-shop-flow-guardian/releases/tag/v2.0.1)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Test Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen.svg)]()
[![Daily Test](https://github.com/yzh317179958/fiido-shop-flow-guardian/actions/workflows/daily-test.yml/badge.svg)](https://github.com/yzh317179958/fiido-shop-flow-guardian/actions/workflows/daily-test.yml)
[![P0 Test](https://github.com/yzh317179958/fiido-shop-flow-guardian/actions/workflows/hourly-p0-test.yml/badge.svg)](https://github.com/yzh317179958/fiido-shop-flow-guardian/actions/workflows/hourly-p0-test.yml)

## 项目简介

为电商独立站构建的通用化、可扩展的 E2E 自动化测试框架。

**当前版本**: v2.0.1 (Web UI + 双模式测试)

**最后更新**: 2025-12-04

### 核心特性

- ✅ **Web UI 界面**: 简洁易用的 Web 界面，支持可视化测试执行
- ✅ **双模式测试**: 快速测试(5步)和全面测试(12步)灵活切换
- ✅ **实时步骤显示**: 测试执行时实时显示每个步骤的状态和结果
- ✅ **通用化设计**: 仅需提供产品 URL，自动完成完整测试
- ✅ **自动发现**: 爬取网站结构，自动发现所有商品和分类
- ✅ **配置驱动**: 通过 JSON 配置文件控制测试范围和行为
- ✅ **一键扩展**: 新产品上线时，仅需更新配置或提供 URL
- ✅ **AI 智能分析**: 自动生成测试报告和失败分析 (支持 DeepSeek + Claude)
- ✅ **完整流程测试**: 商品页 → 购物车 → 结账完整 E2E 覆盖
- ✅ **7x24 监控**: 全天候自动运行，即时发现问题 (CI/CD + 告警系统)
- ✅ **质量看板**: 可视化趋势分析与性能监控

### 项目进度

| Sprint | 主题 | 状态 | 版本 | 完成度 |
|--------|------|------|------|--------|
| Sprint 0 | 框架搭建 | ✅ 完成 | v1.0.0 | 100% |
| Sprint 1 | 产品爬虫 | ✅ 完成 | v1.1.0 | 100% |
| Sprint 2 | 通用测试框架 | ✅ 完成 | v1.2.0 | 100% |
| Sprint 3 | 购物流程 + AI 报告 | ✅ 完成 | v1.3.0 | 100% |
| Sprint 4 | CI/CD + 告警监控 | ✅ 完成 | v1.4.0 | 100% |
| **Sprint 5** | **Web UI + 双模式测试** | **✅ 完成** | **v2.0.1** | **100%** |

**测试覆盖率**: 95%+ (单元测试 + 集成测试 + E2E 测试)

## 🚀 快速开始 (Web UI)

### 启动 Web 界面

```bash
# 1. 启动 Web 服务器
python3 web/app.py

# 2. 在浏览器中访问
http://localhost:5000
```

### Web UI 功能

- **📊 概览页面**: 查看系统状态、最新测试结果和统计数据
- **📦 商品管理**: 浏览和管理所有商品，支持分类筛选
- **▶️ 测试执行**: 配置和运行测试，实时查看执行进度
- **📈 报告中心**: 查看历史测试报告、趋势分析和质量看板

### 双模式测试

**⚡ 快速测试** (推荐日常使用)
- 5个核心步骤：页面访问 → 商品信息 → 加购物车 → 购物车验证 → 支付流程
- 平均耗时：15-20秒
- 用途：快速验证核心购物流程

**🔍 全面测试** (深度检测)
- 12个详细步骤：全链路全场景覆盖
- 平均耗时：40-60秒
- 用途：新功能上线、重大变更验证

## 命令行快速开始

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

# 10. 检测商品变更（增量测试）
./run.sh python scripts/detect_product_changes.py --save-history

# 11. 分析历史趋势（30 天数据）
./run.sh python scripts/analyze_trends.py --days 30

# 12. 生成质量看板（可视化 HTML）
./run.sh python scripts/generate_dashboard.py
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

1. 访问 https://github.com/YOUR_USERNAME/shop-flow-guardian/actions
2. 选择工作流（Daily Test / P0 Test）
3. 点击 "Run workflow"
4. 选择测试范围并运行

### 查看测试报告

测试完成后，可在 Actions 页面下载报告：

1. 进入对应的 workflow run
2. 在 "Artifacts" 部分下载报告
3. 解压查看 HTML 报告和 AI 分析

## 告警与监控 🔔

### 智能告警系统

测试失败时自动发送告警通知，支持多种渠道：

| 渠道 | 国内可用 | 推荐度 | 特点 |
|------|---------|--------|------|
| **Slack** | ❌ 需代理 | ⭐⭐⭐⭐ | 富文本消息、即时通知 |
| **邮件** | ✅ 可用 | ⭐⭐⭐⭐⭐ | 详细报告、适合团队 |
| **企业微信** | ✅ 可用 | ⭐⭐⭐⭐⭐ | 国内友好、企业首选 |

### 告警触发条件

- 🚨 **P0 核心商品失败** - 立即告警
- ⚠️ **通过率低于阈值** - 默认 90%
- ⚠️ **连续失败 3 次** - 趋势恶化
- ℹ️ **失败数量突增** - 异常检测

### 快速配置（3 步）

1. **配置环境变量**

```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 添加 Webhook URL 或 SMTP 配置
# Slack: SLACK_WEBHOOK_URL=https://hooks.slack.com/...
# 邮件: SMTP_USER=your-email@gmail.com
#      SMTP_PASSWORD=your-app-password
```

2. **测试告警**

```bash
# 生成测试结果
python scripts/collect_test_results.py

# 发送测试告警
python scripts/send_alerts.py --channel slack  # 或 email/wechat
```

3. **配置 GitHub Secrets**

在仓库设置中添加（用于 CI/CD）：
- `SLACK_WEBHOOK_URL` (可选)
- `SMTP_USER` 和 `SMTP_PASSWORD` (可选)

详细配置指南: [告警配置指南](docs/alert-setup-guide.md)

### 健康监控

```bash
# 查看测试系统健康状况
python scripts/check_test_health.py

# 输出示例:
# ✅ 测试系统健康报告
# ==========================================
# 状态: HEALTHY
# 平均通过率: 95.2%
# P0 失败次数: 0
# 趋势: 📈 IMPROVING
```

## 商品变更检测与增量测试 🔄

### 智能变更检测

自动识别商品数据变化，仅对变更的商品执行测试，大幅提升测试效率：

```bash
# 检测商品变更
./run.sh python scripts/detect_product_changes.py

# 保存当前数据为历史记录
./run.sh python scripts/detect_product_changes.py --save-history

# 输出 JSON 格式
./run.sh python scripts/detect_product_changes.py --json
```

### 变更类型

自动识别以下变更：

- ✨ **新增商品** - 优先级 P0，立即测试
- 🔄 **价格变更** - 优先级 P0，影响订单金额
- 📝 **名称变更** - 优先级 P1，可能影响 SEO
- 🎨 **变体变更** - 优先级 P1，影响选项选择
- 📦 **库存状态** - 优先级 P0，影响购买流程
- ❌ **商品下架** - 记录但不测试

### 增量测试策略

基于变更检测结果，自动生成测试目标列表：

```json
{
  "test_targets": [
    {
      "id": "product-123",
      "reason": "price_changed",
      "priority": "P0",
      "changes": {
        "price_min": {"old": 999, "new": 899}
      }
    }
  ]
}
```

## 历史趋势分析 📊

### 30 天数据分析

分析过去 30 天的测试数据，生成趋势报告：

```bash
# 分析最近 30 天
./run.sh python scripts/analyze_trends.py --days 30

# 自定义天数
./run.sh python scripts/analyze_trends.py --days 7

# 输出 JSON 格式
./run.sh python scripts/analyze_trends.py --json
```

### 分析维度

**通过率趋势**
- 每日通过率变化
- 平均通过率计算
- 趋势方向识别（improving / stable / declining）

**高频失败分析**
- 失败次数 Top 10 商品
- 主要错误类型统计
- 持续失败天数追踪

**地区性能对比**
- 各地区通过率排行
- 地区失败率对比
- 问题地区识别

**性能指标趋势**
- 页面加载时间变化
- API 响应时间趋势
- 性能优化效果评估

**周期性问题识别**
- 按星期统计失败率
- 识别高风险时间段（如周五部署）
- 建议最佳发布窗口

### 智能洞察

AI 自动分析趋势数据，生成洞察建议：

```json
{
  "insights": [
    {
      "type": "warning",
      "message": "测试通过率呈下降趋势，需要关注",
      "priority": "high"
    },
    {
      "type": "action_required",
      "message": "最高频失败商品: Product A (10 次失败)",
      "priority": "high"
    }
  ]
}
```

## 质量看板可视化 📈

### 生成可视化看板

自动生成包含图表和关键指标的 HTML 看板：

```bash
# 生成质量看板
./run.sh python scripts/generate_dashboard.py

# 自定义报告路径
./run.sh python scripts/generate_dashboard.py \
  --trend-report reports/trend_analysis.json \
  --test-results reports/test_results.json \
  --health-report reports/test_health.json \
  --output reports/dashboard.html
```

### 看板功能

**实时状态卡片**
- 系统健康状态（HEALTHY / WARNING / CRITICAL）
- 平均通过率
- 最近测试结果
- 高频失败商品数量

**可视化图表**
- 📈 通过率趋势折线图（30 天）
- 🌍 地区性能对比柱状图
- ⚡ 性能趋势折线图
- ❌ 高频失败商品列表

**智能洞察面板**
- ✅ 正面趋势提示
- ⚠️ 警告信息
- 🚨 需要立即处理的问题

### 查看看板

生成后在浏览器中打开：

```bash
# Linux/macOS
open reports/dashboard.html

# 或直接用浏览器打开
firefox reports/dashboard.html
```

看板实时更新，自动展示最新的测试数据和趋势分析。

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
