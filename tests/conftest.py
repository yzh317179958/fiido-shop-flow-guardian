"""
Pytest shared fixtures and hooks.

This module wires up dynamic product data loading so that end-to-end tests can
reuse the same discovery output without duplicating boilerplate in each test
module.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List

import pytest
from pydantic import ValidationError
from playwright.async_api import Page
from playwright.sync_api import Page as SyncPage

from core.models import Product
from pages.product_page import ProductPage

logger = logging.getLogger(__name__)

# Screenshot directory configuration
SCREENSHOT_DIR = Path("screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)


@dataclass(frozen=True)
class ProductDataset:
    """Container for a discovered product dataset."""

    path: Path
    metadata: Dict[str, Any]
    products: List[Product]


_DATASET_CACHE: Dict[Path, ProductDataset] = {}
_DEFAULT_PRODUCT_FILES: tuple[Path, ...] = (
    Path("data/discovered_products.json"),
    Path("data/products.json"),
    Path("data/demo_products.json"),
    Path("data/test_products.json"),
)


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register custom command line options used to filter product tests."""
    group = parser.getgroup("fiido-product-options")
    group.addoption(
        "--priority",
        action="store",
        default=None,
        help="Filter discovered products by priority (P0/P1/P2).",
    )
    group.addoption(
        "--category",
        action="store",
        default=None,
        help="Filter discovered products by category substring (case-insensitive).",
    )
    group.addoption(
        "--product-id",
        action="store",
        default=None,
        help="Run tests for a single product id only.",
    )
    group.addoption(
        "--product-file",
        action="store",
        default=None,
        help="Optional path to a discovered_products JSON file. "
             "Defaults to the first existing file among data/discovered_products.json, "
             "data/products.json, data/demo_products.json, data/test_products.json.",
    )


def _resolve_product_file(config: pytest.Config) -> Path:
    """Determine which product dataset JSON file to use."""
    custom_path = config.getoption("--product-file")
    candidates: List[Path] = []
    if custom_path:
        candidates.append(Path(custom_path).expanduser())
    candidates.extend(_DEFAULT_PRODUCT_FILES)

    for candidate in candidates:
        if candidate.exists():
            return candidate

    pytest.skip(
        "未找到商品数据文件。请运行 scripts/discover_products.py 生成 "
        "data/discovered_products.json，或通过 --product-file 指定文件。"
    )


