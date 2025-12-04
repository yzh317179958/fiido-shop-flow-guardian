#!/usr/bin/env python3
"""
专门测试 fiido-d1-battery-shell 商品的脚本
进行多次测试以排查超时问题
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from run_product_test import ProductTester
from core.models import Product


async def test_once(run_number):
    """执行一次测试"""
    print(f"\n{'='*80}")
    print(f"第 {run_number} 次测试 - 时间: {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*80}\n")

    # 加载商品数据
    products_file = PROJECT_ROOT / "data" / "products.json"
    with open(products_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    products = data.get("products", [])
    product_data = next((p for p in products if p["id"] == "fiido-d1-battery-shell"), None)

    if not product_data:
        print("❌ 未找到商品")
        return None

    try:
        product = Product(**product_data)
        tester = ProductTester(product, test_mode="quick", headless=True)
        result = await tester.run()

        # 检查步骤5的状态
        step5_status = "unknown"
        step5_message = ""
        step5_error = ""
        step5_duration = 0

        for step in result['steps']:
            if step['number'] == 5:
                step5_status = step['status']
                step5_message = step.get('message', '')
                step5_error = step.get('error', '')
                step5_duration = step.get('duration', 0)
                break

        print(f"\n📊 测试结果摘要:")
        print(f"  总状态: {result['status']}")
        print(f"  总耗时: {result['duration']:.2f}s")
        print(f"  步骤5状态: {step5_status}")
        print(f"  步骤5耗时: {step5_duration:.2f}s")
        print(f"  步骤5消息: {step5_message}")
        if step5_error:
            print(f"  步骤5错误: {step5_error[:100]}")

        return {
            'run': run_number,
            'success': result['status'] == 'passed' and step5_status == 'passed',
            'step5_status': step5_status,
            'step5_duration': step5_duration,
            'step5_error': step5_error,
            'total_duration': result['duration']
        }

    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return {
            'run': run_number,
            'success': False,
            'step5_status': 'error',
            'step5_duration': 0,
            'step5_error': str(e),
            'total_duration': 0
        }


async def main():
    """主函数 - 进行5次测试"""
    print("="*80)
    print("开始对 fiido-d1-battery-shell 进行多次测试")
    print("="*80)

    results = []
    for i in range(1, 6):
        result = await test_once(i)
        if result:
            results.append(result)

        # 测试间隔2秒
        if i < 5:
            print(f"\n等待2秒后进行下一次测试...")
            await asyncio.sleep(2)

    # 汇总统计
    print("\n" + "="*80)
    print("测试汇总统计")
    print("="*80)

    success_count = sum(1 for r in results if r['success'])
    timeout_count = sum(1 for r in results if 'Timeout' in r['step5_error'])

    print(f"总测试次数: {len(results)}")
    print(f"成功次数: {success_count} ({success_count/len(results)*100:.1f}%)")
    print(f"失败次数: {len(results) - success_count} ({(len(results) - success_count)/len(results)*100:.1f}%)")
    print(f"超时次数: {timeout_count}")

    print(f"\n步骤5耗时统计:")
    step5_durations = [r['step5_duration'] for r in results if r['step5_duration'] > 0]
    if step5_durations:
        print(f"  最小: {min(step5_durations):.2f}s")
        print(f"  最大: {max(step5_durations):.2f}s")
        print(f"  平均: {sum(step5_durations)/len(step5_durations):.2f}s")

    # 详细结果
    print(f"\n详细结果:")
    for r in results:
        status_icon = "✓" if r['success'] else "✗"
        print(f"  {status_icon} 第{r['run']}次: 步骤5={r['step5_status']} 耗时={r['step5_duration']:.2f}s")
        if not r['success'] and r['step5_error']:
            print(f"      错误: {r['step5_error'][:150]}")

    # 结论
    print(f"\n" + "="*80)
    print("结论:")
    print("="*80)
    if timeout_count > 0:
        print(f"⚠️  有 {timeout_count} 次超时，建议:")
        print(f"   1. 增加超时时间限制")
        print(f"   2. 添加重试机制")
        print(f"   3. 检查网络稳定性")
    else:
        print(f"✓ 所有测试均未超时，之前的超时可能是偶发性网络问题")

    if success_count == len(results):
        print(f"✓ 所有测试全部通过，功能正常！")
    elif success_count > len(results) * 0.8:
        print(f"⚠️  大部分测试通过 ({success_count}/{len(results)})，偶有失败")
    else:
        print(f"❌ 测试失败率较高，需要修复代码")


if __name__ == "__main__":
    asyncio.run(main())
