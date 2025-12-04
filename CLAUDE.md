# Claude 开发规范

本文档规定了在使用 Claude 进行 Fiido Shop Flow Guardian 项目开发时必须遵守的规范和原则。

## 核心原则

### 1. 保护现有功能 - 零破坏原则

**规则：**
- ✅ **必须**：每次开发前，先理解现有代码的功能和依赖关系
- ✅ **必须**：使用 Read 工具阅读相关文件，了解代码上下文
- ✅ **必须**：只修改必要的部分，不得随意重构或删除现有代码
- ❌ **禁止**：破坏现有功能
- ❌ **禁止**：修改核心业务逻辑，除非明确要求
- ❌ **禁止**：删除现有 API 端点、函数或类方法

**验证方法：**
```bash
# 修改前
git diff  # 检查修改范围

# 修改后
pytest tests/  # 运行所有测试
python scripts/test_improvements.py  # 运行改进测试
```

**示例：**

❌ **错误示例** - 破坏现有功能：
```python
# 原代码
def discover_products(collection_path, limit=None):
    products = self._discover_via_json(collection_path, limit)
    return products

# 错误修改 - 删除了降级逻辑
def discover_products(collection_path, limit=None):
    return self._discover_via_json(collection_path, limit)  # 移除了 HTML 降级
```

✅ **正确示例** - 扩展而非破坏：
```python
# 原代码保持不变，添加新功能
def discover_products(collection_path, limit=None):
    products = self._discover_via_json(collection_path, limit)
    if not products:
        products = self._discover_via_html(collection_path, limit)
    return products

# 正确修改 - 在不破坏原有逻辑的基础上添加去重
def discover_products(collection_path, limit=None):
    products = self._discover_via_json(collection_path, limit)
    if not products:
        products = self._discover_via_html(collection_path, limit)
    # 新增：去重逻辑
    products = self._deduplicate_products(products)
    return products
```

---

### 2. 代码质量标准

#### 2.1 代码规范性

**必须遵守：**
- ✅ 遵循 PEP 8 Python 代码风格
- ✅ 使用有意义的变量名和函数名
- ✅ 函数单一职责原则（SRP）
- ✅ 适当的错误处理（try-except）
- ✅ 添加类型注解（Type Hints）

**代码规范检查：**
```bash
# 代码格式化
black core/ pages/ scripts/

# 代码风格检查
flake8 core/ pages/ scripts/

# 类型检查
mypy core/ pages/ scripts/
```

**示例：**

❌ **错误示例** - 不规范的代码：
```python
def f(x, y):  # 函数名不明确
    a = x.split('/')[-1]  # 变量名不明确
    b = a.replace('-', ' ').title()  # 变量名不明确
    return b
```

✅ **正确示例** - 规范的代码：
```python
def _format_category_name(self, category_slug: str) -> str:
    """格式化分类名称，将URL slug转换为友好的显示名称

    Args:
        category_slug: URL中的分类名称，如 'electric-bikes'

    Returns:
        格式化后的分类名称，如 'Electric Bikes'
    """
    # 替换连字符为空格
    category = category_slug.replace('-', ' ').replace('_', ' ')

    # 首字母大写（Title Case）
    category = category.title()

    return category
```

#### 2.2 可读性

**必须包含：**
- ✅ Docstring 文档字符串（函数、类、模块）
- ✅ 关键逻辑的注释说明
- ✅ 复杂算法的步骤说明
- ✅ 参数和返回值的说明

**Docstring 模板：**
```python
def function_name(param1: Type1, param2: Type2) -> ReturnType:
    """简短描述（一行）

    详细描述（可选，多行）

    Args:
        param1: 参数1的说明
        param2: 参数2的说明

    Returns:
        返回值的说明

    Raises:
        ExceptionType: 异常情况说明

    Example:
        >>> function_name(value1, value2)
        expected_result
    """
    pass
```

#### 2.3 易扩展性

**设计原则：**
- ✅ 使用配置文件而非硬编码
- ✅ 提取可复用的逻辑为独立函数/类
- ✅ 使用工厂模式或策略模式处理多种情况
- ✅ 保持低耦合、高内聚

**示例：**

