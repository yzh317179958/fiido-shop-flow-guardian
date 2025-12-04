#!/usr/bin/env python3
"""
调试脚本：检查产品页面的实际HTML结构，找到正确的选择器
"""

import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


async def debug_page_structure():
    """调试页面结构"""
    url = "https://fiido.com/products/fiido-t2-longtail-cargo-ebike-for-versatile-all-terrain"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        print(f"访问页面: {url}")
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)

        print("\n" + "="*80)
        print("1. 检查标题选择器")
        print("="*80)

        title_selectors = [
            "h1",
            ".product__title",
            "h1.product__title",
            ".product-title",
            "[data-product-title]"
        ]

        for selector in title_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    is_visible = await element.is_visible()
                    print(f"✓ {selector}: 找到 (visible={is_visible})")
                    print(f"  文本: {text[:60] if text else 'N/A'}")
                else:
                    print(f"✗ {selector}: 未找到")
            except Exception as e:
                print(f"✗ {selector}: 错误 - {e}")

        print("\n" + "="*80)
        print("2. 检查变体选择器 - 查找所有 input 元素")
        print("="*80)

        # 查找所有input元素
        all_inputs = await page.query_selector_all("input")
        print(f"找到 {len(all_inputs)} 个 input 元素\n")

        for i, inp in enumerate(all_inputs[:30]):  # 只显示前30个
            try:
                input_type = await inp.get_attribute("type")
                input_name = await inp.get_attribute("name")
                input_id = await inp.get_attribute("id")
                input_class = await inp.get_attribute("class")

                print(f"Input {i+1}:")
                print(f"  type={input_type}, name={input_name}, id={input_id}")
                print(f"  class={input_class}")
                print()
            except:
                continue

        print("\n" + "="*80)
        print("3. 检查图片选择器")
        print("="*80)

        image_selectors = [
            "img[src*='product']",
            ".product__media img",
            ".product__media-item img",
            ".product-main-image img"
        ]

        for selector in image_selectors:
            try:
                images = await page.query_selector_all(selector)
                print(f"{selector}: 找到 {len(images)} 个图片")

                # 显示前3个图片的src
                for i, img in enumerate(images[:3]):
                    src = await img.get_attribute("src")
                    is_visible = await img.is_visible()
                    print(f"  图片 {i+1}: visible={is_visible}, src={src[:80] if src else 'N/A'}")
            except Exception as e:
                print(f"{selector}: 错误 - {e}")

        print("\n" + "="*80)
        print("4. 检查按钮和可点击元素")
        print("="*80)

        # 查找所有按钮
        all_buttons = await page.query_selector_all("button")
        print(f"找到 {len(all_buttons)} 个按钮\n")

        for i, btn in enumerate(all_buttons[:20]):  # 只显示前20个
            try:
                btn_text = await btn.text_content()
                btn_class = await btn.get_attribute("class")
                btn_name = await btn.get_attribute("name")
                is_visible = await btn.is_visible()

                if is_visible and btn_text and btn_text.strip():
                    print(f"按钮 {i+1}: {btn_text.strip()[:40]}")
                    print(f"  name={btn_name}, class={btn_class[:50] if btn_class else 'N/A'}")
                    print()
            except:
                continue

        print("\n" + "="*80)
        print("5. 查找 fieldset 和 legend (Shopify 常用的变体容器)")
        print("="*80)

        fieldsets = await page.query_selector_all("fieldset")
        print(f"找到 {len(fieldsets)} 个 fieldset\n")

        for i, fs in enumerate(fieldsets):
            try:
                legend = await fs.query_selector("legend")
                if legend:
                    legend_text = await legend.text_content()
                    print(f"Fieldset {i+1}: {legend_text}")

                    # 查找该fieldset下的input
                    inputs = await fs.query_selector_all("input")
                    print(f"  包含 {len(inputs)} 个 input")

                    for j, inp in enumerate(inputs[:5]):  # 只显示前5个
                        input_type = await inp.get_attribute("type")
                        input_name = await inp.get_attribute("name")
                        input_value = await inp.get_attribute("value")
                        print(f"    Input {j+1}: type={input_type}, name={input_name}, value={input_value}")
                    print()
            except:
                continue

        print("\n" + "="*80)
        print("6. 详细检查 radio 类型的 input（变体选择器）")
        print("="*80)

        radio_inputs = await page.query_selector_all("input[type='radio']")
        print(f"找到 {len(radio_inputs)} 个 radio input\n")

        for i, radio in enumerate(radio_inputs):
            try:
                radio_name = await radio.get_attribute("name")
                radio_value = await radio.get_attribute("value")
                radio_id = await radio.get_attribute("id")
                radio_class = await radio.get_attribute("class")
                is_checked = await radio.is_checked()

                # 查找对应的label
                if radio_id:
                    label = await page.query_selector(f"label[for='{radio_id}']")
                    label_text = ""
                    if label:
                        label_text = await label.text_content()
                        label_text = label_text.strip() if label_text else ""

                    print(f"Radio {i+1}:")
                    print(f"  name={radio_name}")
                    print(f"  value={radio_value}")
                    print(f"  id={radio_id}")
                    print(f"  class={radio_class}")
                    print(f"  checked={is_checked}")
                    print(f"  label={label_text[:50] if label_text else 'N/A'}")
                    print()
            except Exception as e:
                print(f"Radio {i+1}: 错误 - {e}")

        print("\n" + "="*80)
        print("7. 查找 checkbox 类型的 input（配件选择器）")
        print("="*80)

        checkbox_inputs = await page.query_selector_all("input[type='checkbox']")
        print(f"找到 {len(checkbox_inputs)} 个 checkbox input\n")

        for i, cb in enumerate(checkbox_inputs):
            try:
                cb_name = await cb.get_attribute("name")
                cb_value = await cb.get_attribute("value")
                cb_id = await cb.get_attribute("id")
                cb_class = await cb.get_attribute("class")
                is_checked = await cb.is_checked()
                is_visible = await cb.is_visible()

                # 只显示可见的checkbox
                if is_visible or cb_class in ['isfree', '']:
                    # 查找对应的label或父元素文本
                    label_text = ""
                    if cb_id:
                        label = await page.query_selector(f"label[for='{cb_id}']")
                        if label:
                            label_text = await label.text_content()
                            label_text = label_text.strip() if label_text else ""

                    print(f"Checkbox {i+1}:")
                    print(f"  name={cb_name}")
                    print(f"  value={cb_value}")
                    print(f"  id={cb_id}")
                    print(f"  class={cb_class}")
                    print(f"  checked={is_checked}, visible={is_visible}")
                    print(f"  label={label_text[:50] if label_text else 'N/A'}")
                    print()
            except Exception as e:
                continue

        await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_page_structure())
