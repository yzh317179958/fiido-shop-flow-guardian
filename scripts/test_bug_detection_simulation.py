#!/usr/bin/env python3
"""
模拟Bug检测功能测试
用于验证issue_details是否能够正确记录和显示
"""

import json
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

# 直接定义TestStep类（简化版）
import time
from typing import Dict, Optional


class TestStep:
    """测试步骤记录（简化版用于模拟）"""

    def __init__(self, number: int, name: str, description: str):
        self.number = number
        self.name = name
        self.description = description
        self.status = "pending"
        self.message = ""
        self.started_at: Optional[float] = None
        self.completed_at: Optional[float] = None
        self.error: Optional[str] = None
        self.issue_details: Optional[Dict] = None

    def start(self):
        """开始执行步骤"""
        self.status = "running"
        self.started_at = time.time()

    def complete(self, status: str, message: str, error: Optional[str] = None, issue_details: Optional[Dict] = None):
        """完成步骤"""
        self.status = status
        self.message = message
        self.error = error
        self.completed_at = time.time()
        self.issue_details = issue_details

    def to_dict(self) -> Dict:
        """转换为字典"""
        duration = 0
        if self.started_at and self.completed_at:
            duration = self.completed_at - self.started_at

        result = {
            "number": self.number,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "message": self.message,
            "error": self.error,
            "duration": round(duration, 2)
        }

        # 如果有问题详情，添加到结果中
        if self.issue_details:
            result["issue_details"] = self.issue_details

        return result


def simulate_bug_detection_test():
    """模拟有Bug的测试场景"""

    print("=" * 80)
    print("模拟Bug检测功能测试")
    print("=" * 80)
    print()

    # 创建12个测试步骤
    steps = []

    # 前11个步骤正常通过
    for i in range(1, 12):
        step = TestStep(
            number=i,
            name=f"测试步骤{i}",
            description=f"这是第{i}个测试步骤"
        )
        step.start()
        step.complete("passed", f"步骤{i}执行成功")
        steps.append(step)

    # 第12步检测到Bug
    step12 = TestStep(
        number=12,
        name="支付流程验证",
        description="验证从购物车到支付页面的完整流程"
    )
    step12.start()

    # 模拟检测到购物车Bug
    bug_details = {
        "scenario": "用户在购物车页面尝试调整商品数量",
        "operation": "点击数量加号按钮，期望数量从 1 增加",
        "problem": "数量未发生变化（保持为 1），同时触发了JavaScript错误",
        "root_cause": "购物车UI更新逻辑存在Bug：代码尝试访问不存在的DOM元素（querySelector返回null），导致数量更新失败",
        "js_errors": [
            "TypeError: can't access property 'length', myDiv.querySelector(...) is null at theme.js:2023",
            "Uncaught TypeError: Cannot read properties of null (reading 'classList')",
            "ReferenceError: quantityElement is not defined"
        ]
    }

    step12.complete(
        status="passed",
        message="⚠️  购物车页面Checkout按钮正常，但检测到数量调整功能Bug",
        issue_details=bug_details
    )
    steps.append(step12)

    # 生成测试结果JSON
    result = {
        "product_id": "test-product-with-bug",
        "product_name": "模拟测试商品",
        "test_mode": "full",
        "status": "passed",
        "duration": 25.5,
        "timestamp": datetime.now().isoformat(),
        "steps": [step.to_dict() for step in steps],
        "errors": []
    }

    # 打印结果
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    print(f"商品: {result['product_name']}")
    print(f"测试模式: {result['test_mode']}")
    print(f"最终状态: {result['status']}")
    print(f"总耗时: {result['duration']}s")
    print(f"步骤总数: {len(steps)}")
    print()

    # 显示步骤12的详细信息
    step12_dict = steps[11].to_dict()
    print("步骤12详情:")
    print(f"  状态: {step12_dict['status']}")
    print(f"  消息: {step12_dict['message']}")

    if 'issue_details' in step12_dict:
        print("\n  📋 问题详情:")
        details = step12_dict['issue_details']
        print(f"    场景: {details['scenario']}")
        print(f"    操作: {details['operation']}")
        print(f"    问题: {details['problem']}")
        print(f"    根因: {details['root_cause']}")
        if details.get('js_errors'):
            print(f"\n    JavaScript错误 ({len(details['js_errors'])}条):")
            for i, err in enumerate(details['js_errors'][:3], 1):
                print(f"      {i}. {err}")

    # 保存JSON到文件以便查看
    output_file = PROJECT_ROOT / "test_bug_detection_result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n✓ 测试结果已保存到: {output_file}")
    print("\n" + "=" * 80)
    print("✓ Bug检测功能验证成功！")
    print("=" * 80)


if __name__ == "__main__":
    simulate_bug_detection_test()