❌ **错误示例** - 难以扩展：
```python
def discover_collections(self):
    url = "https://fiido.com/collections"  # 硬编码
    response = requests.get(url)
    # ... 解析逻辑硬编码在一个方法中
```

✅ **正确示例** - 易于扩展：
```python
def discover_collections(self) -> List[str]:
    """发现所有商品分类

    优先从官网主页发现分类，失败时尝试 /collections 页面。
    """
    collection_links = set()

    # 策略1: 从主页发现
    try:
        homepage_collections = self._discover_collections_from_page(self.base_url)
        collection_links.update(homepage_collections)
    except Exception as e:
        logger.warning(f"Failed to discover from homepage: {e}")

    # 策略2: 从 /collections 页面发现
    try:
        collections_url = f"{self.base_url}/collections"
        collections_page = self._discover_collections_from_page(collections_url)
        collection_links.update(collections_page)
    except Exception as e:
        logger.warning(f"Failed to discover from /collections: {e}")

    return sorted(list(collection_links))

def _discover_collections_from_page(self, url: str) -> set:
    """从指定页面发现商品分类链接（可复用逻辑）"""
    # 通用的解析逻辑
    pass
```

---

### 3. 严禁硬编码 - 数据驱动原则

**规则：**
- ✅ **必须**：所有配置使用配置文件（JSON、YAML、.env）
- ✅ **必须**：前端数据必须通过 API 获取真实数据
- ✅ **必须**：示例数据仅用于文档说明，不得用于实际运行
- ❌ **禁止**：在代码中硬编码 URL、路径、常量
- ❌ **禁止**：前端使用假数据、占位数据

**示例：**

❌ **错误示例** - 硬编码：
```python
# 后端硬编码
def get_products():
    return [
        {"id": "1", "name": "Bike 1", "price": 999},  # 假数据
        {"id": "2", "name": "Bike 2", "price": 1299}
    ]

# 前端硬编码
const data = {
    labels: ['周一', '周二', '周三'],  // 假数据
    datasets: [{
        data: [92, 94, 91]  // 假数据
    }]
};
```

✅ **正确示例** - 数据驱动：
```python
# 后端：从真实数据源获取
def get_products():
    products_file = Path('data/products.json')
    if products_file.exists():
        with open(products_file) as f:
            return json.load(f)
    return []

# 前端：通过 API 获取真实数据
async function loadTrendChart() {
    const response = await fetch('/api/trends/latest');
    const data = await response.json();

    // 使用真实数据
    const chartData = {
        labels: data.dates,
        datasets: [{
            data: data.pass_rates
        }]
    };
}
```

**配置文件使用：**
```python
# config/settings.py
import os
from pathlib import Path

BASE_URL = os.getenv('FIIDO_BASE_URL', 'https://fiido.com')
DATA_DIR = Path('data')
CACHE_TTL_HOURS = int(os.getenv('CACHE_TTL', '24'))

# 使用配置
from config.settings import BASE_URL, DATA_DIR

crawler = ProductCrawler(base_url=BASE_URL)
```

---

### 4. 测试与验收 - 可验证原则

**每次修改后必须提供：**

⚠️ **重要提示**：
- ✅ 每次修改后必须提供手动测试步骤和验收方法
- ✅ 必须说明如何验证修改效果
- ⚠️ **不必每次都创建测试文档**，仅在用户主动要求时创建
- ✅ 可以直接在回复中说明测试步骤，无需生成markdown文档

#### 4.1 手动测试步骤

