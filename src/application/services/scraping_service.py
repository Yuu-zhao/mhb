"""
抓取服务
协调抓取器和数据提取器
"""
from typing import Optional, Dict, Any
import logging

from ...core.scrapers.base import BaseScraper
from ...core.extractors.game_equip_extractor import DataExtractor
from ...domain.entities.page_data import PageData

logger = logging.getLogger(__name__)


class ScrapingService:
    """抓取服务"""
    
    def __init__(self, scraper: BaseScraper, extractor: Optional[DataExtractor] = None):
        """
        初始化抓取服务
        
        Args:
            scraper: 抓取器实例
            extractor: 数据提取器（可选）
        """
        self.scraper = scraper
        self.extractor = extractor or DataExtractor()
    
    def scrape_and_extract(self, url: str, **kwargs) -> Optional[PageData]:
        """
        抓取页面并提取数据
        
        Args:
            url: 要抓取的URL
            **kwargs: 其他参数
            
        Returns:
            PageData实体，失败返回None
        """
        # 抓取页面
        page_data = self.scraper.fetch_page(url, **kwargs)
        if not page_data:
            return None
        
        # 提取结构化数据
        extracted_data = None
        if page_data.get('content'):
            extracted_data = self.extractor.extract_all_info(
                page_data['content'],
                url
            )
        
        # 创建领域实体
        return PageData(
            url=page_data.get('url', url),
            title=page_data.get('title', '无标题'),
            content=page_data.get('content', ''),
            extracted_data=extracted_data
        )
    
    def close(self):
        """关闭资源"""
        if hasattr(self.scraper, 'close'):
            self.scraper.close()
