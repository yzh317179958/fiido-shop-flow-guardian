"""
ProductPage 单元测试

测试商品页面对象的所有交互操作。
"""

import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
import pytest

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pages.product_page import ProductPage
from core.models import Product, ProductVariant, Selectors


@pytest.fixture
def mock_page():
    """创建 Mock Playwright Page 对象"""
    page = AsyncMock()
    page.goto = AsyncMock()
    page.wait_for_load_state = AsyncMock()
    page.click = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.locator = Mock()
    page.screenshot = AsyncMock()
    page.on = Mock()
    return page


@pytest.fixture
def sample_product():
    """创建示例商品"""
    return Product(
        id="test-product",
        name="Test Electric Bike",
        url="https://fiido.com/products/test-bike",
        category="Electric Bikes",
        price_min=999.0,
        price_max=1299.0,
        currency="USD",
        variants=[],
        selectors=Selectors()
    )


@pytest.fixture
def sample_variant():
    """创建示例变体"""
    return ProductVariant(
        name="Black",
        type="color",
        selector="button[data-color='black']",
        available=True
    )


@pytest.fixture
def mock_selector_manager():
    """创建 Mock SelectorManager"""
    mock_mgr = Mock()
    mock_mgr.find_element = AsyncMock(return_value=None)
    mock_mgr.get_selector = Mock(return_value="")
    return mock_mgr


class TestProductPageInit:
    """测试 ProductPage 初始化"""

    def test_init_with_product(self, mock_page, sample_product):
        """测试使用商品对象初始化"""
        product_page = ProductPage(mock_page, sample_product)

        assert product_page.page == mock_page
        assert product_page.product == sample_product
        assert product_page.selector_mgr is not None


class TestNavigate:
    """测试页面导航"""

    @pytest.mark.asyncio
    async def test_navigate_success(self, mock_page, sample_product):
        """测试成功导航到商品页"""
        product_page = ProductPage(mock_page, sample_product)
        await product_page.navigate()

        mock_page.goto.assert_called_once()
        call_args = mock_page.goto.call_args
        assert str(sample_product.url) in str(call_args)

    @pytest.mark.asyncio
    async def test_navigate_with_wait_until(self, mock_page, sample_product):
        """测试使用自定义 wait_until 参数导航"""
        product_page = ProductPage(mock_page, sample_product)
        await product_page.navigate(wait_until='load')

        mock_page.goto.assert_called_once()

    @pytest.mark.asyncio
    async def test_navigate_failure(self, mock_page, sample_product):
        """测试导航失败"""
        mock_page.goto.side_effect = Exception("Navigation failed")

        product_page = ProductPage(mock_page, sample_product)

        with pytest.raises(Exception):
            await product_page.navigate()


class TestGetTitle:
    """测试获取商品标题"""

    @pytest.mark.asyncio
    async def test_get_title_success(self, mock_page, sample_product):
        """测试成功获取标题"""
        mock_element = AsyncMock()
        mock_element.text_content = AsyncMock(return_value="Test Bike Title")

        product_page = ProductPage(mock_page, sample_product)

        # Mock selector_mgr 实例
        mock_selector_mgr = Mock()
        mock_selector_mgr.find_element = AsyncMock(return_value=mock_element)
        product_page.selector_mgr = mock_selector_mgr

        title = await product_page.get_title()

        assert title == "Test Bike Title"

    @pytest.mark.asyncio
    async def test_get_title_element_not_found(self, mock_page, sample_product):
        """测试标题元素未找到"""
        product_page = ProductPage(mock_page, sample_product)

        # Mock selector_mgr 实例
        mock_selector_mgr = Mock()
        mock_selector_mgr.find_element = AsyncMock(return_value=None)
        product_page.selector_mgr = mock_selector_mgr

        title = await product_page.get_title()

        assert title is None

    @pytest.mark.asyncio
    async def test_get_title_with_whitespace(self, mock_page, sample_product):
        """测试标题包含空白字符"""
        mock_element = AsyncMock()
        mock_element.text_content = AsyncMock(return_value="  Test Bike  \n")

        product_page = ProductPage(mock_page, sample_product)
        
        # Mock selector_mgr 实例
        mock_selector_mgr = Mock()
        mock_selector_mgr.find_element = AsyncMock(return_value=mock_element)

        product_page = ProductPage(mock_page, sample_product)
        product_page.selector_mgr = mock_selector_mgr

        title = await product_page.get_title()

        assert title == "Test Bike"


