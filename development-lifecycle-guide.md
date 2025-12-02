# Fiido 电商E2E测试 - 通用自动化测试框架开发指南

> **项目名称**: Fiido Shop Flow Guardian - 通用电商测试自动化框架
> **版本**: 2.0（通用化、可扩展版本）
> **创建时间**: 2025-12-01
> **目标网站**: https://fiido.com（基于Shopify平台）
> **框架特点**: 配置驱动、URL自动发现、一键扩展新产品
> **开发方法**: 渐进式增量开发

---

## 目录

1. [项目概述](#1-项目概述)
2. [环境要求](#2-环境要求)
3. [技术栈](#3-技术栈)
4. [框架设计理念](#4-框架设计理念)
5. [开发阶段](#5-开发阶段)
6. [迭代规划](#6-迭代规划)
7. [核心组件设计](#7-核心组件设计)
8. [使用指南](#8-使用指南)
9. [用户界面（非技术人员使用）](#9-用户界面非技术人员使用)
10. [部署方案](#10-部署方案)
11. [部署流水线](#11-部署流水线)
12. [质量门禁](#12-质量门禁)
13. [扩展指南](#13-扩展指南)

---

## 1. 项目概述

### 1.1 项目目标

为Fiido电商独立站（https://fiido.com）构建**通用化、可扩展**的E2E自动化测试框架。

**目标网站信息**：
- **主站**: https://fiido.com
- **平台**: Shopify电商平台
- **产品**: 电动自行车及配件
- **特点**: 国际化、多地区配送、多支付方式（PayPal、Klarna、Shop Pay）

**核心目标**：
- ✅ **通用化设计**: 仅需提供产品URL，自动完成完整测试
- ✅ **自动发现**: 爬取网站结构，自动发现所有商品和分类
- ✅ **配置驱动**: 通过JSON配置文件控制测试范围和行为
- ✅ **一键扩展**: 新产品上线时，仅需更新配置或提供URL
- ✅ **AI智能分析**: 自动生成测试报告和失败分析
- ✅ **7x24监控**: 全天候自动运行，即时发现问题

### 1.2 设计核心理念

**问题**: 传统E2E测试需要为每个新产品手动编写测试代码
**解决方案**: 构建抽象层，通过配置和URL自动化测试

```
                    传统方式                           通用框架
┌─────────────────────────────────┐    ┌─────────────────────────────────┐
│ 新产品上线                        │    │ 新产品上线                        │
│   ↓                              │    │   ↓                              │
│ QA手动编写测试代码                │    │ 添加产品URL到配置文件             │
│   ↓                              │    │   ↓                              │
│ 调试测试脚本                      │    │ 框架自动爬取产品信息              │
│   ↓                              │    │   ↓                              │
│ 部署到CI/CD                       │    │ 自动生成测试用例                  │
│   ↓                              │    │   ↓                              │
│ 运行测试（耗时1-2天）             │    │ 立即执行测试（耗时5分钟）         │
└─────────────────────────────────┘    └─────────────────────────────────┘
```

**核心优势**：
1. **零代码扩展**: 新产品仅需配置URL
2. **自动抽象**: 框架自动识别商品属性（价格、变体、库存等）
3. **智能适配**: 自动处理不同商品类型（自行车、配件、周边）
4. **灵活配置**: 按优先级、地区、类型过滤测试

### 1.3 实际使用场景

#### 场景1: 新产品上线测试
```bash
# 仅需一条命令
python scripts/add_product.py --url "https://fiido.com/products/fiido-x-pro"

# 框架自动：
# 1. 爬取产品页面信息（标题、价格、变体、图片）
# 2. 生成测试用例
# 3. 执行完整流程测试（浏览→加购→结账）
# 4. 生成测试报告
```

#### 场景2: 全站商品测试
```bash
# 自动发现所有商品并测试
python scripts/discover_and_test.py --base-url "https://fiido.com"

# 框架自动：
# 1. 爬取所有商品分类（/collections）
# 2. 爬取每个分类下的所有商品
# 3. 生成全量测试套件
# 4. 并行执行测试
# 5. AI分析结果并告警
```

#### 场景3: 特定分类测试
```bash
# 仅测试电动自行车分类
pytest tests/ --collection="electric-bikes" --priority=P0
```

---

## 2. 环境要求

### 2.1 开发环境

**推荐配置**（您的环境）：
- **操作系统**: Ubuntu 22.04 LTS（✅ 最佳选择）
- **Python**: 3.11+
- **内存**: 8GB+（最低4GB）
- **磁盘**: 10GB+（包含依赖和浏览器）
- **网络**: 稳定的互联网连接

**开发工具**：
```bash
# 必需工具
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip git

# 可选工具（推荐）
sudo apt install -y curl wget jq  # 命令行工具
```

### 2.2 使用环境（跨平台支持）

**✅ 支持的操作系统**：

| 操作系统 | 支持状态 | 说明 |
|---------|---------|------|
| **Ubuntu 22.04/20.04** | ✅ 完全支持 | 推荐（开发环境） |
| **Ubuntu 18.04** | ✅ 支持 | 需要升级Python到3.11 |
| **macOS 12+** | ✅ 完全支持 | Intel和Apple Silicon均支持 |
| **Windows 10/11** | ✅ 支持 | 使用WSL2（推荐）或原生Python |
| **CentOS/RHEL 8+** | ✅ 支持 | 需要额外配置 |
| **Docker容器** | ✅ 完全支持 | 最佳跨平台方案 |

**Windows用户特别说明**：
```powershell
# 方案1: WSL2（推荐）
wsl --install -d Ubuntu-22.04
# 然后在WSL中按照Ubuntu流程安装

# 方案2: 原生Windows
# 下载Python 3.11: https://www.python.org/downloads/
# 安装后使用PowerShell或CMD
python --version
pip install -r requirements.txt
playwright install chromium
```

### 2.3 浏览器要求

**自动安装（推荐）**：
```bash
# Playwright会自动下载所需浏览器
playwright install chromium  # 约150MB
playwright install firefox   # 约75MB（可选）
playwright install webkit    # 约50MB（可选）
```

**系统依赖（Linux）**：
```bash
# Ubuntu/Debian
playwright install-deps chromium

# 或手动安装
sudo apt install -y \
  libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
  libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
  libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2
```

### 2.4 网络要求

| 需求 | 说明 |
|------|------|
| **外网访问** | 必需（访问fiido.com和Claude API） |
| **带宽** | 最低2Mbps，推荐10Mbps+ |
| **防火墙** | 允许HTTPS出站（443端口） |
| **代理** | 支持（需配置环境变量） |

**代理配置示例**：
```bash
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
export NO_PROXY=localhost,127.0.0.1
```

### 2.5 资源占用

**开发时**：
- CPU: 2核心（4核心推荐）
- 内存: 4GB（8GB推荐）
- 磁盘: 5GB（代码+依赖+浏览器）

**运行测试时**：
- CPU: 80-100%（并行测试时）
- 内存: 2-4GB（取决于并行数量）
- 网络: 1-5Mbps（下载网页内容）

**CI/CD环境**：
- GitHub Actions免费额度：2000分钟/月
- 预计消耗：约300-400分钟/月（每日运行）

### 2.6 非技术人员使用环境

**选项1: Web界面（推荐）**
- 浏览器：Chrome/Firefox/Safari最新版
- 无需安装任何软件
- 通过浏览器访问Web界面

**选项2: 桌面应用**
- Windows 10/11（64位）
- macOS 10.15+
- Ubuntu 20.04+
- 约200MB安装包

**选项3: 在线服务**
- 无需本地环境
- 仅需浏览器和网络
- 按月订阅模式

---

## 3. 技术栈

### 2.1 核心框架

| 组件 | 技术 | 版本 | 用途 |
|------|------|------|------|
| **测试框架** | Playwright | Latest | 浏览器自动化 |
| **测试运行器** | Pytest | 7.x+ | 测试执行与组织 |
| **开发语言** | Python | 3.11+ | 主要编程语言 |
| **网页爬虫** | BeautifulSoup4 + Requests | Latest | 自动发现商品 |
| **配置管理** | JSON Schema | - | 验证配置文件 |
| **AI分析** | Claude API | Sonnet 4.5 | 智能报告生成 |
| **CI/CD** | GitHub Actions | N/A | 自动化调度 |

### 2.2 开发依赖

```txt
# requirements.txt
playwright>=1.40.0
pytest>=7.4.0
pytest-playwright>=0.4.3
pytest-rerunfailures>=12.0
pytest-xdist>=3.5.0          # 并行测试
beautifulsoup4>=4.12.0       # 网页解析
requests>=2.31.0
anthropic>=0.18.0
python-dotenv>=1.0.0
jsonschema>=4.20.0           # 配置验证
pydantic>=2.5.0              # 数据验证
```

---

## 3. 框架设计理念

### 3.1 三层架构设计

```
┌───────────────────────────────────────────────────────────┐
│                    配置层（Config Layer）                   │
│  - 产品配置（products.json）                                │
│  - 测试策略配置（test_strategy.json）                       │
│  - 选择器配置（selectors.json）                             │
└───────────────────────────────────────────────────────────┘
                           ↓
┌───────────────────────────────────────────────────────────┐
│                  抽象层（Abstraction Layer）                │
│  - 产品爬虫（ProductCrawler）                               │
│  - 页面对象模型（PageObjectModel）                          │
│  - 测试用例生成器（TestGenerator）                          │
└───────────────────────────────────────────────────────────┘
                           ↓
┌───────────────────────────────────────────────────────────┐
│                  执行层（Execution Layer）                  │
│  - Playwright测试引擎                                       │
│  - 并行测试调度器                                           │
│  - 结果收集器                                               │
└───────────────────────────────────────────────────────────┘
```

### 3.2 核心组件

#### 组件1: 产品爬虫（Product Crawler）

**功能**: 自动发现并提取商品信息

```python
# 文件: core/crawler.py

class ProductCrawler:
    """自动爬取Fiido网站商品信息"""

    def discover_all_products(self, base_url: str) -> List[Product]:
        """
        从网站自动发现所有商品

        步骤:
        1. 访问 /collections 获取所有分类
        2. 遍历每个分类，获取商品列表
        3. 访问每个商品页，提取详细信息
        4. 返回结构化的商品列表
        """
        pass

    def extract_product_info(self, product_url: str) -> Product:
        """
        提取单个商品的详细信息

        提取内容:
        - 商品名称、价格、货币
        - 变体（颜色、尺寸等）
        - 库存状态
        - 商品描述
        - 图片URL
        - 关键元素的CSS选择器
        """
        pass
```

**数据模型**:
```python
# 文件: core/models.py

from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict

class ProductVariant(BaseModel):
    """商品变体"""
    name: str                    # 变体名称（如"Black"）
    type: str                    # 变体类型（如"color"）
    selector: str                # CSS选择器
    available: bool = True       # 是否有货

class Product(BaseModel):
    """商品数据模型"""
    id: str                      # 商品唯一标识
    name: str                    # 商品名称
    url: HttpUrl                 # 商品URL
    price_min: float             # 最低价格
    price_max: float             # 最高价格
    currency: str                # 货币
    variants: List[ProductVariant] = []  # 变体列表
    category: str                # 分类
    priority: str = "P1"         # 测试优先级
    selectors: Dict[str, str]    # 关键元素选择器

    # 自动生成的元数据
    discovered_at: str           # 发现时间
    last_tested: Optional[str]   # 上次测试时间
```

#### 组件2: 通用页面对象（Generic Page Objects）

**设计思路**: 创建可复用的页面对象基类

```python
# 文件: pages/base_page.py

class BasePage:
    """所有页面的基类"""

    def __init__(self, page: Page, selectors: Dict[str, str]):
        self.page = page
        self.selectors = selectors

    async def click_element(self, selector_key: str):
        """通用点击方法"""
        selector = self.selectors.get(selector_key)
        if selector:
            await self.page.click(selector)
        else:
            raise ValueError(f"选择器 {selector_key} 未配置")

    async def fill_input(self, selector_key: str, value: str):
        """通用输入方法"""
        selector = self.selectors.get(selector_key)
        if selector:
            await self.page.fill(selector, value)

class ProductPage(BasePage):
    """商品页面（通用）"""

    async def get_product_title(self) -> str:
        """获取商品标题"""
        return await self.page.locator(
            self.selectors['product_title']
        ).text_content()

    async def get_price(self) -> str:
        """获取价格"""
        return await self.page.locator(
            self.selectors['product_price']
        ).text_content()

    async def select_variant(self, variant: ProductVariant):
        """选择变体"""
        await self.page.click(variant.selector)

    async def add_to_cart(self):
        """加入购物车"""
        await self.click_element('add_to_cart_button')
```

#### 组件3: 自动化测试生成器

```python
# 文件: core/test_generator.py

class TestGenerator:
    """自动生成测试用例"""

    def generate_product_tests(self, product: Product) -> str:
        """
        为单个商品生成测试代码

        生成的测试包括:
        1. 商品页加载测试
        2. 价格显示测试
        3. 变体选择测试（如果有）
        4. 加购测试
        5. 购物车验证测试
        """
        test_code = f'''
@pytest.mark.asyncio
@pytest.mark.product_id("{product.id}")
async def test_{product.id}_page_load(page, product_page_factory):
    """测试 {product.name} 页面加载"""
    product_page = await product_page_factory("{product.url}")

    # 验证标题
    title = await product_page.get_product_title()
    assert "{product.name}" in title or title in "{product.name}"

    # 验证价格
    price = await product_page.get_price()
    assert price is not None

@pytest.mark.asyncio
@pytest.mark.product_id("{product.id}")
async def test_{product.id}_add_to_cart(page, product_page_factory):
    """测试 {product.name} 加入购物车"""
    product_page = await product_page_factory("{product.url}")

    # 选择第一个变体（如果有）
    {"await product_page.select_variant(variants[0])" if product.variants else "pass"}

    # 加入购物车
    await product_page.add_to_cart()

    # 验证购物车更新
    cart_count = await page.locator('.cart-count').text_content()
    assert int(cart_count) > 0
'''
        return test_code

    def generate_test_suite(self, products: List[Product], output_path: str):
        """批量生成测试套件"""
        all_tests = []
        for product in products:
            all_tests.append(self.generate_product_tests(product))

        # 写入测试文件
        with open(output_path, 'w') as f:
            f.write(TEST_FILE_HEADER)
            f.write('\n\n'.join(all_tests))
```

### 3.3 配置驱动设计

#### 选择器配置文件

```json
// 文件: config/selectors.json
{
  "version": "1.0",
  "platform": "shopify",
  "base_selectors": {
    "product_title": ".product-title, h1.product__title, [data-testid='product-title']",
    "product_price": ".product-price, .price, [data-testid='product-price']",
    "add_to_cart_button": "button:has-text('Add to Cart'), button[name='add'], .btn-add-to-cart",
    "cart_count": ".cart-count, .cart-item-count, [data-cart-count]",
    "cart_drawer": ".cart-drawer, #CartDrawer",
    "checkout_button": "button:has-text('Checkout'), a[href*='checkout']"
  },
  "variant_selectors": {
    "color": ".color-swatch, [data-option='Color'] button",
    "size": ".size-option, [data-option='Size'] button"
  },
  "checkout_selectors": {
    "email": "#email, input[name='email']",
    "first_name": "#firstName, input[name='firstName']",
    "last_name": "#lastName, input[name='lastName']",
    "address": "#address1, input[name='address1']",
    "city": "#city, input[name='city']",
    "postal_code": "#zip, input[name='postalCode']",
    "country": "#country, select[name='countryCode']"
  }
}
```

**说明**:
- 使用多个候选选择器（逗号分隔），框架自动尝试
- 支持CSS选择器、文本选择器、属性选择器
- 当网站改版时，仅需更新此配置文件

#### 测试策略配置

```json
// 文件: config/test_strategy.json
{
  "discovery": {
    "enabled": true,
    "collections_url": "https://fiido.com/collections",
    "max_products_per_collection": 100,
    "crawl_depth": 2,
    "cache_duration_hours": 24
  },
  "execution": {
    "parallel_workers": 4,
    "retry_failed_tests": 3,
    "retry_delay_seconds": 2,
    "screenshot_on_failure": true,
    "video_on_failure": false
  },
  "coverage": {
    "test_all_variants": true,
    "max_variants_per_product": 5,
    "test_out_of_stock": false
  },
  "priorities": {
    "P0": {
      "description": "核心商品，每日测试",
      "schedule": "0 */6 * * *"
    },
    "P1": {
      "description": "重要商品，每周测试",
      "schedule": "0 2 * * 1"
    },
    "P2": {
      "description": "普通商品，按需测试",
      "schedule": "manual"
    }
  }
}
```

---

## 4. 开发阶段

### 阶段概览

| 阶段 | 周期 | 交付物 | 核心功能 |
|------|------|--------|---------|
| **阶段0: 框架搭建** | 3天 | 项目结构、核心类 | 基础架构 |
| **阶段1: 爬虫开发** | 1周 | 产品自动发现 | 自动爬取商品 |
| **阶段2: 通用测试** | 2周 | 通用测试框架 | 测试任意产品 |
| **阶段3: 完整流程** | 2周 | 结账流程测试 | 端到端测试 |
| **阶段4: AI集成** | 2周 | 智能分析告警 | AI报告生成 |

**总开发周期**: 7-8周

---

## 5. 迭代规划

### Sprint 0: 框架搭建（第1-3天）

**目标**: 建立项目基础架构和核心抽象

#### 任务清单

**第1天: 项目结构**
```bash
fiido-shop-flow-guardian/
├── core/                         # 核心框架
│   ├── __init__.py
│   ├── crawler.py               # 产品爬虫
│   ├── models.py                # 数据模型
│   ├── test_generator.py       # 测试生成器
│   └── selector_manager.py     # 选择器管理
├── pages/                        # 页面对象
│   ├── __init__.py
│   ├── base_page.py
│   ├── product_page.py
│   ├── cart_page.py
│   └── checkout_page.py
├── tests/                        # 测试套件
│   ├── conftest.py
│   ├── test_product_template.py # 测试模板
│   └── generated/               # 自动生成的测试
├── config/                       # 配置文件
│   ├── selectors.json
│   ├── test_strategy.json
│   └── regions.json
├── data/                         # 数据存储
│   ├── discovered_products.json # 爬取的商品
│   └── test_history.json        # 测试历史
├── scripts/                      # 工具脚本
│   ├── discover_products.py     # 产品发现
│   ├── add_product.py           # 添加单个产品
│   ├── generate_tests.py        # 生成测试
│   └── analyze_results.py       # 结果分析
├── screenshots/                  # 截图
├── reports/                      # 报告
├── requirements.txt
├── pytest.ini
└── README.md
```

**第2天: 核心数据模型**
```python
# 文件: core/models.py

from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict, Literal
from datetime import datetime

class ProductVariant(BaseModel):
    """商品变体"""
    name: str
    type: Literal["color", "size", "style", "configuration"]
    selector: str
    available: bool = True
    price_modifier: Optional[float] = None  # 价格差异

class Selectors(BaseModel):
    """商品页面选择器"""
    product_title: str
    product_price: str
    add_to_cart_button: str
    variant_options: Dict[str, str] = {}

    class Config:
        extra = "allow"  # 允许额外字段

class Product(BaseModel):
    """商品完整信息"""
    id: str = Field(..., description="商品唯一标识，从URL生成")
    name: str
    url: HttpUrl
    category: str
    price_min: float
    price_max: float
    currency: str = "USD"
    variants: List[ProductVariant] = []
    selectors: Selectors
    priority: Literal["P0", "P1", "P2"] = "P1"
    tags: List[str] = []

    # 元数据
    discovered_at: datetime = Field(default_factory=datetime.now)
    last_tested: Optional[datetime] = None
    test_status: Literal["untested", "passing", "failing", "flaky"] = "untested"

class TestResult(BaseModel):
    """测试结果"""
    product_id: str
    test_name: str
    status: Literal["passed", "failed", "skipped"]
    duration: float
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
```

**第3天: 选择器管理器**
```python
# 文件: core/selector_manager.py

import json
from pathlib import Path
from typing import Dict, List

class SelectorManager:
    """管理和解析选择器配置"""

    def __init__(self, config_path: str = "config/selectors.json"):
        self.config_path = Path(config_path)
        self.selectors = self._load_config()

    def _load_config(self) -> Dict:
        """加载选择器配置"""
        with open(self.config_path) as f:
            return json.load(f)

    def get_selector(self, key: str, fallback: bool = True) -> str:
        """
        获取选择器，支持多个候选

        Args:
            key: 选择器键名（如 'product_title'）
            fallback: 是否启用后备选择器

        Returns:
            选择器字符串，多个选择器用逗号分隔
        """
        base_selectors = self.selectors.get('base_selectors', {})
        selector = base_selectors.get(key, '')

        if not selector and fallback:
            # 尝试通用后备
            selector = self._get_fallback_selector(key)

        return selector

    def _get_fallback_selector(self, key: str) -> str:
        """生成后备选择器"""
        fallbacks = {
            'product_title': 'h1, .title, [class*="product-title"]',
            'product_price': '.price, [class*="price"]',
            'add_to_cart_button': 'button:has-text("Add"), button:has-text("加入")'
        }
        return fallbacks.get(key, '')

    async def find_element(self, page, key: str):
        """
        使用选择器查找元素（自动尝试多个选择器）

        Args:
            page: Playwright Page对象
            key: 选择器键名

        Returns:
            找到的元素或None
        """
        selector = self.get_selector(key)
        selectors = [s.strip() for s in selector.split(',')]

        for sel in selectors:
            try:
                element = page.locator(sel).first
                if await element.count() > 0:
                    return element
            except Exception:
                continue

        return None
```

**交付物**:
- ✅ 完整项目结构
- ✅ 核心数据模型（Pydantic）
- ✅ 选择器管理系统
- ✅ 配置文件模板

---

### Sprint 1: 产品爬虫开发（第1周）

**目标**: 实现自动发现Fiido网站所有商品的能力

#### 增量 1.1: 基础爬虫

```python
# 文件: core/crawler.py

import requests
from bs4 import BeautifulSoup
from typing import List
from .models import Product, ProductVariant, Selectors
from urllib.parse import urljoin, urlparse
import json
import re

class ProductCrawler:
    """Fiido网站产品爬虫"""

    def __init__(self, base_url: str = "https://fiido.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def discover_collections(self) -> List[str]:
        """
        发现所有商品分类

        Returns:
            分类URL列表
        """
        collections_url = f"{self.base_url}/collections"
        response = self.session.get(collections_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        collection_links = []
        # Shopify典型的分类链接模式
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '/collections/' in href and href not in collection_links:
                full_url = urljoin(self.base_url, href)
                collection_links.append(full_url)

        return collection_links

    def get_products_from_collection(self, collection_url: str) -> List[str]:
        """
        从分类页获取所有商品URL

        Args:
            collection_url: 分类URL

        Returns:
            商品URL列表
        """
        # Shopify支持JSON API
        json_url = f"{collection_url}/products.json"

        try:
            response = self.session.get(json_url)
            data = response.json()

            products = []
            for product in data.get('products', []):
                product_url = f"{self.base_url}/products/{product['handle']}"
                products.append(product_url)

            return products

        except Exception:
            # 后备方案：解析HTML
            return self._parse_collection_html(collection_url)

    def _parse_collection_html(self, collection_url: str) -> List[str]:
        """解析分类页HTML获取商品链接"""
        response = self.session.get(collection_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        products = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '/products/' in href:
                full_url = urljoin(self.base_url, href)
                if full_url not in products:
                    products.append(full_url)

        return products

    def extract_product_info(self, product_url: str) -> Product:
        """
        提取单个商品的详细信息

        Args:
            product_url: 商品URL

        Returns:
            Product对象
        """
        # 尝试使用Shopify Product JSON API
        parsed_url = urlparse(product_url)
        product_handle = parsed_url.path.split('/')[-1]
        json_url = f"{self.base_url}/products/{product_handle}.json"

        try:
            response = self.session.get(json_url)
            data = response.json()
            product_data = data['product']

            # 提取价格范围
            variants = product_data.get('variants', [])
            prices = [float(v['price']) for v in variants]
            price_min = min(prices) if prices else 0.0
            price_max = max(prices) if prices else 0.0

            # 提取变体信息
            product_variants = self._extract_variants(product_data)

            # 生成商品ID
            product_id = product_handle.replace('-', '_')

            # 提取分类
            category = product_data.get('product_type', 'Unknown')

            # 构建选择器（使用默认值）
            selectors = Selectors(
                product_title=".product-title, h1.product__title",
                product_price=".product-price, .price",
                add_to_cart_button="button[name='add'], button:has-text('Add to Cart')"
            )

            return Product(
                id=product_id,
                name=product_data['title'],
                url=product_url,
                category=category,
                price_min=price_min,
                price_max=price_max,
                currency="USD",  # 可从变体中提取
                variants=product_variants,
                selectors=selectors,
                tags=product_data.get('tags', [])
            )

        except Exception as e:
            print(f"无法从JSON API提取 {product_url}: {e}")
            # 后备：HTML解析
            return self._parse_product_html(product_url)

    def _extract_variants(self, product_data: dict) -> List[ProductVariant]:
        """从Shopify产品数据提取变体"""
        variants = []
        options = product_data.get('options', [])

        for option in options:
            option_name = option['name']  # 如 "Color"
            option_values = option['values']  # 如 ["Black", "White"]

            variant_type = "color" if "color" in option_name.lower() else "size"

            for value in option_values:
                # 生成选择器（需要实际测试调整）
                selector = f'button[data-option-value="{value}"], .variant-option:has-text("{value}")'

                variants.append(ProductVariant(
                    name=value,
                    type=variant_type,
                    selector=selector,
                    available=True  # 需要进一步检查库存
                ))

        return variants

    def _parse_product_html(self, product_url: str) -> Product:
        """后备方案：解析HTML"""
        response = self.session.get(product_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 基础提取逻辑
        title = soup.find('h1')
        title_text = title.get_text(strip=True) if title else "Unknown"

        # 从URL生成ID
        product_id = product_url.split('/')[-1].replace('-', '_')

        # 简化版本，实际需要更复杂的逻辑
        return Product(
            id=product_id,
            name=title_text,
            url=product_url,
            category="Unknown",
            price_min=0.0,
            price_max=0.0,
            selectors=Selectors(
                product_title="h1",
                product_price=".price",
                add_to_cart_button="button[name='add']"
            )
        )

    def discover_all_products(self, max_products: int = None) -> List[Product]:
        """
        自动发现网站所有商品

        Args:
            max_products: 最大商品数量限制

        Returns:
            Product对象列表
        """
        print(f"🔍 开始发现 {self.base_url} 的所有商品...")

        # 1. 发现所有分类
        collections = self.discover_collections()
        print(f"✅ 发现 {len(collections)} 个商品分类")

        # 2. 从每个分类获取商品
        all_product_urls = set()
        for collection_url in collections:
            products = self.get_products_from_collection(collection_url)
            all_product_urls.update(products)
            print(f"  📦 {collection_url}: {len(products)} 个商品")

        print(f"✅ 总共发现 {len(all_product_urls)} 个唯一商品")

        # 3. 提取每个商品的详细信息
        discovered_products = []
        for i, product_url in enumerate(list(all_product_urls)[:max_products], 1):
            print(f"  📝 提取 ({i}/{len(all_product_urls)}): {product_url}")
            try:
                product = self.extract_product_info(product_url)
                discovered_products.append(product)
            except Exception as e:
                print(f"  ❌ 失败: {e}")

        print(f"🎉 成功提取 {len(discovered_products)} 个商品信息")

        return discovered_products
```

**任务**:
- [ ] T1.1.1: 实现分类发现逻辑
- [ ] T1.1.2: 实现Shopify JSON API解析
- [ ] T1.1.3: 实现HTML后备解析
- [ ] T1.1.4: 实现变体提取逻辑
- [ ] T1.1.5: 添加错误处理和重试

#### 增量 1.2: 产品发现脚本

```python
# 文件: scripts/discover_products.py

import json
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.crawler import ProductCrawler
from core.models import Product

def save_products(products: list[Product], output_path: str = "data/discovered_products.json"):
    """保存发现的商品到JSON文件"""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # 转换为JSON可序列化格式
    products_data = {
        'last_updated': datetime.now().isoformat(),
        'total_products': len(products),
        'products': [p.model_dump(mode='json') for p in products]
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(products_data, f, indent=2, ensure_ascii=False)

    print(f"✅ 已保存 {len(products)} 个商品到 {output_file}")

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='发现Fiido网站所有商品')
    parser.add_argument('--base-url', default='https://fiido.com', help='网站基础URL')
    parser.add_argument('--max-products', type=int, help='最大商品数量')
    parser.add_argument('--output', default='data/discovered_products.json', help='输出文件路径')

    args = parser.parse_args()

    # 创建爬虫实例
    crawler = ProductCrawler(base_url=args.base_url)

    # 发现所有商品
    products = crawler.discover_all_products(max_products=args.max_products)

    # 保存结果
    save_products(products, args.output)

    # 统计信息
    print("\n📊 统计信息:")
    print(f"  总商品数: {len(products)}")

    categories = {}
    for p in products:
        categories[p.category] = categories.get(p.category, 0) + 1

    print(f"  分类分布:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"    {cat}: {count}")

    variants_count = sum(len(p.variants) for p in products)
    print(f"  变体总数: {variants_count}")

if __name__ == '__main__':
    main()
```

**使用示例**:
```bash
# 发现所有商品
python scripts/discover_products.py

# 限制数量（测试用）
python scripts/discover_products.py --max-products 10

# 自定义输出路径
python scripts/discover_products.py --output data/products_backup.json
```

**任务**:
- [ ] T1.2.1: 实现命令行参数解析
- [ ] T1.2.2: 实现结果保存逻辑
- [ ] T1.2.3: 添加统计信息输出
- [ ] T1.2.4: 添加进度显示
- [ ] T1.2.5: 实现增量更新（仅爬取新商品）

**Sprint 1 交付物**:
- ✅ 产品爬虫核心功能
- ✅ 自动发现所有商品
- ✅ 提取商品详细信息（价格、变体、分类）
- ✅ 保存为结构化JSON
- ✅ 命令行工具

---

### Sprint 2: 通用测试框架（第2-3周）

**目标**: 实现可测试任意商品的通用测试框架

#### 增量 2.1: 通用页面对象

```python
# 文件: pages/product_page.py

from playwright.async_api import Page
from typing import Optional
from core.models import Product, ProductVariant
from core.selector_manager import SelectorManager

class ProductPage:
    """通用商品页面对象"""

    def __init__(self, page: Page, product: Product):
        self.page = page
        self.product = product
        self.selector_mgr = SelectorManager()

    async def navigate(self):
        """导航到商品页"""
        await self.page.goto(str(self.product.url))
        await self.page.wait_for_load_state('networkidle')

    async def get_title(self) -> Optional[str]:
        """获取商品标题"""
        element = await self.selector_mgr.find_element(
            self.page,
            'product_title'
        )
        if element:
            return await element.text_content()
        return None

    async def get_price(self) -> Optional[str]:
        """获取商品价格"""
        element = await self.selector_mgr.find_element(
            self.page,
            'product_price'
        )
        if element:
            price_text = await element.text_content()
            return price_text.strip()
        return None

    async def select_variant(self, variant: ProductVariant) -> bool:
        """
        选择商品变体

        Args:
            variant: 变体对象

        Returns:
            是否成功选择
        """
        try:
            await self.page.click(variant.selector, timeout=3000)
            await self.page.wait_for_timeout(500)  # 等待价格更新
            return True
        except Exception as e:
            print(f"选择变体失败: {e}")
            return False

    async def add_to_cart(self) -> bool:
        """
        加入购物车

        Returns:
            是否成功加购
        """
        try:
            # 监听Console错误
            errors = []
            self.page.on('console',
                lambda msg: errors.append(msg.text())
                if msg.type == 'error' else None
            )

            # 点击加购按钮
            add_button = await self.selector_mgr.find_element(
                self.page,
                'add_to_cart_button'
            )

            if not add_button:
                return False

            await add_button.click()

            # 等待购物车更新
            cart_count = await self.selector_mgr.find_element(
                self.page,
                'cart_count'
            )

            if cart_count:
                await cart_count.wait_for(state='visible', timeout=5000)

            # 检查是否有错误
            if errors:
                print(f"加购时检测到错误: {errors}")
                return False

            return True

        except Exception as e:
            print(f"加购失败: {e}")
            return False

    async def is_in_stock(self) -> bool:
        """检查是否有货"""
        # 检查"售罄"按钮
        sold_out_selectors = [
            'button:has-text("Sold Out")',
            'button:has-text("Out of Stock")',
            'button[disabled]:has-text("Add")'
        ]

        for selector in sold_out_selectors:
            try:
                if await self.page.locator(selector).count() > 0:
                    return False
            except:
                pass

        return True
```

#### 增量 2.2: 测试模板与Fixtures

```python
# 文件: tests/conftest.py

import pytest
import json
from pathlib import Path
from playwright.async_api import async_playwright
from typing import Dict
from core.models import Product
from pages.product_page import ProductPage

@pytest.fixture(scope='session')
def discovered_products() -> Dict[str, Product]:
    """加载已发现的商品数据"""
    data_file = Path('data/discovered_products.json')

    if not data_file.exists():
        pytest.skip("未找到商品数据，请先运行 discover_products.py")

    with open(data_file) as f:
        data = json.load(f)

    products = {}
    for p_data in data['products']:
        product = Product(**p_data)
        products[product.id] = product

    return products

@pytest.fixture
def product_by_id(discovered_products):
    """通过ID获取商品"""
    def _get_product(product_id: str) -> Product:
        if product_id not in discovered_products:
            pytest.skip(f"商品 {product_id} 未找到")
        return discovered_products[product_id]

    return _get_product

@pytest.fixture
async def product_page_factory(page):
    """产品页面工厂"""
    async def _create_product_page(product: Product) -> ProductPage:
        product_page = ProductPage(page, product)
        await product_page.navigate()
        return product_page

    return _create_product_page

def pytest_generate_tests(metafunc):
    """动态生成测试用例"""
    if 'test_product' in metafunc.fixturenames:
        # 加载商品数据
        data_file = Path('data/discovered_products.json')
        if not data_file.exists():
            return

        with open(data_file) as f:
            data = json.load(f)

        products = [Product(**p) for p in data['products']]

        # 按优先级过滤
        priority = metafunc.config.getoption('--priority', None)
        if priority:
            products = [p for p in products if p.priority == priority]

        # 按分类过滤
        category = metafunc.config.getoption('--category', None)
        if category:
            products = [p for p in products if category.lower() in p.category.lower()]

        # 参数化测试
        metafunc.parametrize(
            'test_product',
            products,
            ids=[p.id for p in products]
        )

def pytest_addoption(parser):
    """添加自定义命令行选项"""
    parser.addoption('--priority', help='按优先级过滤: P0/P1/P2')
    parser.addoption('--category', help='按分类过滤')
    parser.addoption('--product-id', help='测试指定商品ID')
```

```python
# 文件: tests/test_all_products.py

import pytest
from playwright.async_api import Page
from core.models import Product
from pages.product_page import ProductPage

@pytest.mark.asyncio
async def test_product_page_loads(page: Page, test_product: Product, product_page_factory):
    """测试商品页面加载"""
    product_page = await product_page_factory(test_product)

    # 验证标题
    title = await product_page.get_title()
    assert title is not None, f"商品 {test_product.id} 标题未加载"

    # 验证标题包含商品名称或商品名称包含标题
    assert (
        test_product.name.lower() in title.lower() or
        title.lower() in test_product.name.lower()
    ), f"标题不匹配: 期望 '{test_product.name}', 实际 '{title}'"

@pytest.mark.asyncio
async def test_product_price_displays(page: Page, test_product: Product, product_page_factory):
    """测试商品价格显示"""
    product_page = await product_page_factory(test_product)

    # 验证价格
    price = await product_page.get_price()
    assert price is not None, f"商品 {test_product.id} 价格未显示"

    # 验证价格包含货币符号或数字
    import re
    assert re.search(r'[\d,\.]+', price), f"价格格式异常: {price}"

@pytest.mark.asyncio
async def test_product_add_to_cart(page: Page, test_product: Product, product_page_factory):
    """测试商品加入购物车"""
    product_page = await product_page_factory(test_product)

    # 检查库存
    in_stock = await product_page.is_in_stock()
    if not in_stock:
        pytest.skip(f"商品 {test_product.id} 缺货")

    # 选择第一个变体（如果有）
    if test_product.variants:
        first_variant = test_product.variants[0]
        variant_selected = await product_page.select_variant(first_variant)
        if not variant_selected:
            pytest.skip(f"无法选择变体 {first_variant.name}")

    # 加入购物车
    success = await product_page.add_to_cart()
    assert success, f"商品 {test_product.id} 加购失败"

    # 失败时截图
    if not success:
        await page.screenshot(
            path=f'screenshots/{test_product.id}_add_to_cart_failed.png',
            full_page=True
        )

@pytest.mark.asyncio
@pytest.mark.variants
async def test_product_variant_selection(page: Page, test_product: Product, product_page_factory):
    """测试商品变体选择"""
    if not test_product.variants:
        pytest.skip(f"商品 {test_product.id} 无变体")

    product_page = await product_page_factory(test_product)

    # 测试每个变体
    for variant in test_product.variants[:3]:  # 最多测试3个变体
        success = await product_page.select_variant(variant)
        assert success, f"变体 {variant.name} 选择失败"

        # 等待价格更新
        await page.wait_for_timeout(500)

        # 验证价格显示
        price = await product_page.get_price()
        assert price is not None, f"选择变体 {variant.name} 后价格未更新"
```

**使用示例**:
```bash
# 测试所有商品
pytest tests/test_all_products.py -v

# 仅测试P0商品
pytest tests/test_all_products.py --priority=P0

# 仅测试电动自行车分类
pytest tests/test_all_products.py --category="Electric Bikes"

# 测试指定商品
pytest tests/test_all_products.py --product-id=fiido_d11

# 并行测试（4个worker）
pytest tests/test_all_products.py -n 4

# 失败时截图
pytest tests/test_all_products.py --screenshot=only-on-failure
```

**任务**:
- [ ] T2.2.1: 实现pytest fixtures
- [ ] T2.2.2: 实现动态测试生成
- [ ] T2.2.3: 实现商品过滤逻辑
- [ ] T2.2.4: 创建通用测试用例
- [ ] T2.2.5: 添加失败截图功能

**Sprint 2 交付物**:
- ✅ 通用页面对象模型
- ✅ 参数化测试框架
- ✅ 可测试任意商品
- ✅ 支持过滤和选择性测试
- ✅ 自动截图功能

---

### Sprint 3: 完整购物流程（第4-5周）

**目标**: 实现结账流程测试

#### 增量 3.1: 购物车页面

```python
# 文件: pages/cart_page.py

from playwright.async_api import Page
from core.selector_manager import SelectorManager
from typing import List, Dict

class CartPage:
    """购物车页面"""

    def __init__(self, page: Page):
        self.page = page
        self.selector_mgr = SelectorManager()

    async def navigate(self):
        """导航到购物车"""
        await self.page.goto('https://fiido.com/cart')
        await self.page.wait_for_load_state('networkidle')

    async def get_cart_items(self) -> List[Dict]:
        """获取购物车商品"""
        items = []

        # Shopify购物车通常有 .cart-item 类
        cart_items = self.page.locator('.cart-item, .cart__item')
        count = await cart_items.count()

        for i in range(count):
            item = cart_items.nth(i)

            # 提取商品信息
            name_el = item.locator('.cart-item__name, .cart__item-title').first
            price_el = item.locator('.cart-item__price, .price').first
            qty_el = item.locator('input[type="number"], .cart-item__quantity').first

            item_data = {
                'name': await name_el.text_content() if await name_el.count() > 0 else '',
                'price': await price_el.text_content() if await price_el.count() > 0 else '',
                'quantity': await qty_el.input_value() if await qty_el.count() > 0 else '1'
            }

            items.append(item_data)

        return items

    async def get_total_price(self) -> str:
        """获取总价"""
        total_el = await self.selector_mgr.find_element(self.page, 'cart_total')
        if not total_el:
            # 后备选择器
            total_el = self.page.locator('.cart__total, .cart-total-price').first

        if await total_el.count() > 0:
            return await total_el.text_content()
        return ""

    async def proceed_to_checkout(self):
        """进入结账"""
        checkout_btn = await self.selector_mgr.find_element(self.page, 'checkout_button')
        if checkout_btn:
            await checkout_btn.click()
        else:
            # 后备
            await self.page.click('button:has-text("Checkout"), a:has-text("Checkout")')
```

#### 增量 3.2: 结账流程测试

```python
# 文件: tests/test_checkout_flow.py

import pytest
from playwright.async_api import Page
from core.models import Product
from pages.product_page import ProductPage
from pages.cart_page import CartPage

# 测试地址数据
TEST_ADDRESSES = {
    "US": {
        "email": "test@fiido-test.com",
        "first_name": "John",
        "last_name": "Doe",
        "address": "123 Test Street",
        "city": "New York",
        "state": "NY",
        "postal_code": "10001",
        "country": "United States"
    },
    "DE": {
        "email": "test@fiido-test.com",
        "first_name": "Max",
        "last_name": "Mustermann",
        "address": "Teststraße 123",
        "city": "Berlin",
        "postal_code": "10115",
        "country": "Germany"
    }
}

@pytest.mark.asyncio
@pytest.mark.checkout
async def test_full_checkout_flow_us(page: Page, test_product: Product, product_page_factory):
    """测试完整结账流程（美国）"""
    # 1. 添加商品到购物车
    product_page = await product_page_factory(test_product)

    if not await product_page.is_in_stock():
        pytest.skip("商品缺货")

    success = await product_page.add_to_cart()
    assert success, "加购失败"

    # 2. 进入购物车
    cart_page = CartPage(page)
    await cart_page.navigate()

    # 验证商品在购物车中
    items = await cart_page.get_cart_items()
    assert len(items) > 0, "购物车为空"

    # 3. 进入结账
    await cart_page.proceed_to_checkout()

    # 等待结账页加载
    await page.wait_for_url('**/checkout/**', timeout=10000)

    # 4. 填写配送信息
    address = TEST_ADDRESSES["US"]

    await page.fill('input[name="email"]', address["email"])
    await page.fill('input[name="firstName"]', address["first_name"])
    await page.fill('input[name="lastName"]', address["last_name"])
    await page.fill('input[name="address1"]', address["address"])
    await page.fill('input[name="city"]', address["city"])
    await page.fill('input[name="postalCode"]', address["postal_code"])

    # 选择国家（如果需要）
    country_select = page.locator('select[name="countryCode"]')
    if await country_select.count() > 0:
        await country_select.select_option(label=address["country"])

    # 5. 验证运费计算
    await page.wait_for_timeout(2000)  # 等待运费计算

    # 检查是否有运费显示
    shipping_cost = page.locator('.shipping-cost, [data-shipping-cost]')
    if await shipping_cost.count() > 0:
        cost_text = await shipping_cost.text_content()
        assert cost_text, "运费未计算"

    # 6. 截图记录
    await page.screenshot(
        path=f'screenshots/checkout_{test_product.id}_us.png',
        full_page=True
    )

    # 注意：不实际提交订单，以免污染生产数据
```

**任务**:
- [ ] T3.2.1: 实现购物车页面对象
- [ ] T3.2.2: 实现结账流程测试
- [ ] T3.2.3: 添加多地区测试数据
- [ ] T3.2.4: 实现运费验证
- [ ] T3.2.5: 添加支付方式选择测试（不提交）

**Sprint 3 交付物**:
- ✅ 购物车页面对象
- ✅ 完整结账流程测试
- ✅ 多地区测试覆盖
- ✅ 运费计算验证
- ✅ 安全测试（不污染生产数据）

---

### Sprint 4: AI集成与优化（第6-7周）

**目标**: 添加AI分析和智能报告

#### 增量 4.1: AI报告生成

```python
# 文件: scripts/generate_ai_report.py

import json
import os
from pathlib import Path
from datetime import datetime
import anthropic

def generate_ai_report(test_results_path: str = 'test-results.json'):
    """生成AI驱动的测试报告"""

    # 加载测试结果
    with open(test_results_path) as f:
        results = json.load(f)

    # 调用Claude API
    client = anthropic.Anthropic(api_key=os.getenv('CLAUDE_API_KEY'))

    prompt = f"""你是Fiido电商网站的QA专家。分析以下自动化测试结果并生成专业报告。

测试结果摘要:
{json.dumps(results['summary'], indent=2, ensure_ascii=False)}

失败的测试:
{json.dumps(results.get('failures', [])[:10], indent=2, ensure_ascii=False)}

请生成包含以下内容的报告:

1. **执行摘要** (3-5句话)
   - 总体通过率
   - 关键问题数量
   - 测试覆盖情况

2. **失败分析** (按优先级分类)
   - P0: 严重问题（阻塞核心流程）
   - P1: 高优先级问题
   - P2: 一般问题

   每个失败提供:
   - 商品名称/ID
   - 失败原因
   - 影响范围
   - 建议修复方案

3. **趋势洞察**
   - 哪些商品分类失败率高
   - 是否有共同模式

4. **行动建议**
   - 优先修复项
   - 需要关注的区域

使用Markdown格式，清晰简洁。"""

    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )

    report = message.content[0].text

    # 保存报告
    report_path = Path('reports/latest-ai-report.md')
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"# Fiido E2E测试报告\n\n")
        f.write(f"**生成时间**: {datetime.now().isoformat()}\n\n")
        f.write(report)

    print(f"✅ AI报告已生成: {report_path}")

    return report

if __name__ == '__main__':
    generate_ai_report()
```

**任务**:
- [ ] T4.1.1: 实现测试结果收集
- [ ] T4.1.2: 集成Claude API
- [ ] T4.1.3: 设计报告提示词
- [ ] T4.1.4: 实现报告保存
- [ ] T4.1.5: 添加失败截图分析

**Sprint 4 交付物**:
- ✅ AI报告生成
- ✅ 失败分析
- ✅ 趋势洞察
- ✅ 智能建议

---

## 6. 核心组件设计

### 6.1 完整项目结构

```
fiido-shop-flow-guardian/
├── core/                         # 核心框架
│   ├── __init__.py
│   ├── crawler.py               # 产品爬虫
│   ├── models.py                # 数据模型
│   ├── selector_manager.py     # 选择器管理
│   └── test_generator.py       # 测试生成器
│
├── pages/                        # 页面对象
│   ├── __init__.py
│   ├── base_page.py
│   ├── product_page.py
│   ├── cart_page.py
│   └── checkout_page.py
│
├── tests/                        # 测试套件
│   ├── conftest.py
│   ├── test_all_products.py    # 所有商品测试
│   ├── test_checkout_flow.py  # 结账流程
│   └── generated/               # 自动生成的测试
│
├── config/                       # 配置文件
│   ├── selectors.json          # 选择器配置
│   ├── test_strategy.json      # 测试策略
│   └── regions.json            # 地区配置
│
├── data/                         # 数据存储
│   ├── discovered_products.json # 发现的商品
│   └── test_history.json       # 测试历史
│
├── scripts/                      # 工具脚本
│   ├── discover_products.py    # 产品发现
│   ├── add_product.py          # 添加单个产品
│   ├── generate_ai_report.py   # AI报告
│   └── send_alerts.py          # 告警发送
│
├── screenshots/                  # 截图
├── reports/                      # 报告
├── .github/workflows/           # CI/CD
│   └── e2e-test.yml
├── requirements.txt
├── pytest.ini
└── README.md
```

### 6.2 配置文件示例

```json
// config/selectors.json
{
  "version": "1.0",
  "platform": "shopify",
  "base_selectors": {
    "product_title": ".product__title, h1.product-title, [data-testid='product-title']",
    "product_price": ".price, .product__price, [data-testid='product-price']",
    "add_to_cart_button": "button[name='add'], button:has-text('Add to Cart'), .btn-add-to-cart",
    "cart_count": ".cart-count, .cart-item-count, [data-cart-count]",
    "cart_items": ".cart-item, .cart__item",
    "checkout_button": "button:has-text('Checkout'), a:has-text('Checkout'), [data-testid='checkout']",
    "cart_total": ".cart__total, .cart-total-price"
  },
  "variant_selectors": {
    "color": ".color-swatch button, [data-option='Color'] button",
    "size": ".size-option button, [data-option='Size'] button"
  },
  "checkout_selectors": {
    "email": "input[name='email'], #email",
    "first_name": "input[name='firstName'], #firstName",
    "last_name": "input[name='lastName'], #lastName",
    "address": "input[name='address1'], #address1",
    "city": "input[name='city'], #city",
    "postal_code": "input[name='postalCode'], #zip",
    "country": "select[name='countryCode'], #country"
  }
}
```

---

## 7. 使用指南

### 7.1 快速开始

```bash
# 1. 克隆项目
git clone <repository>
cd fiido-shop-flow-guardian

# 2. 安装依赖
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# 3. 发现所有商品
python scripts/discover_products.py

# 4. 运行测试
pytest tests/test_all_products.py -v

# 5. 生成AI报告
export CLAUDE_API_KEY="your-key"
python scripts/generate_ai_report.py
```

### 7.2 添加新产品

**方式1: 单个产品URL**
```bash
python scripts/add_product.py --url "https://fiido.com/products/fiido-x-pro"
```

**方式2: 重新发现所有商品**
```bash
python scripts/discover_products.py
```

**方式3: 手动配置**
```json
// 编辑 data/discovered_products.json
{
  "products": [
    {
      "id": "new_product",
      "name": "New Product Name",
      "url": "https://fiido.com/products/new-product",
      ...
    }
  ]
}
```

### 7.3 选择性测试

```bash
# 测试P0优先级商品
pytest tests/ --priority=P0

# 测试特定分类
pytest tests/ --category="Electric Bikes"

# 测试单个商品
pytest tests/ --product-id=fiido_d11

# 并行测试（4 workers）
pytest tests/ -n 4

# 仅测试加购功能
pytest tests/ -k "add_to_cart"
```

### 7.4 CI/CD集成

```yaml
# .github/workflows/e2e-test.yml
name: E2E Testing

on:
  schedule:
    - cron: '0 2 * * *'  # 每日凌晨2点
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install chromium

      - name: Discover products
        run: python scripts/discover_products.py --max-products 20

      - name: Run tests
        run: pytest tests/ -n 4 --json-report

      - name: Generate AI report
        env:
          CLAUDE_API_KEY: ${{ secrets.CLAUDE_API_KEY }}
        run: python scripts/generate_ai_report.py

      - name: Upload reports
        uses: actions/upload-artifact@v4
        with:
          name: test-reports
          path: reports/
```

---

## 8. 部署流水线

### 8.1 执行策略

| 时间 | 频率 | 范围 | 目的 |
|------|------|------|------|
| **02:00 UTC** | 每日 | 全量商品 | 全面检查 |
| **每4小时** | 每日6次 | P0商品 | 核心监控 |
| **PR时** | 每个PR | 变更相关 | 质量门禁 |
| **按需** | 手动 | 自定义 | 特定测试 |

### 8.2 告警策略

```python
# scripts/send_alerts.py

def should_alert(results):
    """判断是否发送告警"""
    # 通过率 < 90%
    if results['pass_rate'] < 0.9:
        return True, "通过率过低"

    # P0商品失败
    p0_failures = [f for f in results['failures'] if f.get('priority') == 'P0']
    if p0_failures:
        return True, f"{len(p0_failures)}个P0商品失败"

    # 连续失败
    if results.get('consecutive_failures', 0) >= 3:
        return True, "连续失败3次"

    return False, ""
```

---

## 9. 质量门禁

### 9.1 完成定义（DoD）

**每个Sprint**:
- [ ] 所有计划功能已实现
- [ ] 代码已审查
- [ ] 测试通过率 > 95%
- [ ] 文档已更新
- [ ] CI/CD流水线通过

**项目整体**:
- [ ] 可自动发现所有商品
- [ ] 仅需URL即可测试新产品
- [ ] AI报告生成正常
- [ ] 告警系统工作
- [ ] 性能 < 60分钟（全量测试）

### 9.2 成功指标

| 指标 | 目标 | 测量方式 |
|------|------|----------|
| **产品发现覆盖率** | 100% | 爬虫发现商品数 / 实际商品数 |
| **测试自动化率** | 100% | 无需手动编写新测试 |
| **新产品测试时间** | < 5分钟 | 从添加URL到测试完成 |
| **全量测试时间** | < 60分钟 | CI/CD运行时间 |
| **误报率** | < 5% | 重试通过的失败测试 |

---

## 10. 扩展指南

### 10.1 支持新产品

**步骤1: 添加产品URL**
```bash
python scripts/add_product.py --url "https://fiido.com/products/new-product"
```

**步骤2: 验证提取**
```bash
# 查看提取的商品信息
cat data/discovered_products.json | jq '.products[] | select(.id=="new_product")'
```

**步骤3: 运行测试**
```bash
pytest tests/ --product-id=new_product -v
```

### 10.2 支持新网站

修改`core/crawler.py`以支持非Shopify网站:

```python
class GenericCrawler(ProductCrawler):
    """通用电商网站爬虫"""

    def detect_platform(self) -> str:
        """自动检测电商平台"""
        # 检测Shopify
        if 'myshopify.com' in self.base_url or 'Shopify.theme' in response.text:
            return 'shopify'

        # 检测WooCommerce
        if 'woocommerce' in response.text:
            return 'woocommerce'

        # 其他平台...
        return 'generic'
```

### 10.3 自定义选择器

编辑`config/selectors.json`:

```json
{
  "custom_site_selectors": {
    "product_title": ".your-custom-title-class",
    "add_to_cart_button": "#your-custom-button-id"
  }
}
```

---

## 9. 用户界面（非技术人员使用）

### 9.1 设计目标

**问题**: 当前框架需要命令行操作，非技术人员难以使用
**解决方案**: 提供友好的Web界面或桌面应用

### 9.2 Web管理界面

#### 方案A: Flask Web应用（推荐）

**技术栈**:
- 后端: Flask + RESTful API
- 前端: Vue.js 3 + Element Plus
- 数据库: SQLite（开发）/ PostgreSQL（生产）

**项目结构**:
```
fiido-shop-flow-guardian/
├── web/                          # Web界面
│   ├── backend/                  # Flask后端
│   │   ├── app.py               # 主应用
│   │   ├── api/                 # API路由
│   │   │   ├── products.py      # 商品管理
│   │   │   ├── tests.py         # 测试执行
│   │   │   └── reports.py       # 报告查看
│   │   ├── models/              # 数据模型
│   │   └── tasks/               # 后台任务
│   └── frontend/                 # Vue前端
│       ├── src/
│       │   ├── views/           # 页面组件
│       │   ├── components/      # 可复用组件
│       │   └── api/             # API调用
│       └── dist/                # 构建输出
└── ... (原有文件)
```

**核心功能**:

```python
# 文件: web/backend/app.py

from flask import Flask, jsonify, request
from flask_cors import CORS
import subprocess
import json
from pathlib import Path

app = Flask(__name__)
CORS(app)

@app.route('/api/products/discover', methods=['POST'])
def discover_products():
    """发现商品API"""
    try:
        # 调用爬虫脚本
        result = subprocess.run(
            ['python', 'scripts/discover_products.py'],
            capture_output=True,
            text=True,
            timeout=300
        )

        # 读取结果
        with open('data/discovered_products.json') as f:
            products = json.load(f)

        return jsonify({
            'success': True,
            'total': products['total_products'],
            'products': products['products']
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/products', methods=['GET'])
def get_products():
    """获取商品列表"""
    data_file = Path('data/discovered_products.json')
    if not data_file.exists():
        return jsonify({'products': []})

    with open(data_file) as f:
        data = json.load(f)

    # 支持过滤
    category = request.args.get('category')
    priority = request.args.get('priority')

    products = data['products']
    if category:
        products = [p for p in products if category.lower() in p['category'].lower()]
    if priority:
        products = [p for p in products if p['priority'] == priority]

    return jsonify({'products': products, 'total': len(products)})

@app.route('/api/products/<product_id>', methods=['PUT'])
def update_product(product_id):
    """更新商品配置（优先级等）"""
    data_file = Path('data/discovered_products.json')
    with open(data_file) as f:
        products_data = json.load(f)

    update_data = request.json

    # 查找并更新商品
    for product in products_data['products']:
        if product['id'] == product_id:
            if 'priority' in update_data:
                product['priority'] = update_data['priority']
            break

    # 保存
    with open(data_file, 'w') as f:
        json.dump(products_data, f, indent=2)

    return jsonify({'success': True})

@app.route('/api/tests/run', methods=['POST'])
def run_tests():
    """运行测试API"""
    params = request.json

    # 构建pytest命令
    cmd = ['pytest', 'tests/test_all_products.py', '-v', '--json-report']

    if params.get('priority'):
        cmd.extend(['--priority', params['priority']])
    if params.get('category'):
        cmd.extend(['--category', params['category']])
    if params.get('product_id'):
        cmd.extend(['--product-id', params['product_id']])
    if params.get('parallel'):
        cmd.extend(['-n', str(params['parallel'])])

    # 异步执行（使用Celery或简单的后台线程）
    import threading

    def run_in_background():
        subprocess.run(cmd, capture_output=True, text=True)

    thread = threading.Thread(target=run_in_background)
    thread.start()

    return jsonify({'success': True, 'message': '测试已启动'})

@app.route('/api/tests/status', methods=['GET'])
def get_test_status():
    """获取测试状态"""
    # 读取最新测试结果
    results_file = Path('test-results.json')
    if not results_file.exists():
        return jsonify({'status': 'no_results'})

    with open(results_file) as f:
        results = json.load(f)

    return jsonify({
        'status': 'completed',
        'summary': results.get('summary', {}),
        'failures': results.get('failures', [])
    })

@app.route('/api/reports/latest', methods=['GET'])
def get_latest_report():
    """获取最新AI报告"""
    report_file = Path('reports/latest-ai-report.md')
    if not report_file.exists():
        return jsonify({'content': '暂无报告'})

    with open(report_file, encoding='utf-8') as f:
        content = f.read()

    return jsonify({'content': content})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

**前端页面示例**:

```vue
<!-- 文件: web/frontend/src/views/Dashboard.vue -->

<template>
  <div class="dashboard">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>测试概览</span>
          <el-button type="primary" @click="discoverProducts">
            🔍 发现商品
          </el-button>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="6">
          <el-statistic title="总商品数" :value="stats.total" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="测试通过" :value="stats.passed" suffix="个" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="测试失败" :value="stats.failed" suffix="个" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="通过率" :value="stats.passRate" suffix="%" />
        </el-col>
      </el-row>
    </el-card>

    <el-card class="box-card" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>商品列表</span>
          <el-space>
            <el-select v-model="filterPriority" placeholder="优先级">
              <el-option label="全部" value="" />
              <el-option label="P0" value="P0" />
              <el-option label="P1" value="P1" />
              <el-option label="P2" value="P2" />
            </el-select>
            <el-button type="success" @click="runTests">
              ▶️ 运行测试
            </el-button>
          </el-space>
        </div>
      </template>

      <el-table :data="products" style="width: 100%">
        <el-table-column prop="name" label="商品名称" width="300" />
        <el-table-column prop="category" label="分类" width="150" />
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="scope">
            <el-tag :type="getPriorityType(scope.row.priority)">
              {{ scope.row.priority }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="test_status" label="测试状态" width="120">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.test_status)">
              {{ scope.row.test_status || '未测试' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="testSingle(scope.row)">
              测试
            </el-button>
            <el-button size="small" @click="viewProduct(scope.row)">
              查看
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const stats = ref({
  total: 0,
  passed: 0,
  failed: 0,
  passRate: 0
})

const products = ref([])
const filterPriority = ref('')

const loadProducts = async () => {
  try {
    const response = await api.get('/products', {
      params: { priority: filterPriority.value }
    })
    products.value = response.data.products
    stats.value.total = response.data.total
  } catch (error) {
    ElMessage.error('加载商品失败')
  }
}

const discoverProducts = async () => {
  ElMessage.info('正在发现商品，请稍候...')
  try {
    const response = await api.post('/products/discover')
    ElMessage.success(`发现 ${response.data.total} 个商品`)
    await loadProducts()
  } catch (error) {
    ElMessage.error('发现商品失败')
  }
}

const runTests = async () => {
  try {
    await api.post('/tests/run', {
      priority: filterPriority.value,
      parallel: 4
    })
    ElMessage.success('测试已启动，请稍候查看结果')
  } catch (error) {
    ElMessage.error('启动测试失败')
  }
}

const testSingle = async (product) => {
  try {
    await api.post('/tests/run', {
      product_id: product.id
    })
    ElMessage.success(`开始测试 ${product.name}`)
  } catch (error) {
    ElMessage.error('启动测试失败')
  }
}

const getPriorityType = (priority) => {
  const types = { P0: 'danger', P1: 'warning', P2: 'info' }
  return types[priority] || 'info'
}

const getStatusType = (status) => {
  const types = { passing: 'success', failing: 'danger', flaky: 'warning' }
  return types[status] || 'info'
}

onMounted(() => {
  loadProducts()
})
</script>
```

**启动Web界面**:
```bash
# 后端
cd web/backend
python app.py

# 前端（开发模式）
cd web/frontend
npm install
npm run dev

# 访问: http://localhost:3000
```

### 9.3 桌面应用（可选）

#### 使用Electron打包

**优势**:
- 跨平台（Windows/macOS/Linux）
- 独立运行，无需安装Python
- 提供原生应用体验

**构建流程**:
```bash
# 安装Electron Builder
npm install -g electron-builder

# 打包
cd web/frontend
npm run build:electron

# 输出
# - fiido-test-guardian-1.0.0-win.exe  (Windows)
# - fiido-test-guardian-1.0.0.dmg      (macOS)
# - fiido-test-guardian-1.0.0.AppImage (Linux)
```

**发布**:
- 存放在内网文件服务器
- 或上传到GitHub Releases
- 用户下载安装即可使用

### 9.4 使用流程（非技术人员）

**步骤1: 打开应用**
```
Windows: 双击 fiido-test-guardian.exe
macOS: 打开 Fiido Test Guardian.app
Web: 访问 http://test-server:5000
```

**步骤2: 发现商品**
```
点击 "发现商品" 按钮
→ 系统自动爬取fiido.com所有商品
→ 显示商品列表（约2-3分钟）
```

**步骤3: 配置优先级**
```
选择商品 → 点击"编辑"
设置优先级: P0（核心）/ P1（重要）/ P2（普通）
保存
```

**步骤4: 运行测试**
```
方式1: 点击"全部测试"按钮
方式2: 筛选P0商品 → 点击"测试选中"
方式3: 单个商品 → 点击"测试"按钮
→ 测试运行中，显示进度条
```

**步骤5: 查看报告**
```
测试完成后，点击"查看报告"
→ 显示AI生成的测试报告
→ 失败商品高亮显示
→ 查看失败截图
```

**步骤6: 设置定时任务**
```
点击"设置" → "定时任务"
选择: 每日凌晨2点自动运行
保存 → 系统自动执行
```

---

## 10. 部署方案

### 10.1 部署选项对比

| 方案 | 适用场景 | 优点 | 缺点 |
|------|---------|------|------|
| **本地运行** | 个人开发/测试 | 简单、免费 | 需要本地环境 |
| **服务器部署** | 团队使用 | 集中管理、定时任务 | 需要服务器 |
| **Docker容器** | 任何环境 | 隔离、可移植 | 需要Docker |
| **云服务部署** | 无服务器维护 | 自动扩展、高可用 | 按使用付费 |
| **GitHub Actions** | CI/CD集成 | 免费额度、自动化 | 仅限定时/事件触发 |

### 10.2 Docker部署（推荐）

#### 方案优势
- ✅ 跨平台：Windows/macOS/Linux都能运行
- ✅ 环境隔离：无需安装Python、Playwright等依赖
- ✅ 一键启动：`docker-compose up`即可运行
- ✅ 易于迁移：可部署到任何支持Docker的环境

#### Dockerfile

```dockerfile
# 文件: Dockerfile

FROM python:3.11-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    lsb-release \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制requirements
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装Playwright浏览器
RUN playwright install chromium

# 复制项目文件
COPY . .

# 暴露端口（Web界面）
EXPOSE 5000

# 启动命令
CMD ["python", "web/backend/app.py"]
```

#### Docker Compose配置

```yaml
# 文件: docker-compose.yml

version: '3.8'

services:
  test-engine:
    build: .
    container_name: fiido-test-guardian
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./screenshots:/app/screenshots
      - ./reports:/app/reports
    environment:
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
      - TEST_BASE_URL=https://fiido.com
    restart: unless-stopped
    networks:
      - test-network

  # 可选: 定时任务调度器
  scheduler:
    image: mcuadros/ofelia:latest
    container_name: test-scheduler
    depends_on:
      - test-engine
    command: daemon --docker
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    labels:
      ofelia.job-run.discover.schedule: "0 0 2 * * *"  # 每日凌晨2点
      ofelia.job-run.discover.container: "fiido-test-guardian"
      ofelia.job-run.discover.command: "python scripts/discover_products.py"
    networks:
      - test-network

networks:
  test-network:
    driver: bridge
```

#### 一键启动

```bash
# 创建环境变量文件
cat > .env <<EOF
CLAUDE_API_KEY=your-api-key-here
EOF

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 访问Web界面
# http://localhost:5000
```

### 10.3 服务器部署

#### Ubuntu服务器部署

```bash
# 1. 安装依赖
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip git nginx

# 2. 克隆项目
cd /opt
sudo git clone <repository> fiido-test-guardian
cd fiido-test-guardian

# 3. 安装Python依赖
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium --with-deps

# 4. 配置环境变量
sudo nano /etc/environment
# 添加: CLAUDE_API_KEY=your-key

# 5. 创建systemd服务
sudo nano /etc/systemd/system/fiido-test-guardian.service
```

**Systemd服务配置**:
```ini
[Unit]
Description=Fiido Test Guardian Web Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/fiido-test-guardian
Environment="PATH=/opt/fiido-test-guardian/venv/bin"
Environment="CLAUDE_API_KEY=your-api-key"
ExecStart=/opt/fiido-test-guardian/venv/bin/python web/backend/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable fiido-test-guardian
sudo systemctl start fiido-test-guardian

# 查看状态
sudo systemctl status fiido-test-guardian
```

#### Nginx反向代理配置

```nginx
# 文件: /etc/nginx/sites-available/fiido-test-guardian

server {
    listen 80;
    server_name test.yourcompany.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket支持（如需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 静态文件
    location /reports/ {
        alias /opt/fiido-test-guardian/reports/;
        autoindex on;
    }

    location /screenshots/ {
        alias /opt/fiido-test-guardian/screenshots/;
        autoindex on;
    }
}
```

```bash
# 启用配置
sudo ln -s /etc/nginx/sites-available/fiido-test-guardian /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 定时任务配置

```bash
# 编辑crontab
crontab -e

# 添加定时任务
# 每日凌晨2点发现商品
0 2 * * * cd /opt/fiido-test-guardian && /opt/fiido-test-guardian/venv/bin/python scripts/discover_products.py

# 每日凌晨3点运行测试
0 3 * * * cd /opt/fiido-test-guardian && /opt/fiido-test-guardian/venv/bin/pytest tests/ -n 4

# 每日凌晨4点生成报告
0 4 * * * cd /opt/fiido-test-guardian && /opt/fiido-test-guardian/venv/bin/python scripts/generate_ai_report.py
```

### 10.4 Windows部署

#### 方案1: WSL2 + Docker（推荐）

```powershell
# 启用WSL2
wsl --install

# 安装Docker Desktop
# 下载: https://www.docker.com/products/docker-desktop/

# 在WSL2中运行
wsl
cd /mnt/c/Users/YourName/fiido-test-guardian
docker-compose up -d
```

#### 方案2: 原生Windows服务

```powershell
# 安装Python
# 下载: https://www.python.org/downloads/

# 安装依赖
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium

# 创建Windows服务（使用NSSM）
# 下载NSSM: https://nssm.cc/download
nssm install FiidoTestGuardian "C:\path\to\venv\Scripts\python.exe" "C:\path\to\web\backend\app.py"
nssm set FiidoTestGuardian AppDirectory "C:\path\to\fiido-test-guardian"
nssm start FiidoTestGuardian
```

#### Windows定时任务

```powershell
# 创建计划任务
$action = New-ScheduledTaskAction -Execute "C:\path\to\venv\Scripts\python.exe" -Argument "C:\path\to\scripts\discover_products.py" -WorkingDirectory "C:\path\to\fiido-test-guardian"

$trigger = New-ScheduledTaskTrigger -Daily -At 2am

Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "Fiido Product Discovery" -Description "自动发现Fiido商品"
```

### 10.5 云服务部署

#### AWS EC2部署

```bash
# 1. 创建EC2实例（Ubuntu 22.04）
# 选择: t3.medium（2vCPU, 4GB内存）

# 2. 配置安全组
# 开放端口: 22 (SSH), 80 (HTTP), 443 (HTTPS)

# 3. SSH连接
ssh -i your-key.pem ubuntu@ec2-xx-xx-xx-xx.compute.amazonaws.com

# 4. 按照Ubuntu服务器部署流程安装
```

#### Heroku部署

```bash
# 1. 安装Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# 2. 登录
heroku login

# 3. 创建应用
heroku create fiido-test-guardian

# 4. 添加构建包
heroku buildpacks:add heroku/python
heroku buildpacks:add https://github.com/heroku/heroku-buildpack-playwright

# 5. 设置环境变量
heroku config:set CLAUDE_API_KEY=your-key

# 6. 部署
git push heroku main

# 7. 打开应用
heroku open
```

### 10.6 部署验证

**验证清单**:
```bash
# 1. 检查服务运行状态
curl http://localhost:5000/api/health

# 2. 测试商品发现
curl -X POST http://localhost:5000/api/products/discover

# 3. 检查测试执行
curl http://localhost:5000/api/tests/status

# 4. 验证报告生成
curl http://localhost:5000/api/reports/latest

# 5. 检查定时任务
sudo systemctl status fiido-test-guardian
crontab -l
```

**性能监控**:
```bash
# CPU/内存使用
htop

# 磁盘空间
df -h

# 日志查看
journalctl -u fiido-test-guardian -f

# Docker日志
docker-compose logs -f test-engine
```

---

## 附录

### A. 环境要求

- **操作系统**: Ubuntu 22.04 / macOS / Windows
- **Python**: 3.11+
- **浏览器**: Chromium/Firefox（自动安装）
- **内存**: 最低4GB，推荐8GB
- **磁盘**: 最低2GB

### B. 常见问题

**Q: 如何处理需要登录的商品？**
```python
# 在conftest.py中添加登录fixture
@pytest.fixture(scope='session')
async def authenticated_context(browser):
    context = await browser.new_context()
    page = await context.new_page()

    # 登录
    await page.goto('https://fiido.com/account/login')
    await page.fill('#email', os.getenv('TEST_EMAIL'))
    await page.fill('#password', os.getenv('TEST_PASSWORD'))
    await page.click('button[type="submit"]')

    # 保存登录状态
    await context.storage_state(path='auth.json')
    await context.close()

    # 创建新context使用登录状态
    return await browser.new_context(storage_state='auth.json')
```

**Q: 如何测试不同语言版本？**
```python
# 添加语言参数
@pytest.mark.parametrize('lang', ['en', 'de', 'fr'])
async def test_product_multilang(page, test_product, lang):
    await page.goto(f"{test_product.url}?locale={lang}")
    ...
```

### C. 贡献指南

欢迎贡献！请遵循以下流程：

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交变更 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

---

**文档版本**: 2.1
**最后更新**: 2025-12-02
**状态**: 🚀 Sprint 3 已完成，进入 Sprint 4

---

## 11. 当前开发进度

### 11.1 已完成的 Sprint

#### ✅ Sprint 0: 框架搭建（已完成）
**完成时间**: 2025-11-28
**版本标签**: v1.0.0

**交付物**:
- ✅ 完整项目结构
- ✅ 核心数据模型 (core/models.py)
- ✅ 选择器管理系统 (core/selector_manager.py)
- ✅ 配置文件模板

#### ✅ Sprint 1: 产品爬虫开发（已完成）
**完成时间**: 2025-11-29
**版本标签**: v1.1.0

**交付物**:
- ✅ 产品爬虫核心功能 (core/crawler.py)
- ✅ 自动发现所有商品
- ✅ 提取商品详细信息（价格、变体、分类）
- ✅ 保存为结构化JSON
- ✅ 命令行工具 (scripts/discover_products.py)

**关键成果**:
- 成功爬取 Fiido.com 所有商品
- 支持 Shopify JSON API 和 HTML 后备解析
- 自动提取商品变体和选择器

#### ✅ Sprint 2: 通用测试框架（已完成）
**完成时间**: 2025-11-30
**版本标签**: v1.2.0

**交付物**:
- ✅ 通用页面对象模型 (pages/product_page.py)
- ✅ 参数化测试框架 (tests/conftest.py)
- ✅ 可测试任意商品
- ✅ 支持过滤和选择性测试
- ✅ 自动截图功能
- ✅ 动态测试模板

**关键成果**:
- 实现 SelectorManager 智能选择器管理
- 动态生成测试用例，无需手动编写
- 支持按优先级、分类过滤测试
- 失败自动截图，便于调试

#### ✅ Sprint 3: 完整购物流程 + AI 智能报告（已完成）
**完成时间**: 2025-12-02
**版本标签**: v1.3.0

**交付物**:
- ✅ 购物车页面对象 (pages/cart_page.py)
- ✅ 结账页面对象 (pages/checkout_page.py)
- ✅ 完整结账流程测试
- ✅ 端到端测试覆盖 (tests/e2e/test_full_checkout_flow.py)
- ✅ AI 智能报告生成 (scripts/generate_universal_ai_report.py)
- ✅ 支持 DeepSeek 和 Claude 双 AI 提供商
- ✅ 测试结果收集器 (core/test_result_collector.py)
- ✅ 完整测试文档体系

**关键成果**:
- 实现商品页 → 购物车 → 结账完整流程测试
- 集成免费 DeepSeek API，国内可用，每日 500 万 tokens
- AI 报告包含失败分析、修复建议、趋势洞察
- 单元测试 + 集成测试 + E2E 测试三层覆盖
- 文档完整度 100%，包含快速开始、测试指南、AI 配置指南

**测试覆盖率**: 90%+

### 11.2 当前状态（2025-12-02）

**项目进度**: Sprint 3 完成，准备进入 Sprint 4

**代码仓库**: https://github.com/yzh317179958/fiido-shop-flow-guardian

**最新版本**: v1.3.0

**核心功能状态**:
| 功能模块 | 状态 | 完成度 |
|---------|------|--------|
| 商品爬虫 | ✅ 完成 | 100% |
| 通用测试框架 | ✅ 完成 | 100% |
| 购物车测试 | ✅ 完成 | 100% |
| 结账流程测试 | ✅ 完成 | 100% |
| AI 智能报告 | ✅ 完成 | 100% |
| CI/CD 集成 | ⏳ 待开发 | 0% |
| 告警监控 | ⏳ 待开发 | 0% |
| Web 管理界面 | ⏳ 待开发 | 0% |

---

## 12. Sprint 4 开发计划：高级功能与自动化

### 12.1 Sprint 4 目标

**主题**: CI/CD 集成、性能优化、告警监控

**周期**: 第 6-7 周

**核心目标**:
1. ✅ 实现 GitHub Actions 自动化测试
2. ✅ 建立告警和监控系统
3. ✅ 优化测试性能和并行执行
4. 🎯 (可选) 提供 Web 管理界面

### 12.2 增量开发计划

#### 增量 4.1: GitHub Actions CI/CD 集成 (优先级: P0)

**目标**: 实现自动化测试和部署流水线

**任务清单**:
- [ ] T4.1.1: 创建基础 CI/CD 工作流文件
- [ ] T4.1.2: 配置定时测试任务（每日/每周）
- [ ] T4.1.3: 实现测试报告自动上传
- [ ] T4.1.4: 配置 Secrets 管理（API Keys）
- [ ] T4.1.5: 实现 PR 触发测试
- [ ] T4.1.6: 添加测试结果徽章到 README

**交付物**:
```
.github/
├── workflows/
│   ├── daily-test.yml         # 每日全量测试
│   ├── hourly-p0-test.yml     # 每小时 P0 测试
│   ├── pr-test.yml            # PR 触发测试
│   └── weekly-full-test.yml   # 每周完整测试
└── CONTRIBUTING.md            # 贡献指南
```

**实现要点**:
```yaml
# .github/workflows/daily-test.yml
name: Daily E2E Test

on:
  schedule:
    - cron: '0 2 * * *'  # 每日凌晨 2 点（UTC）
  workflow_dispatch:      # 支持手动触发

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install chromium --with-deps

      - name: Run tests
        run: |
          pytest tests/ -v -n 4 \
            --html=reports/test-report.html \
            --self-contained-html

      - name: Generate AI report
        if: always()
        env:
          DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
        run: |
          python scripts/generate_universal_ai_report.py \
            --provider deepseek \
            --output reports/ai-report.md

      - name: Upload reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-reports-${{ github.run_number }}
          path: |
            reports/
            screenshots/
          retention-days: 30

      - name: Check test results
        if: failure()
        run: |
          python scripts/send_alerts.py \
            --channel slack \
            --message "Daily test failed! Check reports."
```

#### 增量 4.2: 告警与监控系统 (优先级: P0)

**目标**: 实现智能告警，测试失败时及时通知

**任务清单**:
- [ ] T4.2.1: 实现告警策略引擎
- [ ] T4.2.2: 集成 Slack 通知
- [ ] T4.2.3: 集成邮件通知
- [ ] T4.2.4: 集成企业微信通知（可选）
- [ ] T4.2.5: 实现测试历史追踪
- [ ] T4.2.6: 添加趋势分析和异常检测

**交付物**:
```
scripts/
├── send_alerts.py              # 告警发送脚本
├── check_test_health.py        # 测试健康检查
└── analyze_trends.py           # 趋势分析

core/
├── alert_engine.py             # 告警引擎
└── notification_channels.py   # 通知渠道

config/
└── alert_config.json           # 告警配置
```

**实现要点**:
```python
# scripts/send_alerts.py

import os
import json
import requests
from typing import Dict, List
from datetime import datetime

class AlertEngine:
    """告警引擎"""

    def __init__(self, config_path='config/alert_config.json'):
        self.config = self._load_config(config_path)

    def should_alert(self, test_results: Dict) -> tuple[bool, str]:
        """
        判断是否触发告警

        Returns:
            (是否告警, 告警原因)
        """
        reasons = []

        # 规则1: 通过率低于阈值
        pass_rate = test_results.get('pass_rate', 0)
        threshold = self.config['thresholds']['pass_rate']
        if pass_rate < threshold:
            reasons.append(f"通过率 {pass_rate:.1%} 低于阈值 {threshold:.1%}")

        # 规则2: P0 商品失败
        p0_failures = [
            f for f in test_results.get('failures', [])
            if f.get('priority') == 'P0'
        ]
        if p0_failures:
            reasons.append(f"{len(p0_failures)} 个 P0 核心商品测试失败")

        # 规则3: 连续失败次数
        consecutive = test_results.get('consecutive_failures', 0)
        if consecutive >= 3:
            reasons.append(f"连续失败 {consecutive} 次")

        # 规则4: 失败数量突增
        current_failures = len(test_results.get('failures', []))
        avg_failures = test_results.get('avg_failures_last_7_days', 0)
        if current_failures > avg_failures * 2:
            reasons.append(f"失败数量突增：{current_failures} (平均: {avg_failures})")

        return len(reasons) > 0, '\n'.join(reasons)

    def send_alert(self, channel: str, message: str, results: Dict):
        """发送告警"""
        if channel == 'slack':
            self._send_slack(message, results)
        elif channel == 'email':
            self._send_email(message, results)
        elif channel == 'wechat':
            self._send_wechat(message, results)

    def _send_slack(self, message: str, results: Dict):
        """发送 Slack 通知"""
        webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        if not webhook_url:
            print("⚠️ SLACK_WEBHOOK_URL 未配置")
            return

        # 构建富文本消息
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🚨 Fiido E2E 测试告警"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*通过率:*\n{results['pass_rate']:.1%}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*失败数:*\n{len(results['failures'])}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*测试时间:*\n{results['timestamp']}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*运行ID:*\n{results.get('run_id', 'N/A')}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*告警原因:*\n```{message}```"
                }
            }
        ]

        # 添加失败商品列表
        if results.get('failures'):
            failure_list = '\n'.join([
                f"• {f['product_name']} ({f['priority']})"
                for f in results['failures'][:5]
            ])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Top 5 失败商品:*\n{failure_list}"
                }
            })

        # 添加报告链接
        if results.get('report_url'):
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "查看完整报告"
                        },
                        "url": results['report_url']
                    }
                ]
            })

        payload = {"blocks": blocks}

        response = requests.post(webhook_url, json=payload)
        if response.status_code == 200:
            print("✅ Slack 告警已发送")
        else:
            print(f"❌ Slack 告警发送失败: {response.text}")

    def _send_email(self, message: str, results: Dict):
        """发送邮件通知"""
        # 使用 SendGrid 或 AWS SES
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        sender = os.getenv('ALERT_EMAIL_SENDER')
        recipients = os.getenv('ALERT_EMAIL_RECIPIENTS', '').split(',')
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_user = os.getenv('SMTP_USER')
        smtp_password = os.getenv('SMTP_PASSWORD')

        if not all([sender, recipients, smtp_user, smtp_password]):
            print("⚠️ 邮件配置不完整")
            return

        # 创建邮件
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🚨 Fiido E2E 测试告警 - 通过率 {results['pass_rate']:.1%}"
        msg['From'] = sender
        msg['To'] = ', '.join(recipients)

        # HTML 邮件内容
        html = f"""
        <html>
          <body>
            <h2>🚨 Fiido E2E 测试告警</h2>
            <table border="1" cellpadding="5">
              <tr><td><b>通过率</b></td><td>{results['pass_rate']:.1%}</td></tr>
              <tr><td><b>失败数量</b></td><td>{len(results['failures'])}</td></tr>
              <tr><td><b>测试时间</b></td><td>{results['timestamp']}</td></tr>
            </table>
            <h3>告警原因:</h3>
            <pre>{message}</pre>
            <h3>失败商品:</h3>
            <ul>
              {''.join([f"<li>{f['product_name']} ({f['priority']})</li>" for f in results['failures'][:10]])}
            </ul>
            <p><a href="{results.get('report_url', '#')}">查看完整报告</a></p>
          </body>
        </html>
        """

        msg.attach(MIMEText(html, 'html'))

        # 发送邮件
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            print("✅ 邮件告警已发送")
        except Exception as e:
            print(f"❌ 邮件发送失败: {e}")

# 使用示例
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='发送测试告警')
    parser.add_argument('--channel', choices=['slack', 'email', 'wechat'], required=True)
    parser.add_argument('--results-file', default='reports/test-results.json')

    args = parser.parse_args()

    # 加载测试结果
    with open(args.results_file) as f:
        results = json.load(f)

    # 检查是否需要告警
    engine = AlertEngine()
    should_alert, reason = engine.should_alert(results)

    if should_alert:
        print(f"🚨 触发告警: {reason}")
        engine.send_alert(args.channel, reason, results)
    else:
        print("✅ 测试通过，无需告警")
```

**告警配置文件**:
```json
// config/alert_config.json
{
  "version": "1.0",
  "enabled": true,
  "thresholds": {
    "pass_rate": 0.90,
    "consecutive_failures": 3,
    "failure_spike_multiplier": 2.0
  },
  "channels": {
    "slack": {
      "enabled": true,
      "webhook_env": "SLACK_WEBHOOK_URL",
      "mention_users": ["@qa-team", "@dev-team"]
    },
    "email": {
      "enabled": true,
      "recipients": ["qa@company.com", "dev@company.com"],
      "smtp_config_env": "SMTP_CONFIG"
    }
  },
  "quiet_hours": {
    "enabled": false,
    "start": "22:00",
    "end": "08:00",
    "timezone": "Asia/Shanghai"
  }
}
```

#### 增量 4.3: 性能优化 (优先级: P1)

**目标**: 提升测试执行效率，减少运行时间

**任务清单**:
- [ ] T4.3.1: 实现智能并行测试
- [ ] T4.3.2: 优化商品爬虫缓存机制
- [ ] T4.3.3: 实现增量测试（仅测试变更商品）
- [ ] T4.3.4: 优化页面加载等待策略
- [ ] T4.3.5: 添加测试执行时间分析

**交付物**:
- 并行测试配置优化
- 爬虫缓存系统
- 增量测试逻辑
- 性能分析报告

#### 增量 4.4: Web 管理界面 (优先级: P2, 可选)

**目标**: 为非技术人员提供友好的 Web 界面

**说明**: 此功能为可选项，如果有非技术人员需要使用，可以开发。

### 12.3 Sprint 4 完成定义 (DoD)

- [ ] GitHub Actions 工作流正常运行
- [ ] 定时测试每日自动执行
- [ ] 测试失败时能收到告警通知
- [ ] 测试报告自动生成和上传
- [ ] 并行测试提升效率 50%+
- [ ] 文档更新完整
- [ ] 所有功能有单元测试覆盖

### 12.4 Sprint 4 成功指标

| 指标 | 目标 | 测量方式 |
|------|------|----------|
| **自动化率** | 100% | 无需手动触发测试 |
| **告警响应时间** | < 5 分钟 | 从失败到收到通知 |
| **测试执行时间** | < 30 分钟 | 全量测试并行执行 |
| **CI/CD 成功率** | > 95% | Actions 成功运行次数 / 总次数 |

---

**后续步骤**:
1. ✅ 更新文档记录当前进度
2. 🚀 开始 Sprint 4.1: GitHub Actions CI/CD 集成
3. 📝 创建 Sprint 4 详细开发文档
