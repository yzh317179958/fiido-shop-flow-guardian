#!/usr/bin/env python3
"""
测试步骤覆盖验证脚本

目的：验证快速测试和全面测试的每个步骤是否能正确识别通过/失败情况
- 选择不同特性的商品来覆盖各种场景
- 分析每个步骤的通过率和失败原因
- 确保测试逻辑能正确区分网站Bug和功能缺失

快速测试步骤 (5步):
1. 页面访问 - 访问商品页面并检查页面是否正常加载
2. 商品信息显示 - 验证商品标题、价格等核心信息是否正确显示
3. 添加购物车 - 点击添加购物车按钮，验证能否成功加入
4. 购物车验证 - 检查购物车中是否有新增商品
5. 支付流程 - 访问购物车页面，验证Checkout按钮是否可用

全面测试步骤 (12步):
1. 页面访问 - 访问商品页面并等待完全加载
2. 页面结构检测 - 检查页面基础DOM结构是否完整
3. 商品标题验证 - 验证商品标题显示是否正确
4. 价格信息验证 - 检查商品价格显示是否完整
5. 商品图片验证 - 验证商品图片是否加载成功
6. 商品描述验证 - 检查商品描述内容是否存在
7. 变体选择测试 - 测试颜色/尺寸等变体选项功能
8. 数量选择测试 - 测试商品数量增减功能
9. 添加购物车 - 测试添加购物车功能
10. 购物车验证 - 验证购物车商品数量变化
11. 相关推荐验证 - 检查相关商品推荐是否显示
12. 支付流程验证 - 验证从购物车到支付页面的完整流程
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from run_product_test import ProductTester
from core.models import Product


@dataclass
class StepCoverageResult:
    """步骤覆盖测试结果"""
    step_number: int
    step_name: str
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    failure_reasons: List[str] = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        if self.total_tests == 0:
            return 0.0
        return self.passed / self.total_tests * 100


@dataclass
class TestCaseResult:
    """单个测试用例结果"""
    product_id: str
    product_name: str
    test_mode: str
    status: str
    duration: float
    steps: List[Dict]
    category: str = ""


def load_test_products() -> List[Dict]:
    """加载测试商品，选择不同类型以覆盖各种场景"""
    products_file = PROJECT_ROOT / "data" / "products.json"
    with open(products_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_products = [p for p in data.get("products", []) if '#' not in str(p.get('id', ''))]

    # 选择策略：
    # 1. P0整车 - 通常有完整的商品页面（变体、图片、描述等）
    # 2. P1重要配件 - 电池/充电器，可能有不同的页面结构
    # 3. P2普通配件 - 简单配件，可能缺少某些元素
    # 4. 不同价格区间的商品
    # 5. 有/无变体的商品

    selected = []

    # P0整车 - 选择2个
    p0_products = [p for p in all_products if p.get('priority') == 'P0']
    if p0_products:
        selected.extend(p0_products[:2])

    # P1重要配件 - 选择2个
    p1_products = [p for p in all_products if p.get('priority') == 'P1']
    if p1_products:
        selected.extend(p1_products[:2])

    # P2普通配件 - 选择2个（有变体和无变体各1个）
    p2_products = [p for p in all_products if p.get('priority') == 'P2']
    p2_with_variants = [p for p in p2_products if p.get('variants') and len(p.get('variants', [])) > 0]
    p2_without_variants = [p for p in p2_products if not p.get('variants') or len(p.get('variants', [])) == 0]

    if p2_with_variants:
        selected.append(p2_with_variants[0])
    if p2_without_variants:
        selected.append(p2_without_variants[0])

    # 确保至少有6个商品
    if len(selected) < 6:
        remaining = [p for p in all_products if p not in selected]
        selected.extend(remaining[:6 - len(selected)])

    return selected


async def run_single_test(product_data: Dict, test_mode: str) -> TestCaseResult:
    """运行单个商品测试"""
    print(f"  🔄 测试: {product_data['name'][:50]}... ({test_mode})")

    try:
        product = Product(**product_data)
        tester = ProductTester(product, test_mode=test_mode, headless=True)
        result = await tester.run()

        status_icon = "✓" if result['status'] == 'passed' else "✗"
        print(f"    {status_icon} {result['status'].upper()} ({result['duration']:.1f}s)")

        return TestCaseResult(
            product_id=str(product_data['id']),
            product_name=product_data['name'],
            test_mode=test_mode,
            status=result['status'],
            duration=result['duration'],
            steps=result['steps'],
            category=product_data.get('category', '')
        )

    except Exception as e:
        print(f"    ✗ ERROR: {str(e)[:50]}")
        return TestCaseResult(
            product_id=str(product_data['id']),
            product_name=product_data['name'],
            test_mode=test_mode,
            status='error',
            duration=0,
            steps=[],
            category=product_data.get('category', '')
        )


def analyze_step_coverage(results: List[TestCaseResult], test_mode: str) -> Dict[int, StepCoverageResult]:
    """分析步骤覆盖情况"""
    # 定义步骤
    if test_mode == 'quick':
        steps_def = {
            1: "页面访问",
            2: "商品信息显示",
            3: "添加购物车",
            4: "购物车验证",
            5: "支付流程"
        }
    else:
        steps_def = {
            1: "页面访问",
            2: "页面结构检测",
            3: "商品标题验证",
            4: "价格信息验证",
            5: "商品图片验证",
            6: "商品描述验证",
            7: "变体选择测试",
            8: "数量选择测试",
            9: "添加购物车",
            10: "购物车验证",
            11: "相关推荐验证",
            12: "支付流程验证"
        }

    coverage = {}
    for step_num, step_name in steps_def.items():
        coverage[step_num] = StepCoverageResult(
            step_number=step_num,
            step_name=step_name
        )

    for result in results:
        if result.test_mode != test_mode:
            continue

        for step in result.steps:
            step_num = step.get('number', 0)
            if step_num not in coverage:
                continue

            coverage[step_num].total_tests += 1
            status = step.get('status', '')

            if status == 'passed':
                coverage[step_num].passed += 1
            elif status == 'failed':
                coverage[step_num].failed += 1
                # 记录失败原因
                reason = step.get('message', '') or step.get('error', '') or 'Unknown'
                if step.get('issue_details'):
                    details = step['issue_details']
                    reason = f"{details.get('problem', reason)}"
                coverage[step_num].failure_reasons.append(
                    f"[{result.product_name[:30]}] {reason[:100]}"
                )
            elif status == 'skipped':
                coverage[step_num].skipped += 1

    return coverage


def print_coverage_report(coverage: Dict[int, StepCoverageResult], test_mode: str):
    """打印覆盖率报告"""
    mode_name = "快速测试" if test_mode == 'quick' else "全面测试"

    print(f"\n{'='*70}")
    print(f"📊 {mode_name} 步骤覆盖率报告")
    print('='*70)

    print(f"\n{'步骤':<6} {'名称':<20} {'总数':<6} {'通过':<6} {'失败':<6} {'跳过':<6} {'通过率':<10}")
    print('-'*70)

    for step_num in sorted(coverage.keys()):
        step = coverage[step_num]
        pass_rate_str = f"{step.pass_rate:.1f}%"

        # 根据通过率设置颜色提示
        if step.pass_rate >= 90:
            status_icon = "✅"
        elif step.pass_rate >= 70:
            status_icon = "⚠️"
        else:
            status_icon = "❌"

        print(f"{step_num:<6} {step.step_name:<20} {step.total_tests:<6} {step.passed:<6} {step.failed:<6} {step.skipped:<6} {status_icon} {pass_rate_str:<10}")

    # 打印失败详情
    failed_steps = [s for s in coverage.values() if s.failed > 0]
    if failed_steps:
        print(f"\n{'='*70}")
        print("❌ 失败步骤详情")
        print('='*70)

        for step in failed_steps:
            print(f"\n步骤 {step.step_number}: {step.step_name} (失败 {step.failed} 次)")
            for i, reason in enumerate(step.failure_reasons[:5], 1):
                print(f"  {i}. {reason}")
            if len(step.failure_reasons) > 5:
                print(f"  ... 还有 {len(step.failure_reasons) - 5} 个失败")


def generate_summary_report(
    quick_results: List[TestCaseResult],
    full_results: List[TestCaseResult],
    quick_coverage: Dict[int, StepCoverageResult],
    full_coverage: Dict[int, StepCoverageResult]
) -> Dict:
    """生成汇总报告"""

    def calc_stats(results):
        passed = sum(1 for r in results if r.status == 'passed')
        failed = sum(1 for r in results if r.status == 'failed')
        errors = sum(1 for r in results if r.status == 'error')
        return {
            'total': len(results),
            'passed': passed,
            'failed': failed,
            'errors': errors,
            'pass_rate': passed / len(results) * 100 if results else 0
        }

    def coverage_to_dict(coverage):
        return {
            step_num: {
                'step_name': step.step_name,
                'total_tests': step.total_tests,
                'passed': step.passed,
                'failed': step.failed,
                'skipped': step.skipped,
                'pass_rate': step.pass_rate,
                'failure_reasons': step.failure_reasons
            }
            for step_num, step in coverage.items()
        }

    report = {
        'timestamp': datetime.now().isoformat(),
        'quick_test': {
            'summary': calc_stats(quick_results),
            'step_coverage': coverage_to_dict(quick_coverage),
            'results': [
                {
                    'product_id': r.product_id,
                    'product_name': r.product_name,
                    'category': r.category,
                    'status': r.status,
                    'duration': r.duration,
                    'steps': r.steps
                }
                for r in quick_results
            ]
        },
        'full_test': {
            'summary': calc_stats(full_results),
            'step_coverage': coverage_to_dict(full_coverage),
            'results': [
                {
                    'product_id': r.product_id,
                    'product_name': r.product_name,
                    'category': r.category,
                    'status': r.status,
                    'duration': r.duration,
                    'steps': r.steps
                }
                for r in full_results
            ]
        }
    }

    return report


async def main():
    """主函数"""
    print("\n" + "="*70)
    print("🧪 测试步骤覆盖验证")
    print("="*70)
    print("目的：验证快速测试和全面测试的每个步骤是否能正确识别通过/失败")
    print("="*70)

    # 加载测试商品
    test_products = load_test_products()
    print(f"\n📦 已选择 {len(test_products)} 个测试商品:")
    for i, p in enumerate(test_products, 1):
        priority = p.get('priority', 'P2')
        variants = len(p.get('variants', []))
        print(f"  {i}. [{priority}] {p['name'][:50]} (变体: {variants})")

    # ==================== 快速测试 ====================
    print(f"\n{'='*70}")
    print("⚡ 运行快速测试 (5步)")
    print('='*70)

    quick_results = []
    for i, product in enumerate(test_products, 1):
        print(f"\n[{i}/{len(test_products)}]", end="")
        result = await run_single_test(product, 'quick')
        quick_results.append(result)

    quick_coverage = analyze_step_coverage(quick_results, 'quick')
    print_coverage_report(quick_coverage, 'quick')

    # ==================== 全面测试 ====================
    print(f"\n{'='*70}")
    print("🔍 运行全面测试 (12步)")
    print('='*70)

    full_results = []
    for i, product in enumerate(test_products, 1):
        print(f"\n[{i}/{len(test_products)}]", end="")
        result = await run_single_test(product, 'full')
        full_results.append(result)

    full_coverage = analyze_step_coverage(full_results, 'full')
    print_coverage_report(full_coverage, 'full')

    # ==================== 汇总 ====================
    print(f"\n{'='*70}")
    print("📋 测试汇总")
    print('='*70)

    quick_passed = sum(1 for r in quick_results if r.status == 'passed')
    quick_failed = sum(1 for r in quick_results if r.status == 'failed')
    full_passed = sum(1 for r in full_results if r.status == 'passed')
    full_failed = sum(1 for r in full_results if r.status == 'failed')

    print(f"\n快速测试: 通过 {quick_passed}/{len(quick_results)}, 失败 {quick_failed}")
    print(f"全面测试: 通过 {full_passed}/{len(full_results)}, 失败 {full_failed}")

    # 计算平均步骤通过率
    quick_avg_pass = sum(s.pass_rate for s in quick_coverage.values()) / len(quick_coverage) if quick_coverage else 0
    full_avg_pass = sum(s.pass_rate for s in full_coverage.values()) / len(full_coverage) if full_coverage else 0

    print(f"\n快速测试平均步骤通过率: {quick_avg_pass:.1f}%")
    print(f"全面测试平均步骤通过率: {full_avg_pass:.1f}%")

    # 识别问题步骤
    print(f"\n{'='*70}")
    print("🔍 问题步骤分析")
    print('='*70)

    problem_steps = []
    for mode, coverage in [('快速', quick_coverage), ('全面', full_coverage)]:
        for step in coverage.values():
            if step.pass_rate < 80 and step.total_tests > 0:
                problem_steps.append((mode, step))

    if problem_steps:
        for mode, step in problem_steps:
            print(f"\n⚠️ [{mode}测试] 步骤 {step.step_number}: {step.step_name}")
            print(f"   通过率: {step.pass_rate:.1f}% (通过 {step.passed}, 失败 {step.failed}, 跳过 {step.skipped})")
            if step.failure_reasons:
                print("   失败原因示例:")
                for reason in step.failure_reasons[:2]:
                    print(f"   - {reason[:80]}")
    else:
        print("✅ 所有步骤通过率均 >= 80%")

    # 保存详细报告
    report = generate_summary_report(quick_results, full_results, quick_coverage, full_coverage)

    report_file = PROJECT_ROOT / "reports" / f"step_coverage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_file.parent.mkdir(exist_ok=True)

    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n📄 详细报告已保存: {report_file}")

    # 返回结论
    print(f"\n{'='*70}")
    print("💡 结论")
    print('='*70)

    if quick_avg_pass >= 80 and full_avg_pass >= 80:
        print("✅ 测试系统整体表现良好，各步骤能正确识别通过/失败情况")
    else:
        print("⚠️ 部分步骤通过率较低，需要进一步分析:")
        print("  - 可能是测试逻辑问题（选择器过时、超时时间不足）")
        print("  - 可能是网站真实存在的Bug")
        print("  - 可能是功能缺失（某些商品页面没有该功能）")


if __name__ == "__main__":
    asyncio.run(main())
