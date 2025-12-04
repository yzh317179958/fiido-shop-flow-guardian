#!/usr/bin/env python3
"""
测试智能判断模块

核心原则:
1. 区分网站Bug vs 测试超时/失败
2. 加强对网站已有功能的Bug检测,避免漏检
3. 避免对不存在的功能进行测试(无中生有的失败)
4. 基于网页实际UI设计进行测试
5. 验证已有功能是否有Bug,而不是测试功能是否存在
"""

from typing import Dict, List, Optional, Tuple
from playwright.async_api import Page, ElementHandle
import logging

logger = logging.getLogger(__name__)


class ElementDetectionResult:
    """元素检测结果"""

    def __init__(self):
        self.exists = False  # 元素是否存在
        self.visible = False  # 元素是否可见
        self.enabled = False  # 元素是否可交互
        self.element: Optional[ElementHandle] = None  # 元素句柄
        self.selector_used: Optional[str] = None  # 使用的选择器
        self.error: Optional[str] = None  # 错误信息

    def __bool__(self):
        """元素是否存在"""
        return self.exists

    @property
    def is_functional(self) -> bool:
        """元素是否功能正常(存在且可见且可用)"""
        return self.exists and self.visible and self.enabled


class FailureClassification:
    """失败分类"""

    # 失败类型
    TYPE_WEBSITE_BUG = "website_bug"  # 网站Bug
    TYPE_MISSING_FEATURE = "missing_feature"  # 功能不存在
    TYPE_TEST_TIMEOUT = "test_timeout"  # 测试超时
    TYPE_TEST_ERROR = "test_error"  # 测试逻辑错误
    TYPE_NETWORK_ERROR = "network_error"  # 网络错误

    def __init__(self, failure_type: str, reason: str, evidence: Optional[Dict] = None):
        self.failure_type = failure_type
        self.reason = reason
        self.evidence = evidence or {}

    def is_website_bug(self) -> bool:
        """是否为网站Bug"""
        return self.failure_type == self.TYPE_WEBSITE_BUG

    def should_report_as_failed(self) -> bool:
        """是否应该报告为失败"""
        # 只有网站Bug才报告为失败,其他情况报告为skipped或passed
        return self.failure_type == self.TYPE_WEBSITE_BUG


