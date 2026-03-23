"""
爬取辅助：抓取页面 + 提取核心数据 + 判断是否需要登录
供 GUI 调用，不包含界面逻辑。

注意：藏宝阁正常商品页 HTML 里导航/页脚也常含「登录」二字，不能用全文关键词判断，
否则会导致误判为「需要登录」并反复弹窗。以最终 URL（是否被重定向到 show_login）和
DOM（是否出现 goodsInfo 结构）为准。
"""
from typing import Optional, Dict, Any, Tuple
import logging

from playwright_scraper import PlaywrightScraper
from data_extractor import DataExtractor
from cbg_extractors import extract_structured_payload, merge_flat_for_display
from cbg_classification import extract_eid_from_url
from character_links import extract_child_equip_urls

logger = logging.getLogger(__name__)


def _final_url_is_login_page(final_url: str) -> bool:
    """最终地址是否被重定向到登录页（藏宝阁）"""
    if not final_url:
        return False
    u = final_url.lower()
    return "show_login" in u or "act=show_login" in u


def _html_looks_like_cbg_equip_loaded(content: str) -> bool:
    """页面 HTML 是否已出现商品信息容器（说明已拿到详情页，而非登录页壳子）"""
    if not content:
        return False
    return "infoList" in content and "goodsInfo" in content


def _attach_character_children(
    scraper: PlaywrightScraper,
    structured: Dict[str, Any],
    main_html: str,
    main_page_url: str,
) -> Dict[str, Any]:
    """角色详情页：顺序抓取页面内 equip 链接，写入 structured['children']。"""
    self_eid = structured.get("eid") or extract_eid_from_url(main_page_url)
    if isinstance(self_eid, str):
        self_eid = self_eid.strip() or None
    urls = extract_child_equip_urls(main_html, main_page_url, self_eid)
    parent_no = structured.get("goods_no")
    children: list = []
    for cu in urls:
        try:
            pd = scraper.fetch_page(cu)
            if not pd:
                continue
            child_html = pd.get("content") or ""
            child_final = (pd.get("url") or cu).strip()
            if _final_url_is_login_page(child_final):
                logger.warning("关联页被重定向登录，跳过: %s", child_final[:80])
                continue
            if not child_html or not _html_looks_like_cbg_equip_loaded(child_html):
                logger.warning("关联页未加载商品容器，跳过: %s", child_final[:80])
                continue
            ch = extract_structured_payload(child_html, child_final)
            ch["parent_goods_no"] = parent_no
            ch.pop("children", None)
            children.append(ch)
        except Exception as e:
            logger.warning("抓取关联商品失败 %s: %s", cu[:80], e)
    structured["children"] = children
    return structured


def scrape_page(
    url: str,
    storage_state_path: Optional[str] = None,
    headless: bool = True,
    deep_associated: bool = False,
    fetch_role_tabs: bool = True,
) -> Tuple[Optional[Dict[str, Any]], Dict[str, Any], bool]:
    """
    抓取页面并提取核心数据。

    Args:
        url: 要抓取的页面 URL
        storage_state_path: 登录态文件路径（可选）
        headless: 是否无头模式
        deep_associated: 若为 True 且商品为角色(CHAR)，在同一浏览器会话内继续抓取页面内关联的装备/召唤兽等详情并写入 payload['children']
        fetch_role_tabs: 若为 True 且商品为角色(CHAR)，在同一浏览器内依次点击「人物/修炼、技能、道具…」等 Tab，抓取各面板结构化数据写入 payload['character_tabs']（需在关联子商品爬取之前执行）

    Returns:
        (page_data, extracted_data, need_login)
    """
    extracted: Dict[str, Any] = {}
    need_login = False
    page_data: Optional[Dict[str, Any]] = None

    scraper = PlaywrightScraper(headless=headless, storage_state_path=storage_state_path)
    try:
        try:
            scraper.start()
            page_data = scraper.fetch_page(url)
        except Exception as e:
            logger.exception("抓取异常: %s", e)
            need_login = "登录" in str(e) or "login" in str(e).lower()
            return None, extracted, True

        if not page_data:
            return None, extracted, True

        content = page_data.get("content") or ""
        title = page_data.get("title") or ""
        final_url = page_data.get("url") or ""

        if _final_url_is_login_page(final_url):
            logger.info("最终 URL 为登录页，需要登录: %s", final_url[:120])
            return page_data, extracted, True

        try:
            extractor = DataExtractor()
            if "cbg.163.com" in url or "xyq.cbg.163.com" in final_url or "cbg.163.com" in final_url:
                flat = extractor.extract_game_equip_info(content, url)
                if not flat and content:
                    if _html_looks_like_cbg_equip_loaded(content):
                        logger.warning("页面含 goodsInfo 容器但抽取为空，可能 DOM 变更")
                        need_login = False
                    else:
                        need_login = True
                else:
                    need_login = False
                if flat or _html_looks_like_cbg_equip_loaded(content):
                    try:
                        structured = extract_structured_payload(content, final_url or url)
                        # 关联 equip 链接可能分散在各 Tab 的 DOM 中，合并后再抽链接
                        html_for_child_links = content
                        # 角色页：先切换各 Tab 再抓关联子商品（避免先离开页面导致无法点 Tab）
                        if (
                            fetch_role_tabs
                            and structured.get("category_code") == "CHAR"
                            and _html_looks_like_cbg_equip_loaded(content)
                        ):
                            try:
                                from role_tabs import scrape_all_character_tabs

                                tabs_data, merged_html = scrape_all_character_tabs(
                                    scraper, final_url or url, content
                                )
                                structured["character_tabs"] = tabs_data
                                structured.setdefault("sections", {})["角色页签"] = tabs_data
                                structured["schema_version"] = max(
                                    int(structured.get("schema_version") or 1), 2
                                )
                                if merged_html:
                                    html_for_child_links = merged_html
                            except Exception as e:
                                logger.exception("角色 Tab 抓取失败: %s", e)
                        if (
                            deep_associated
                            and structured.get("category_code") == "CHAR"
                            and _html_looks_like_cbg_equip_loaded(content)
                        ):
                            structured = _attach_character_children(
                                scraper,
                                structured,
                                html_for_child_links,
                                final_url or url,
                            )
                        extracted = merge_flat_for_display(structured)
                        extracted["__goods_payload__"] = structured
                    except Exception as e:
                        logger.exception("结构化抽取失败，回退为扁平: %s", e)
                        extracted = flat or {}
                else:
                    extracted = flat or {}
            else:
                extracted = {"标题": title, "链接": url}
                need_login = False
        except Exception as e:
            logger.exception("提取数据异常: %s", e)

        return page_data, extracted, need_login
    finally:
        try:
            scraper.close()
        except Exception as e:
            logger.warning("关闭浏览器时出错: %s", e)
