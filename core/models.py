"""
核心数据模型

本模块定义了测试框架的核心数据结构，使用 Pydantic 进行数据验证。
"""

from datetime import datetime
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, HttpUrl


class ProductVariant(BaseModel):
    """
    商品变体模型

    表示商品的不同变体（如颜色、尺寸等）
    """

    name: str = Field(..., description="变体名称，如 'Black' 或 'Large'")
    type: Literal["color", "size", "style", "configuration"] = Field(
        ..., description="变体类型"
    )
    selector: str = Field(..., description="用于选择此变体的 CSS 选择器")
    available: bool = Field(default=True, description="是否有货")
    price_modifier: Optional[float] = Field(
        default=None, description="价格差异（相对于基础价格）"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Black",
                "type": "color",
                "selector": "button[data-option-value='Black']",
                "available": True,
                "price_modifier": 0.0
            }
        }


class Selectors(BaseModel):
    """
    页面选择器配置

    存储商品页面关键元素的 CSS 选择器
    """

    product_title: str = Field(
        default=".product-title, h1.product__title",
        description="商品标题选择器"
    )
    product_price: str = Field(
        default=".product-price, .price",
        description="商品价格选择器"
    )
    add_to_cart_button: str = Field(
        default="button[name='add'], button:has-text('Add to Cart')",
        description="加购按钮选择器"
    )
    variant_options: Dict[str, str] = Field(
        default_factory=dict,
        description="变体选项选择器映射"
    )

    class Config:
        extra = "allow"  # 允许额外字段
        json_schema_extra = {
            "example": {
                "product_title": ".product__title",
                "product_price": ".price",
                "add_to_cart_button": "button[name='add']",
                "variant_options": {
                    "color": ".color-swatch button",
                    "size": ".size-option button"
                }
            }
        }


class Product(BaseModel):
    """
    商品完整信息模型

    包含商品的所有属性和元数据
    """

    id: str = Field(..., description="商品唯一标识，从 URL 生成")
    name: str = Field(..., description="商品名称")
    url: HttpUrl = Field(..., description="商品页面 URL")
    category: str = Field(..., description="商品分类")
    price_min: float = Field(..., ge=0, description="最低价格")
    price_max: float = Field(..., ge=0, description="最高价格")
    currency: str = Field(default="USD", description="货币代码")
    variants: List[ProductVariant] = Field(
        default_factory=list,
        description="商品变体列表"
    )
    selectors: Selectors = Field(..., description="页面选择器配置")
    priority: Literal["P0", "P1", "P2"] = Field(
        default="P1",
        description="测试优先级: P0=核心, P1=重要, P2=普通"
    )
    tags: List[str] = Field(default_factory=list, description="商品标签")

    # 元数据
    discovered_at: datetime = Field(
        default_factory=datetime.now,
        description="商品发现时间"
    )
    last_tested: Optional[datetime] = Field(
        default=None,
        description="上次测试时间"
    )
    test_status: Literal["untested", "passing", "failing", "flaky"] = Field(
        default="untested",
        description="测试状态"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "fiido_d11",
                "name": "FIIDO D11",
                "url": "https://fiido.com/products/fiido-d11",
                "category": "Electric Bikes",
                "price_min": 999.0,
                "price_max": 1299.0,
                "currency": "USD",
                "variants": [],
                "selectors": {
                    "product_title": ".product__title",
                    "product_price": ".price",
                    "add_to_cart_button": "button[name='add']"
                },
                "priority": "P0",
                "tags": ["electric-bike", "bestseller"]
            }
        }


class TestResult(BaseModel):
    """
    测试结果模型

    记录单个测试用例的执行结果
    """

    product_id: str = Field(..., description="测试的商品 ID")
    test_name: str = Field(..., description="测试用例名称")
    status: Literal["passed", "failed", "skipped"] = Field(
        ..., description="测试状态"
    )
    duration: float = Field(..., ge=0, description="测试执行时长（秒）")
    error_message: Optional[str] = Field(
        default=None,
        description="错误信息（如果失败）"
    )
    screenshot_path: Optional[str] = Field(
        default=None,
        description="失败截图路径"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="测试执行时间"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "fiido_d11",
                "test_name": "test_product_page_loads",
                "status": "passed",
                "duration": 2.5,
                "error_message": None,
                "screenshot_path": None,
                "timestamp": "2025-12-01T10:00:00"
            }
        }


class TestSummary(BaseModel):
    """
    测试摘要模型

    汇总所有测试结果的统计信息
    """

    total: int = Field(..., ge=0, description="总测试数")
    passed: int = Field(..., ge=0, description="通过数")
    failed: int = Field(..., ge=0, description="失败数")
    skipped: int = Field(..., ge=0, description="跳过数")
    duration: float = Field(..., ge=0, description="总执行时长（秒）")
    pass_rate: float = Field(..., ge=0, le=100, description="通过率（百分比）")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="测试执行时间"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "total": 100,
                "passed": 95,
                "failed": 3,
                "skipped": 2,
                "duration": 120.5,
                "pass_rate": 95.0,
                "timestamp": "2025-12-01T10:00:00"
            }
        }
