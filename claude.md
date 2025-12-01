# Claude Code 开发规范与要求

**项目名称**: Fiido Shop Flow Guardian - 电商自动化测试框架
**开发方法**: 渐进式增量开发（Incremental Development）
**质量标准**: 测试驱动、零破坏、持续集成
**创建时间**: 2025-12-03

---

## 一、核心开发原则

### 1.1 小步渐进式开发

**原则说明**：每次开发仅完成一个小的、独立的功能模块，避免一次性大规模改动。

**具体要求**：

1. **单一职责**
   - 每次开发仅聚焦于一个功能点
   - 每个 commit 只包含一个逻辑变更
   - 功能模块之间保持独立性

2. **增量交付**
   - 按照 Sprint 0-4 的顺序逐步实现
   - 每个 Sprint 内部按照任务清单（T1.1.1, T1.1.2...）顺序开发
   - 先实现核心功能，后实现扩展功能

3. **可回退性**
   - 每个增量必须是可独立回退的
   - 使用 Git 进行版本控制，每个功能点一个分支
   - 合并前必须通过测试

**示例**：
```
错误做法：一次性开发完整的 ProductCrawler 类（500行代码）
正确做法：
  Step 1: 实现 discover_collections() 方法（50行代码）→ 测试
  Step 2: 实现 get_products_from_collection() 方法（80行代码）→ 测试
  Step 3: 实现 extract_product_info() 方法（100行代码）→ 测试
```

---

### 1.2 测试优先开发（Test-First Development）

**原则说明**：每次开发新功能后，必须立即编写并运行测试，确保功能正确。

**具体要求**：

1. **开发流程**
   ```
   编写功能代码 → 编写测试用例 → 运行测试 → 修复问题 → 再次测试 → 提交代码
   ```

2. **测试覆盖要求**
   - 每个新增的类必须有对应的测试文件
   - 每个公共方法必须有至少 1 个测试用例
   - 关键业务逻辑必须有正反两种测试用例（正常情况 + 异常情况）

3. **测试类型**
   - **单元测试**：测试单个函数/方法的正确性
   - **集成测试**：测试多个模块协同工作的正确性
   - **端到端测试**：测试完整业务流程的正确性

**示例**：
```python
# 开发 ProductCrawler.discover_collections() 后，立即编写测试

# 文件: tests/test_crawler.py
import pytest
from core.crawler import ProductCrawler

def test_discover_collections():
    """测试发现商品分类功能"""
    crawler = ProductCrawler("https://fiido.com")
    collections = crawler.discover_collections()

    # 验证返回类型
    assert isinstance(collections, list)

    # 验证返回结果不为空
    assert len(collections) > 0

    # 验证 URL 格式正确
    for url in collections:
        assert url.startswith("https://fiido.com/collections/")

# 运行测试
# pytest tests/test_crawler.py::test_discover_collections -v
```

---

### 1.3 零破坏原则（Non-Breaking Changes）

**原则说明**：新增功能不能破坏已有功能，所有已通过的测试必须继续通过。

**具体要求**：

1. **向后兼容**
   - 修改已有函数时，保持函数签名不变（参数、返回值）
   - 如需改变接口，使用 `@deprecated` 标记旧接口，同时提供新接口
   - 保留旧接口至少一个版本周期

2. **回归测试**
   - 每次提交代码前，运行全量测试套件
   - 确保所有已有测试用例仍然通过
   - 如有测试失败，必须修复后才能提交

3. **兼容性验证**
   ```bash
   # 提交代码前必须执行的检查清单

   # 1. 运行全量测试
   pytest tests/ -v

   # 2. 检查代码覆盖率
   pytest tests/ --cov=core --cov=pages --cov-report=html

   # 3. 代码风格检查
   flake8 core/ pages/ tests/

   # 4. 类型检查（如使用 type hints）
   mypy core/ pages/
   ```

**示例**：
```python
# 错误做法：直接修改函数签名
# 原函数
def extract_product_info(product_url: str) -> Product:
    pass

# 修改后（破坏了兼容性）
def extract_product_info(product_url: str, include_reviews: bool) -> Product:
    pass

# 正确做法：添加可选参数
def extract_product_info(product_url: str, include_reviews: bool = False) -> Product:
    """
    提取商品信息

    Args:
        product_url: 商品URL
        include_reviews: 是否包含用户评论（默认 False，保持向后兼容）
    """
    pass
```

