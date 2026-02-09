"""
多标签页抓取服务
支持依次点击不同标签页并提取数据
"""
from typing import Optional, Dict, Any, List
import logging
import time as time_module

from ...core.scrapers.base import BaseScraper
from ...core.extractors.game_equip_extractor import DataExtractor
from ...core.extractors.skill_extractor import SkillExtractor
from ...core.extractors.equip_extractor import EquipExtractor
from ...domain.entities.page_data import PageData

logger = logging.getLogger(__name__)


class MultiTabScrapingService:
    """多标签页抓取服务"""
    
    def __init__(self, scraper: BaseScraper):
        """
        初始化多标签页抓取服务
        
        Args:
            scraper: 抓取器实例（必须是PlaywrightScraper，支持页面交互）
        """
        self.scraper = scraper
        self.basic_extractor = DataExtractor()
        self.skill_extractor = SkillExtractor()
        self.equip_extractor = EquipExtractor()
    
    def scrape_all_tabs(self, url: str, **kwargs) -> Optional[PageData]:
        """
        抓取所有标签页的数据
        
        Args:
            url: 要抓取的URL
            **kwargs: 其他参数
            
        Returns:
            PageData实体，包含所有标签页的数据
        """
        
        try:
            # 1. 抓取初始页面（人物/修炼）
            logger.info("正在抓取初始页面（人物/修炼）...")
            page_data = self.scraper.fetch_page(url, **kwargs)
            if not page_data:
                return None
            
            # 提取基础信息
            basic_data = {}
            if page_data.get('content'):
                # 使用extract_game_equip_info方法
                basic_data = self.basic_extractor.extract_game_equip_info(
                    page_data['content'],
                    url
                )
            
            # 2. 点击技能标签页
            logger.info("正在点击技能标签页...")
            skill_data = self._click_and_extract_tab('role_skill', self.skill_extractor.extract_skill_info)
            
            # 3. 点击道具标签页
            logger.info("正在点击道具标签页...")
            equip_data = self._click_and_extract_tab('role_equips', self.equip_extractor.extract_equip_info)
            
            # 合并所有数据
            all_data = {
                'basic_info': basic_data,
                'skill_info': skill_data,
                'equip_info': equip_data
            }
            
            # 创建领域实体
            return PageData(
                url=page_data.get('url', url),
                title=page_data.get('title', '无标题'),
                content=page_data.get('content', ''),
                extracted_data=all_data
            )
            
        except Exception as e:
            logger.error(f"多标签页抓取失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _click_and_extract_tab(self, tab_id: str, extractor_func) -> Dict[str, Any]:
        """
        点击标签页并提取数据
        
        Args:
            tab_id: 标签页ID（如 'role_skill', 'role_equips'）
            extractor_func: 提取函数
            
        Returns:
            提取的数据
        """
        try:
            page = self.scraper.page
            
            # 点击标签页
            tab_selector = f"li#{tab_id}"
            tab_element = page.query_selector(tab_selector)
            
            if not tab_element:
                logger.warning(f"未找到标签页: {tab_id}")
                return {}
            
            # 点击标签
            tab_element.click()
            time_module.sleep(1)  # 等待内容加载
            
            # 等待tabCont内容更新
            page.wait_for_selector('div.tabCont', timeout=5000)
            time_module.sleep(0.5)  # 额外等待确保内容完全加载
            
            # 获取更新后的HTML
            html_content = page.content()
            
            # 提取数据
            return extractor_func(html_content)
            
        except Exception as e:
            logger.error(f"点击标签页 {tab_id} 失败: {str(e)}")
            return {}
