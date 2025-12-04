#!/usr/bin/env python3
"""
改进的购物车调试脚本 - 确保商品被添加到购物车
"""

import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


async def debug_cart_with_guaranteed_item():
    """调试购物车页面,确保先添加商品"""

    product_url = "https://fiido.com/products/fiido-t2-longtail-cargo-ebike-for-versatile-all-terrain"
    cart_url = "https://fiido.com/cart"

    async with async_playwright() as p:
        # 使用可见模式
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context()
        page = await context.new_page()

        # 监听console消息
        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))

        # 监听页面错误
        page_errors = []
        page.on("pageerror", lambda exc: page_errors.append(str(exc)))

        print("=" * 80)
        print("步骤1: 访问商品页面并添加到购物车")
        print("=" * 80)

        await page.goto(product_url, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)

        # 查找并点击添加购物车按钮
        add_btn = await page.query_selector("button[name='add']")
        if add_btn:
            is_enabled = await add_btn.is_enabled()
            print(f"✓ 找到添加购物车按钮, enabled={is_enabled}")

            if is_enabled:
                await add_btn.click()
                print("✓ 点击了添加购物车按钮")
                await page.wait_for_timeout(3000)

                # 检查购物车数量badge
                cart_count = await page.query_selector(".header__cart-count, .cart-count, [data-cart-count]")
                if cart_count:
                    count_text = await cart_count.text_content()
                    print(f"✓ 购物车数量badge显示: {count_text}")
            else:
                print("⚠️  添加购物车按钮不可用,可能需要选择变体")
        else:
            print("❌ 未找到添加购物车按钮")

        print("\n" + "=" * 80)
        print("步骤2: 导航到购物车页面(不刷新页面,直接导航)")
        print("=" * 80)

        # 方式1: 直接导航(可能丢失会话)
        await page.goto(cart_url, wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)

        print(f"当前URL: {page.url}")

        print("\n" + "=" * 80)
        print("步骤3: 检查购物车内容")
        print("=" * 80)

        # 检查购物车是否为空
        empty_indicators = [
            "text='Your cart is empty'",
            "text='购物车为空'",
            ".cart-empty",
            ".empty-cart"
        ]

        is_empty = False
        for indicator in empty_indicators:
            elem = await page.query_selector(indicator)
            if elem:
                is_empty = True
                print(f"❌ 购物车为空(找到指示器: {indicator})")
                break

        if not is_empty:
            print("✓ 购物车不为空,查找商品项...")

            # 尝试多种选择器查找购物车商品
            cart_item_selectors = [
                ".cart-item",
                ".cart__item",
                "[class*='cart-item']",
                ".line-item",
                "[data-cart-item]",
                "form[action='/cart'] .cart-items > *",
                "cart-items > *"
            ]

            cart_items = []
            for selector in cart_item_selectors:
                items = await page.query_selector_all(selector)
                if items:
                    print(f"  ✓ 选择器 '{selector}' 找到 {len(items)} 个商品项")
                    cart_items = items
                    break

            if cart_items:
                print(f"\n找到 {len(cart_items)} 个购物车商品\n")

                # 详细分析第一个商品项
                item = cart_items[0]
                print("【第一个商品项详细分析】")

                # 查找数量输入框
                qty_selectors = [
                    "input[name*='quantity']",
                    "input[name*='qty']",
                    "input[name*='updates']",
                    "input[type='number']",
                    ".quantity input",
                    "cart-remove-button input"
                ]

                qty_input = None
                for selector in qty_selectors:
                    qty_input = await item.query_selector(selector)
                    if qty_input:
                        value = await qty_input.get_attribute("value")
                        name = await qty_input.get_attribute("name")
                        is_visible = await qty_input.is_visible()
                        print(f"  ✓ 数量输入框('{selector}'): value={value}, name={name}, visible={is_visible}")
                        break

                # 查找加号按钮
                plus_selectors = [
                    "button[name='plus']",
                    "button[name='increase']",
                    "button:has-text('+')",
                    ".quantity__button--plus",
                    "[aria-label*='Increase']"
                ]

                plus_btn = None
                for selector in plus_selectors:
                    plus_btn = await item.query_selector(selector)
                    if plus_btn:
                        is_visible = await plus_btn.is_visible()
                        is_enabled = await plus_btn.is_enabled()
                        btn_text = await plus_btn.text_content()
                        print(f"  ✓ 加号按钮('{selector}'): text='{btn_text.strip()}', visible={is_visible}, enabled={is_enabled}")

                        if is_visible and is_enabled and qty_input:
                            # 测试点击加号
                            print("\n【测试点击加号按钮】")
                            old_value = await qty_input.get_attribute("value")
                            print(f"  点击前数量: {old_value}")

                            js_errors_before = len(page_errors)
                            await plus_btn.click()
                            await page.wait_for_timeout(2000)

                            new_value = await qty_input.get_attribute("value")
                            new_errors = page_errors[js_errors_before:]

                            print(f"  点击后数量: {new_value}")

                            if int(new_value) > int(old_value):
                                print("  ✅ 数量增加成功!")
                            else:
                                print("  ❌ 数量未变化 - 这是Bug!")
                                if new_errors:
                                    print(f"  ⚠️  触发了 {len(new_errors)} 个JavaScript错误:")
                                    for err in new_errors[:3]:
                                        print(f"     - {err[:100]}")
                        break

                if not plus_btn:
                    print("  ⚠️  未找到加号按钮")
                if not qty_input:
                    print("  ⚠️  未找到数量输入框")
            else:
                print("❌ 未找到任何购物车商品项")
        else:
            print("购物车为空,无法测试数量调整功能")

        # 显示JavaScript错误
        if page_errors:
            print("\n" + "=" * 80)
            print("【JavaScript错误】")
            print("=" * 80)
            for i, error in enumerate(page_errors, 1):
                print(f"{i}. {error}")

        print("\n" + "=" * 80)
        print("调试完成 - 浏览器窗口将保持打开15秒供查看")
        print("=" * 80)

        # 保持浏览器打开
        await page.wait_for_timeout(15000)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_cart_with_guaranteed_item())