---

### 1.4 扩展式开发（Extension-Based Development）

**原则说明**：通过扩展而非修改来实现新功能，遵循开闭原则（Open-Closed Principle）。

**具体要求**：

1. **使用继承扩展**
   ```python
   # 基础类
   class ProductCrawler:
       def extract_product_info(self, url: str) -> Product:
           # 基础实现
           pass

   # 扩展类（新增功能，不修改基础类）
   class EnhancedProductCrawler(ProductCrawler):
       def extract_product_info(self, url: str) -> Product:
           # 调用父类方法
           product = super().extract_product_info(url)

           # 新增功能：提取用户评论
           product.reviews = self._extract_reviews(url)
           return product

       def _extract_reviews(self, url: str) -> list:
           # 新功能实现
           pass
   ```

2. **使用配置扩展**
   ```python
   # 通过配置文件扩展功能，而非修改代码

   # config/selectors.json（原有配置）
   {
       "product_title": ".product-title",
       "product_price": ".product-price"
   }

   # 扩展配置（新增字段，不删除旧字段）
   {
       "product_title": ".product-title",
       "product_price": ".product-price",
       "product_reviews": ".reviews-section"  # 新增
   }
   ```

3. **使用插件扩展**
   ```python
   # 使用插件机制扩展功能

   class TestRunner:
       def __init__(self):
           self.plugins = []

       def register_plugin(self, plugin):
           """注册插件"""
           self.plugins.append(plugin)

       def run_tests(self):
           # 运行测试前执行插件钩子
           for plugin in self.plugins:
               plugin.before_test()

           # 运行测试...

           # 运行测试后执行插件钩子
           for plugin in self.plugins:
               plugin.after_test()
   ```

---

## 二、开发流程规范

### 2.1 分支管理策略

**主分支**：
- `main`：生产环境代码，始终保持稳定
- `develop`：开发主分支，集成所有功能

**功能分支**：
- `feature/sprint0-project-setup`：Sprint 0 功能分支
- `feature/sprint1-crawler`：Sprint 1 功能分支
- `feature/T1.1.1-discover-collections`：单个任务分支

**分支流程**：
```bash
# 1. 从 develop 创建功能分支
git checkout develop
git pull origin develop
git checkout -b feature/T1.1.1-discover-collections

# 2. 开发功能并提交
git add core/crawler.py tests/test_crawler.py
git commit -m "实现商品分类发现功能 (T1.1.1)

- 实现 ProductCrawler.discover_collections() 方法
- 支持从 Shopify 网站自动发现所有商品分类
- 添加单元测试，覆盖正常和异常情况
- 测试通过率: 100%"

# 3. 推送到远程
git push origin feature/T1.1.1-discover-collections

# 4. 创建 Pull Request（合并到 develop）
# 在 GitHub/GitLab 上创建 PR，填写描述和测试结果

# 5. 代码审查通过后合并
git checkout develop
git merge feature/T1.1.1-discover-collections
git push origin develop

# 6. 删除功能分支
git branch -d feature/T1.1.1-discover-collections
```

---

### 2.2 提交规范（Commit Message）

**格式要求**：
```
<类型>: <简短描述>（不超过 50 字符）

<详细说明>（可选，换行后填写）

- 变更点 1
- 变更点 2
- 测试结果
- 相关任务编号
```

**类型标识**：
- `feat`: 新功能
- `fix`: Bug 修复
- `test`: 添加测试
- `refactor`: 代码重构（不改变功能）
- `docs`: 文档更新
- `style`: 代码格式调整（不影响逻辑）
- `chore`: 构建/工具配置变更

**示例**：
```
feat: 实现商品分类自动发现功能 (T1.1.1)

- 添加 ProductCrawler.discover_collections() 方法
- 支持从 Shopify /collections 页面提取所有分类链接
- 使用 BeautifulSoup 解析 HTML
- 添加错误处理和重试机制
- 测试覆盖率: 100%
- 所有测试通过: 5/5

相关任务: T1.1.1
```

---

### 2.3 代码审查清单（Code Review Checklist）

**提交 Pull Request 前必须自查**：

- [ ] **功能完整性**
  - [ ] 功能符合需求文档描述
  - [ ] 边界条件已处理（空值、异常输入等）
  - [ ] 错误处理完善

- [ ] **测试覆盖**
  - [ ] 所有新增代码有对应测试
  - [ ] 测试用例包含正常和异常情况
  - [ ] 所有测试通过（`pytest tests/ -v`）

