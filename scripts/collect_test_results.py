#!/usr/bin/env python3
"""
测试结果收集脚本

从 pytest 输出和报告文件中收集测试结果，
生成统一格式的 JSON 文件供后续分析和告警使用。
"""

import json
import sys
import os
import re
import glob
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import argparse


class TestResultCollector:
    """测试结果收集器"""

    def __init__(self, output_file: str = "reports/test-results.json"):
        self.output_file = Path(output_file)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "pass_rate": 0.0,
            "duration": 0.0,
            "failures": [],
            "summary": {}
        }

    def collect_from_pytest_output(self, pytest_log: str = None):
        """
        从 pytest 输出中收集结果

        Args:
            pytest_log: pytest 日志文件路径
        """
        if pytest_log and os.path.exists(pytest_log):
            with open(pytest_log) as f:
                content = f.read()
                self._parse_pytest_output(content)

    def collect_from_html_reports(self, reports_dir: str = "reports"):
        """
        从 HTML 报告中收集结果

        Args:
            reports_dir: 报告目录
        """
        html_files = glob.glob(f"{reports_dir}/*-report.html")

        for html_file in html_files:
            print(f"📄 解析报告: {html_file}")
            with open(html_file, encoding='utf-8') as f:
                content = f.read()
                self._parse_html_report(content)

    def collect_from_json_reports(self, reports_dir: str = "reports"):
        """
        从 JSON 报告中收集结果

        Args:
            reports_dir: 报告目录
        """
        json_files = glob.glob(f"{reports_dir}/*.json")

        for json_file in json_files:
            # 跳过我们自己生成的结果文件
            if 'test-results' in json_file or 'p0-results' in json_file:
                continue

            print(f"📄 解析 JSON 报告: {json_file}")
            try:
                with open(json_file) as f:
                    data = json.load(f)
                    self._parse_json_report(data)
            except Exception as e:
                print(f"⚠️ 解析失败: {e}")

    def _parse_pytest_output(self, content: str):
        """解析 pytest 输出"""
        # 提取测试统计
        match = re.search(r'=+ ([\d]+) passed.*?in ([\d.]+)s', content)
        if match:
            self.results['passed'] = int(match.group(1))
            self.results['duration'] = float(match.group(2))

        # 提取失败信息
        failed_match = re.search(r'([\d]+) failed', content)
        if failed_match:
            self.results['failed'] = int(failed_match.group(1))

        # 提取跳过信息
        skipped_match = re.search(r'([\d]+) skipped', content)
        if skipped_match:
            self.results['skipped'] = int(skipped_match.group(1))

    def _parse_html_report(self, content: str):
        """解析 HTML 报告"""
        # 提取统计信息
        passed_match = re.search(r'(\d+)\s*passed', content)
        failed_match = re.search(r'(\d+)\s*failed', content)
        skipped_match = re.search(r'(\d+)\s*skipped', content)

        if passed_match:
            self.results['passed'] += int(passed_match.group(1))
        if failed_match:
            self.results['failed'] += int(failed_match.group(1))
        if skipped_match:
            self.results['skipped'] += int(skipped_match.group(1))

    def _parse_json_report(self, data: Dict):
        """解析 JSON 报告"""
        if 'summary' in data:
            summary = data['summary']
            self.results['passed'] += summary.get('passed', 0)
            self.results['failed'] += summary.get('failed', 0)
            self.results['skipped'] += summary.get('skipped', 0)

        if 'tests' in data:
            for test in data['tests']:
                if test.get('outcome') == 'failed':
                    self.results['failures'].append({
                        'test_name': test.get('nodeid', 'unknown'),
                        'product_name': test.get('product_name', 'unknown'),
                        'priority': test.get('priority', 'P2'),
                        'error_message': test.get('call', {}).get('longrepr', '')
                    })

    def calculate_metrics(self):
        """计算指标"""
        self.results['total'] = (
            self.results['passed'] +
            self.results['failed'] +
            self.results['skipped']
        )

        if self.results['total'] > 0:
            self.results['pass_rate'] = (
                self.results['passed'] / self.results['total']
            )

        # 生成摘要
        self.results['summary'] = {
            'total_tests': self.results['total'],
            'passed': self.results['passed'],
            'failed': self.results['failed'],
            'skipped': self.results['skipped'],
            'pass_rate': f"{self.results['pass_rate']:.1%}",
            'duration': f"{self.results['duration']:.2f}s",
            'failure_count': len(self.results['failures'])
        }

        # 按优先级分组失败
        p0_failures = [f for f in self.results['failures'] if f['priority'] == 'P0']
        p1_failures = [f for f in self.results['failures'] if f['priority'] == 'P1']

        self.results['summary']['p0_failures'] = len(p0_failures)
        self.results['summary']['p1_failures'] = len(p1_failures)

    def save_results(self):
        """保存结果到文件"""
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"\n✅ 测试结果已保存到: {self.output_file}")
        print(f"\n📊 测试摘要:")
        print(f"  总测试数: {self.results['total']}")
        print(f"  通过: {self.results['passed']}")
        print(f"  失败: {self.results['failed']}")
        print(f"  跳过: {self.results['skipped']}")
        print(f"  通过率: {self.results['pass_rate']:.1%}")

        if self.results['failed'] > 0:
            print(f"\n⚠️  发现 {self.results['failed']} 个失败测试")
            if self.results['summary']['p0_failures'] > 0:
                print(f"  🚨 P0 核心失败: {self.results['summary']['p0_failures']}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='收集测试结果')
    parser.add_argument(
        '--output',
        default='reports/test-results.json',
        help='输出文件路径'
    )
    parser.add_argument(
        '--reports-dir',
        default='reports',
        help='报告目录路径'
    )
    parser.add_argument(
        '--pytest-log',
        help='pytest 日志文件路径'
    )

    args = parser.parse_args()

    collector = TestResultCollector(output_file=args.output)

    print("🔍 开始收集测试结果...")

    # 从 pytest 日志收集
    if args.pytest_log:
        collector.collect_from_pytest_output(args.pytest_log)

    # 从 HTML 报告收集
    collector.collect_from_html_reports(args.reports_dir)

    # 从 JSON 报告收集
    collector.collect_from_json_reports(args.reports_dir)

    # 计算指标
    collector.calculate_metrics()

    # 保存结果
    collector.save_results()

    # 返回退出码
    if collector.results['failed'] > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
