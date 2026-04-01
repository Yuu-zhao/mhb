"""
数据提取模块
从网页内容中提取结构化信息
严格按照DOM结构定位规则进行抽取（终版）
"""
from bs4 import BeautifulSoup, NavigableString
from typing import Dict, Optional, Any
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataExtractor:
    """数据提取器 - 严格基于 DOM + strong 语义定位"""

    # =========================
    # 对外主入口
    # =========================
    def extract_game_equip_info(self, html_content: str, url: str = "") -> Dict[str, Optional[str]]:
        soup = BeautifulSoup(html_content, "lxml")
        result: Dict[str, Optional[str]] = {}

        try:
            # -------------------------------------------------
            # 一、定位 infoList.goodsInfo（硬前置条件）
            # -------------------------------------------------
            goods_info = self._find_goods_info_container(soup)
            if not goods_info:
                logger.warning("❌ 未命中 infoList.goodsInfo，页面可能未登录或结构变更")
                return result

            logger.info("✅ 命中 infoList.goodsInfo，开始抽取商品基础信息")

            # -------------------------------------------------
            # 二、商品基础信息
            # -------------------------------------------------
            result["亮点"] = self._extract_highlights(goods_info)
            result["编号"] = self._extract_li_text(goods_info, "编号：")
            result["卖家"] = self._extract_li_text(goods_info, "卖家：")
            result["卖家ID"] = self._extract_seller_id(goods_info)
            # 新模板：状态：上架中；旧模板：是否上架：已上架
            status_new = self._extract_li_text(goods_info, "状态：")
            status_old = self._extract_li_text(goods_info, "是否上架：")
            result["状态"] = status_new or status_old
            result["是否上架"] = self._derive_onsale_status(status_new, status_old)
            result["类型"] = self._extract_li_text(goods_info, "类型：")
            result.update(self._extract_names_row(goods_info))
            result["价格"] = self._extract_price(goods_info)
            result["是否接受还价"] = self._extract_bargain(goods_info)
            result["出售剩余时间"] = self._extract_li_text(goods_info, "出售剩余时间：")

            # -------------------------------------------------
            # 三、人物 / 修炼模块
            # -------------------------------------------------
            role_box = soup.find("div", id="role_info_box")
            if role_box:
                logger.info("✅ 命中 role_info_box，开始抽取人物与修炼信息")
                result.update(self._extract_character_basic(role_box))
                result.update(self._extract_cultivation(role_box))
            else:
                logger.debug("未找到 role_info_box（非角色页可忽略）")

            # -------------------------------------------------
            # 四、关键字段校验（仅人物详情页）
            # -------------------------------------------------
            if soup.find("div", id="role_info_box"):
                required = ["编号", "价格", "级别", "门派"]
                missing = [f for f in required if not result.get(f)]
                if missing:
                    logger.warning(f"⚠️ 关键字段缺失: {missing}")
                else:
                    logger.info("✅ 关键字段完整")

        except Exception as e:
            logger.exception(f"❌ 数据抽取异常: {e}")

        return result

    # =========================
    # 一、基础结构定位
    # =========================
    def _find_goods_info_container(self, soup) -> Optional[BeautifulSoup]:
        for div in soup.find_all("div", class_=True):
            classes = div.get("class", [])
            if "infoList" in classes and "goodsInfo" in classes:
                return div
        return None

    # =========================
    # 二、基础商品信息
    # =========================
    def _extract_li_text(self, container, label: str) -> Optional[str]:
        for li in container.find_all("li"):
            strong = li.find("strong")
            if not strong or strong.get_text(strip=True) != label:
                continue

            for node in strong.next_siblings:
                if isinstance(node, NavigableString):
                    text = node.strip()
                    if text:
                        return text
                elif getattr(node, "name", None) not in ("script", "style"):
                    text = node.get_text(strip=True)
                    if text:
                        return text
        return None

    def _derive_onsale_status(self, status_new: Optional[str], status_old: Optional[str]) -> Optional[str]:
        if status_old:
            return status_old
        if status_new:
            if "上架" in status_new:
                return "已上架" if "已" in status_new or "中" in status_new else status_new
            return status_new
        return None

    def _extract_names_row(self, container) -> Dict[str, Optional[str]]:
        """
        新模板 li.names：服务器 / ID（展示名） / 等级
        例：ID：玉蝶翩（灵饰名）、ID：九州海沸（坤）（武器昵称）
        """
        out: Dict[str, Optional[str]] = {}
        for li in container.find_all("li", class_=True):
            if "names" not in (li.get("class") or []):
                continue
            text = li.get_text(" ", strip=True).replace("\xa0", " ")
            m_srv = re.search(r"服务器[：:]\s*(.+?)\s*ID[：:]", text)
            if m_srv:
                out["服务器"] = m_srv.group(1).strip()
            m_id = re.search(r"ID[：:]\s*(.+?)\s*等级[：:]", text)
            if m_id:
                out["展示ID"] = m_id.group(1).strip()
            m_lv = re.search(r"等级[：:]\s*([0-9]+)", text)
            if m_lv:
                out["模版等级"] = m_lv.group(1).strip()
            break
        return out

    def _extract_highlights(self, container) -> Optional[str]:
        for li in container.find_all("li"):
            strong = li.find("strong")
            if strong and strong.get_text(strip=True) == "亮点：":
                spans = [s.get_text(strip=True) for s in li.find_all("span") if s.get_text(strip=True)]
                return "|".join(spans) if spans else None
        return None

    def _extract_seller_id(self, container) -> Optional[str]:
        text = self._extract_li_text(container, "卖家ID：")
        if not text:
            return None
        m = re.search(r"\d+", text)
        return m.group(0) if m else text

    def _extract_price(self, container) -> Optional[str]:
        price_box = container.select_one("span.price")
        if not price_box:
            return None

        num_span = price_box.find("span", class_=re.compile(r"p\d+"))
        raw = (num_span or price_box).get_text(strip=True)
        raw = re.sub(r"[￥（元）()]", "", raw)
        return raw.strip()

    def _extract_bargain(self, container) -> Optional[str]:
        for li in container.find_all("li"):
            strong = li.find("strong")
            if strong and strong.get_text(strip=True) == "是否接受还价：":
                return "是" if li.find("input", id="bargain_button") else "否"
        return None

    # =========================
    # 三、人物基础信息
    # =========================
    def _extract_character_basic(self, role_box) -> Dict[str, Optional[str]]:
        result = {}

        table = role_box.find("table", class_="role_basic_attr_table")
        if not table:
            return result

        for td in table.find_all("td"):
            strong = td.find("strong")
            if not strong:
                continue

            key = strong.get_text(strip=True).replace("：", "")
            value = self._extract_td_value(td, strong)

            if key == "门派":
                span = td.find("span", id="kindName")
                value = span.get_text(strip=True) if span else value

            if key:
                result[key] = value

        return result

    def _extract_td_value(self, td, strong) -> Optional[str]:
        clone = BeautifulSoup(str(td), "lxml").find("td")
        for i in clone.find_all("i"):
            i.decompose()

        strong_clone = clone.find("strong")
        if not strong_clone:
            return None

        texts = []
        for node in strong_clone.next_siblings:
            if isinstance(node, NavigableString):
                t = node.strip()
                if t:
                    texts.append(t)
            elif getattr(node, "name", None):
                t = node.get_text(strip=True)
                if t:
                    texts.append(t)

        return " ".join(texts) if texts else None

    # =========================
    # 四、修炼 / 控制力
    # =========================
    def _extract_cultivation(self, role_box) -> Dict[str, Optional[str]]:
        result = {}

        h4 = role_box.find("h4", string=re.compile("角色修炼及宠修"))
        if not h4:
            return result

        parent = h4.find_parent()
        for table in parent.find_all("table", class_="tb02"):
            for tr in table.find_all("tr"):
                th, td = tr.find("th"), tr.find("td")
                if not th or not td:
                    continue
                key = th.get_text(strip=True).replace("：", "")
                val = td.get_text(strip=True)
                if key and val:
                    result[key] = val

        return result

    # =========================
    # 通用入口
    # =========================
    def extract_all_info(self, html_content: str, url: str = "") -> Dict[str, Any]:
        if "cbg.163.com" in url:
            return self.extract_game_equip_info(html_content, url)
        return self._extract_generic(html_content)

    def _extract_generic(self, html_content: str) -> Dict[str, Any]:
        soup = BeautifulSoup(html_content, "lxml")
        return {
            "标题": soup.title.get_text(strip=True) if soup.title else None,
            "链接数量": len(soup.find_all("a", href=True)),
            "图片数量": len(soup.find_all("img", src=True)),
        }