**模板：**
```markdown
## 本次修改测试验收指南

### 修改内容
- 修改了 XXX 功能
- 添加了 YYY 功能
- 修复了 ZZZ 问题

### 影响范围
- 文件：core/crawler.py, scripts/discover_products.py
- 功能：商品发现、去重机制
- API：/api/products/discover, /api/products/list

### 手动测试步骤

#### 测试1: 商品发现功能
**目的**: 验证能从主页发现所有分类

1. 打开终端，执行：
   ```bash
   ./run.sh python3 scripts/discover_products.py
   ```

2. 预期结果：
   - ✅ 日志显示 "Found X collections from homepage"
   - ✅ 日志显示 "Total unique collections discovered: X"
   - ✅ 显示所有发现的分类列表
   - ✅ 无报错信息

3. 验收标准：
   - 分类数量 > 0
   - 分类名称格式正确（如 "Electric Bikes"）

#### 测试2: 去重机制
**目的**: 验证不会保存重复商品

1. 运行商品发现（同测试1）

2. 检查输出日志：
   ```bash
   grep "De-duplication" logs/discover.log
   ```

3. 预期结果：
   - ✅ 如果有重复，显示 "Removed X duplicate products"
   - ✅ 最终商品列表无重复ID

#### 测试3: Web界面分类显示
**目的**: 验证Web界面能按分类筛选

1. 启动Web服务：
   ```bash
   python3 web/app.py
   ```

2. 浏览器访问：http://localhost:5000/products

3. 操作步骤：
   - 点击"发现商品"按钮
   - 等待任务完成
   - 查看分类筛选器下拉菜单

4. 预期结果：
   - ✅ 分类筛选器中显示所有真实分类
   - ✅ 选择分类后，商品列表正确过滤
   - ✅ 商品卡片显示正确的分类标签

### 回滚方案
如果测试失败，执行：
```bash
git checkout core/crawler.py
git checkout scripts/discover_products.py
```
```

#### 4.2 自动化测试

**必须包含：**
```python
# tests/unit/test_improvements.py
def test_discover_collections():
    """测试分类发现功能"""
    crawler = ProductCrawler()
    collections = crawler.discover_collections()

    assert len(collections) > 0, "应该发现至少一个分类"
    assert all(c.startswith('/collections/') for c in collections), "分类路径格式错误"

def test_deduplication():
    """测试去重功能"""
    products = [
        Product(id="1", name="Bike 1"),
        Product(id="1", name="Bike 1"),  # 重复
        Product(id="2", name="Bike 2")
    ]

    deduplicated = deduplicate_products(products)

    assert len(deduplicated) == 2, "应该去除重复商品"
```

**运行测试：**
```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/unit/test_improvements.py -v

# 生成覆盖率报告
pytest --cov=core --cov=pages --cov-report=html
```

---

## 开发流程规范

### 标准开发流程

1. **需求分析**
   ```markdown
   - 阅读用户需求
   - 明确修改范围
   - 识别影响的文件和功能
   ```

2. **代码调研**
   ```bash
   # 使用 Read 工具阅读相关代码
   Read core/crawler.py
   Read scripts/discover_products.py

   # 理解现有逻辑
   grep -r "discover_products" .
   ```

3. **设计方案**
   ```markdown
   - 设计修改方案
   - 确保不破坏现有功能
   - 考虑扩展性
   ```

4. **编写代码**
   ```python
   # 遵循代码规范
   # 添加完整注释
   # 处理边界情况
   ```

5. **编写测试**
   ```python
   # 单元测试
   # 集成测试
   # 手动测试步骤
   ```

6. **执行测试**
   ```bash
   pytest tests/
   python scripts/test_improvements.py
   ```

7. **输出测试指南**
   ```markdown
   ## 本次修改测试验收指南

   ### 修改内容
   ...

   ### 手动测试步骤
   ...
   ```

---

## 常见场景规范

### 场景1: 添加新功能

**步骤：**
1. ✅ 阅读相关代码，理解现有架构
2. ✅ 在不修改现有代码的基础上，添加新函数/类
3. ✅ 通过配置或参数控制新功能的启用
4. ✅ 添加单元测试
5. ✅ 提供手动测试步骤

**示例：**
```python
# 添加新功能：分类名称格式化
def _format_category_name(self, category_slug: str) -> str:
    """新增方法，不影响现有代码"""
    category = category_slug.replace('-', ' ').title()
    return category

# 在现有方法中调用（可选）
def _parse_product_from_json(self, product_data, collection_path):
    # ... 现有代码 ...

    # 新增：使用格式化后的分类名称
    category_slug = collection_path.split('/')[-1]
    category = self._format_category_name(category_slug)

    # ... 其余代码不变 ...
```

### 场景2: 修复Bug

