"""
根据页面 DOM / kindid 判断商品大类与道具子类
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional, Tuple

from bs4 import BeautifulSoup

from cbg_catalog import KINDID_TO_ITEM_SUBCATEGORY

# 召唤兽在详情页可能以 pet 面板出现；kindid 65 常见于召唤兽
SUMMON_KINDIDS = {"65", "66"}


def _parse_kindid(html: str) -> Optional[str]:
    m = re.search(r'"kindid"\s*:\s*"(\d+)"', html)
    if m:
        return m.group(1)
    m = re.search(r"kindid['\"]?\s*[=:]\s*['\"]?(\d+)", html, re.I)
    return m.group(1) if m else None


def _parse_storage_type(html: str) -> Optional[str]:
    m = re.search(r'"storage_type"\s*:\s*(\d+)', html)
    if m:
        return m.group(1)
    return None


def classify_cbg_page(html: str) -> Tuple[str, Optional[str], Dict[str, Any]]:
    """
    返回 (一级 category_code, 二级 sub_category_code 或 None, 分类附加上下文)
    """
    soup = BeautifulSoup(html, "lxml")
    ctx: Dict[str, Any] = {}
    kindid = _parse_kindid(html)
    storage = _parse_storage_type(html)
    ctx["kindid"] = kindid
    ctx["storage_type"] = storage

    if soup.find("div", id="role_info_box"):
        return "CHAR", None, ctx

    if soup.find("div", id="pet_attr_panel"):
        return "SUMMON", None, ctx

    # 道具类：无角色框、无宠物属性面板
    if kindid in SUMMON_KINDIDS and storage == "2":
        return "SUMMON", None, ctx

    sub = KINDID_TO_ITEM_SUBCATEGORY.get(kindid or "", "ITEM_OTHER")
    return "ITEM", sub, ctx


def extract_eid_from_url(url: str) -> Optional[str]:
    m = re.search(r"[?&]eid=([^&]+)", url)
    return m.group(1) if m else None