- [ ] **代码质量**
  - [ ] 代码符合 PEP 8 风格规范
  - [ ] 函数/类有清晰的文档字符串（docstring）
  - [ ] 变量命名语义化（避免 `a`, `b`, `temp` 等）
  - [ ] 无重复代码（遵循 DRY 原则）

- [ ] **兼容性**
  - [ ] 未破坏已有功能（运行全量测试通过）
  - [ ] 保持 API 向后兼容
  - [ ] 依赖版本无冲突

- [ ] **文档更新**
  - [ ] README 更新（如有新功能）
  - [ ] 配置文件模板更新（如有新配置）
  - [ ] 注释清晰，逻辑易懂

---

### 2.4 测试驱动开发流程（TDD）

**标准 TDD 流程**：

```
1. 编写测试（Red）→ 2. 实现功能（Green）→ 3. 重构优化（Refactor）→ 循环
```

**具体步骤**：

**步骤 1：编写失败的测试（Red）**
```python
# tests/test_crawler.py
def test_extract_product_info():
    """测试提取商品信息功能"""
    crawler = ProductCrawler()
    product = crawler.extract_product_info("https://fiido.com/products/fiido-d11")

    # 此时功能未实现，测试会失败（预期行为）
    assert product.name == "FIIDO D11"
    assert product.price_min > 0
```

**步骤 2：实现最小可用功能（Green）**
```python
# core/crawler.py
class ProductCrawler:
    def extract_product_info(self, url: str) -> Product:
        """提取商品信息"""
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 最小实现，只为通过测试
        name = soup.find('h1').get_text(strip=True)
        price = float(soup.find('.price').get_text().replace('$', ''))

        return Product(name=name, price_min=price, price_max=price)
```

**步骤 3：运行测试，确保通过**
```bash
pytest tests/test_crawler.py::test_extract_product_info -v
# PASSED
```

**步骤 4：重构优化（Refactor）**
```python
# core/crawler.py
class ProductCrawler:
    def extract_product_info(self, url: str) -> Product:
        """提取商品信息"""
        response = self._fetch_url(url)  # 提取重复逻辑
        soup = self._parse_html(response.text)

        name = self._extract_name(soup)
        price_min, price_max = self._extract_price_range(soup)

        return Product(name=name, price_min=price_min, price_max=price_max)

    def _fetch_url(self, url: str):
        """获取 URL 内容"""
        return requests.get(url, timeout=10)

    def _parse_html(self, html: str):
        """解析 HTML"""
        return BeautifulSoup(html, 'html.parser')

    def _extract_name(self, soup) -> str:
        """提取商品名称"""
        title = soup.find('h1', class_='product-title')
        return title.get_text(strip=True) if title else ""

    def _extract_price_range(self, soup) -> tuple:
        """提取价格区间"""
        # 实现细节...
        pass
```

**步骤 5：再次运行测试，确保重构后仍通过**
```bash
pytest tests/test_crawler.py::test_extract_product_info -v
# PASSED
```

---

## 三、质量保障措施

### 3.1 自动化测试要求

**测试覆盖率目标**：
- 核心模块（core/）：覆盖率 ≥ 90%
- 页面对象（pages/）：覆盖率 ≥ 80%
- 工具脚本（scripts/）：覆盖率 ≥ 60%

**测试命令**：
```bash
# 运行全量测试
pytest tests/ -v

# 查看覆盖率报告
pytest tests/ --cov=core --cov=pages --cov-report=html

# 仅运行单元测试（快速验证）
pytest tests/unit/ -v

# 仅运行集成测试
pytest tests/integration/ -v

# 仅运行 E2E 测试（较慢）
pytest tests/e2e/ -v --headed
```

---

### 3.2 持续集成（CI）配置

**GitHub Actions 自动化检查**：

每次 Push 或 Pull Request 时，自动运行：

1. **代码风格检查**（Linting）
2. **单元测试**（Unit Tests）
3. **集成测试**（Integration Tests）
4. **覆盖率检查**（Coverage ≥ 80%）

