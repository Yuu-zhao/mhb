"""
数据库模型（SQLAlchemy ORM）
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


class PageDataModel(Base):
    """页面数据表模型（ORM）"""
    __tablename__ = 'page_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(500), nullable=False, index=True)
    title = Column(String(500))
    content = Column(Text)
    extracted_data = Column(Text)  # JSON格式的提取数据
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<PageDataModel(id={self.id}, url='{self.url}', title='{self.title}')>"
