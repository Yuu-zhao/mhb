"""
抓取器抽象基类
定义统一的抓取接口
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """抓取器抽象基类"""
    
    @abstractmethod
    def fetch_page(self, url: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        抓取网页内容
        
        Args:
            url: 要抓取的URL
            **kwargs: 其他参数
            
        Returns:
            包含url、title、content等字段的字典，失败返回None
        """
        pass
    
    @abstractmethod
    def close(self):
        """关闭资源"""
        pass
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
