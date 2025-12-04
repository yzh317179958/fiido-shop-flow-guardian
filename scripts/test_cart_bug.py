#!/usr/bin/env python3
"""
专门测试购物车加减按钮功能
"""

import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


async def test_cart_quantity_buttons():
    """测试购物车数量调整按钮"""

    product_url = "https://fiido.com/products/fiido-t2-longtail-cargo-ebike-for-versatile-all-terrain"
    cart_url = "https://fiido.com/cart"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # 无头模式
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
        await page.wait_for_timeout(3000)

        print("\n" + "=" * 80)
        print("步骤3: 查找数量输入框和按钮")
        print("=" * 80)

        # 查找数量输入框
        qty_inputs = await page.query_selector_all("input[name*='quantity'], input[name*='updates']")
        print(f"\n找到 {len(qty_inputs)} 个数量输入框")

        for i, inp in enumerate(qty_inputs):
            value = await inp.get_attribute("value")
            name = await inp.get_attribute("name")
            is_visible = await inp.is_visible()
            print(f"  Input {i+1}: name={name}, value={value}, visible={is_visible}")

        # 查找所有可见按钮
        all_buttons = await page.query_selector_all("button")
        print(f"\n找到 {len(all_buttons)} 个按钮")

        plus_buttons = []
        minus_buttons = []

        for btn in all_buttons:
            try:
                if not await btn.is_visible():
                    continue

                text = await btn.text_content()
                if text and text.strip():
                    text = text.strip()
                    if '+' in text or 'plus' in text.lower():
                        plus_buttons.append(btn)
                        print(f"  找到加号按钮: {text[:30]}")
                    elif '-' in text or 'minus' in text.lower():
                        minus_buttons.append(btn)
                        print(f"  找到减号按钮: {text[:30]}")
            except:
                continue

        print(f"\n总计: 加号按钮 {len(plus_buttons)} 个, 减号按钮 {len(minus_buttons)} 个")

        if len(plus_buttons) > 0 and len(qty_inputs) > 0:
            print("\n" + "=" * 80)
            print("步骤4: 测试点击加号按钮")
            print("=" * 80)

            # 清空之前的错误
            page_errors.clear()
            console_messages.clear()

            # 获取点击前的数量
            qty_input = qty_inputs[0]
            old_value = await qty_input.get_attribute("value")
            print(f"\n当前数量: {old_value}")

            # 点击加号
            print("点击加号按钮...")
            await plus_buttons[0].click()

            # 等待更新
            await page.wait_for_timeout(2000)

            # 获取点击后的数量
            new_value = await qty_input.get_attribute("value")
            print(f"点击后数量: {new_value}")

            # 检查是否有变化
            if int(new_value) > int(old_value):
                print("✓ 数量增加成功！")
            else:
                print("✗ 数量没有变化")

            # 显示Console消息
            if console_messages:
                print("\n" + "=" * 80)
                print("Console消息:")
                print("=" * 80)
                for msg in console_messages[-10:]:  # 只显示最后10条
                    print(msg)

            # 显示页面错误
            if page_errors:
                print("\n" + "=" * 80)
                print("⚠️  页面JavaScript错误:")
                print("=" * 80)
                for error in page_errors:
                    print(f"  {error}")

                print("\n⚠️  发现JavaScript错误！这说明购物车加减功能存在Bug")
            else:
                print("\n✓ 没有JavaScript错误")

        else:
            print("\n⚠️  未找到加号按钮或数量输入框")

        print("\n" + "=" * 80)
        print("测试完成")
        print("=" * 80)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(test_cart_quantity_buttons())
