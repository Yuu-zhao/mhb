"""
藏宝阁角色详情页：主区域为多 Tab，需切换后才能拿到对应 DOM。
依次点击 li#role_*，等待 div.tabCont 更新后抓取整页 HTML，再按 Tab 类型抽取结构化字段。
"""
from __future__ import annotations

import logging
import re
from typing import Any, Callable, Dict, List, Optional, Tuple

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# 与页面 <div class="tabs"><ul><li id="..."> 一致
ROLE_TAB_SEQUENCE: List[Tuple[str, str]] = [
    ("role_basic", "人物/修炼"),
    ("role_skill", "技能"),
    ("role_equips", "道具/法宝"),
    ("role_pets", "召唤兽/孩子"),
    ("role_riders", "坐骑"),
    ("role_clothes", "锦衣/外观"),
    ("role_home", "玩家之家"),
]


def _parse_role_info_box_tables(html: str) -> Dict[str, Any]:
    """首屏「人物/修炼」：解析 #role_info_box 内 td/strong 键值与摘要。"""
    soup = BeautifulSoup(html, "lxml")
    box = soup.find("div", id="role_info_box")
    if not box:
        return {}

    kv: Dict[str, str] = {}
    for td in box.find_all("td"):
        strong = td.find("strong")
        if not strong:
            continue
        k = strong.get_text(strip=True).replace("：", "").replace(":", "")
        if not k:
            continue
        full = td.get_text(strip=True)
        sk = strong.get_text(strip=True)
        val = full.replace(sk, "", 1).strip() if sk in full else full
        kv[k] = val

    out: Dict[str, Any] = {"键值对": kv}
    txt = box.get_text("\n", strip=True)
    if txt:
        out["原始文本摘要"] = txt[:8000] + ("…" if len(txt) > 8000 else "")

    school_ul = box.find("ul", id="school_skill_lists")
    if school_ul:
        skills = []
        for li in school_ul.find_all("li"):
            h5 = li.find("h5")
            p = li.find("p")
            if h5:
                skills.append({"name": h5.get_text(strip=True), "level": p.get_text(strip=True) if p else ""})
        if skills:
            out["师门技能预览"] = skills[:20]
    return out


def _get_extractor_map():
    """延迟导入，避免未安装依赖时阻塞其它模块。"""
    from src.core.extractors.skill_extractor import SkillExtractor
    from src.core.extractors.equip_extractor import EquipExtractor
    from src.core.extractors.pet_extractor import PetExtractor
    from src.core.extractors.mount_extractor import MountExtractor
    from src.core.extractors.appearance_extractor import AppearanceExtractor
    from src.core.extractors.home_extractor import HomeExtractor

    sk = SkillExtractor()
    eq = EquipExtractor()
    pe = PetExtractor()
    mo = MountExtractor()
    ap = AppearanceExtractor()
    ho = HomeExtractor()

    return {
        "role_basic": _parse_role_info_box_tables,
        "role_skill": sk.extract_skill_info,
        "role_equips": eq.extract_equip_info,
        "role_pets": pe.extract_pet_info,
        "role_riders": mo.extract_mount_info,
        "role_clothes": ap.extract_appearance_info,
        "role_home": ho.extract_home_info,
    }


def _click_tab(page, tab_id: str) -> bool:
    """点击顶部 Tab li#tab_id"""
    selectors = (
        f"div.tabs li#{tab_id}",
        f"div.tabs ul li#{tab_id}",
        f"li#{tab_id}",
    )
    last_err: Optional[Exception] = None
    for sel in selectors:
        try:
            page.click(sel, timeout=10000)
            return True
        except Exception as e:
            last_err = e
            continue
    logger.warning("点击 Tab %s 失败: %s", tab_id, last_err)
    return False


def _wait_tab_content(page, timeout_ms: int = 12000) -> None:
    try:
        page.wait_for_selector("div.tabCont", timeout=timeout_ms)
    except Exception as e:
        logger.debug("wait tabCont: %s", e)
    page.wait_for_timeout(450)


def scrape_all_character_tabs(
    scraper, url: str, initial_html: str
) -> Tuple[Dict[str, Any], str]:
    """
    在已打开角色详情页、且 scraper.page 有效时，切换全部 Tab 并抽取数据。

    Args:
        scraper: PlaywrightScraper 实例（已 start 且已 fetch 过 url）
        url: 当前页 URL（仅用于日志）
        initial_html: 首次 fetch_page 得到的 HTML（用于 role_basic，避免多点一次）

    Returns:
        (tab_payload, merged_html)
        - tab_payload: { tab_id: {"label","extracted","error"?} }
        - merged_html: 各 Tab 切换后页面 HTML 拼接，用于提取仅出现在某 Tab 内的 equip 链接
    """
    page = getattr(scraper, "page", None)
    if not page:
        logger.warning("scrape_all_character_tabs: 无 page")
        return {}, initial_html or ""

    extractors = _get_extractor_map()
    result: Dict[str, Any] = {}
    merged_chunks: List[str] = [initial_html or ""]

    # 人物/修炼：使用首屏 HTML（当前即为该 Tab）
    try:
        result["role_basic"] = {
            "label": "人物/修炼",
            "extracted": extractors["role_basic"](initial_html),
        }
    except Exception as e:
        logger.exception("解析人物/修炼 Tab 失败: %s", e)
        result["role_basic"] = {"label": "人物/修炼", "error": str(e), "extracted": {}}

    for tab_id, label in ROLE_TAB_SEQUENCE:
        if tab_id == "role_basic":
            continue
        fn: Callable[[str], Any] = extractors.get(tab_id)  # type: ignore
        if not fn:
            continue
        entry: Dict[str, Any] = {"label": label, "extracted": {}}
        try:
            if not _click_tab(page, tab_id):
                entry["error"] = "tab_not_found"
                result[tab_id] = entry
                continue
            _wait_tab_content(page)
            html = page.content()
            merged_chunks.append(html)
            entry["extracted"] = fn(html) or {}
        except Exception as e:
            logger.exception("Tab %s 抽取失败: %s", tab_id, e)
            entry["error"] = str(e)
        result[tab_id] = entry

    merged_html = "\n".join(merged_chunks)
    logger.info("角色 Tab 抓取完成 url=%s tabs=%s", url[:80], list(result.keys()))
    return result, merged_html
