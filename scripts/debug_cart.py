#!/usr/bin/env python3
"""
调试脚本：检查购物车页面的数量调整元素
"""

import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


async def debug_cart_page():
    """调试购物车页面结构"""
    # 先添加一个商品到购物车
    product_url = "https://fiido.com/products/bike-rack-pannier-bag"
    cart_url = "https://fiido.com/cart"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        print(f"1. 访问商品页面并添加到购物车: {product_url}")
        await page.goto(product_url, wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        # 点击加购按钮
        add_btn = await page.query_selector("button[name='add'], button:has-text('Add to Cart')")
        if add_btn:
            await add_btn.click()
            print("   ✓ 成功添加商品到购物车")
            await page.wait_for_timeout(2000)
        else:
            print("   ✗ 未找到加购按钮")

        print(f"\n2. 导航到购物车页面: {cart_url}")
        await page.goto(cart_url, wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        print("\n" + "="*80)
        print("3. 查找购物车中的数量相关元素")
        print("="*80)

        # 查找所有input元素
        all_inputs = await page.query_selector_all("input")
        print(f"\n找到 {len(all_inputs)} 个 input 元素\n")

        for i, inp in enumerate(all_inputs):
            try:
                input_type = await inp.get_attribute("type")
                input_name = await inp.get_attribute("name")
                input_value = await inp.get_attribute("value")
                input_class = await inp.get_attribute("class")
                is_visible = await inp.is_visible()

                # 只显示可能与数量相关的input
                if input_name and ("quantity" in input_name.lower() or "updates" in input_name.lower()):
                    print(f"Input {i+1} (可能是数量输入框):")
                    print(f"  type={input_type}, name={input_name}")
                    print(f"  value={input_value}, visible={is_visible}")
                    print(f"  class={input_class}")
                    print()
            except:
                continue

        print("\n" + "="*80)
        print("4. 查找所有按钮")
        print("="*80)

        all_buttons = await page.query_selector_all("button")
        print(f"\n找到 {len(all_buttons)} 个按钮\n")

        for i, btn in enumerate(all_buttons):
            try:
                btn_text = await btn.text_content()
                btn_name = await btn.get_attribute("name")
                btn_class = await btn.get_attribute("class")
                btn_aria = await btn.get_attribute("aria-label")
                is_visible = await btn.is_visible()

                # 只显示可见的按钮
                if is_visible and btn_text:
                    btn_text_clean = btn_text.strip()
                    # 过滤掉空文本和特殊按钮
                    if btn_text_clean and len(btn_text_clean) < 50:
                        print(f"按钮 {i+1}: {btn_text_clean[:30]}")
                        print(f"  name={btn_name}, aria-label={btn_aria}")
                        print(f"  class={btn_class[:60] if btn_class else 'N/A'}")
                        print()
            except:
                continue

        print("\n" + "="*80)
        print("5. 查找特定的数量调整按钮")
        print("="*80)

        # 测试不同的选择器
        selectors = [
            "button[name='plus']",
            "button[name='minus']",
            "button.cart-item__quantity-plus",
            "button.cart-item__quantity-minus",
            "button:has-text('+')",
            "button:has-text('-')",
            ".quantity__button",
            "[data-quantity='plus']",
            "[data-quantity='minus']"
        ]

        for selector in selectors:
            elements = await page.query_selector_all(selector)
            if elements:
                print(f"\n✓ {selector}: 找到 {len(elements)} 个元素")
                for i, elem in enumerate(elements[:2]):  # 只显示前2个
                    is_visible = await elem.is_visible()
                    text = await elem.text_content()
                    print(f"   元素 {i+1}: visible={is_visible}, text={text[:20] if text else 'N/A'}")
            else:
                print(f"✗ {selector}: 未找到")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_cart_page())
