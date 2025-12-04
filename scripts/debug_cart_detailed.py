#!/usr/bin/env python3
"""
详细调试购物车页面 - 可视化模式
检查数量调整按钮的真实情况
"""

import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


async def debug_cart_with_screenshots():
    """调试购物车页面,截图保存"""

    product_url = "https://fiido.com/products/fiido-t2-longtail-cargo-ebike-for-versatile-all-terrain"
    cart_url = "https://fiido.com/cart"

    async with async_playwright() as p:
        # 使用可见模式
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context()
        page = await context.new_page()

        # 监听console消息
        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))

        # 监听页面错误
        page_errors = []
        page.on("pageerror", lambda exc: page_errors.append(str(exc)))

        print("=" * 80)
        print("步骤1: 添加商品到购物车")
        print("=" * 80)

        await page.goto(product_url, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)

        # 添加到购物车
        add_btn = await page.query_selector("button[name='add']")
        if add_btn:
            await add_btn.click()
            print("✓ 点击了添加购物车按钮")
            await page.wait_for_timeout(3000)

        print("\n" + "=" * 80)
        print("步骤2: 导航到购物车页面")
        print("=" * 80)

        await page.goto(cart_url, wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)  # 给足时间让动态内容加载

        # 截图1: 购物车整体页面
        screenshot_path = PROJECT_ROOT / "debug_cart_full.png"
        await page.screenshot(path=str(screenshot_path), full_page=True)
        print(f"\n✓ 已截图: {screenshot_path}")

        print("\n" + "=" * 80)
        print("步骤3: 详细分析购物车DOM结构")
        print("=" * 80)

        # 1. 查找所有input元素
        print("\n【所有Input元素】")
        all_inputs = await page.query_selector_all("input")
        for i, inp in enumerate(all_inputs):
            try:
                input_type = await inp.get_attribute("type")
                input_name = await inp.get_attribute("name")
                input_value = await inp.get_attribute("value")
                input_id = await inp.get_attribute("id")
                input_class = await inp.get_attribute("class")
                is_visible = await inp.is_visible()

                print(f"\nInput #{i+1}:")
                print(f"  type={input_type}")
                print(f"  name={input_name}")
                print(f"  value={input_value}")
                print(f"  id={input_id}")
                print(f"  class={input_class}")
                print(f"  visible={is_visible}")
            except:
                continue

        # 2. 查找所有button元素
        print("\n\n【所有Button元素】")
        all_buttons = await page.query_selector_all("button")
        print(f"总共找到 {len(all_buttons)} 个按钮\n")

        visible_buttons = []
        for i, btn in enumerate(all_buttons):
            try:
                is_visible = await btn.is_visible()
                if is_visible:
                    btn_text = await btn.text_content()
                    btn_name = await btn.get_attribute("name")
                    btn_class = await btn.get_attribute("class")
                    btn_aria = await btn.get_attribute("aria-label")

                    visible_buttons.append({
                        'index': i+1,
                        'text': btn_text.strip() if btn_text else '',
                        'name': btn_name,
                        'class': btn_class,
                        'aria': btn_aria
                    })
            except:
                continue

        print(f"可见按钮: {len(visible_buttons)} 个\n")
        for btn in visible_buttons:
            if btn['text'] and len(btn['text']) < 100:  # 过滤掉太长的文本
                print(f"Button #{btn['index']}:")
                print(f"  text: {btn['text'][:50]}")
                print(f"  name: {btn['name']}")
                print(f"  class: {btn['class'][:60] if btn['class'] else 'N/A'}")
                print(f"  aria: {btn['aria']}")
                print()

        # 3. 查找cart-item相关元素
        print("\n【购物车商品项】")
        cart_items = await page.query_selector_all(".cart-item, [class*='cart-item'], .line-item")
        print(f"找到 {len(cart_items)} 个购物车商品项\n")

        for i, item in enumerate(cart_items):
            print(f"\n购物车商品 #{i+1}:")

            # 查找该商品项内的所有button
            item_buttons = await item.query_selector_all("button")
            print(f"  该商品项内的按钮数: {len(item_buttons)}")

            for j, btn in enumerate(item_buttons):
                try:
                    is_visible = await btn.is_visible()
                    btn_text = await btn.text_content()
                    btn_name = await btn.get_attribute("name")
                    btn_class = await btn.get_attribute("class")

                    if is_visible:
                        print(f"    按钮#{j+1}: text='{btn_text.strip() if btn_text else ''}', name={btn_name}, class={btn_class[:40] if btn_class else 'N/A'}")
                except:
                    continue

            # 查找该商品项内的所有input
            item_inputs = await item.query_selector_all("input")
            print(f"  该商品项内的输入框数: {len(item_inputs)}")

            for j, inp in enumerate(item_inputs):
                try:
                    input_type = await inp.get_attribute("type")
                    input_name = await inp.get_attribute("name")
                    input_value = await inp.get_attribute("value")
                    is_visible = await inp.is_visible()

                    if is_visible or "quantity" in (input_name or "").lower():
                        print(f"    输入框#{j+1}: type={input_type}, name={input_name}, value={input_value}, visible={is_visible}")
                except:
                    continue

        # 4. 使用更广泛的选择器搜索
        print("\n\n【使用广泛选择器搜索数量相关元素】")

        quantity_selectors = [
            "input[name*='quantity']",
            "input[name*='qty']",
            "input[name*='updates']",
            "input[type='number']",
            ".quantity input",
            ".qty input",
            "[data-quantity]",
            ".cart-item__quantity input",
            ".line-item__quantity input"
        ]

        for selector in quantity_selectors:
            elements = await page.query_selector_all(selector)
            if elements:
                print(f"\n✓ 选择器 '{selector}' 找到 {len(elements)} 个元素")
                for i, elem in enumerate(elements[:2]):  # 只显示前2个
                    try:
                        value = await elem.get_attribute("value")
                        name = await elem.get_attribute("name")
                        is_visible = await elem.is_visible()
                        print(f"   元素#{i+1}: value={value}, name={name}, visible={is_visible}")
                    except:
                        pass

        # 5. 查找plus/minus按钮
        print("\n\n【查找加减按钮】")

        plus_selectors = [
            "button[name='plus']",
            "button[name='increase']",
            "button:has-text('+')",
            "button.quantity-plus",
            "button.qty-plus",
            ".quantity__button--plus",
            "[aria-label*='Increase']",
            "[data-action='increase-quantity']"
        ]

        minus_selectors = [
            "button[name='minus']",
            "button[name='decrease']",
            "button:has-text('-')",
            "button.quantity-minus",
            "button.qty-minus",
            ".quantity__button--minus",
            "[aria-label*='Decrease']",
            "[data-action='decrease-quantity']"
        ]

        print("\n加号按钮:")
        for selector in plus_selectors:
            elements = await page.query_selector_all(selector)
            if elements:
                print(f"  ✓ '{selector}': {len(elements)} 个")

        print("\n减号按钮:")
        for selector in minus_selectors:
            elements = await page.query_selector_all(selector)
            if elements:
                print(f"  ✓ '{selector}': {len(elements)} 个")

        # 6. 显示Console和页面错误
        if console_messages:
            print("\n\n【Console消息】")
            for msg in console_messages[-20:]:
                print(f"  {msg}")

        if page_errors:
            print("\n\n【页面JavaScript错误】")
            for error in page_errors:
                print(f"  ⚠️  {error}")

        print("\n" + "=" * 80)
        print("调试完成 - 浏览器窗口将保持打开10秒供查看")
        print("=" * 80)

        # 保持浏览器打开,方便查看
        await page.wait_for_timeout(10000)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_cart_with_screenshots())