class TestGetPrice:
    """测试获取商品价格"""

    @pytest.mark.asyncio
    async def test_get_price_success(self, mock_page, sample_product):
        """测试成功获取价格"""
        mock_element = AsyncMock()
        mock_element.text_content = AsyncMock(return_value="$999.00")

        product_page = ProductPage(mock_page, sample_product)
        
        # Mock selector_mgr 实例
        mock_selector_mgr = Mock()
        mock_selector_mgr.find_element = AsyncMock(return_value=mock_element)

        product_page = ProductPage(mock_page, sample_product)
        product_page.selector_mgr = mock_selector_mgr

        price = await product_page.get_price()

        assert price == "$999.00"

    @pytest.mark.asyncio
    async def test_get_price_element_not_found(self, mock_page, sample_product):
        """测试价格元素未找到"""
        product_page = ProductPage(mock_page, sample_product)
        
        # Mock selector_mgr 实例
        mock_selector_mgr = Mock()
        mock_selector_mgr.find_element = AsyncMock(return_value=None)

        product_page = ProductPage(mock_page, sample_product)
        product_page.selector_mgr = mock_selector_mgr

        price = await product_page.get_price()

        assert price is None


class TestSelectVariant:
    """测试选择商品变体"""

    @pytest.mark.asyncio
    async def test_select_variant_success(self, mock_page, sample_product, sample_variant):
        """测试成功选择变体"""
        product_page = ProductPage(mock_page, sample_product)

        result = await product_page.select_variant(sample_variant)

        assert result is True
        mock_page.click.assert_called_once_with(sample_variant.selector, timeout=3000)
        mock_page.wait_for_timeout.assert_called()

    @pytest.mark.asyncio
    async def test_select_variant_with_custom_wait_time(self, mock_page, sample_product, sample_variant):
        """测试使用自定义等待时间选择变体"""
        product_page = ProductPage(mock_page, sample_product)

        result = await product_page.select_variant(sample_variant, wait_time=1000)

        assert result is True
        mock_page.wait_for_timeout.assert_called_with(1000)

    @pytest.mark.asyncio
    async def test_select_variant_failure(self, mock_page, sample_product, sample_variant):
        """测试选择变体失败"""
        mock_page.click.side_effect = Exception("Click failed")

        product_page = ProductPage(mock_page, sample_product)

        result = await product_page.select_variant(sample_variant)

        assert result is False


class TestAddToCart:
    """测试加入购物车"""

    @pytest.mark.asyncio
    async def test_add_to_cart_success(self, mock_page, sample_product):
        """测试成功加入购物车"""
        mock_add_button = AsyncMock()
        mock_add_button.click = AsyncMock()

        product_page = ProductPage(mock_page, sample_product)
        
        # Mock selector_mgr 实例
        mock_selector_mgr = Mock()
        mock_selector_mgr.find_element = AsyncMock(return_value=mock_add_button)

        product_page = ProductPage(mock_page, sample_product)
        product_page.selector_mgr = mock_selector_mgr

        result = await product_page.add_to_cart()

        assert result is True
        mock_add_button.click.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_to_cart_button_not_found(self, mock_page, sample_product):
        """测试加购按钮未找到"""
        product_page = ProductPage(mock_page, sample_product)
        
        # Mock selector_mgr 实例
        mock_selector_mgr = Mock()
        mock_selector_mgr.find_element = AsyncMock(return_value=None)

        product_page = ProductPage(mock_page, sample_product)
        product_page.selector_mgr = mock_selector_mgr

        result = await product_page.add_to_cart()

        assert result is False

    @pytest.mark.asyncio
    async def test_add_to_cart_with_error(self, mock_page, sample_product):
        """测试加购时出现错误"""
        mock_add_button = AsyncMock()
        mock_add_button.click.side_effect = Exception("Click failed")

        product_page = ProductPage(mock_page, sample_product)
        
        # Mock selector_mgr 实例
        mock_selector_mgr = Mock()
        mock_selector_mgr.find_element = AsyncMock(return_value=mock_add_button)

        product_page = ProductPage(mock_page, sample_product)
        product_page.selector_mgr = mock_selector_mgr

        result = await product_page.add_to_cart()

        assert result is False


