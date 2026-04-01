"""
按页面类型分块抽取，输出可落库的嵌套结构（与 cbg_catalog 分类对应）
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from cbg_classification import classify_cbg_page, extract_eid_from_url
from data_extractor import DataExtractor
from item_name_catalog import (
    enrich_classification_page_type,
    enrich_classification_with_item_name,
    item_meta_to_sub_category_code,
    match_longest_known_name_in_text,
    resolve_item_name_to_type,
    resolve_page_type_zh_to_subcode,
)


def _find_goods_info(soup: BeautifulSoup):
    for div in soup.find_all("div", class_=True):
        cls = div.get("class", [])
        if "infoList" in cls and "goodsInfo" in cls:
            return div
    return None


def _tb02_to_dict(table) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for tr in table.find_all("tr"):
        th, td = tr.find("th"), tr.find("td")
        if not th or not td:
            continue
        k = th.get_text(strip=True).replace("：", "")
        v = td.get_text(strip=True)
        if k:
            out[k] = v
    return out


def _extract_pet_sections(soup: BeautifulSoup) -> Dict[str, Any]:
    panel = soup.find("div", id="pet_attr_panel")
    if not panel:
        return {}

    sections: Dict[str, Any] = {"属性": {}, "资质": {}, "技能": [], "特性": "", "装备": [], "饰品": [], "内丹": []}

    tables = panel.find_all("table", class_="tb02")
    if tables:
        sections["属性"] = _tb02_to_dict(tables[0])

    zizi = panel.find("table", class_=re.compile(r"petZiZhiTb"))
    if zizi:
        sections["资质"] = _tb02_to_dict(zizi)

    skill_grid = panel.find("div", id="pet_skill_grid_con")
    if skill_grid:
        names: List[str] = []
        for img in skill_grid.find_all("img"):
            n = img.get("data_store_name")
            if n:
                names.append(n)
        sections["技能"] = names

    h4s = panel.find_all("h4")
    for h4 in h4s:
        t = h4.get_text(strip=True)
        if t.startswith("特性"):
            nxt = h4.find_next_sibling("div")
            if nxt:
                sections["特性"] = nxt.get_text(strip=True)

    neidan_tb = panel.find("table", id="RolePetNeidan")
    if neidan_tb:
        for tr in neidan_tb.find_all("tr"):
            th = tr.find("th")
            tds = tr.find_all("td")
            if th and len(tds) >= 2:
                sections["内丹"].append(
                    {"名称": th.get_text(strip=True), "层数": tds[-1].get_text(strip=True)}
                )

    return sections


def _extract_forge_original_shape(text: str) -> Optional[str]:
    """如「铸斧原始造型：晓风残月」→ 晓风残月（武器造型枚举名）。"""
    if not text:
        return None
    m = re.search(r"铸\w*原始造型[：:]\s*(\S+)", text)
    return m.group(1).strip() if m else None


def _extract_item_sections(soup: BeautifulSoup) -> Dict[str, Any]:
    panel = soup.find("p", id="equip_desc_panel")
    if not panel:
        return {}
    raw = panel.get_text("\n", strip=True)
    out: Dict[str, Any] = {
        "属性原文": raw,
        "伤害": _re_first(r"伤害\s*\+?\s*([\d]+)", raw),
        "法术伤害": _re_first(r"法术伤害\s*\+?\s*([\d]+)", raw),
        "固定伤害": _re_first(r"固定伤害\s*\+?\s*([\d]+)", raw),
        "命中": _re_first(r"命中\s*\+?\s*([\d]+)", raw),
        "防御": _re_first(r"防御\s*\+?\s*([\d]+)", raw),
        "灵力": _re_first(r"灵力\s*\+?\s*([\d]+)", raw),
        "气血": _re_first(r"气血\s*\+?\s*([\d]+)", raw),
        "敏捷": _re_first(r"敏捷\s*\+?\s*([\d]+)", raw),
        "精炼等级": _re_first(r"精炼等级\s*(\d+)", raw),
        "特技": _re_first(r"特技[：:]\s*([^\n]+)", raw),
        "特效": _re_first(r"特效[：:]\s*([^\n]+)", raw),
        "原始造型": _extract_forge_original_shape(raw),
    }
    return out


def _re_first(pat: str, text: str) -> Optional[str]:
    m = re.search(pat, text)
    return m.group(1).strip() if m else None


_LING_SHI_PAGE_TYPES = frozenset({"戒指", "耳饰", "手镯", "佩饰"})


def _guess_item_display_name(soup: BeautifulSoup, flat: Dict[str, Any], item_sections: Dict[str, Any]) -> str:
    """从道具详情面板 / 扁平字段中推测装备名称，供名称枚举匹配（对齐 html/daoju、html/lingshi 模板）。"""
    page_ty = (flat.get("类型") or "").strip()
    raw_panel = ""
    panel = soup.find("p", id="equip_desc_panel")
    if panel:
        raw_panel = panel.get_text("\n", strip=True)

    # 武器：铸X原始造型：标准名（daoju 模板）
    shape = (item_sections or {}).get("原始造型") or _extract_forge_original_shape(raw_panel)
    if shape and resolve_item_name_to_type(shape):
        return shape

    # 灵饰：列表行「ID：玉蝶翩」即标准名（lingshi 模板）
    if page_ty in _LING_SHI_PAGE_TYPES:
        sid = (flat.get("展示ID") or "").strip()
        if sid and resolve_item_name_to_type(sid):
            return sid

    if raw_panel:
        first = raw_panel.split("\n")[0].strip()
        if resolve_item_name_to_type(first):
            return first
        hit = match_longest_known_name_in_text(raw_panel)
        if hit:
            return hit[0]
    raw2 = (item_sections or {}).get("属性原文") or ""
    if raw2:
        hit = match_longest_known_name_in_text(raw2)
        if hit:
            return hit[0]
        first = raw2.split("\n")[0].strip()
        if resolve_item_name_to_type(first):
            return first
    for key in ("名称", "装备名称", "道具名称", "展示ID"):
        v = flat.get(key)
        if v:
            s = str(v).strip()
            if s:
                return s
    hl = flat.get("亮点") or ""
    if hl:
        hit = match_longest_known_name_in_text(str(hl))
        if hit:
            return hit[0]
    return ""


def _apply_item_resolved_category(payload: Dict[str, Any], flat: Dict[str, Any]) -> None:
    """名称枚举优先，其次页面「类型」→ 重写 sub_category_code（与 cbg_catalog 细分子类一致）。"""
    cls = payload.setdefault("classification", {})
    enrich_classification_page_type(cls, page_type_zh=flat.get("类型"))

    ir = cls.get("item_name_resolution")
    sub: Optional[str] = None
    source: Optional[str] = None

    if isinstance(ir, dict) and ir.get("matched_name"):
        meta = resolve_item_name_to_type(ir["matched_name"])
        if meta:
            sub = item_meta_to_sub_category_code(meta)
            source = "name_enum"

    if not sub:
        sub = resolve_page_type_zh_to_subcode((flat.get("类型") or "").strip())
        if sub:
            source = "page_type"

    if sub:
        payload["sub_category_code"] = sub
        cls["resolved_sub_category_code"] = sub
        cls["sub_category_source"] = source
        payload["category_code"] = "ITEM"
        payload["product_type"] = "ITEM"


def extract_structured_payload(html: str, url: str) -> Dict[str, Any]:
    """
    统一入口：返回带分类与分块的业务 JSON，供 goods_record.payload_json 存储。
    """
    soup = BeautifulSoup(html, "lxml")
    cat, sub, ctx = classify_cbg_page(html)
    de = DataExtractor()
    flat = de.extract_game_equip_info(html, url)

    eid = extract_eid_from_url(url)
    goods_no = flat.get("编号") or eid

    payload: Dict[str, Any] = {
        "schema_version": 1,
        "product_type": cat,
        "category_code": cat,
        "sub_category_code": sub,
        "classification": ctx,
        "eid": eid,
        "goods_no": goods_no,
        "source_url": url,
        "basic": {
            "亮点": flat.get("亮点"),
            "编号": goods_no,
            "卖家": flat.get("卖家"),
            "卖家ID": flat.get("卖家ID"),
            "是否上架": flat.get("是否上架"),
            "价格": flat.get("价格"),
            "是否接受还价": flat.get("是否接受还价"),
            "出售剩余时间": flat.get("出售剩余时间"),
        },
        "sections": {},
    }

    if cat == "ITEM":
        payload["basic"].update(
            {
                "类型": flat.get("类型"),
                "状态": flat.get("状态"),
                "服务器": flat.get("服务器"),
                "展示ID": flat.get("展示ID"),
                "模版等级": flat.get("模版等级"),
            }
        )

    basic_keys = {
        "亮点",
        "编号",
        "卖家",
        "卖家ID",
        "是否上架",
        "价格",
        "是否接受还价",
        "出售剩余时间",
        "类型",
        "状态",
        "服务器",
        "展示ID",
        "模版等级",
    }

    if cat == "CHAR":
        payload["sections"]["角色与详情"] = {
            k: v for k, v in flat.items() if k not in basic_keys and v
        }

    elif cat == "SUMMON":
        payload["sections"]["召唤兽"] = _extract_pet_sections(soup)
        payload["sections"]["商品信息补充"] = {
            k: v for k, v in flat.items() if k not in basic_keys and v
        }

    else:  # ITEM
        item_detail = _extract_item_sections(soup)
        payload["sections"]["道具详情"] = item_detail
        payload["sections"]["商品信息补充"] = {
            k: v for k, v in flat.items() if k not in basic_keys and v
        }
        guessed = _guess_item_display_name(soup, flat, item_detail)
        desc_blob = (item_detail.get("属性原文") or "") + "\n" + str(flat.get("亮点") or "")
        payload["classification"] = enrich_classification_with_item_name(
            payload.get("classification") or {},
            item_name_hint=guessed or None,
            description_text=desc_blob.strip() or None,
        )
        ir = payload["classification"].get("item_name_resolution")
        if isinstance(ir, dict):
            payload["item_name_resolution"] = ir
        _apply_item_resolved_category(payload, flat)

    return payload


def merge_flat_for_display(payload: Dict[str, Any]) -> Dict[str, Any]:
    """GUI 列表展示用：合并 basic + 关键 sections 为一层键值（简化）"""
    out: Dict[str, Any] = {}
    out.update(payload.get("basic") or {})
    out["分类"] = payload.get("category_code")
    out["商品类型"] = payload.get("product_type") or payload.get("category_code")
    out["子类"] = payload.get("sub_category_code") or ""
    ch = payload.get("children")
    if isinstance(ch, list) and ch:
        out["关联商品数"] = len(ch)
        for i, c in enumerate(ch[:20], 1):
            if not isinstance(c, dict):
                continue
            label = f"关联{i}_{c.get('product_type') or c.get('category_code') or '?'}"
            name = (c.get("basic") or {}).get("亮点") or c.get("goods_no") or ""
            out[label] = str(name)[:200]
    ct = payload.get("character_tabs")
    if isinstance(ct, dict) and ct:
        out["角色Tab已抓取"] = ",".join(
            k for k, v in ct.items() if isinstance(v, dict) and v.get("extracted") and not v.get("error")
        )
    if payload.get("sections"):
        sec = payload["sections"]
        if "角色与详情" in sec and isinstance(sec["角色与详情"], dict):
            out.update(sec["角色与详情"])
        if "召唤兽" in sec and isinstance(sec["召唤兽"], dict):
            for k, v in sec["召唤兽"].items():
                if isinstance(v, (dict, list)):
                    out[k] = str(v)[:500]
                else:
                    out[k] = v
        if "道具详情" in sec:
            out.update({f"道具_{k}": v for k, v in sec["道具详情"].items() if v})
    cls = payload.get("classification") or {}
    ir = cls.get("item_name_resolution")
    if isinstance(ir, dict) and ir.get("matched_name"):
        out["名称识别"] = ir.get("matched_name")
        out["名称大类"] = ir.get("major_category_zh") or ""
        out["名称细类"] = ir.get("family_zh") or ""
        out["名称子类码"] = ir.get("item_sub_code") or ""
    rsub = cls.get("resolved_sub_category_code")
    if rsub:
        out["子类"] = rsub
        out["子类来源"] = cls.get("sub_category_source") or ""
    return out
