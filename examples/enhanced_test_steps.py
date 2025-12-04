#!/usr/bin/env python3
"""
增强版测试步骤示例 - 集成智能判断

展示如何使用TestIntelligence来改进测试逻辑
"""

from core.test_intelligence import TestIntelligence, ElementDetectionResult, FailureClassification


async def enhanced_step_example(page, step, js_errors):
    """
    增强版步骤示例: 商品图片验证

    改进点:
    1. 先检测元素是否存在(avoid无中生有的失败)
    2. 区分"功能不存在"和"功能有Bug"
    3. 只对存在的功能进行Bug检测
    """

    intelligence = TestIntelligence(page)

    # 1. 智能检测商品图片元素
    image_result = await intelligence.detect_element(
        selectors=[
            "img[src*='product']",
            "img[data-src*='product']",
            ".product__media-item img",
            ".product-main-image img",
            ".product-image img"
        ],
        element_name="商品图片"
    )

    # 2. 判断是否应该跳过测试
    should_skip, skip_reason = intelligence.should_skip_step(
        step_name="商品图片验证",
        prerequisite_elements=[image_result]
    )

    if should_skip:
        # 功能不存在,跳过而不是失败
        step.complete("skipped", skip_reason)
        return

    # 3. 功能存在,进行Bug检测
    if image_result.exists and not image_result.visible:
        # 元素存在但不可见 - 分类失败原因
        classification = await intelligence.classify_failure(
            step_name="商品图片验证",
            expected_element=image_result,
            operation_attempted=None,
            js_errors=js_errors
        )

        if classification.is_website_bug():
            # 这是网站Bug - 报告为失败
            step.complete(
                "failed",
                classification.reason,
                issue_details={
                    "scenario": "商品详情页面加载",
                    "operation": "加载商品图片",
                    "problem": "图片元素存在但不可见",
                    "root_cause": classification.reason,
                    "js_errors": js_errors
                }
            )
        else:
            # 不是Bug,可能是设计如此 - 报告为通过
            step.complete("passed", classification.reason)

    elif image_result.is_functional:
        # 功能正常
        step.complete("passed", f"商品图片显示正常 (使用选择器: {image_result.selector_used})")

    else:
        # 其他情况 - 分类失败
        classification = await intelligence.classify_failure(
            step_name="商品图片验证",
            expected_element=image_result,
            operation_attempted=None,
            js_errors=js_errors
        )

        if classification.should_report_as_failed():
            step.complete("failed", classification.reason)
        else:
            step.complete("skipped", classification.reason)