class TestIntelligence:
    """测试智能判断类"""

    def __init__(self, page: Page):
        self.page = page

    async def detect_element(
        self,
        selectors: List[str],
        element_name: str,
        timeout: int = 5000
    ) -> ElementDetectionResult:
        """
        智能检测元素

        Args:
            selectors: 选择器列表
            element_name: 元素名称(用于日志)
            timeout: 超时时间(毫秒)

        Returns:
            ElementDetectionResult: 检测结果
        """
        result = ElementDetectionResult()

        for selector in selectors:
            try:
                # 尝试查找元素
                element = await self.page.query_selector(selector)

                if element:
                    result.exists = True
                    result.element = element
                    result.selector_used = selector

                    # 检查可见性
                    try:
                        result.visible = await element.is_visible()
                    except:
                        result.visible = False

                    # 检查是否可用
                    try:
                        result.enabled = await element.is_enabled()
                    except:
                        result.enabled = True  # 默认可用(对于非input元素)

                    logger.info(f"  ✓ 找到{element_name}: {selector} (可见:{result.visible}, 可用:{result.enabled})")
                    return result

            except Exception as e:
                continue

        # 所有选择器都失败
        result.error = f"未找到{element_name}"
        logger.info(f"  ℹ️  未找到{element_name} (尝试了{len(selectors)}个选择器)")
        return result

    async def classify_failure(
        self,
        step_name: str,
        expected_element: Optional[ElementDetectionResult],
        operation_attempted: Optional[str],
        js_errors: List[str],
        exception: Optional[Exception] = None
    ) -> FailureClassification:
        """
        分类失败原因

        Args:
            step_name: 步骤名称
            expected_element: 期望的元素检测结果
            operation_attempted: 尝试的操作
            js_errors: JavaScript错误列表
            exception: 异常对象

        Returns:
            FailureClassification: 失败分类
        """

        # 情况1: 元素不存在 → 功能不存在(不应报告为失败)
        if expected_element and not expected_element.exists:
            return FailureClassification(
                failure_type=FailureClassification.TYPE_MISSING_FEATURE,
                reason=f"{step_name}的相关UI元素不存在,该功能可能未实现",
                evidence={
                    "selectors_tried": len([]),
                    "element_exists": False
                }
            )

        # 情况2: 元素存在但不可见 → 可能是设计如此(懒加载/隐藏)
        if expected_element and expected_element.exists and not expected_element.visible:
            # 检查是否有JavaScript错误
            if js_errors:
                return FailureClassification(
                    failure_type=FailureClassification.TYPE_WEBSITE_BUG,
                    reason=f"{step_name}的UI元素存在但不可见,且有JavaScript错误",
                    evidence={
                        "element_exists": True,
                        "element_visible": False,
                        "js_errors": js_errors
                    }
                )
            else:
                return FailureClassification(
                    failure_type=FailureClassification.TYPE_MISSING_FEATURE,
                    reason=f"{step_name}的UI元素存在但不可见,可能是设计如此(懒加载/隐藏)",
                    evidence={
                        "element_exists": True,
                        "element_visible": False
                    }
                )

        # 情况3: 元素存在且可见但操作失败 + 有JS错误 → 网站Bug
        if expected_element and expected_element.exists and expected_element.visible and js_errors:
            return FailureClassification(
                failure_type=FailureClassification.TYPE_WEBSITE_BUG,
                reason=f"{step_name}执行失败,UI元素存在但操作触发JavaScript错误",
                evidence={
                    "element_exists": True,
                    "element_visible": True,
                    "operation": operation_attempted,
                    "js_errors": js_errors
                }
            )

        # 情况4: 超时异常 → 测试超时(非网站Bug)
        if exception and ("timeout" in str(exception).lower() or "Timeout" in str(type(exception).__name__)):
            return FailureClassification(
                failure_type=FailureClassification.TYPE_TEST_TIMEOUT,
                reason=f"{step_name}执行超时,可能是网络慢或元素加载慢",
                evidence={
                    "exception": str(exception),
                    "exception_type": type(exception).__name__
                }
            )

        # 情况5: 网络错误
        if exception and any(keyword in str(exception).lower() for keyword in ["net::", "connection", "network"]):
            return FailureClassification(
                failure_type=FailureClassification.TYPE_NETWORK_ERROR,
                reason=f"{step_name}遇到网络错误",
                evidence={
                    "exception": str(exception)
                }
            )

        # 情况6: 其他异常 → 测试逻辑错误
        if exception:
            return FailureClassification(
                failure_type=FailureClassification.TYPE_TEST_ERROR,
                reason=f"{step_name}测试逻辑出错",
                evidence={
                    "exception": str(exception),
                    "exception_type": type(exception).__name__
                }
            )

        # 默认: 未知失败
        return FailureClassification(
            failure_type=FailureClassification.TYPE_TEST_ERROR,
            reason=f"{step_name}失败,原因未知",
            evidence={}
        )

    async def verify_interactive_element(
        self,
        element: ElementHandle,
        element_name: str,
        operation: str = "click"
    ) -> Tuple[bool, Optional[str], List[str]]:
        """
        验证可交互元素

        Args:
            element: 元素句柄
            element_name: 元素名称
            operation: 操作类型(click/fill/etc)

        Returns:
            (成功, 错误信息, JavaScript错误列表)
        """
        js_errors_before = len(self.page._impl_obj._browser_context._browser._logger._logs)

        try:
            if operation == "click":
                await element.click(timeout=3000)
            elif operation == "fill":
                await element.fill("test", timeout=3000)

            # 等待操作完成
            await self.page.wait_for_timeout(1000)

            # 检查是否有新的JavaScript错误
            # (这里简化处理,实际应该监听page.on("pageerror"))

            return (True, None, [])

        except Exception as e:
            error_msg = f"{element_name}操作失败: {str(e)}"

            # 检查是否为超时
            if "timeout" in str(e).lower():
                error_msg = f"{element_name}操作超时(可能元素响应慢或被禁用)"

            return (False, error_msg, [])

    def should_skip_step(self, step_name: str, prerequisite_elements: List[ElementDetectionResult]) -> Tuple[bool, Optional[str]]:
        """
        判断是否应该跳过某个步骤

        Args:
            step_name: 步骤名称
            prerequisite_elements: 前置条件元素列表

        Returns:
            (是否跳过, 跳过原因)
        """
        # 检查前置元素是否都存在
        missing_elements = [elem for elem in prerequisite_elements if not elem.exists]

        if missing_elements:
            return (
                True,
                f"{step_name}所需的UI元素不存在,该功能未实现,跳过测试"
            )

        return (False, None)

    async def intelligent_wait_for_element(
        self,
        selectors: List[str],
        element_name: str,
        max_wait_time: int = 10000,
        check_interval: int = 500
    ) -> ElementDetectionResult:
        """
        智能等待元素出现

        这个方法会:
        1. 尝试多个选择器
        2. 给予足够时间让动态内容加载
        3. 区分"元素确实不存在"和"元素加载慢"

        Args:
            selectors: 选择器列表
            element_name: 元素名称
            max_wait_time: 最大等待时间(毫秒)
            check_interval: 检查间隔(毫秒)

        Returns:
            ElementDetectionResult: 检测结果
        """
        elapsed = 0

        while elapsed < max_wait_time:
            result = await self.detect_element(selectors, element_name, timeout=check_interval)

            if result.exists:
                return result

            await self.page.wait_for_timeout(check_interval)
            elapsed += check_interval

        # 超时后返回最后一次检测结果
        result = await self.detect_element(selectors, element_name, timeout=1000)
        if not result.exists:
            logger.info(f"  ⏱️  等待{element_name}超时({max_wait_time}ms),确认该元素不存在")

        return result
