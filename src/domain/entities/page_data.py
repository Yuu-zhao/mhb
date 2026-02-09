"""
页面数据实体
"""
from datetime import datetime
from typing import Optional, Dict, Any
import json


class PageData:
    """页面数据实体"""
    
    def __init__(
        self,
        url: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        extracted_data: Optional[Dict[str, Any]] = None,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None
    ):
        self.id = id
        self.url = url
        self.title = title or "无标题"
        self.content = content or ""
        self.extracted_data = extracted_data or {}
        self.created_at = created_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'content': self.content,
            'extracted_data': self.extracted_data,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<PageData(id={self.id}, url='{self.url}', title='{self.title}')>"
