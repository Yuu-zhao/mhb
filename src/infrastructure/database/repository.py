"""
数据仓库实现
提供数据持久化接口
"""
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from typing import List, Optional
import logging
import json
from datetime import datetime

from .models import Base, PageDataModel
from ...domain.entities.page_data import PageData

logger = logging.getLogger(__name__)


class PageDataRepository:
    """页面数据仓库"""
    
    def __init__(self, db_path='page_data.db'):
        """
        初始化数据仓库
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self._ensure_tables_exist()
    
    def _ensure_tables_exist(self):
        """确保数据库表存在"""
        try:
            inspector = inspect(self.engine)
            existing_tables = inspector.get_table_names()
            
            # 检查新表名和旧表名（向后兼容）
            if 'raw_page_data' not in existing_tables and 'page_data' not in existing_tables:
                logger.info("表 raw_page_data 不存在，正在创建...")
                Base.metadata.create_all(self.engine, checkfirst=True)
                logger.info("表 raw_page_data 创建成功")
        except Exception as e:
            logger.error(f"检查/创建表时出错: {str(e)}")
            Base.metadata.create_all(self.engine, checkfirst=True)
    
    def save(self, page_data: PageData) -> PageData:
        """
        保存页面数据
        
        Args:
            page_data: 页面数据实体
            
        Returns:
            保存后的页面数据实体（包含ID）
        """
        session = self.SessionLocal()
        try:
            # 将extracted_data转换为JSON字符串
            extracted_json = None
            if page_data.extracted_data:
                extracted_json = json.dumps(page_data.extracted_data, ensure_ascii=False, indent=2)
            
            # 如果提供了extracted_data，content可以只保存摘要
            content = page_data.content
            if page_data.extracted_data and content:
                if len(content) > 10000:
                    content = content[:10000] + "\n\n... (内容已截断，关键信息已提取)"
            
            model = PageDataModel(
                url=page_data.url,
                title=page_data.title,
                content=content,
                extracted_data_json=extracted_json,  # 使用新字段名
                created_at=page_data.created_at
            )
            session.add(model)
            session.commit()
            session.refresh(model)
            
            # 更新实体的ID
            page_data.id = model.id
            return page_data
        except Exception as e:
            session.rollback()
            logger.error(f"保存数据失败: {str(e)}")
            raise
        finally:
            session.close()
    
    def find_all(self) -> List[PageData]:
        """获取所有页面数据"""
        session = self.SessionLocal()
        try:
            models = session.query(PageDataModel).all()
            return [self._model_to_entity(m) for m in models]
        finally:
            session.close()
    
    def find_by_id(self, id: int) -> Optional[PageData]:
        """根据ID查找"""
        session = self.SessionLocal()
        try:
            model = session.query(PageDataModel).filter(PageDataModel.id == id).first()
            return self._model_to_entity(model) if model else None
        finally:
            session.close()
    
    def find_by_url(self, url: str) -> Optional[PageData]:
        """根据URL查找"""
        session = self.SessionLocal()
        try:
            model = session.query(PageDataModel).filter(PageDataModel.url == url).first()
            return self._model_to_entity(model) if model else None
        finally:
            session.close()
    
    def _model_to_entity(self, model: PageDataModel) -> PageData:
        """将ORM模型转换为领域实体"""
        extracted_data = None
        # 兼容新旧字段名
        extracted_json = getattr(model, 'extracted_data_json', None) or getattr(model, 'extracted_data', None)
        if extracted_json:
            try:
                extracted_data = json.loads(extracted_json) if isinstance(extracted_json, str) else extracted_json
            except:
                pass
        
        return PageData(
            id=model.id,
            url=model.url,
            title=model.title,
            content=model.content,
            extracted_data=extracted_data,
            created_at=model.created_at
        )
