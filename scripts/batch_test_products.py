#!/usr/bin/env python3
"""
批量测试多个商品的快速测试脚本
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from run_product_test import ProductTester
from core.models import Product


async def test_product(product_data, index, total):
    """测试单个商品"""
    print(f"\n{'='*80}")
    print(f"[{index}/{total}] 测试商品: {product_data['name']}")
    print(f"商品ID: {product_data['id']}")
    print(f"{'='*80}\n")

    try:
        product = Product(**product_data)
        tester = ProductTester(product, test_mode="quick", headless=True)
        result = await tester.run()

        return {
            'product_id': product_data['id'],
            'product_name': product_data['name'],
            'status': result['status'],
            'duration': result['duration'],
            'steps': result['steps'],
            'errors': result.get('errors', [])
        }
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return {
            'product_id': product_data['id'],
            'product_name': product_data['name'],
            'status': 'error',
            'duration': 0,
            'steps': [],
            'errors': [str(e)]
        }


async def main():
    """主函数"""
    # 加载商品数据
    products_file = PROJECT_ROOT / "data" / "products.json"
    with open(products_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    products = data.get("products", [])

    # 选择20个不同的商品进行测试
    selected_products = []
    categories_seen = set()

    # 优先选择不同分类的商品
    for p in products:
        if len(selected_products) >= 20:
            break
        cat = p.get('category', 'unknown')
        # 跳过带#的变体URL
        if '#' not in p['id']:
            if cat not in categories_seen or len(selected_products) < 10:
                selected_products.append(p)
                categories_seen.add(cat)

    # 如果不够20个,补充其他商品(也跳过#变体)
    if len(selected_products) < 20:
        for p in products:
            if p not in selected_products and '#' not in p['id']:
                selected_products.append(p)
                if len(selected_products) >= 20:
                    break

    print("="*80)
    print(f"批量测试开始 - 共 {len(selected_products)} 个商品")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # 逐个测试商品
    results = []
    start_time = datetime.now()

    for i, product_data in enumerate(selected_products, 1):
        result = await test_product(product_data, i, len(selected_products))
        results.append(result)

        # 简短总结
        status_icon = "✓" if result['status'] == 'passed' else "✗"
        print(f"\n{status_icon} [{i}/{len(selected_products)}] {result['product_name'][:60]} - {result['status'].upper()} ({result['duration']:.1f}s)")

        # 显示失败的步骤
        if result['status'] != 'passed':
            for step in result['steps']:
                if step['status'] == 'failed':
                    print(f"  ✗ 步骤{step['number']}: {step['name']} - {step.get('message', 'N/A')}")
                    if step.get('error'):
                        print(f"     错误: {step['error'][:100]}")

    end_time = datetime.now()
    total_duration = (end_time - start_time).total_seconds()

    # 生成汇总报告
    print("\n" + "="*80)
    print("批量测试完成")
    print("="*80)

    passed_count = sum(1 for r in results if r['status'] == 'passed')
    failed_count = sum(1 for r in results if r['status'] == 'failed')
    error_count = sum(1 for r in results if r['status'] == 'error')

    print(f"总商品数: {len(results)}")
    print(f"通过: {passed_count} ({passed_count/len(results)*100:.1f}%)")
    print(f"失败: {failed_count} ({failed_count/len(results)*100:.1f}%)")
    print(f"异常: {error_count} ({error_count/len(results)*100:.1f}%)")
    print(f"总耗时: {total_duration:.1f}秒 (平均 {total_duration/len(results):.1f}秒/商品)")

    # 失败商品详情
    if failed_count > 0 or error_count > 0:
        print("\n" + "="*80)
        print("失败/异常商品详情:")
        print("="*80)
        for r in results:
            if r['status'] != 'passed':
                print(f"\n商品: {r['product_name']}")
                print(f"ID: {r['product_id']}")
                print(f"状态: {r['status']}")

                # 显示失败的步骤
                for step in r['steps']:
                    if step['status'] == 'failed':
                        print(f"  ✗ 步骤{step['number']}: {step['name']}")
                        print(f"     结果: {step.get('message', 'N/A')}")
                        if step.get('error'):
                            print(f"     错误: {step['error']}")

                # 显示异常信息
                if r['errors']:
                    print(f"  异常信息:")
                    for error in r['errors']:
                        print(f"    - {error}")

    # 保存详细结果
    report_file = PROJECT_ROOT / "reports" / f"batch_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_file.parent.mkdir(exist_ok=True)

    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total': len(results),
            'passed': passed_count,
            'failed': failed_count,
            'error': error_count,
            'total_duration': total_duration,
            'results': results
        }, f, ensure_ascii=False, indent=2)

    print(f"\n详细报告已保存: {report_file}")
    print("="*80)

    # 返回退出码
    sys.exit(0 if failed_count == 0 and error_count == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
