"""
梦幻西游装备/灵饰名称枚举 → 类型属性（大类 / 细类 / 与 cbg_catalog 对齐的 sub_code）。

用于：根据商品「名称」或描述首行识别 灵饰·戒指/耳饰/手镯/佩饰、武器·各系、装备·部位 等。
名称表来自业务整理，匹配规则为**精确匹配**；在正文中识别时优先**最长名称**避免短词误伤。
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, TypedDict


class ItemTypeMeta(TypedDict, total=False):
    """名称解析后的类型属性（写入 payload.classification 或 item_name_resolution）"""

    major_category_zh: str  # 灵饰 / 武器 / 装备
    family_zh: str  # 如 戒指、枪、头盔
    item_sub_code: str  # ITEM_LINGSHI / ITEM_WEAPON / ITEM_ARMOR
    ling_shi_slot_zh: str  # 灵饰部位：戒指、耳饰、手镯、佩饰
    weapon_family_zh: str  # 武器系别：枪、剑、…
    armor_slot_zh: str  # 装备部位：发钗、头盔、腰带、靴子、男衣、女衣、饰品


# 构建：名称 -> 元数据
_NAME_TO_META: Dict[str, ItemTypeMeta] = {}
# 按长度降序，供正文扫描最长匹配
_SORTED_NAMES: List[str] = []


def _add(
    names: List[str],
    *,
    major: str,
    family: str,
    item_sub_code: str,
    ling_shi_slot: str = "",
    weapon_family: str = "",
    armor_slot: str = "",
) -> None:
    meta: ItemTypeMeta = {
        "major_category_zh": major,
        "family_zh": family,
        "item_sub_code": item_sub_code,
    }
    if ling_shi_slot:
        meta["ling_shi_slot_zh"] = ling_shi_slot
    if weapon_family:
        meta["weapon_family_zh"] = weapon_family
    if armor_slot:
        meta["armor_slot_zh"] = armor_slot
    for raw in names:
        n = raw.strip()
        if not n:
            continue
        if n in _NAME_TO_META and _NAME_TO_META[n] != meta:
            raise ValueError(f"duplicate name with different meta: {n!r}")
        _NAME_TO_META[n] = meta


def _build_catalog() -> None:
    if _NAME_TO_META:
        return

    # ---------- 一、灵饰类 ----------
    _add(
        ["枫华戒", "芙蓉戒", "金麟绕", "悦碧水", "九曜光华", "太虚渺云"],
        major="灵饰",
        family="戒指",
        item_sub_code="ITEM_LINGSHI",
        ling_shi_slot="戒指",
    )
    _add(
        ["翠叶环", "明月珰", "玉蝶翩", "点星芒", "凤羽流苏", "焰云霞珠"],
        major="灵饰",
        family="耳饰",
        item_sub_code="ITEM_LINGSHI",
        ling_shi_slot="耳饰",
    )
    _add(
        ["香木镯", "翡玉镯", "墨影扣", "花映月", "金水菩提", "浮雪幻音"],
        major="灵饰",
        family="手镯",
        item_sub_code="ITEM_LINGSHI",
        ling_shi_slot="手镯",
    )
    _add(
        ["芝兰佩", "逸云佩", "莲音玦", "相思染", "玄龙苍珀", "碧海青天"],
        major="灵饰",
        family="佩饰",
        item_sub_code="ITEM_LINGSHI",
        ling_shi_slot="佩饰",
    )

    # ---------- 二、武器类（系别 -> 各等级名）----------
    _W = "武器"
    _C = "ITEM_WEAPON"

    _add(
        [
            "玄铁矛",
            "金蛇信",
            "丈八点钢矛",
            "暗夜",
            "梨花",
            "霹雳",
            "刑天之逆",
            "五虎断魂",
            "飞龙在天",
            "天龙破城",
            "弑皇",
        ],
        major=_W,
        family="枪",
        item_sub_code=_C,
        weapon_family="枪",
    )
    _add(
        [
            "乌金鬼头镰",
            "狂魔镰",
            "恶龙之齿",
            "破魄",
            "肃魂",
            "无敌",
            "五丁开山",
            "元神禁锢",
            "护法灭魔",
            "碧血干戚",
            "裂天",
        ],
        major=_W,
        family="斧钺",
        item_sub_code=_C,
        weapon_family="斧钺",
    )
    _add(
        [
            "游龙剑",
            "北斗七星剑",
            "碧玉剑",
            "湛卢",
            "倚天",
            "鱼肠",
            "魏武青虹",
            "四法青云",
            "灵犀神剑",
            "霜冷九州",
            "擒龙",
        ],
        major=_W,
        family="剑",
        item_sub_code=_C,
        weapon_family="剑",
    )
    _add(
        [
            "赤焰双剑",
            "墨玉双剑",
            "梅花双剑",
            "阴阳",
            "月光",
            "灵蛇",
            "金龙双剪",
            "连理双树",
            "祖龙对剑",
            "紫电青霜",
            "浮犀",
        ],
        major=_W,
        family="双短剑",
        item_sub_code=_C,
        weapon_family="双短剑",
    )
    _add(
        [
            "七彩罗刹",
            "缚神绫",
            "九天仙绫",
            "彩虹",
            "流云",
            "碧波",
            "秋水落霞",
            "此最相思",
            "晃金仙绳",
            "揽月摘星",
            "九霄",
        ],
        major=_W,
        family="飘带",
        item_sub_code=_C,
        weapon_family="飘带",
    )
    _add(
        [
            "青刚刺",
            "华光刺",
            "龙鳞刺",
            "撕天",
            "毒牙",
            "胭脂",
            "九阴勾魂",
            "雪蚕之刺",
            "贵霜之牙",
            "忘川三途",
            "离钩",
        ],
        major=_W,
        family="爪刺",
        item_sub_code=_C,
        weapon_family="爪刺",
    )
    _add(
        [
            "神火扇",
            "阴风扇",
            "风雨雷电",
            "太极",
            "玉龙",
            "秋风",
            "画龙点睛",
            "秋水人家",
            "逍遥江湖",
            "浩气长舒",
            "星瀚",
        ],
        major=_W,
        family="扇",
        item_sub_code=_C,
        weapon_family="扇",
    )
    _add(
        [
            "满天星",
            "水晶棒",
            "日月光华",
            "沧海",
            "盘龙",
            "红莲",
            "降魔玉杵",
            "青藤玉树",
            "墨玉骷髅",
            "丝萝乔木",
            "醍醐",
        ],
        major=_W,
        family="魔棒",
        item_sub_code=_C,
        weapon_family="魔棒",
    )
    _add(
        [
            "震天锤",
            "巨灵神锤",
            "天崩地裂",
            "八卦",
            "鬼牙",
            "雷神",
            "混元金锤",
            "九瓣莲花",
            "鬼王蚀日",
            "狂澜碎岳",
            "碎寂",
        ],
        major=_W,
        family="锤",
        item_sub_code=_C,
        weapon_family="锤",
    )
    _add(
        [
            "青藤柳叶鞭",
            "雷鸣嗜血鞭",
            "混元金钩",
            "龙筋",
            "百花",
            "吹雪",
            "游龙惊鸿",
            "仙人指路",
            "血之刺藤",
            "牧云清歌",
            "霜陨",
        ],
        major=_W,
        family="鞭",
        item_sub_code=_C,
        weapon_family="鞭",
    )
    # 环圈：不含「月光」——与双短剑分支短名冲突，同名无法仅凭名称区分
    _add(
        [
            "蛇形月",
            "子母双月",
            "斜月狼牙",
            "如意",
            "乾坤",
            "别情离恨",
            "金玉双环",
            "九天金线",
            "无关风月",
            "朝夕",
        ],
        major=_W,
        family="环圈",
        item_sub_code=_C,
        weapon_family="环圈",
    )
    _add(
        [
            "狼牙刀",
            "龙鳞宝刀",
            "黑炎魔刀",
            "冷月",
            "屠龙",
            "偃月青龙",
            "晓风残月",
            "斩妖泣血",
            "业火三灾",
            "鸣鸿",
        ],
        major=_W,
        family="刀",
        item_sub_code=_C,
        weapon_family="刀",
    )
    _add(
        [
            "腾云杖",
            "引魂杖",
            "碧玺杖",
            "业焰",
            "玉辉",
            "鹿鸣",
            "庄周梦蝶",
            "凤翼流珠",
            "雪蟒霜寒",
            "碧海潮生",
            "弦月",
        ],
        major=_W,
        family="法杖",
        item_sub_code=_C,
        weapon_family="法杖",
    )
    _add(
        [
            "如意宝珠",
            "沧海明珠",
            "无量玉璧",
            "离火",
            "飞星",
            "月华",
            "回风舞雪",
            "紫金葫芦",
            "裂云啸日",
            "云雷万里",
            "赤明",
        ],
        major=_W,
        family="宝珠",
        item_sub_code=_C,
        weapon_family="宝珠",
    )
    _add(
        [
            "连珠神弓",
            "游鱼戏珠",
            "灵犀望月",
            "幽篁",
            "非攻",
            "百鬼",
            "冥火薄天",
            "龙鸣寒水",
            "太极流光",
            "九霄风雷",
            "若木",
        ],
        major=_W,
        family="弓弩",
        item_sub_code=_C,
        weapon_family="弓弩",
    )
    _add(
        [
            "孔雀羽",
            "金刚伞",
            "落梅伞",
            "鬼骨",
            "云梦",
            "枕霞",
            "碧火琉璃",
            "雪羽穿云",
            "月影星痕",
            "浮生归梦",
            "晴雪",
        ],
        major=_W,
        family="伞",
        item_sub_code=_C,
        weapon_family="伞",
    )
    _add(
        [
            "玲珑盏",
            "玉兔盏",
            "冰心盏",
            "蟠龙",
            "云鹤",
            "风荷",
            "金风玉露",
            "凰火燎原",
            "风露清愁",
            "夭桃秾李",
            "荒尘",
        ],
        major=_W,
        family="灯笼",
        item_sub_code=_C,
        weapon_family="灯笼",
    )
    _add(
        [
            "惊涛雪",
            "醉浮生",
            "沉戟天戉",
            "昆吾",
            "弦歌",
            "鸦九",
            "秋水澄流",
            "腾蛇郁刃",
            "墨骨枯麟",
            "百辟镇魂",
            "长息",
        ],
        major=_W,
        family="巨剑",
        item_sub_code=_C,
        weapon_family="巨剑",
    )
    _add(
        [
            "飞头蛮",
            "竹叶青",
            "鲛煞",
            "啖月",
            "义战",
            "恶来",
            "烬世野火",
            "九州海沸",
            "八狱末劫",
            "罗喉计都",
            "非天",
        ],
        major=_W,
        family="巨斧",
        item_sub_code=_C,
        weapon_family="巨斧",
    )
    _add(
        [
            "破浪须",
            "雷公木",
            "渡魂篙",
            "斩海",
            "惊魇",
            "燎天",
            "架海金梁",
            "擎天玉柱",
            "随心铁杆",
            "水火囚龙",
            "定海",
        ],
        major=_W,
        family="棍",
        item_sub_code=_C,
        weapon_family="棍",
    )

    # ---------- 三、装备类（防具部位）----------
    _E = "装备"
    _A = "ITEM_ARMOR"

    _add(
        [
            "玉女发冠",
            "魔女发冠",
            "七彩花环",
            "凤翅金翎",
            "寒雉霜蚕",
            "曜月嵌星",
            "郁金流苏簪",
            "玉翼附蝉翎",
            "鸾羽九凤冠",
            "金珰紫焰冠",
            "乾元鸣凤冕",
        ],
        major=_E,
        family="发钗",
        item_sub_code=_A,
        armor_slot="发钗",
    )
    _add(
        [
            "水晶帽",
            "乾坤帽",
            "黑魔冠",
            "白玉龙冠",
            "水晶夔帽",
            "翡翠曜冠",
            "金丝黑玉冠",
            "白玉琉璃冠",
            "兽鬼珐琅面",
            "紫金磐龙冠",
            "浑天玄火盔",
        ],
        major=_E,
        family="头盔",
        item_sub_code=_A,
        armor_slot="头盔",
    )
    _add(
        [
            "攫魂铃",
            "双魂引",
            "兽王腰带",
            "百窜云",
            "八卦锻带",
            "圣王坠",
            "幻彩玉带",
            "珠翠玉环",
            "金蟾含珠",
            "乾坤紫玉带",
            "琉璃寒玉带",
            "蝉翼鱼佩带",
            "磐龙凤翔带",
            "紫霄云芒带",
        ],
        major=_E,
        family="腰带",
        item_sub_code=_A,
        armor_slot="腰带",
    )
    _add(
        [
            "追星踏月",
            "九州履",
            "万里追云履",
            "踏雪无痕",
            "平步青云",
            "追云逐电",
            "乾坤天罡履",
            "七星逐月靴",
            "碧霞流云履",
            "金丝逐日履",
            "辟尘分光履",
        ],
        major=_E,
        family="靴子",
        item_sub_code=_A,
        armor_slot="靴子",
    )
    _add(
        [
            "夜魔披风",
            "龙骨甲",
            "死亡斗篷",
            "神谕披风",
            "珊瑚玉衣",
            "金蚕披风",
            "乾坤护心甲",
            "蝉翼金丝甲",
            "金丝鱼鳞甲",
            "紫金磐龙甲",
            "混元一气甲",
        ],
        major=_E,
        family="男衣",
        item_sub_code=_A,
        armor_slot="男衣",
    )
    _add(
        [
            "霓裳羽衣",
            "流云素裙",
            "七宝天衣",
            "飞天羽衣",
            "穰花翠裙",
            "金蚕丝裙",
            "紫香金乌裙",
            "碧霞彩云衣",
            "金丝蝉翼衫",
            "五彩凤翅衣",
            "鎏金浣月衣",
        ],
        major=_E,
        family="女衣",
        item_sub_code=_A,
        armor_slot="女衣",
    )
    _add(
        [
            "风月宝链",
            "八卦坠",
            "碧水青龙",
            "鬼牙攫魂",
            "万里卷云",
            "疾风之铃",
            "七彩玲珑",
            "黄玉琉佩",
            "鸾飞凤舞",
            "衔珠金凤佩",
            "七璜珠玉佩",
            "鎏金点翠佩",
            "紫金碧玺佩",
            "落霞陨星坠",
        ],
        major=_E,
        family="饰品",
        item_sub_code=_A,
        armor_slot="饰品",
    )

    global _SORTED_NAMES
    _SORTED_NAMES = sorted(_NAME_TO_META.keys(), key=len, reverse=True)


_build_catalog()


def normalize_item_name(name: str) -> str:
    """去首尾空白、全角空格。"""
    if not name:
        return ""
    s = name.strip().replace("\u3000", " ")
    s = re.sub(r"\s+", "", s)
    return s


def resolve_item_name_to_type(name: str) -> Optional[ItemTypeMeta]:
    """
    根据装备/灵饰**标准名称**精确解析类型属性。
    若名称含等级、特技等后缀，请先抽出纯名称再调用，或使用 ``match_longest_known_name_in_text``。
    """
    n = normalize_item_name(name)
    if not n:
        return None
    return _NAME_TO_META.get(n)


def match_longest_known_name_in_text(text: str) -> Optional[tuple[str, ItemTypeMeta]]:
    """
    在一段描述文本中查找**最长**的已知装备名并返回 (匹配到的名称, 类型元数据)。
    用于从「属性原文」「亮点」等字段中反查类型。
    """
    if not text or not text.strip():
        return None
    t = text.strip()
    for name in _SORTED_NAMES:
        if name in t:
            return name, _NAME_TO_META[name]
    return None


def enrich_classification_with_item_name(
    classification: Dict[str, Any],
    *,
    item_name_hint: Optional[str] = None,
    description_text: Optional[str] = None,
) -> Dict[str, Any]:
    """
    在已有 classification 上合并名称解析结果（不覆盖 kindid 等原始字段）。
    """
    out = dict(classification) if classification else {}
    meta: Optional[ItemTypeMeta] = None
    matched_name: Optional[str] = None

    if item_name_hint:
        n = normalize_item_name(item_name_hint)
        meta = resolve_item_name_to_type(n)
        if meta:
            matched_name = n

    if meta is None and description_text:
        hit = match_longest_known_name_in_text(description_text)
        if hit:
            matched_name, meta = hit

    if meta:
        out["item_name_resolution"] = {
            "matched_name": matched_name,
            "major_category_zh": meta.get("major_category_zh"),
            "family_zh": meta.get("family_zh"),
            "item_sub_code": meta.get("item_sub_code"),
            "ling_shi_slot_zh": meta.get("ling_shi_slot_zh", "") or None,
            "weapon_family_zh": meta.get("weapon_family_zh", "") or None,
            "armor_slot_zh": meta.get("armor_slot_zh", "") or None,
        }
    return out


# 灵饰部位（页面「类型」或枚举）→ cbg_catalog 细分子类码
LING_SHI_SLOT_ZH_TO_SUBCODE: Dict[str, str] = {
    "戒指": "ITEM_LINGSHI_RING",
    "耳饰": "ITEM_LINGSHI_EAR",
    "手镯": "ITEM_LINGSHI_BRACELET",
    "佩饰": "ITEM_LINGSHI_PENDANT",
}

# 游戏内武器「类型」文案（新模板 li）→ 与枚举 family 对齐的提示（仅 classification，子类码仍为 ITEM_WEAPON）
PAGE_WEAPON_TYPE_ZH_TO_FAMILY: Dict[str, str] = {
    "枪": "枪",
    "斧钺": "斧钺",
    "剑": "剑",
    "双短剑": "双短剑",
    "飘带": "飘带",
    "爪刺": "爪刺",
    "扇": "扇",
    "魔棒": "魔棒",
    "锤": "锤",
    "鞭": "鞭",
    "环圈": "环圈",
    "刀": "刀",
    "法杖": "法杖",
    "宝珠": "宝珠",
    "弓弩": "弓弩",
    "弓": "弓弩",
    "弩": "弓弩",
    "伞": "伞",
    "灯笼": "灯笼",
    "巨剑": "巨剑",
    "巨斧": "巨斧",
    "双斧": "巨斧",
    "棍": "棍",
}


def item_meta_to_sub_category_code(meta: ItemTypeMeta) -> str:
    """名称枚举命中时：最细子类码（灵饰四位 / 武器 ITEM_WEAPON / 防具 ITEM_ARMOR）。"""
    code = meta.get("item_sub_code") or "ITEM_OTHER"
    if code == "ITEM_LINGSHI":
        slot = meta.get("ling_shi_slot_zh") or ""
        return LING_SHI_SLOT_ZH_TO_SUBCODE.get(slot, "ITEM_LINGSHI")
    return code


def resolve_page_type_zh_to_subcode(page_type_zh: str) -> Optional[str]:
    """
    仅根据页面「类型：xxx」解析子类码（名称未命中枚举时的回退）。
    灵饰四类 → ITEM_LINGSHI_*；其余武器类 → ITEM_WEAPON；常见防具类型 → ITEM_ARMOR。
    """
    if not page_type_zh:
        return None
    pt = page_type_zh.strip()
    if pt in LING_SHI_SLOT_ZH_TO_SUBCODE:
        return LING_SHI_SLOT_ZH_TO_SUBCODE[pt]
    if pt in PAGE_WEAPON_TYPE_ZH_TO_FAMILY:
        return "ITEM_WEAPON"
    # 防具（页面常见类型）
    armor = {
        "发钗": "ITEM_ARMOR",
        "头盔": "ITEM_ARMOR",
        "腰带": "ITEM_ARMOR",
        "靴子": "ITEM_ARMOR",
        "男衣": "ITEM_ARMOR",
        "女衣": "ITEM_ARMOR",
        "饰品": "ITEM_ARMOR",
        "项链": "ITEM_ARMOR",
    }
    if pt in armor:
        return armor[pt]
    return None


def enrich_classification_page_type(
    classification: Dict[str, Any],
    *,
    page_type_zh: Optional[str] = None,
) -> Dict[str, Any]:
    """合并页面「类型」字段，供子类回退与展示。"""
    out = dict(classification) if classification else {}
    if page_type_zh:
        out["page_type_zh"] = page_type_zh.strip()
        if page_type_zh.strip() in PAGE_WEAPON_TYPE_ZH_TO_FAMILY:
            out["page_weapon_family_hint_zh"] = PAGE_WEAPON_TYPE_ZH_TO_FAMILY[page_type_zh.strip()]
    return out


def list_all_registered_names() -> List[str]:
    """调试：返回已注册的全部名称（排序）。"""
    return sorted(_NAME_TO_META.keys())