**步骤：**
1. ✅ 重现Bug，理解问题原因
2. ✅ 找到最小修改范围
3. ✅ 修复Bug，确保不影响其他功能
4. ✅ 添加回归测试
5. ✅ 验证修复效果

**示例：**
```python
# 原代码（有Bug）
def get_price(self):
    price_text = self.page.locator('.price').text_content()
    return float(price_text.replace('$', ''))  # Bug: 未处理空字符串

# 修复（最小改动）
def get_price(self):
    price_text = self.page.locator('.price').text_content()
    if not price_text:  # 修复：添加空值检查
        return 0.0
    return float(price_text.replace('$', ''))
```

### 场景3: 重构代码

**步骤：**
1. ❌ **警告**：除非明确要求，否则不要重构
2. ✅ 如需重构，必须保证功能完全一致
3. ✅ 使用 Git diff 确认修改范围
4. ✅ 运行全部测试确保无破坏

**原则：**
- 重构必须有充分理由（性能问题、可维护性严重下降）
- 重构不得改变外部接口和行为
- 重构必须有完整的测试覆盖

---

## Git 提交规范

### Commit Message 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type 类型：**
- `feat`: 新功能
- `fix`: Bug修复
- `refactor`: 重构（不改变功能）
- `docs`: 文档修改
- `test`: 测试相关
- `chore`: 构建/工具修改

**示例：**
```
feat(crawler): 添加从主页发现分类的功能

- 优先从主页扫描分类链接
- 从 /collections 页面作为补充
- 添加分类路径验证逻辑

Closes #123
```

---

## 检查清单

在提交代码前，请确认以下检查清单：

### 功能检查
- [ ] 现有功能未被破坏
- [ ] 新功能按预期工作
- [ ] 边界情况已处理
- [ ] 错误处理完善

### 代码质量检查
- [ ] 代码符合 PEP 8 规范
- [ ] 函数/类有完整的 Docstring
- [ ] 变量名有意义
- [ ] 复杂逻辑有注释说明

### 硬编码检查
- [ ] 无硬编码的 URL、路径
- [ ] 配置使用配置文件
- [ ] 前端数据通过 API 获取
- [ ] 无假数据、占位数据

### 测试检查
- [ ] 编写了单元测试
- [ ] 所有测试通过
- [ ] 提供了手动测试步骤
- [ ] 测试覆盖率 > 80%

### 文档检查
- [ ] 提供了修改说明
- [ ] 提供了手动测试指南
- [ ] 更新了相关文档（如需要）

---

## 违规处理

如发现违反本规范的情况：

1. **立即停止开发**
2. **回滚到上一个稳定版本**
   ```bash
   git checkout <last-stable-commit>
   ```
3. **重新按规范开发**
4. **运行完整测试验证**

---

## 附录

### 常用命令

```bash
# 代码质量检查
black core/ pages/ scripts/  # 格式化
flake8 core/ pages/ scripts/  # 风格检查
mypy core/  # 类型检查

# 测试
pytest tests/  # 运行所有测试
pytest tests/unit/  # 运行单元测试
pytest --cov=core --cov-report=html  # 生成覆盖率报告

# Git
git diff  # 查看修改
git status  # 查看状态
git log --oneline  # 查看提交历史

# 项目相关
./run.sh python3 scripts/discover_products.py  # 发现商品
./run_tests.sh  # 运行测试
python3 web/app.py  # 启动Web服务
```

### 参考资源

