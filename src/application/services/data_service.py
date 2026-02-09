"""
数据服务
处理数据的保存和查询
"""
from typing import List, Optional
import logging

from ...domain.entities.page_data import PageData
from ...infrastructure.database.repository import PageDataRepository

logger = logging.getLogger(__name__)


class DataService:
    """数据服务"""
    
    def __init__(self, repository: Optional[PageDataRepository] = None):
        """
        初始化数据服务
        
        Args:
            repository: 数据仓库（如果为None，则创建默认仓库）
        """
        self.repository = repository or PageDataRepository()
    
    def save_page_data(self, page_data: PageData) -> PageData:
        """
        保存页面数据
        
        Args:
            page_data: 页面数据实体
            
        Returns:
            保存后的页面数据实体
        """
        return self.repository.save(page_data)
    
    def get_all_pages(self) -> List[PageData]:
        """获取所有页面数据"""
        return self.repository.find_all()
    
    def get_page_by_id(self, page_id: int) -> Optional[PageData]:
        """根据ID获取页面数据"""
        return self.repository.find_by_id(page_id)
    
    def get_page_by_url(self, url: str) -> Optional[PageData]:
        """根据URL获取页面数据"""
        return self.repository.find_by_url(url)
