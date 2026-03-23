"""
从角色详情页 HTML 中提取关联商品链接（道具/召唤兽等独立详情页）
参考 html/rule/rule_detail.html 中 equip?、equip_detail 等链接形态。
"""
from __future__ import annotations

import re
from typing import List, Optional, Set
from urllib.parse import urljoin, urlparse, parse_qs

BASE = "https://xyq.cbg.163.com"


def _normalize_url(href: str, base_url: str) -> str:
    href = href.strip()
    if href.startswith("//"):
        return "https:" + href
    if href.startswith("/"):
        return BASE + href
    if href.startswith("http"):
        return href
    return urljoin(base_url or BASE + "/", href)


def extract_eid_from_href(href: str) -> Optional[str]:
    m = re.search(r"[?&]eid=([^&]+)", href)
    return m.group(1) if m else None


def extract_child_equip_urls(html: str, page_url: str, self_eid: Optional[str] = None) -> List[str]:
    """
    从页面中提取藏宝阁商品详情链接，去重并排除当前主商品。
    """
    seen: Set[str] = set()
    out: List[str] = []

    for m in re.finditer(
        r'https?://xyq\.cbg\.163\.com(?:/cgi-bin)?/[^\s"\'<>]+?(?:equip_detail|equip\?)[^\s"\'<>]*',
        html,
        re.I,
    ):
        u = m.group(0).rstrip('.,;)"\'')
        if u in seen:
            continue
        eid = extract_eid_from_href(u)
        if self_eid and eid == self_eid:
            continue
        if "show_login" in u.lower():
            continue
        seen.add(u)
        out.append(u)

    # 相对路径 /equip?...
    base = page_url or BASE
    for m in re.finditer(r'href\s*=\s*["\']([^"\']*?(?:equip\?|equip_detail)[^"\']*)["\']', html, re.I):
        u = _normalize_url(m.group(1), base)
        if u in seen:
            continue
        eid = extract_eid_from_href(u)
        if self_eid and eid == self_eid:
            continue
        if "xyq.cbg.163.com" not in u:
            continue
        seen.add(u)
        out.append(u)

    return out[:50]