- [PEP 8 -- Style Guide for Python Code](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Pytest Documentation](https://docs.pytest.org/)
- [Type Hints - Python Documentation](https://docs.python.org/3/library/typing.html)

---

## 测试智能化原则 (新增 v2.0.4)

### 核心测试理念

**测试的目标是验证网站已有功能是否工作正常,而不是测试"网站是否具备某个功能"。**

### 5大核心原则

#### 原则1: 区分网站Bug vs 测试失败

**规则:**
- ✅ **必须**:明确区分网站自身的Bug和测试脚本的超时/失败
- ✅ **必须**:对失败进行分类(website_bug/missing_feature/test_timeout/test_error/network_error)
- ✅ **必须**:只有确认是网站Bug时,才报告为"failed"
- ❌ **禁止**:将测试超时、网络问题等误判为网站Bug

**失败分类标准:**

```python
from core.test_intelligence import FailureClassification

# 1. 网站Bug: 元素存在 + 操作失败 + 有JavaScript错误
FailureClassification.TYPE_WEBSITE_BUG
示例: 点击按钮无响应,且Console有TypeError

# 2. 功能缺失: 元素不存在
FailureClassification.TYPE_MISSING_FEATURE
示例: 找不到数量调整按钮 → 该页面未实现此功能

# 3. 测试超时: 操作超时,可能是网络慢或元素加载慢
FailureClassification.TYPE_TEST_TIMEOUT
示例: 等待元素出现超过3秒

# 4. 测试错误: 测试逻辑本身的问题
FailureClassification.TYPE_TEST_ERROR
示例: 选择器写错,导致找不到元素

# 5. 网络错误: 网络连接问题
FailureClassification.TYPE_NETWORK_ERROR
示例: net::ERR_CONNECTION_REFUSED
```

**实践示例:**

❌ **错误做法**:
```python
# 不区分失败原因,一律报错
try:
    button = await page.query_selector("button.add-to-cart")
    await button.click()
except:
    step.complete("failed", "添加购物车失败")  # 太笼统!
```

✅ **正确做法**:
```python
from core.test_intelligence import TestIntelligence

intelligence = TestIntelligence(page)

# 1. 先检测元素是否存在
button_result = await intelligence.detect_element(
    selectors=["button.add-to-cart", "[data-add-to-cart]"],
    element_name="添加购物车按钮"
)

if not button_result.exists:
    # 元素不存在 = 功能缺失,不是Bug
    step.complete("skipped", "该页面未提供添加购物车功能")
    return

# 2. 元素存在,尝试操作
try:
    await button_result.element.click(timeout=3000)
    step.complete("passed", "成功添加到购物车")
except Exception as e:
    # 3. 操作失败,分类原因
    classification = await intelligence.classify_failure(
        step_name="添加购物车",
        expected_element=button_result,
        operation_attempted="点击按钮",
        js_errors=js_errors_list,
        exception=e
    )

    if classification.failure_type == FailureClassification.TYPE_TEST_TIMEOUT:
        step.complete("skipped", "测试超时,可能网络慢")
    elif classification.is_website_bug():
        step.complete("failed", classification.reason, issue_details=...)
    else:
        step.complete("skipped", classification.reason)
```

---

#### 原则2: 加强已有功能的Bug检测,避免漏检

**规则:**
- ✅ **必须**:对网页中实际存在的UI元素进行全面测试
- ✅ **必须**:检测元素的可见性、可用性、交互响应
- ✅ **必须**:监听JavaScript错误,关联用户操作
- ❌ **禁止**:假设元素存在就一定能正常工作

**Bug检测机制:**

```python
# 三级检测机制
class ElementDetectionResult:
    exists: bool       # 1. 元素是否存在
    visible: bool      # 2. 元素是否可见
    enabled: bool      # 3. 元素是否可交互

    @property
    def is_functional(self) -> bool:
        """功能是否正常(三者都满足)"""
        return self.exists and self.visible and self.enabled
```

**实践示例:**

❌ **错误做法** - 浅层检测:
```python
# 只检查元素存在,不检查功能
image = await page.query_selector("img.product-image")
if image:
    step.complete("passed", "商品图片存在")  # 不够深入!
```

✅ **正确做法** - 深度检测:
```python
# 1. 检测元素
image_result = await intelligence.detect_element(
    selectors=["img[src*='product']", ".product-image img"],
    element_name="商品图片"
)

if not image_result.exists:
    step.complete("skipped", "该商品页面无图片")
    return

# 2. 检查可见性
if not image_result.visible:
    # 元素存在但不可见 - 可能是Bug
    if js_errors:
        step.complete("failed", "图片元素存在但不可见,且有JS错误",
                     issue_details={"js_errors": js_errors})
    else:
        step.complete("passed", "图片元素存在但隐藏(可能是懒加载)")
    return

# 3. 检查图片是否加载成功
src = await image_result.element.get_attribute("src")
if not src or src == "placeholder.jpg":
    step.complete("failed", "图片URL无效或为占位符")
else:
    step.complete("passed", f"商品图片正常显示 ({src})")
```

---

#### 原则3: 避免"无中生有"的失败

**规则:**
- ✅ **必须**:先检测功能是否存在,再测试功能
- ✅ **必须**:对不存在的功能,报告为"skipped"而非"failed"
- ✅ **必须**:基于网页实际UI进行测试
- ❌ **禁止**:对根本不存在的元素进行测试并报告失败

**判断逻辑:**

```python
def should_skip_step(self, step_name: str, prerequisite_elements: List[ElementDetectionResult]) -> Tuple[bool, Optional[str]]:
    """判断是否应该跳过某个步骤"""
    missing_elements = [elem for elem in prerequisite_elements if not elem.exists]

    if missing_elements:
        return (True, f"{step_name}所需的UI元素不存在,该功能未实现,跳过测试")

    return (False, None)
```

**实践示例:**

❌ **错误做法** - 强行测试不存在的功能:
```python
# 不管元素是否存在,都尝试测试
step = TestStep(7, "商品评论测试", "测试用户评论功能")
try:
    comments = await page.query_selector_all(".product-reviews .comment")
    if len(comments) == 0:
        step.complete("failed", "未找到商品评论")  # 错误!
except:
    step.complete("failed", "评论功能测试失败")  # 错误!
```

✅ **正确做法** - 先判断功能是否存在:
```python
# 1. 先检测评论区域是否存在
review_section = await intelligence.detect_element(
    selectors=[".product-reviews", "#reviews", "[data-reviews]"],
    element_name="评论区域"
)

# 2. 判断是否跳过
should_skip, skip_reason = intelligence.should_skip_step(
    step_name="商品评论测试",
    prerequisite_elements=[review_section]
)

if should_skip:
    # 评论区域不存在 = 该商品页面未实现评论功能
    step.complete("skipped", "该商品页面未实现评论功能,跳过测试")
    return

# 3. 评论区域存在,测试评论功能
comments = await page.query_selector_all(f"{review_section.selector_used} .comment")
if len(comments) > 0:
    step.complete("passed", f"评论功能正常,共{len(comments)}条评论")
else:
    step.complete("passed", "评论区域存在但暂无评论")
```

---

#### 原则4: 基于网页实际UI设计进行测试

**规则:**
- ✅ **必须**:测试前先观察网页实际的UI结构
- ✅ **必须**:使用与网页匹配的选择器
- ✅ **必须**:测试网页实际提供的交互方式
- ❌ **禁止**:假设网页必须有某个元素
- ❌ **禁止**:使用过时的或不匹配的选择器

**选择器策略:**

```python
# 多重选择器fallback机制
selectors = [
    # 1. 网站特定的class (最优先)
    ".fiido-add-to-cart",
    "button.add-to-cart",

    # 2. 通用的语义化选择器
    "button[name='add']",
    "button:has-text('Add to Cart')",

    # 3. 数据属性选择器
    "[data-add-to-cart]",
    "[data-action='add-to-cart']",

    # 4. 兜底选择器
    "form[action*='cart'] button[type='submit']"
]
```

**实践示例:**

❌ **错误做法** - 假设UI结构:
```python
# 假设所有商品页面都有数量加减按钮
plus_button = await page.query_selector("button.quantity-plus")
if not plus_button:
    step.complete("failed", "未找到数量加号按钮")  # 错误!
```

✅ **正确做法** - 适应实际UI:
```python
# 1. 先检测有哪些数量控制元素
quantity_input = await intelligence.detect_element(
    selectors=["input[name='quantity']"],
    element_name="数量输入框"
)

plus_button = await intelligence.detect_element(
    selectors=["button.quantity-plus", "button:has-text('+')"],
    element_name="数量加号按钮"
)

# 2. 根据实际UI决定测试策略
if quantity_input.exists and plus_button.exists:
    # UI方式1: 输入框 + 加减按钮
    step.complete("passed", "数量控制使用按钮方式")
elif quantity_input.exists and not plus_button.exists:
    # UI方式2: 仅输入框(手动输入)
    step.complete("passed", "数量控制使用手动输入方式")
else:
    # UI方式3: 无数量控制(可能默认数量为1)
    step.complete("skipped", "该商品页面未提供数量控制功能")
```

---

#### 原则5: 验证功能是否有Bug,而非功能是否存在

**规则:**
- ✅ **必须**:测试重点是"已有功能是否正常工作"
- ✅ **必须**:功能存在 + 操作失败 + 有JS错误 = Bug
- ✅ **必须**:功能不存在 = 跳过测试(不报告为失败)
- ❌ **禁止**:将"功能缺失"误判为"功能有Bug"

**判断流程:**

```
┌─────────────────┐
│  检测元素存在性  │
└────────┬────────┘
         │
    ┌────▼─────┐
    │ 元素存在? │
    └─┬──────┬─┘
      │NO    │YES
      │      │
 ┌────▼───┐  └────►┌───────────┐
 │ 跳过测试│         │ 测试功能   │
 │(skipped)│         └─────┬─────┘
 └─────────┘               │
                      ┌────▼─────┐
                      │ 功能正常? │
                      └─┬──────┬─┘
                        │YES   │NO
                        │      │
                   ┌────▼───┐  └────►┌────────────┐
                   │ 通过测试│         │ 有JS错误?   │
                   │(passed)│         └─┬────────┬─┘
                   └─────────┘           │YES     │NO
                                         │        │
                                    ┌────▼───┐  ┌─▼──────┐
                                    │ Bug!   │  │ 正常   │
                                    │(failed)│  │(passed)│
                                    └────────┘  └────────┘
```

**实践示例:**

❌ **错误做法** - 混淆功能缺失和Bug:
```python
# 例子1: 错误地报告失败
checkout_button = await page.query_selector("button[name='checkout']")
if not checkout_button:
    step.complete("failed", "Checkout功能异常")  # 错误!应该是skipped

# 例子2: 忽略真正的Bug
try:
    await checkout_button.click()
    step.complete("passed", "Checkout按钮正常")  # 错误!没检查是否真的跳转了
except:
    step.complete("failed", "Checkout失败")  # 笼统,没分析原因
```

✅ **正确做法** - 精确判断:
```python
# 1. 检测元素
checkout_button = await intelligence.detect_element(
    selectors=["button[name='checkout']", "a[href*='/checkout']"],
    element_name="Checkout按钮"
)

# 2. 元素不存在 - 功能缺失,不是Bug
if not checkout_button.exists:
    step.complete("skipped", "该页面未提供Checkout功能")
    return

# 3. 元素存在,检查是否可用
if not checkout_button.is_functional:
    # 元素存在但不可用 - 可能是业务限制(如购物车为空)
    empty_cart = await page.query_selector(".cart-empty")
    if empty_cart:
        step.complete("skipped", "购物车为空,Checkout按钮被禁用(正常)")
    else:
        step.complete("passed", "Checkout按钮存在但不可用,可能需要满足其他条件")
    return

# 4. 元素可用,测试功能
js_errors_before = len(js_errors_list)
try:
    current_url = page.url
    await checkout_button.element.click(timeout=3000)
    await page.wait_for_timeout(2000)

    new_url = page.url
    new_js_errors = js_errors_list[js_errors_before:]

    # 判断是否真的跳转了
    if '/checkout' in new_url or '/payment' in new_url:
        step.complete("passed", "Checkout功能正常,成功跳转到支付页面")
    elif new_js_errors:
        # 没跳转 + 有JS错误 = Bug
        step.complete("failed", "Checkout按钮点击后未跳转,且有JavaScript错误",
                     issue_details={
                         "scenario": "用户点击Checkout按钮",
                         "operation": "点击按钮,期望跳转到支付页面",
                         "problem": f"URL未变化({current_url}),且有JS错误",
                         "root_cause": "Checkout跳转逻辑存在Bug",
                         "js_errors": new_js_errors
                     })
    else:
        # 没跳转但无JS错误 - 可能是需要满足其他条件
        step.complete("passed", "Checkout按钮点击后未跳转,可能需要填写配送信息等")

except Exception as e:
    # 分类失败原因
    classification = await intelligence.classify_failure(
        step_name="Checkout功能测试",
        expected_element=checkout_button,
        operation_attempted="点击Checkout按钮",
        js_errors=js_errors_list[js_errors_before:],
        exception=e
    )

    if classification.is_website_bug():
        step.complete("failed", classification.reason)
    else:
        step.complete("skipped", classification.reason)
```

---

### 测试智能化工具

**核心模块:** `core/test_intelligence.py`

**主要类:**

1. **TestIntelligence**: 测试智能判断类
   - `detect_element()`: 智能检测元素
   - `classify_failure()`: 分类失败原因
   - `should_skip_step()`: 判断是否跳过步骤
   - `intelligent_wait_for_element()`: 智能等待元素

2. **ElementDetectionResult**: 元素检测结果
   - `exists`: 元素是否存在
   - `visible`: 元素是否可见
   - `enabled`: 元素是否可用
   - `is_functional`: 功能是否正常

3. **FailureClassification**: 失败分类
   - `TYPE_WEBSITE_BUG`: 网站Bug
   - `TYPE_MISSING_FEATURE`: 功能缺失
   - `TYPE_TEST_TIMEOUT`: 测试超时
   - `TYPE_TEST_ERROR`: 测试错误
   - `TYPE_NETWORK_ERROR`: 网络错误

**使用示例:**

```python
from core.test_intelligence import TestIntelligence

async def enhanced_test_step(page, step, js_errors):
    intelligence = TestIntelligence(page)

    # 1. 智能检测元素
    button = await intelligence.detect_element(
        selectors=["button.add-to-cart", "[data-add-to-cart]"],
        element_name="添加购物车按钮"
    )

    # 2. 判断是否跳过
    should_skip, reason = intelligence.should_skip_step(
        step_name="添加购物车",
        prerequisite_elements=[button]
    )

    if should_skip:
        step.complete("skipped", reason)
        return

    # 3. 测试功能
    # ... 测试逻辑 ...
```

---

### 测试报告规范

**步骤状态定义:**

- `passed`: 功能正常工作
- `failed`: 确认是网站Bug
- `skipped`: 功能不存在或测试无法进行(不是Bug)

**示例报告:**

```json
{
  "steps": [
    {
      "number": 5,
      "name": "商品图片验证",
      "status": "skipped",
      "message": "该商品页面无图片元素,功能未实现"
    },
    {
      "number": 7,
      "name": "变体选择测试",
      "status": "passed",
      "message": "变体选择功能正常(颜色:2个选项,型号:2个选项)"
    },
    {
      "number": 12,
      "name": "支付流程验证",
      "status": "failed",
      "message": "Checkout按钮点击后未跳转,且有JavaScript错误",
      "issue_details": {
        "scenario": "用户点击Checkout按钮",
        "operation": "点击按钮,期望跳转到支付页面",
        "problem": "URL未变化,且有JS错误",
        "root_cause": "Checkout跳转逻辑存在Bug",
        "js_errors": ["TypeError: Cannot read property 'value' of null"]
      }
    }
  ]
}
```

---

### 检查清单

在编写测试步骤时,请确认:

#### 元素检测
- [ ] 使用`detect_element()`而非直接`query_selector()`
- [ ] 提供多个fallback选择器
- [ ] 检查元素的`exists/visible/enabled`三个维度

#### 失败分类
- [ ] 使用`classify_failure()`分类失败原因
- [ ] 区分Bug、功能缺失、超时、测试错误
- [ ] 只有确认是Bug才报告为`failed`

#### 跳过判断
- [ ] 功能不存在时使用`skipped`而非`failed`
- [ ] 使用`should_skip_step()`判断前置条件
- [ ] 在跳过消息中说明原因

#### Bug检测
- [ ] 监听JavaScript错误
- [ ] 关联用户操作和错误
- [ ] 提供详细的`issue_details`

#### 测试覆盖
- [ ] 只测试网页实际存在的功能
- [ ] 不对不存在的功能进行测试
- [ ] 基于实际UI结构编写选择器

---

**版本**: v2.0.4
**更新日期**: 2025-12-04
**维护者**: Fiido Shop Flow Guardian Team
**新增内容**: 测试智能化原则与工具
