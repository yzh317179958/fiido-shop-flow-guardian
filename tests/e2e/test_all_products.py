"""
End-to-end tests for all discovered products.

This test module dynamically parameterizes itself based on the discovered
products dataset. Each product gets tested for:
- Page loads successfully
- Price is displayed
- Add-to-cart button is visible

Usage:
    # Run all products
    pytest tests/e2e/test_all_products.py -v

    # Filter by priority
    pytest tests/e2e/test_all_products.py --priority=P0 -v

    # Filter by category
    pytest tests/e2e/test_all_products.py --category=bike -v

    # Test single product
    pytest tests/e2e/test_all_products.py --product-id=fiido-d11 -v
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from core.models import Product


def test_product_page_loads(
    test_product: Product,
    page: Page,
) -> None:
    """
    Verify that the product page loads successfully.

    Checks:
    - Navigation completes without errors
    - Page title contains product name or brand
    - Page URL matches expected product URL
    """
    # Navigate to the product page with longer timeout and less strict wait condition
    page.goto(str(test_product.url), wait_until="domcontentloaded", timeout=60000)

    # Verify the page loaded
    expect(page).to_have_url(str(test_product.url), timeout=10000)

    # Verify page title contains meaningful content
    title = page.title()
    assert title, f"Page title is empty for product {test_product.id}"
    assert (
        test_product.name.lower() in title.lower()
        or "fiido" in title.lower()
    ), f"Page title '{title}' doesn't contain product name or brand"


def test_product_price_displayed(
    test_product: Product,
    page: Page,
) -> None:
    """
    Verify that the product price is visible on the page.

    Checks:
    - Price element exists and is visible
    - Price text is not empty
    """
    # Navigate to product page
    page.goto(str(test_product.url), wait_until="domcontentloaded", timeout=60000)

    # Try to find price using selectors from product metadata
    price_selector = test_product.selectors.product_price
    price_locator = page.locator(price_selector).first

    # Check if price is visible
    expect(price_locator).to_be_visible(timeout=10000)

    # Verify price text is not empty
    price_text = price_locator.inner_text()
    assert price_text.strip(), f"Price text is empty for product {test_product.id}"


def test_add_to_cart_button_exists(
    test_product: Product,
    page: Page,
) -> None:
    """
    Verify that the add-to-cart button is visible and enabled.

    Checks:
    - Add-to-cart button exists
    - Button is visible
    - Button is enabled (not disabled)
    """
    # Navigate to product page
    page.goto(str(test_product.url), wait_until="domcontentloaded", timeout=60000)

    # Try to find add-to-cart button using selectors from product metadata
    add_to_cart_selector = test_product.selectors.add_to_cart_button
    add_to_cart_btn = page.locator(add_to_cart_selector).first

    # Check if add-to-cart button is visible
    expect(add_to_cart_btn).to_be_visible(timeout=10000)

    # Verify button is enabled
    is_disabled = add_to_cart_btn.is_disabled()
    assert not is_disabled, (
        f"Add-to-cart button is disabled for product {test_product.id}"
    )
