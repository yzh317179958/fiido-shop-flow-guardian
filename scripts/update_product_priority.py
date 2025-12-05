#!/usr/bin/env python3
"""
更新商品优先级脚本

优先级分类逻辑（基于业务价值）：
- P0 (核心产品): 整车/电动车/滑板车 - 这是核心营收来源
- P1 (重要配件): 电池、充电器、电机 - 高价值配件，影响用户体验
- P2 (普通配件): 其他配件 - 刹车、链条、显示屏、车架配件等

分类依据：
1. 整车是核心产品，用户购买车辆后才会购买配件
2. 电池/充电器/电机是高价值配件，且直接影响车辆使用
3. 其他配件属于常规维护/升级需求
"""

import json
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def classify_product_priority(product: dict) -> str:
    """
    根据商品信息分类优先级

    Args:
        product: 商品数据字典

    Returns:
        优先级等级 ('P0', 'P1', 'P2')
    """
    name = product.get('name', '').lower()
    product_id = product.get('id', '').lower()
    category = product.get('category', '').lower()

    # ========== P0: 整车/核心产品 ==========
    # 整车型号关键词 - 必须是完整的车辆描述
    bike_patterns = [
        'electric bike', 'e-bike', 'electric scooter',
        'folding bike', 'city bike', 'commuter bike', 'cargo bike',
        'fat tire bike', 'gravel bike', 'touring bike', 'utility bike',
        'mountain bike', 'mini bike', 'hybrid bike', 'e-gravel'
    ]

    # 配件关键词（用于排除 - 如果包含这些则不是整车）
    accessory_keywords = [
        'battery', 'charger', 'motor', 'display', 'brake', 'chain',
        'tube', 'rack', 'seat', 'saddle', 'pedal', 'tire', 'wheel',
        'lock', 'key', 'cover', 'fender', 'light', 'bell', 'mirror',
        'bag', 'basket', 'controller', 'throttle', 'cable', 'grip',
        'kickstand', 'mudguard', 'horn', 'reflector', 'pannier',
        'inner', 'outer', 'disc', 'rotor', 'lever', 'pad', 'shell',
        'handlebar', 'stem', 'fork', 'frame', 'hub', 'spoke', 'rim',
        'accelerator', 'sensor', ' for ', '-for-', 'strip', 'port',
        'switch', 'rails', 'extender', 'combo', 'trailer', 'bushing',
        'spring', 'clamp', 'cage', 'bottle', 'holder', 'hanger',
        'derailleur', 'crank', 'crankset', 'freewheel', 'headset',
        'hook', 'quick release', 'handlepost', 'seatpost', 'booster'
    ]

    # 配件类分类（如果在这些分类中，一定不是整车）
    accessory_categories = ['accessories', 'replacement parts', 'batteries chargers']

    # 检查是否是整车
    is_bike = any(bp in name for bp in bike_patterns)
    has_accessory_keyword = any(ak in name for ak in accessory_keywords) or \
                            any(ak.replace(' ', '-') in str(product_id) for ak in accessory_keywords)
    is_accessory_category = any(ac in category for ac in accessory_categories)

    if is_bike and not has_accessory_keyword and not is_accessory_category:
        return 'P0'

    # ========== P1: 核心配件 (电池/充电器/电机) ==========
    core_part_keywords = ['battery', 'charger', 'motor']

    # 排除电池配件（如电池锁、电池盖）
    battery_accessory_keywords = ['lock', 'cover', 'shell', 'base', 'rails', 'switch', 'port', 'strip', 'bag', 'rack']

    is_core_part = any(kw in name for kw in core_part_keywords) or \
                   any(kw in category for kw in core_part_keywords)

    if is_core_part:
        # 检查是否是电池配件而非电池本身
        is_battery_accessory = any(kw in name for kw in battery_accessory_keywords)
        if not is_battery_accessory or 'combo' in name:  # combo包含电池
            return 'P1'

    # ========== P2: 普通配件 ==========
    return 'P2'


def get_priority_description(priority: str) -> str:
    """获取优先级描述"""
    descriptions = {
        'P0': '核心产品 (整车)',
        'P1': '重要配件 (电池/充电器/电机)',
        'P2': '普通配件'
    }
    return descriptions.get(priority, '未知')


def main():
    """主函数"""
    print("="*70)
    print("📦 更新商品优先级")
    print("="*70)

    # 加载商品数据
    products_file = PROJECT_ROOT / "data" / "products.json"
    with open(products_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    products = data.get("products", [])
    metadata = data.get("metadata", {})

    print(f"\n加载了 {len(products)} 个商品")

    # 统计
    priority_counts = {'P0': 0, 'P1': 0, 'P2': 0}
    priority_examples = {'P0': [], 'P1': [], 'P2': []}

    # 更新优先级
    for product in products:
        priority = classify_product_priority(product)
        product['priority'] = priority
        priority_counts[priority] += 1

        # 收集示例
        if len(priority_examples[priority]) < 5:
            priority_examples[priority].append(product['name'])

    # 打印统计
    print("\n📊 优先级分布:")
    print("-"*50)
    for p in ['P0', 'P1', 'P2']:
        pct = priority_counts[p] / len(products) * 100 if products else 0
        print(f"  {p} ({get_priority_description(p)}): {priority_counts[p]} ({pct:.1f}%)")

    # 打印示例
    print("\n📋 各优先级示例商品:")
    print("-"*50)
    for p in ['P0', 'P1', 'P2']:
        print(f"\n{p} - {get_priority_description(p)}:")
        for name in priority_examples[p]:
            print(f"  • {name[:60]}")

    # 更新元数据
    metadata['priority_updated_at'] = datetime.now().isoformat()
    metadata['priority_counts'] = priority_counts
    metadata['priority_logic'] = {
        'P0': '整车/电动车/滑板车 - 核心营收产品',
        'P1': '电池、充电器、电机 - 高价值核心配件',
        'P2': '其他配件 - 维护/升级配件'
    }

    # 保存
    data['products'] = products
    data['metadata'] = metadata

    with open(products_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 已更新 {len(products)} 个商品的优先级")
    print(f"📄 保存到: {products_file}")


if __name__ == "__main__":
    main()