def _load_dataset_from_file(file_path: Path) -> ProductDataset:
    """Load the dataset from disk and convert entries into Product models."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except json.JSONDecodeError as exc:
        raise pytest.UsageError(f"Invalid JSON in {file_path}: {exc}") from exc

    metadata = raw_data.get("metadata", {})
    products_raw = raw_data.get("products", [])

    products: List[Product] = []
    invalid_entries = 0

    for entry in products_raw:
        try:
            products.append(Product(**entry))
        except ValidationError as exc:
            invalid_entries += 1
            logger.warning(
                "Skipping invalid product entry %s: %s",
                entry.get("id", "<unknown>"),
                exc,
            )

    if not products:
        pytest.skip(f"{file_path} 不包含可用的商品数据。")

    if invalid_entries:
        logger.warning(
            "Skipped %d invalid product entries while loading %s",
            invalid_entries,
            file_path,
        )

    return ProductDataset(path=file_path, metadata=metadata, products=products)


def _get_product_dataset(config: pytest.Config) -> ProductDataset:
    """Load (and cache) the product dataset for the current test session."""
    dataset_path = _resolve_product_file(config)
    cache_key = dataset_path.resolve()

    if cache_key not in _DATASET_CACHE:
        _DATASET_CACHE[cache_key] = _load_dataset_from_file(cache_key)

    return _DATASET_CACHE[cache_key]


def _filter_products(products: List[Product], config: pytest.Config) -> List[Product]:
    """Apply CLI filters to the loaded product list."""
    product_id = config.getoption("--product-id")
    if product_id:
        match = next((p for p in products if p.id == product_id), None)
        if not match:
            pytest.skip(f"商品 {product_id} 未在数据集中找到。")
        return [match]

    filtered = list(products)

    priority = config.getoption("--priority")
    if priority:
        normalized = priority.strip().upper()
        if normalized not in {"P0", "P1", "P2"}:
            raise pytest.UsageError(
                f"未知的优先级 '{priority}'，请使用 P0/P1/P2。"
            )
        filtered = [p for p in filtered if p.priority.upper() == normalized]

    category = config.getoption("--category")
    if category:
        keyword = category.strip().lower()
        filtered = [p for p in filtered if keyword in p.category.lower()]

    return filtered


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    """Dynamically parameterize tests that depend on discovered products."""
    if "test_product" not in metafunc.fixturenames:
        return

    dataset = _get_product_dataset(metafunc.config)
    filtered_products = _filter_products(dataset.products, metafunc.config)

    if not filtered_products:
        pytest.skip(
            f"过滤条件没有匹配到任何商品（数据集: {dataset.path})."
        )

    metafunc.parametrize(
        "test_product",
        filtered_products,
        ids=[product.id for product in filtered_products],
    )


@pytest.fixture(scope="session")
def product_dataset(pytestconfig: pytest.Config) -> ProductDataset:
    """Provide the loaded dataset so tests can inspect metadata when needed."""
    return _get_product_dataset(pytestconfig)


@pytest.fixture(scope="session")
def discovered_products(product_dataset: ProductDataset) -> Dict[str, Product]:
    """Map of product id -> Product for quick lookup inside tests."""
    return {product.id: product for product in product_dataset.products}


@pytest.fixture(scope="session")
def product_by_id(discovered_products: Dict[str, Product]) -> Callable[[str], Product]:
    """Helper fixture to fetch a product by id and skip tests if it is missing."""

    def _get_product(product_id: str) -> Product:
        if product_id not in discovered_products:
            pytest.skip(f"商品 {product_id} 未在数据集中，已跳过。")
        return discovered_products[product_id]

    return _get_product


@pytest.fixture
def product_page_factory(page: Page) -> Callable[[Product], Awaitable[ProductPage]]:
    """Create a ProductPage bound to the shared Playwright page."""

    async def _create(product: Product, *, wait_until: str = "networkidle") -> ProductPage:
        product_page = ProductPage(page, product)
        await product_page.navigate(wait_until=wait_until)
        return product_page

    return _create


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Pytest hook to capture test results and take screenshots on failure.

    This hook runs after each test phase (setup, call, teardown) and captures
    the test outcome. If a test fails during the 'call' phase, it triggers
    a screenshot capture.
    """
    # Execute all other hooks to obtain the report object
    outcome = yield
    report = outcome.get_result()

    # Only process failures during the actual test call (not setup/teardown)
    if report.when == "call" and report.failed:
        # Check if the test uses a Playwright page fixture
        if "page" in item.fixturenames:
            try:
                page = item.funcargs.get("page")
                if page and isinstance(page, SyncPage):
                    _capture_screenshot_on_failure(item, page)
            except Exception as e:
                logger.warning(f"Failed to capture screenshot: {e}")


def _capture_screenshot_on_failure(item: pytest.Item, page: SyncPage) -> None:
    """
    Capture a screenshot when a test fails.

    Args:
        item: The pytest test item
        page: The Playwright page object
    """
    # Generate a unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_name = item.nodeid.replace("::", "_").replace("/", "_")
    screenshot_name = f"FAILED_{test_name}_{timestamp}.png"
    screenshot_path = SCREENSHOT_DIR / screenshot_name

    try:
        # Capture full page screenshot
        page.screenshot(path=str(screenshot_path), full_page=True)
        logger.info(f"Screenshot saved: {screenshot_path}")

        # Add screenshot path to test report (visible in pytest output)
        if hasattr(item, "user_properties"):
            item.user_properties.append(("screenshot", str(screenshot_path)))

        # Print to console for immediate visibility
        print(f"\n📸 Screenshot saved to: {screenshot_path}")

    except Exception as e:
        logger.error(f"Failed to save screenshot to {screenshot_path}: {e}")