**配置示例**：
```yaml
# .github/workflows/ci.yml
name: Continuous Integration

on:
  push:
    branches: [develop, main]
  pull_request:
    branches: [develop, main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install chromium

      - name: Run linting
        run: flake8 core/ pages/ tests/

      - name: Run unit tests
        run: pytest tests/unit/ -v

      - name: Run integration tests
        run: pytest tests/integration/ -v

      - name: Check coverage
        run: |
          pytest tests/ --cov=core --cov=pages --cov-report=xml
          # 覆盖率 < 80% 则失败
          coverage report --fail-under=80
```

---

### 3.3 代码质量工具

**必须使用的工具**：

1. **Flake8**（代码风格检查）
   ```bash
   flake8 core/ pages/ tests/
   ```

2. **Black**（自动格式化）
   ```bash
   black core/ pages/ tests/
   ```

3. **isort**（import 排序）
   ```bash
   isort core/ pages/ tests/
   ```

4. **Mypy**（类型检查，可选）
   ```bash
   mypy core/ pages/
   ```

**配置文件**：
```ini
# setup.cfg
[flake8]
max-line-length = 100
exclude = .git,__pycache__,venv,build,dist
ignore = E203,W503

[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

[coverage:run]
source = core,pages
omit = */tests/*,*/venv/*

[coverage:report]
fail_under = 80
show_missing = True
```

---

## 四、开发最佳实践

### 4.1 文档字符串（Docstring）规范

**所有公共函数/类必须有 docstring**：

```python
def extract_product_info(self, product_url: str) -> Product:
    """
    从商品页面提取详细信息

    Args:
        product_url: 商品页面完整 URL，如 https://fiido.com/products/fiido-d11

    Returns:
        Product: 包含商品名称、价格、变体等信息的 Product 对象

    Raises:
        RequestException: 当 URL 无法访问时
        ValueError: 当 URL 格式不正确时

    Examples:
        >>> crawler = ProductCrawler()
        >>> product = crawler.extract_product_info("https://fiido.com/products/fiido-d11")
        >>> print(product.name)
        'FIIDO D11'
    """
    pass
```

---

### 4.2 错误处理规范

**所有外部调用必须有错误处理**：

```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def extract_product_info(self, product_url: str) -> Optional[Product]:
    """提取商品信息"""
    try:
        response = requests.get(product_url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"无法访问 {product_url}: {e}")
        return None

    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        product_data = self._parse_product_page(soup)
        return Product(**product_data)
    except Exception as e:
        logger.error(f"解析商品页面失败 {product_url}: {e}")
        return None
```

---

### 4.3 日志记录规范

**使用 Python logging 模块记录关键操作**：

```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class ProductCrawler:
    def discover_all_products(self):
        logger.info("开始发现商品...")

        collections = self.discover_collections()
        logger.info(f"发现 {len(collections)} 个商品分类")

        products = []
        for i, url in enumerate(collections):
            logger.debug(f"处理分类 {i+1}/{len(collections)}: {url}")
            try:
                prods = self.get_products_from_collection(url)
                products.extend(prods)
                logger.info(f"从 {url} 提取 {len(prods)} 个商品")
            except Exception as e:
                logger.error(f"提取分类失败 {url}: {e}")

        logger.info(f"总共发现 {len(products)} 个商品")
        return products
```

---

### 4.4 配置管理规范

**敏感信息不能硬编码**：

```python
# 错误做法
API_KEY = "sk-abc123xyz"  # 硬编码密钥

# 正确做法
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('CLAUDE_API_KEY')
if not API_KEY:
    raise ValueError("未设置 CLAUDE_API_KEY 环境变量")
```

**配置文件示例**：
```bash
# .env（不提交到 Git）
CLAUDE_API_KEY=sk-xxx
TEST_BASE_URL=https://fiido.com
TEST_EMAIL=test@fiido.com
```

```
# .env.example（提交到 Git 作为模板）
CLAUDE_API_KEY=your-api-key-here
TEST_BASE_URL=https://fiido.com
TEST_EMAIL=test@example.com
```

---

## 五、Sprint 开发检查清单

### Sprint 0：框架搭建

- [ ] 创建项目目录结构
- [ ] 配置 Python 虚拟环境
- [ ] 安装所有依赖（requirements.txt）
- [ ] 创建核心数据模型（core/models.py）
- [ ] 编写模型单元测试
- [ ] 运行测试，确保通过
- [ ] 提交代码到 feature/sprint0-setup 分支
- [ ] 创建 Pull Request
- [ ] 代码审查通过后合并到 develop

**完成标准**：
- 项目结构完整
- 所有测试通过
- 代码覆盖率 ≥ 80%
- 文档完善（README.md）

