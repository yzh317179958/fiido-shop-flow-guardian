"""
SelectorManager 单元测试

测试选择器管理器的配置加载、选择器查找、后备机制等功能。
"""

import json
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
import pytest

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.selector_manager import SelectorManager


class TestSelectorManagerInit:
    """测试 SelectorManager 初始化"""

    def test_init_with_existing_config(self):
        """测试使用现有配置文件初始化"""
        manager = SelectorManager(config_path="config/selectors.json")
        assert manager.config_path.name == "selectors.json"
        assert manager.selectors is not None
        assert 'base_selectors' in manager.selectors

    def test_init_with_nonexistent_config(self, tmp_path):
        """测试配置文件不存在时使用默认配置"""
        config_path = tmp_path / "nonexistent.json"
        manager = SelectorManager(config_path=str(config_path))

        # 应该使用默认配置
        assert 'base_selectors' in manager.selectors
        assert 'product_title' in manager.selectors['base_selectors']

    def test_init_with_invalid_json(self, tmp_path):
        """测试无效 JSON 配置文件"""
        config_path = tmp_path / "invalid.json"
        config_path.write_text("invalid json content", encoding='utf-8')

        with pytest.raises(json.JSONDecodeError):
            SelectorManager(config_path=str(config_path))


class TestGetSelector:
    """测试获取选择器"""

    @pytest.fixture
    def manager(self):
        """创建 SelectorManager 实例"""
        return SelectorManager(config_path="config/selectors.json")

    def test_get_existing_selector(self, manager):
        """测试获取存在的选择器"""
        selector = manager.get_selector('product_title')
        assert selector
        assert isinstance(selector, str)
        assert len(selector) > 0

    def test_get_nonexistent_selector_with_fallback(self, manager):
        """测试获取不存在的选择器（启用后备）"""
        selector = manager.get_selector('nonexistent_key', fallback=True)
        # 应该返回空字符串或后备选择器
        assert isinstance(selector, str)

    def test_get_nonexistent_selector_without_fallback(self, manager):
        """测试获取不存在的选择器（禁用后备）"""
        selector = manager.get_selector('nonexistent_key', fallback=False)
        assert selector == ''

    def test_get_selector_with_type(self, manager):
        """测试获取不同类型的选择器"""
        # base_selectors
        base_selector = manager.get_selector('product_title', selector_type='base_selectors')
        assert base_selector

        # variant_selectors
        variant_selector = manager.get_selector('color', selector_type='variant_selectors')
        assert variant_selector

        # checkout_selectors
        checkout_selector = manager.get_selector('email', selector_type='checkout_selectors')
        assert checkout_selector


class TestFallbackSelectors:
    """测试后备选择器"""

    @pytest.fixture
    def manager(self):
        """创建 SelectorManager 实例"""
        return SelectorManager(config_path="config/selectors.json")

    def test_fallback_product_title(self, manager):
        """测试 product_title 后备选择器"""
        fallback = manager._get_fallback_selector('product_title')
        assert 'h1' in fallback
        assert 'title' in fallback

    def test_fallback_product_price(self, manager):
        """测试 product_price 后备选择器"""
        fallback = manager._get_fallback_selector('product_price')
        assert 'price' in fallback

    def test_fallback_add_to_cart_button(self, manager):
        """测试 add_to_cart_button 后备选择器"""
        fallback = manager._get_fallback_selector('add_to_cart_button')
        assert 'button' in fallback
        assert 'Add' in fallback

    def test_fallback_unknown_key(self, manager):
        """测试未知键的后备选择器"""
        fallback = manager._get_fallback_selector('unknown_key_12345')
        assert fallback == ''


class TestFindElement:
    """测试查找元素"""

    @pytest.fixture
    def manager(self):
        """创建 SelectorManager 实例"""
        return SelectorManager(config_path="config/selectors.json")

    @pytest.mark.asyncio
    async def test_find_element_success(self, manager):
        """测试成功找到元素"""
        # Mock Playwright Page
        mock_page = Mock()
        mock_locator = AsyncMock()
        mock_locator.count = AsyncMock(return_value=1)
        mock_page.locator = Mock(return_value=mock_locator)
        mock_locator.first = mock_locator

        element = await manager.find_element(mock_page, 'product_title')
        assert element is not None

    @pytest.mark.asyncio
    async def test_find_element_not_found(self, manager):
        """测试找不到元素"""
        # Mock Playwright Page
        mock_page = Mock()
        mock_locator = AsyncMock()
        mock_locator.count = AsyncMock(return_value=0)
        mock_page.locator = Mock(return_value=mock_locator)
        mock_locator.first = mock_locator

        element = await manager.find_element(mock_page, 'product_title')
        assert element is None

    @pytest.mark.asyncio
    async def test_find_element_tries_multiple_selectors(self, manager):
        """测试尝试多个选择器"""
        # Mock Playwright Page
        mock_page = Mock()

        # 第一个选择器失败，第二个成功
        call_count = [0]

        def mock_locator_func(selector):
            call_count[0] += 1
            mock_locator = AsyncMock()
            if call_count[0] == 1:
                # 第一个选择器失败
                mock_locator.count = AsyncMock(return_value=0)
            else:
                # 第二个选择器成功
                mock_locator.count = AsyncMock(return_value=1)
            mock_locator.first = mock_locator
            return mock_locator

        mock_page.locator = mock_locator_func

        element = await manager.find_element(mock_page, 'product_title')
        assert element is not None
        assert call_count[0] >= 1


