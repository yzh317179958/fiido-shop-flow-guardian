"""
核心数据模型单元测试

测试 core/models.py 中定义的所有数据模型
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from core.models import (
    Product,
    ProductVariant,
    Selectors,
    TestResult,
    TestSummary
)


class TestProductVariant:
    """测试 ProductVariant 模型"""

    def test_create_valid_variant(self):
        """测试创建有效的商品变体"""
        variant = ProductVariant(
            name="Black",
            type="color",
            selector="button[data-option='Black']",
            available=True
        )

        assert variant.name == "Black"
        assert variant.type == "color"
        assert variant.selector == "button[data-option='Black']"
        assert variant.available is True
        assert variant.price_modifier is None

    def test_variant_with_price_modifier(self):
        """测试带有价格差异的变体"""
        variant = ProductVariant(
            name="Large",
            type="size",
            selector=".size-large",
            available=True,
            price_modifier=50.0
        )

        assert variant.price_modifier == 50.0

    def test_variant_type_validation(self):
        """测试变体类型验证"""
        # 有效类型
        for valid_type in ["color", "size", "style", "configuration"]:
            variant = ProductVariant(
                name="Test",
                type=valid_type,
                selector=".test"
            )
            assert variant.type == valid_type

        # 无效类型应该抛出验证错误
        with pytest.raises(ValidationError):
            ProductVariant(
                name="Test",
                type="invalid_type",
                selector=".test"
            )

    def test_variant_unavailable(self):
        """测试缺货变体"""
        variant = ProductVariant(
            name="Red",
            type="color",
            selector=".color-red",
            available=False
        )

        assert variant.available is False


class TestSelectors:
    """测试 Selectors 模型"""

    def test_default_selectors(self):
        """测试默认选择器"""
        selectors = Selectors()

        assert selectors.product_title == ".product-title, h1.product__title"
        assert selectors.product_price == ".product-price, .price"
        assert "add" in selectors.add_to_cart_button.lower()
        assert isinstance(selectors.variant_options, dict)

    def test_custom_selectors(self):
        """测试自定义选择器"""
        selectors = Selectors(
            product_title=".custom-title",
            product_price=".custom-price",
            add_to_cart_button="#add-button"
        )

        assert selectors.product_title == ".custom-title"
        assert selectors.product_price == ".custom-price"
        assert selectors.add_to_cart_button == "#add-button"

    def test_variant_options(self):
        """测试变体选项选择器"""
        selectors = Selectors(
            variant_options={
                "color": ".color-swatch button",
                "size": ".size-option button"
            }
        )

        assert "color" in selectors.variant_options
        assert "size" in selectors.variant_options
        assert selectors.variant_options["color"] == ".color-swatch button"

    def test_extra_fields_allowed(self):
        """测试允许额外字段"""
        selectors = Selectors(
            product_title=".title",
            custom_field="custom_value"
        )

        # Pydantic 应该允许额外字段
        assert hasattr(selectors, "custom_field")


class TestProduct:
    """测试 Product 模型"""

    def test_create_minimal_product(self):
        """测试创建最小必需字段的商品"""
        product = Product(
            id="test_product",
            name="Test Product",
            url="https://fiido.com/products/test",
            category="Test Category",
            price_min=100.0,
            price_max=150.0,
            selectors=Selectors()
        )

        assert product.id == "test_product"
        assert product.name == "Test Product"
        assert str(product.url) == "https://fiido.com/products/test"
        assert product.category == "Test Category"
        assert product.price_min == 100.0
        assert product.price_max == 150.0
        assert product.currency == "USD"  # 默认值
        assert product.priority == "P1"  # 默认值
        assert product.test_status == "untested"  # 默认值

    def test_product_with_variants(self):
        """测试带有变体的商品"""
        variants = [
            ProductVariant(
                name="Black",
                type="color",
                selector=".color-black"
            ),
            ProductVariant(
                name="White",
                type="color",
                selector=".color-white"
            )
        ]

        product = Product(
            id="test_bike",
            name="Test Bike",
            url="https://fiido.com/products/test-bike",
            category="Electric Bikes",
            price_min=999.0,
            price_max=999.0,
            selectors=Selectors(),
            variants=variants
        )

        assert len(product.variants) == 2
        assert product.variants[0].name == "Black"
        assert product.variants[1].name == "White"

    def test_product_priority_validation(self):
        """测试优先级验证"""
        # 有效优先级
        for priority in ["P0", "P1", "P2"]:
            product = Product(
                id="test",
                name="Test",
                url="https://fiido.com/products/test",
                category="Test",
                price_min=100.0,
                price_max=100.0,
                selectors=Selectors(),
                priority=priority
            )
            assert product.priority == priority

        # 无效优先级
        with pytest.raises(ValidationError):
            Product(
                id="test",
                name="Test",
                url="https://fiido.com/products/test",
                category="Test",
                price_min=100.0,
                price_max=100.0,
                selectors=Selectors(),
                priority="P3"
            )

    def test_product_price_validation(self):
        """测试价格验证（必须非负）"""
        # 有效价格
        product = Product(
            id="test",
            name="Test",
            url="https://fiido.com/products/test",
            category="Test",
            price_min=0.0,
            price_max=100.0,
            selectors=Selectors()
        )
        assert product.price_min == 0.0

        # 负数价格应该抛出验证错误
        with pytest.raises(ValidationError):
            Product(
                id="test",
                name="Test",
                url="https://fiido.com/products/test",
                category="Test",
                price_min=-10.0,
                price_max=100.0,
                selectors=Selectors()
            )

    def test_product_url_validation(self):
        """测试 URL 格式验证"""
        # 有效 URL
        product = Product(
            id="test",
            name="Test",
            url="https://fiido.com/products/test",
            category="Test",
            price_min=100.0,
            price_max=100.0,
            selectors=Selectors()
        )
        assert str(product.url) == "https://fiido.com/products/test"

        # 无效 URL 应该抛出验证错误
        with pytest.raises(ValidationError):
            Product(
                id="test",
                name="Test",
                url="not-a-valid-url",
                category="Test",
                price_min=100.0,
                price_max=100.0,
                selectors=Selectors()
            )

    def test_product_timestamps(self):
        """测试时间戳字段"""
        product = Product(
            id="test",
            name="Test",
            url="https://fiido.com/products/test",
            category="Test",
            price_min=100.0,
            price_max=100.0,
            selectors=Selectors()
        )

        # discovered_at 应该自动设置
        assert isinstance(product.discovered_at, datetime)
        assert product.last_tested is None


class TestTestResult:
    """测试 TestResult 模型"""

    def test_create_passed_result(self):
        """测试创建通过的测试结果"""
        result = TestResult(
            product_id="fiido_d11",
            test_name="test_page_load",
            status="passed",
            duration=2.5
        )

        assert result.product_id == "fiido_d11"
        assert result.test_name == "test_page_load"
        assert result.status == "passed"
        assert result.duration == 2.5
        assert result.error_message is None
        assert result.screenshot_path is None

    def test_create_failed_result(self):
        """测试创建失败的测试结果"""
        result = TestResult(
            product_id="fiido_d11",
            test_name="test_add_to_cart",
            status="failed",
            duration=3.0,
            error_message="Button not found",
            screenshot_path="screenshots/test_failed.png"
        )

        assert result.status == "failed"
        assert result.error_message == "Button not found"
        assert result.screenshot_path == "screenshots/test_failed.png"

    def test_duration_validation(self):
        """测试执行时长验证（必须非负）"""
        # 有效时长
        result = TestResult(
            product_id="test",
            test_name="test",
            status="passed",
            duration=0.0
        )
        assert result.duration == 0.0

        # 负数时长应该抛出验证错误
        with pytest.raises(ValidationError):
            TestResult(
                product_id="test",
                test_name="test",
                status="passed",
                duration=-1.0
            )


class TestTestSummary:
    """测试 TestSummary 模型"""

    def test_create_summary(self):
        """测试创建测试摘要"""
        summary = TestSummary(
            total=100,
            passed=95,
            failed=3,
            skipped=2,
            duration=120.5,
            pass_rate=95.0
        )

        assert summary.total == 100
        assert summary.passed == 95
        assert summary.failed == 3
        assert summary.skipped == 2
        assert summary.duration == 120.5
        assert summary.pass_rate == 95.0

    def test_pass_rate_validation(self):
        """测试通过率验证（0-100）"""
        # 有效通过率
        summary = TestSummary(
            total=10,
            passed=10,
            failed=0,
            skipped=0,
            duration=10.0,
            pass_rate=100.0
        )
        assert summary.pass_rate == 100.0

        # 超过 100 应该抛出验证错误
        with pytest.raises(ValidationError):
            TestSummary(
                total=10,
                passed=10,
                failed=0,
                skipped=0,
                duration=10.0,
                pass_rate=150.0
            )

        # 负数应该抛出验证错误
        with pytest.raises(ValidationError):
            TestSummary(
                total=10,
                passed=0,
                failed=10,
                skipped=0,
                duration=10.0,
                pass_rate=-10.0
            )