---

### Sprint 1：产品爬虫开发

**增量 1.1：基础爬虫**

- [ ] T1.1.1：实现 discover_collections()
  - [ ] 编写测试用例
  - [ ] 实现功能
  - [ ] 运行测试确保通过
  - [ ] 提交代码

- [ ] T1.1.2：实现 Shopify JSON API 解析
  - [ ] 编写测试用例
  - [ ] 实现功能
  - [ ] 运行测试确保通过
  - [ ] 提交代码

- [ ] T1.1.3：实现 HTML 后备解析
- [ ] T1.1.4：实现变体提取逻辑
- [ ] T1.1.5：添加错误处理和重试

**增量 1.2：产品发现脚本**

- [ ] 实现命令行参数解析
- [ ] 实现结果保存逻辑
- [ ] 添加统计信息输出
- [ ] 添加进度显示
- [ ] 实现增量更新

**完成标准**：
- 能够自动爬取 fiido.com 所有商品
- 保存为 JSON 格式
- 测试覆盖率 ≥ 90%
- 运行 `python scripts/discover_products.py` 成功

---

### Sprint 2：通用测试框架

- [ ] 实现通用页面对象（ProductPage）
- [ ] 实现 pytest fixtures
- [ ] 实现动态测试生成
- [ ] 创建通用测试用例
- [ ] 添加失败截图功能

**完成标准**：
- 可测试任意商品
- 支持过滤（优先级、分类）
- 测试通过率 100%
- 截图功能正常

---

### Sprint 3：完整购物流程

- [ ] 实现购物车页面对象
- [ ] 实现结账流程测试
- [ ] 添加多地区测试数据
- [ ] 实现运费验证
- [ ] 添加支付方式测试

**完成标准**：
- 完整测试从商品页到订单确认
- 支持 20+ 地区测试
- 不污染生产数据
- 测试通过率 ≥ 95%

---

### Sprint 4：AI 集成与优化

- [ ] 集成 Claude API
- [ ] 实现测试结果收集
- [ ] 实现 AI 报告生成
- [ ] 实现截图分析
- [ ] 配置告警系统

**完成标准**：
- AI 报告生成正常
- 失败截图自动分析
- 告警及时推送
- 质量看板完善

---

## 六、常见问题与解决方案

### 6.1 如何处理依赖冲突？

**问题**：安装新依赖时与已有依赖冲突

**解决方案**：
```bash
# 1. 使用虚拟环境隔离
python -m venv venv
source venv/bin/activate

# 2. 锁定依赖版本
pip freeze > requirements.txt

# 3. 使用 pip-tools 管理依赖
pip install pip-tools
pip-compile requirements.in  # 生成 requirements.txt
pip-sync requirements.txt     # 同步依赖
```

---

### 6.2 如何调试测试失败？

**问题**：测试失败，不知道原因

**解决方案**：
```bash
# 1. 查看详细输出
pytest tests/test_crawler.py -v -s

# 2. 进入调试模式
pytest tests/test_crawler.py --pdb

# 3. 仅运行失败的测试
pytest tests/test_crawler.py --lf

# 4. 查看覆盖率详情
pytest tests/ --cov=core --cov-report=html
open htmlcov/index.html
```

---

### 6.3 如何保持代码质量？

**问题**：代码质量难以维持

**解决方案**：
```bash
# 1. 提交前自动检查（使用 pre-commit hooks）
pip install pre-commit
pre-commit install

# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black

  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

# 2. 每次提交前运行
pre-commit run --all-files
```

---

## 七、总结

### 核心要求（必须遵守）

1. **小步开发**：每次只完成一个小功能
2. **测试优先**：开发后立即测试
3. **零破坏**：不破坏已有功能
4. **扩展式**：通过扩展而非修改实现新功能
5. **文档完善**：代码有注释，功能有文档

### 质量标准（验收条件）

- 测试覆盖率 ≥ 80%
- 所有测试通过
- 代码符合 PEP 8
- 无安全漏洞
- 文档完整

### 开发节奏（建议）

- 每天提交 1-3 个小功能
- 每周完成 1 个增量
- 每 2 周完成 1 个 Sprint
- 总周期 6-8 周

---

**文档版本**: 1.0
**最后更新**: 2025-12-03
**维护者**: Fiido 技术团队
**适用范围**: Fiido Shop Flow Guardian 项目全体开发人员