class TestGetAllSelectors:
    """测试获取所有选择器"""

    @pytest.fixture
    def manager(self):
        """创建 SelectorManager 实例"""
        return SelectorManager(config_path="config/selectors.json")

    def test_get_all_base_selectors(self, manager):
        """测试获取所有基础选择器"""
        selectors = manager.get_all_selectors('base_selectors')
        assert isinstance(selectors, dict)
        assert len(selectors) > 0
        assert 'product_title' in selectors

    def test_get_all_variant_selectors(self, manager):
        """测试获取所有变体选择器"""
        selectors = manager.get_all_selectors('variant_selectors')
        assert isinstance(selectors, dict)

    def test_get_all_nonexistent_type(self, manager):
        """测试获取不存在类型的选择器"""
        selectors = manager.get_all_selectors('nonexistent_type')
        assert selectors == {}


class TestGetSelectorTypes:
    """测试获取选择器类型"""

    @pytest.fixture
    def manager(self):
        """创建 SelectorManager 实例"""
        return SelectorManager(config_path="config/selectors.json")

    def test_get_selector_types(self, manager):
        """测试获取所有选择器类型"""
        types = manager.get_selector_types()
        assert isinstance(types, list)
        assert 'base_selectors' in types
        assert 'variant_selectors' in types
        assert 'checkout_selectors' in types


class TestUpdateSelector:
    """测试更新选择器"""

    @pytest.fixture
    def manager(self):
        """创建 SelectorManager 实例"""
        return SelectorManager(config_path="config/selectors.json")

    def test_update_existing_selector(self, manager):
        """测试更新已存在的选择器"""
        new_value = '.new-product-title'
        manager.update_selector('product_title', new_value, selector_type='base_selectors')

        selector = manager.get_selector('product_title')
        assert selector == new_value

    def test_update_creates_new_selector(self, manager):
        """测试更新不存在的选择器（创建新的）"""
        new_key = 'custom_element'
        new_value = '.custom-class'
        manager.update_selector(new_key, new_value, selector_type='base_selectors')

        selector = manager.get_selector(new_key)
        assert selector == new_value

    def test_update_creates_new_selector_type(self, manager):
        """测试创建新的选择器类型"""
        manager.update_selector('test_key', '.test-class', selector_type='new_type')

        assert 'new_type' in manager.selectors
        assert manager.selectors['new_type']['test_key'] == '.test-class'


class TestSaveConfig:
    """测试保存配置"""

    @pytest.fixture
    def manager(self):
        """创建 SelectorManager 实例"""
        return SelectorManager(config_path="config/selectors.json")

    def test_save_config_to_new_path(self, manager, tmp_path):
        """测试保存配置到新路径"""
        output_path = tmp_path / "test_selectors.json"
        manager.save_config(output_path=str(output_path))

        assert output_path.exists()

        # 验证保存的内容
        with open(output_path, 'r', encoding='utf-8') as f:
            saved_config = json.load(f)

        assert 'base_selectors' in saved_config

    def test_save_config_preserves_changes(self, manager, tmp_path):
        """测试保存时保留更改"""
        output_path = tmp_path / "test_selectors.json"

        # 修改选择器
        manager.update_selector('product_title', '.new-title')

        # 保存
        manager.save_config(output_path=str(output_path))

        # 加载并验证
        with open(output_path, 'r', encoding='utf-8') as f:
            saved_config = json.load(f)

        assert saved_config['base_selectors']['product_title'] == '.new-title'


class TestDefaultConfig:
    """测试默认配置"""

    def test_default_config_structure(self):
        """测试默认配置结构"""
        manager = SelectorManager(config_path="nonexistent_path.json")

        assert 'version' in manager.selectors
        assert 'platform' in manager.selectors
        assert 'base_selectors' in manager.selectors
        assert 'variant_selectors' in manager.selectors
        assert 'checkout_selectors' in manager.selectors

    def test_default_config_has_essential_selectors(self):
        """测试默认配置包含必要的选择器"""
        manager = SelectorManager(config_path="nonexistent_path.json")

        base_selectors = manager.selectors['base_selectors']
        assert 'product_title' in base_selectors
        assert 'product_price' in base_selectors
        assert 'add_to_cart_button' in base_selectors
        assert 'cart_count' in base_selectors
