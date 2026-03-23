"""
藏宝阁商品分类目录（可扩展）

后续新增类型：在 CATEGORIES 中追加一行 (code, parent_code, name_zh, sort_order)，
并在 cbg_classification.KINDID_TO_CATEGORY 或 DOM 规则中补充映射即可。
"""
from __future__ import annotations

from typing import List, Optional, Tuple

# (code, parent_code, name_zh, sort_order)
CATEGORIES: List[Tuple[str, Optional[str], str, int]] = [
    # 一级
    ("CHAR", None, "角色", 10),
    ("SUMMON", None, "召唤兽", 20),
    ("ITEM", None, "道具", 30),
    # 角色下（业务标签，可与页面 tab 对应）
    ("CHAR_BASIC", "CHAR", "基本信息", 11),
    ("CHAR_ROLE", "CHAR", "人物/修炼", 12),
    ("CHAR_SKILL", "CHAR", "技能", 13),
    ("CHAR_ITEM_TAB", "CHAR", "道具/法宝", 14),
    ("CHAR_PET", "CHAR", "召唤兽/孩子", 15),
    ("CHAR_MOUNT", "CHAR", "坐骑", 16),
    ("CHAR_APPEARANCE", "CHAR", "锦衣/外观", 17),
    ("CHAR_HOME", "CHAR", "玩家之家", 18),
    # 召唤兽
    ("SUMMON_BASIC", "SUMMON", "基本信息", 21),
    ("SUMMON_ATTR", "SUMMON", "资质", 22),
    ("SUMMON_SKILL", "SUMMON", "技能", 23),
    ("SUMMON_TRAIT", "SUMMON", "特性", 24),
    ("SUMMON_EQUIP", "SUMMON", "装备", 25),
    ("SUMMON_ORNAMENT", "SUMMON", "饰品", 26),
    ("SUMMON_NEIDAN", "SUMMON", "内丹", 27),
    # 道具（二级）
    ("ITEM_WEAPON", "ITEM", "武器", 31),
    ("ITEM_ARMOR", "ITEM", "防具", 32),
    ("ITEM_LINGSHI", "ITEM", "灵饰", 33),
    ("ITEM_ANCIENT_JADE", "ITEM", "上古玉魄", 34),
    ("ITEM_OTHER", "ITEM", "其它道具", 39),
]

# kindid → 道具子类 code（来自藏宝阁接口，可按需扩展）
# 参考示例：7 武器，61 灵饰戒指，65 召唤兽（storage_type=2 时走 SUMMON 而非 ITEM）
KINDID_TO_ITEM_SUBCATEGORY = {
    "7": "ITEM_WEAPON",
    "8": "ITEM_WEAPON",
    "9": "ITEM_WEAPON",
    "10": "ITEM_WEAPON",
    "11": "ITEM_WEAPON",
    "12": "ITEM_WEAPON",
    "13": "ITEM_WEAPON",
    "14": "ITEM_WEAPON",
    "61": "ITEM_LINGSHI",
    "62": "ITEM_LINGSHI",
    "63": "ITEM_LINGSHI",
    "64": "ITEM_LINGSHI",
    "85": "ITEM_WEAPON",
    "86": "ITEM_WEAPON",
}