class TestIsInStock:
    """测试检查库存状态"""

    @pytest.mark.asyncio
    async def test_is_in_stock_true(self, mock_page, sample_product):
        """测试商品有货"""
        mock_locator = Mock()
        mock_locator.count = AsyncMock(return_value=0)
        mock_page.locator.return_value = mock_locator

        product_page = ProductPage(mock_page, sample_product)

        result = await product_page.is_in_stock()

        assert result is True

    @pytest.mark.asyncio
    async def test_is_in_stock_false(self, mock_page, sample_product):
        """测试商品缺货"""
        mock_locator = Mock()
        mock_locator.count = AsyncMock(return_value=1)
        mock_page.locator.return_value = mock_locator

        product_page = ProductPage(mock_page, sample_product)

        result = await product_page.is_in_stock()

        assert result is False


class TestGetAvailableVariants:
    """测试获取可用变体"""

    @pytest.mark.asyncio
    async def test_get_available_variants_empty(self, mock_page, sample_product):
        """测试无可用变体"""
        mock_page.locator.return_value.all = AsyncMock(return_value=[])

        product_page = ProductPage(mock_page, sample_product)
        
        # Mock selector_mgr 实例
        mock_selector_mgr = Mock()
        mock_selector_mgr.get_selector = Mock(return_value="")

        product_page = ProductPage(mock_page, sample_product)
        product_page.selector_mgr = mock_selector_mgr

        variants = await product_page.get_available_variants()

        assert variants == []

    @pytest.mark.asyncio
    async def test_get_available_variants_with_colors(self, mock_page, sample_product):
        """测试获取颜色变体"""
        mock_element1 = AsyncMock()
        mock_element1.text_content = AsyncMock(return_value="Black")
        mock_element2 = AsyncMock()
        mock_element2.text_content = AsyncMock(return_value="White")

        mock_locator = Mock()
        mock_locator.all = AsyncMock(return_value=[mock_element1, mock_element2])
        mock_page.locator.return_value = mock_locator

        product_page = ProductPage(mock_page, sample_product)
        
        # Mock selector_mgr 实例
        mock_selector_mgr = Mock()
        mock_selector_mgr.get_selector = Mock(return_value=".color-swatch")

        product_page = ProductPage(mock_page, sample_product)
        product_page.selector_mgr = mock_selector_mgr

        variants = await product_page.get_available_variants()

        assert "Black" in variants
        assert "White" in variants


class TestTakeScreenshot:
    """测试截图功能"""

    @pytest.mark.asyncio
    async def test_take_screenshot_success(self, mock_page, sample_product):
        """测试成功截图"""
        product_page = ProductPage(mock_page, sample_product)

        await product_page.take_screenshot("test.png")

        mock_page.screenshot.assert_called_once_with(path="test.png", full_page=True)

    @pytest.mark.asyncio
    async def test_take_screenshot_failure(self, mock_page, sample_product):
        """测试截图失败"""
        mock_page.screenshot.side_effect = Exception("Screenshot failed")

        product_page = ProductPage(mock_page, sample_product)

        with pytest.raises(Exception):
            await product_page.take_screenshot("test.png")


class TestGetProductInfo:
    """测试获取完整商品信息"""

    @pytest.mark.asyncio
    async def test_get_product_info(self, mock_page, sample_product):
        """测试获取完整商品信息"""
        mock_locator = Mock()
        mock_locator.count = AsyncMock(return_value=0)
        mock_page.locator.return_value = mock_locator

        mock_element_title = AsyncMock()
        mock_element_title.text_content = AsyncMock(return_value="Test Title")

        mock_element_price = AsyncMock()
        mock_element_price.text_content = AsyncMock(return_value="$999")

        product_page = ProductPage(mock_page, sample_product)
        
        # Mock selector_mgr 实例
        mock_selector_mgr = Mock()
        async def mock_find_element(page, key):
            if key == 'product_title':
                return mock_element_title
            elif key == 'product_price':
                return mock_element_price
            return None

        mock_selector_mgr.find_element = mock_find_element
        mock_selector_mgr.get_selector = Mock(return_value="")

        product_page = ProductPage(mock_page, sample_product)
        product_page.selector_mgr = mock_selector_mgr

        info = await product_page.get_product_info()

        assert info['title'] == "Test Title"
        assert info['price'] == "$999"
        assert info['in_stock'] is True
        assert isinstance(info['variants'], list)