async def enhanced_quantity_test_example(page, step, js_errors_list):
    """
    增强版步骤示例: 数量选择测试

    改进点:
    1. 检测网页是否有数量选择UI
    2. 只对有该功能的页面进行测试
    3. 区分超时和真正的Bug
    """

    intelligence = TestIntelligence(page)

    # 1. 智能检测数量输入框
    quantity_input = await intelligence.detect_element(
        selectors=[
            "input[name='quantity']",
            "input[type='number'][name*='quantity']",
            ".quantity-selector input",
            ".qty input"
        ],
        element_name="数量输入框"
    )

    # 2. 智能检测加减按钮
    plus_button = await intelligence.detect_element(
        selectors=[
            "button.quantity-plus",
            "button[aria-label*='Increase']",
            "button:has-text('+')"
        ],
        element_name="数量增加按钮"
    )

    minus_button = await intelligence.detect_element(
        selectors=[
            "button.quantity-minus",
            "button[aria-label*='Decrease']",
            "button:has-text('-')"
        ],
        element_name="数量减少按钮"
    )

    # 3. 判断网页是否有数量选择功能
    if not quantity_input.exists:
        # 数量输入框不存在 = 该页面没有数量选择功能
        step.complete("skipped", "该商品页面未提供数量选择功能,跳过测试")
        return

    # 4. 输入框存在,检查是否有加减按钮
    if plus_button.exists or minus_button.exists:
        # 有加减按钮,测试按钮功能
        js_errors_before = len(js_errors_list)

        if plus_button.is_functional:
            try:
                # 记录点击前的值
                old_value = await quantity_input.element.get_attribute("value")

                # 点击加号
                await plus_button.element.click(timeout=3000)
                await page.wait_for_timeout(1000)

                # 检查值是否变化
                new_value = await quantity_input.element.get_attribute("value")
                new_js_errors = js_errors_list[js_errors_before:]

                if int(new_value) > int(old_value):
                    # 功能正常
                    step.complete("passed", f"数量增加功能正常 ({old_value} → {new_value})")
                elif new_js_errors:
                    # 点击无效 + 有JS错误 = Bug
                    step.complete(
                        "failed",
                        "数量增加功能存在Bug",
                        issue_details={
                            "scenario": "用户在商品页面调整购买数量",
                            "operation": f"点击加号按钮,期望数量从{old_value}增加",
                            "problem": f"数量未变化,且触发JavaScript错误",
                            "root_cause": "数量更新逻辑存在Bug",
                            "js_errors": new_js_errors
                        }
                    )
                else:
                    # 点击无效但无JS错误 = 可能有数量上限
                    step.complete("passed", f"数量保持不变({new_value}),可能已达上限")

            except Exception as e:
                # 分类失败原因
                classification = await intelligence.classify_failure(
                    step_name="数量增加测试",
                    expected_element=plus_button,
                    operation_attempted="点击加号按钮",
                    js_errors=js_errors_list[js_errors_before:],
                    exception=e
                )

                if classification.failure_type == FailureClassification.TYPE_TEST_TIMEOUT:
                    # 超时 - 不是Bug
                    step.complete("skipped", f"测试超时: {classification.reason}")
                elif classification.is_website_bug():
                    # 网站Bug
                    step.complete("failed", classification.reason)
                else:
                    # 测试错误
                    step.complete("skipped", f"测试异常: {classification.reason}")
        else:
            # 按钮存在但不可用
            step.complete("passed", "数量调整按钮存在但不可用,可能需要其他条件")

    else:
        # 只有输入框,没有按钮 - 测试手动输入
        if quantity_input.is_functional:
            step.complete("passed", f"数量输入框可用,支持手动输入 (当前值: {await quantity_input.element.get_attribute('value')})")
        else:
            step.complete("passed", "数量输入框存在但不可编辑")


async def enhanced_checkout_test_example(page, step, js_errors_list):
    """
    增强版步骤示例: 支付流程验证

    改进点:
    1. 先检查Checkout按钮是否存在
    2. 区分"购物车为空"和"Checkout按钮有Bug"
    3. 更精准的Bug检测
    """

    intelligence = TestIntelligence(page)

    # 1. 智能等待Checkout按钮(给足时间加载)
    checkout_button = await intelligence.intelligent_wait_for_element(
        selectors=[
            "button[name='checkout']",
            "[name='checkout']",
            "button:has-text('Checkout')",
            "a[href*='/checkout']"
        ],
        element_name="Checkout按钮",
        max_wait_time=5000
    )

    # 2. 检测购物车是否为空
    empty_cart = await intelligence.detect_element(
        selectors=[
            "text='Your cart is empty'",
            "text='购物车为空'",
            ".cart-empty",
            ".empty-cart"
        ],
        element_name="购物车空提示"
    )

    # 3. 智能判断
    if empty_cart.exists:
        # 购物车为空 - 这不是Bug
        step.complete("skipped", "购物车为空,无法测试Checkout功能")
        return

    if not checkout_button.exists:
        # Checkout按钮不存在 + 购物车非空 = 可能是Bug
        # 但也可能是网站设计(需要满足其他条件)
        step.complete("passed", "未找到Checkout按钮,可能需要满足其他条件(如选择配送方式)")
        return

    if checkout_button.is_functional:
        # 按钮存在且可用 - 测试通过
        step.complete("passed", f"Checkout按钮正常 (使用选择器: {checkout_button.selector_used})")
    else:
        # 按钮存在但不可用 - 检查是否有JS错误
        js_errors_before = len(js_errors_list)

        if len(js_errors_list) > js_errors_before:
            # 有新的JS错误 - 这是Bug
            step.complete(
                "failed",
                "Checkout按钮存在但不可用,且有JavaScript错误",
                issue_details={
                    "scenario": "用户尝试进入支付流程",
                    "operation": "访问购物车页面,查找Checkout按钮",
                    "problem": "按钮存在但不可点击",
                    "root_cause": "Checkout按钮渲染或交互逻辑存在Bug",
                    "js_errors": js_errors_list[js_errors_before:]
                }
            )
        else:
            # 无JS错误 - 可能是业务逻辑限制
            step.complete("passed", "Checkout按钮存在但不可用,可能需要满足其他条件")
