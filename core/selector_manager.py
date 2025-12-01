"""
选择器管理器模块

管理和解析 CSS 选择器配置，支持多个后备选择器和自动查找元素。
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class SelectorManager:
    """管理和解析选择器配置

    负责加载选择器配置文件，提供选择器查找和后备机制。
    支持 Playwright Page 对象的元素查找。
    """

    def __init__(self, config_path: str = "config/selectors.json"):
        """初始化选择器管理器

        Args:
            config_path: 选择器配置文件路径
        """
        self.config_path = Path(config_path)
        self.selectors = self._load_config()
        logger.info(f"SelectorManager initialized with config: {config_path}")

    def _load_config(self) -> Dict[str, Any]:
        """加载选择器配置

        Returns:
            配置字典

        Raises:
            FileNotFoundError: 配置文件不存在
            json.JSONDecodeError: 配置文件格式错误
        """
        if not self.config_path.exists():
            logger.warning(f"Config file not found: {self.config_path}, using defaults")
            return self._get_default_config()

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                logger.debug(f"Loaded selectors config: {len(config.get('base_selectors', {}))} base selectors")
                return config
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置

        Returns:
            默认选择器配置
        """
        return {
            'version': '1.0',
            'platform': 'shopify',
            'base_selectors': {
                'product_title': '.product-title, h1.product__title',
                'product_price': '.product-price, .price',
                'add_to_cart_button': "button[name='add'], button:has-text('Add to Cart')",
                'cart_count': '.cart-count, .cart-item-count, [data-cart-count]',
                'cart_drawer': '.cart-drawer, #CartDrawer',
                'checkout_button': "button:has-text('Checkout'), a[href*='checkout']"
            },
            'variant_selectors': {
                'color': '.color-swatch, [data-option="Color"] button',
                'size': '.size-option, [data-option="Size"] button'
            },
            'checkout_selectors': {
                'email': '#email, input[name="email"]',
                'first_name': '#firstName, input[name="firstName"]',
                'last_name': '#lastName, input[name="lastName"]',
                'address': '#address1, input[name="address1"]',
                'city': '#city, input[name="city"]',
                'postal_code': '#zip, input[name="postalCode"]',
                'country': '#country, select[name="countryCode"]'
            }
        }

    def get_selector(self, key: str, selector_type: str = 'base_selectors', fallback: bool = True) -> str:
        """获取选择器，支持多个候选

        Args:
            key: 选择器键名（如 'product_title'）
            selector_type: 选择器类型（'base_selectors', 'variant_selectors', 'checkout_selectors'）
            fallback: 是否启用后备选择器

        Returns:
            选择器字符串，多个选择器用逗号分隔
        """
        selectors_group = self.selectors.get(selector_type, {})
        selector = selectors_group.get(key, '')

        if not selector and fallback:
            # 尝试通用后备
            selector = self._get_fallback_selector(key)
            if selector:
                logger.debug(f"Using fallback selector for '{key}': {selector}")

        return selector

    def _get_fallback_selector(self, key: str) -> str:
        """生成后备选择器

        Args:
            key: 选择器键名

        Returns:
            后备选择器字符串
        """
        fallbacks = {
            'product_title': 'h1, .title, [class*="product-title"], [class*="product_title"]',
            'product_price': '.price, [class*="price"], [data-price]',
            'add_to_cart_button': 'button:has-text("Add"), button:has-text("加入"), button[name="add"]',
            'cart_count': '[class*="cart-count"], [class*="cart_count"], [data-cart-count]',
            'cart_drawer': '[class*="cart-drawer"], [class*="cart_drawer"], #cart-drawer',
            'checkout_button': 'button:has-text("Checkout"), button:has-text("结账"), a[href*="checkout"]',
            # 变体后备
            'color': '[data-option="Color"] button, [data-option="color"] button, .color-swatch',
            'size': '[data-option="Size"] button, [data-option="size"] button, .size-option',
            # 结账表单后备
            'email': 'input[type="email"], input[name*="email"]',
            'first_name': 'input[name*="first"], input[name*="firstName"]',
            'last_name': 'input[name*="last"], input[name*="lastName"]',
            'address': 'input[name*="address"]',
            'city': 'input[name*="city"]',
            'postal_code': 'input[name*="postal"], input[name*="zip"]',
            'country': 'select[name*="country"]'
        }
        return fallbacks.get(key, '')

    async def find_element(self, page, key: str, selector_type: str = 'base_selectors', timeout: int = 5000):
        """使用选择器查找元素（自动尝试多个选择器）

        Args:
            page: Playwright Page 对象
            key: 选择器键名
            selector_type: 选择器类型
            timeout: 查找超时时间（毫秒）

        Returns:
            找到的元素 Locator 或 None
        """
        selector = self.get_selector(key, selector_type=selector_type)
        selectors = [s.strip() for s in selector.split(',') if s.strip()]

        logger.debug(f"Trying to find element with key='{key}', selectors={selectors}")

        for sel in selectors:
            try:
                element = page.locator(sel).first
                # 检查元素是否存在
                count = await element.count()
                if count > 0:
                    logger.debug(f"Found element with selector: {sel}")
                    return element
            except Exception as e:
                logger.debug(f"Selector '{sel}' failed: {e}")
                continue

        logger.warning(f"Could not find element with key='{key}'")
        return None

    def get_all_selectors(self, selector_type: str = 'base_selectors') -> Dict[str, str]:
        """获取某个类型的所有选择器

        Args:
            selector_type: 选择器类型

        Returns:
            选择器字典
        """
        return self.selectors.get(selector_type, {})

    def get_selector_types(self) -> List[str]:
        """获取所有可用的选择器类型

        Returns:
            选择器类型列表
        """
        return [key for key in self.selectors.keys() if key.endswith('_selectors')]

    def update_selector(self, key: str, value: str, selector_type: str = 'base_selectors'):
        """更新选择器（运行时修改，不保存到文件）

        Args:
            key: 选择器键名
            value: 新的选择器值
            selector_type: 选择器类型
        """
        if selector_type not in self.selectors:
            self.selectors[selector_type] = {}

        self.selectors[selector_type][key] = value
        logger.info(f"Updated selector: {selector_type}.{key} = {value}")

    def save_config(self, output_path: Optional[str] = None):
        """保存配置到文件

        Args:
            output_path: 输出路径，默认为原配置文件路径
        """
        save_path = Path(output_path) if output_path else self.config_path
        save_path.parent.mkdir(parents=True, exist_ok=True)

        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(self.selectors, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved selector config to {save_path}")
