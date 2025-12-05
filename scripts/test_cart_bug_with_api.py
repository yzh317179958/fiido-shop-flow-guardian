#!/usr/bin/env python3
"""
购物车Bug测试 - 使用Shopify Cart API确保购物车有商品
"""

import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


async def test_cart_bug_with_api():
    """使用Shopify Cart API添加商品后测试购物车Bug"""

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context()
        page = await context.new_page()

        # 监听JavaScript错误
        js_errors = []
        page.on("pageerror", lambda exc: js_errors.append(str(exc)))

        console_errors = []
        def on_console(msg):
            if msg.type == "error":
                console_errors.append(msg.text)
        page.on("console", on_console)

        print("=" * 80)
        print("步骤1: 访问Fiido网站建立会话")
        print("=" * 80)

        await page.goto("https://fiido.com", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        print("✓ 已访问首页,建立会话")

        print("\n" + "=" * 80)
        print("步骤2: 使用Shopify Cart API添加商品")
        print("=" * 80)

        # Shopify Cart API: POST /cart/add.js
        # variant_id需要从产品页获取
        # 示例: Fiido T2的variant ID

        # 方法1: 通过JavaScript直接调用Shopify Cart API
        add_to_cart_script = """
        async () => {
            // Shopify Cart API
            const response = await fetch('/cart/add.js', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    items: [{
                        id: 51235613540565,  // Fiido T2 variant ID
                        quantity: 1
                    }]
                })
            });

            const data = await response.json();
            return data;
        }
        """

        try:
            result = await page.evaluate(add_to_cart_script)
            print(f"✓ Cart API返回: {result}")
            await page.wait_for_timeout(2000)
        except Exception as e:
            print(f"❌ Cart API失败: {e}")
            print("尝试通过访问商品页添加...")

            # 降级方案: 访问商品页点击添加按钮
            product_url = "https://fiido.com/products/fiido-t2-longtail-cargo-ebike-for-versatile-all-terrain"
            await page.goto(product_url, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)

            add_btn = await page.query_selector("button[name='add']")
            if add_btn and await add_btn.is_enabled():
                await add_btn.click()
                await page.wait_for_timeout(3000)
                print("✓ 已通过商品页添加到购物车")

        print("\n" + "=" * 80)
        print("步骤3: 导航到购物车页面")
        print("=" * 80)

        await page.goto("https://fiido.com/cart", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)

        print(f"当前URL: {page.url}")

        # 检查购物车是否为空
        empty_cart = await page.query_selector("text='Your cart is empty'")
        if empty_cart:
            print("❌ 购物车为空!")
            await browser.close()
            return

        print("\n" + "=" * 80)
        print("步骤4: 查找购物车元素")
        print("=" * 80)

        # 根据图片,查找数量输入框和加号按钮
        # 购物车UI结构: 减号 - 数量 - 加号

        # 🎯 新策略: 不管元素类型,直接通过文本查找并获取数量
        # 根据UI,数量显示在 - 和 + 之间

        # 方法1: 查找包含"Quantity"列的所有元素
        print("查找数量显示...")

        # 先尝试查找数字1(从截图看,数量显示为纯数字)
        # 在Quantity列下查找
        qty_text = None

        # 尝试多种方式获取当前数量
        # 1. 查找input元素
        qty_input = await page.query_selector("input[type='number']")
        if qty_input:
            qty_text = await qty_input.get_attribute("value")
            print(f"✓ 从input获取数量: {qty_text}")

        # 2. 如果没有input,尝试从页面文本中提取
        if not qty_text:
            # 从页面截图我们知道数量在 - 和 + 之间
            # 先获取整个Quantity列的内容
            page_text = await page.content()
            print("未找到input元素,将通过点击测试数量变化...")

        # 📍 新策略: 直接通过DOM结构查找
        # 从截图看,购物车商品在table row或div中
        # 数量控制在Quantity列

        print("\n查找购物车商品行...")

        # 查找所有可能的商品行
        cart_items = []
        item_selectors = [
            "tr",  # 表格行
            "[data-line-item]",
            ".cart-item",
            ".line-item",
            "cart-item"
        ]

        for selector in item_selectors:
            items = await page.query_selector_all(selector)
            if items and len(items) > 0:
                print(f"✓ 找到 {len(items)} 个元素使用选择器: {selector}")
                cart_items = items
                break

        if not cart_items:
            print("❌ 未找到购物车商品行")
            await page.screenshot(path="no_cart_items.png", full_page=True)
            await browser.close()
            return

        # 使用第一个商品进行测试(跳过可能的表头)
        test_item = None
        for i, item in enumerate(cart_items):
            # 检查是否包含button/a元素
            buttons = await item.query_selector_all("button, a")
            if len(buttons) > 0:
                test_item = item
                print(f"使用第{i+1}个元素作为商品行(包含{len(buttons)}个button/a)")
                break

        if not test_item:
            print("❌ 所有元素都不包含button/a")
            await page.screenshot(path="no_buttons_in_items.png", full_page=True)
            await browser.close()
            return

        #使用test_item而不是first_item
        first_item = test_item

        # 在商品行内查找所有button和a元素
        buttons_in_item = await first_item.query_selector_all("button, a")
        print(f"该商品行内找到 {len(buttons_in_item)} 个button/a元素")

        # 打印每个button的内容
        plus_btn = None
        for i, btn in enumerate(buttons_in_item):
            try:
                is_visible = await btn.is_visible()
                if is_visible:
                    text = await btn.text_content()
                    inner_html = await btn.inner_html()
                    tag_name = await btn.evaluate("el => el.tagName")
                    name = await btn.get_attribute("name")

                    print(f"  元素#{i+1}: {tag_name}, name={name}, text='{text.strip() if text else ''}', html={inner_html[:50]}")

                    # 查找包含"+"的元素
                    if text and '+' in text.strip():
                        print(f"    ✓ 这是加号按钮!")
                        plus_btn = btn
                    elif name and 'plus' in name.lower():
                        print(f"    ✓ 这是加号按钮(通过name属性)!")
                        plus_btn = btn
                    elif inner_html and ('+' in inner_html or 'plus' in inner_html.lower()):
                        print(f"    ✓ 可能是加号按钮(HTML包含+或plus)!")
                        if not plus_btn:  # 如果还没找到,用这个
                            plus_btn = btn
            except:
                continue

        if not plus_btn:
            print("❌ 在商品行内未找到加号按钮")
            await page.screenshot(path="no_plus_in_item.png", full_page=True)
            await browser.close()
            return

        print(f"\n✓ 找到加号按钮")

        print("\n" + "=" * 80)
        print("步骤5: 测试点击加号按钮")
        print("=" * 80)

        js_errors_before = len(js_errors)
        console_errors_before = len(console_errors)

        # 📸 点击前截图
        await page.screenshot(path="before_click.png")
        print("已截图(点击前): before_click.png")

        try:
            # 🎯 核心测试: 点击加号按钮
            print("🖱️  点击加号按钮...")
            await plus_btn.click(timeout=3000)
            await page.wait_for_timeout(2000)

            # 📸 点击后截图
            await page.screenshot(path="after_click.png")
            print("已截图(点击后): after_click.png")

            # 检查JavaScript错误
            new_js_errors = js_errors[js_errors_before:]
            new_console_errors = console_errors[console_errors_before:]

            # 🔍 检查数量是否变化
            # 方法1: 如果有input,检查value
            if qty_input:
                new_qty = await qty_input.get_attribute("value")
                print(f"点击后数量(从input): {new_qty}")

                if qty_text and int(new_qty) > int(qty_text):
                    print("✅ 数量增加成功 - 功能正常!")
                elif qty_text:
                    # 🚨 Bug检测!
                    print(f"\n{'='*60}")
                    print("❌ 检测到Bug: UI有加号按钮,但点击后数量未变化!")
                    print(f"{'='*60}")
                    print(f"点击前数量: {qty_text}")
                    print(f"点击后数量: {new_qty}")

                    if new_js_errors or new_console_errors:
                        print(f"\n⚠️  触发了 {len(new_js_errors) + len(new_console_errors)} 个JavaScript错误:")
                        for i, err in enumerate((new_js_errors + new_console_errors)[:5], 1):
                            print(f"  {i}. {err[:200]}")
                    else:
                        print("\n⚠️  无JavaScript错误 - 可能是逻辑Bug或事件绑定失败")

                    print(f"\n📋 Bug详情:")
                    print(f"  场景: 用户在购物车页面尝试调整商品数量")
                    print(f"  操作: 点击数量加号按钮,期望数量从 {qty_text} 增加")
                    print(f"  问题: 数量未发生变化(保持为 {new_qty}),UI按钮存在但功能不工作")
                    print(f"  根因: 购物车数量调整功能存在Bug")
                else:
                    # 第一次没获取到数量,现在有了
                    print(f"✓ 获取到数量: {new_qty}")
            else:
                # 方法2: 没有input,通过截图对比或其他方式
                print("⚠️  无法通过input验证,请人工对比截图:")
                print("   - before_click.png")
                print("   - after_click.png")

                if new_js_errors or new_console_errors:
                    print(f"\n⚠️  点击触发了 {len(new_js_errors) + len(new_console_errors)} 个JavaScript错误:")
                    for i, err in enumerate((new_js_errors + new_console_errors)[:5], 1):
                        print(f"  {i}. {err[:200]}")
                    print("\n可能存在Bug!")
                else:
                    print("\n无JavaScript错误")

        except Exception as e:
            print(f"❌ 点击失败: {e}")
            await page.screenshot(path="click_error.png")
            print("已截图保存: click_error.png")

        print("\n" + "=" * 80)
        print("测试完成 - 浏览器保持打开20秒")
        print("=" * 80)

        await page.wait_for_timeout(20000)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(test_cart_bug_with_api())
