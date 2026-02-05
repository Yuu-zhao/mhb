"""
数据库模型和操作
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()


class PageData(Base):
    """页面数据表"""
    __tablename__ = 'page_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(500), nullable=False, index=True)
    title = Column(String(500))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<PageData(id={self.id}, url='{self.url}', title='{self.title}')>"


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path='page_data.db'):
        """
        初始化数据库连接
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        # 确保表被创建
        self._ensure_tables_exist()
    
    def _ensure_tables_exist(self):
        """确保数据库表存在，如果不存在则创建"""
        try:
            inspector = inspect(self.engine)
            existing_tables = inspector.get_table_names()
            
            if 'page_data' not in existing_tables:
                logger.info("表 page_data 不存在，正在创建...")
                Base.metadata.create_all(self.engine, checkfirst=True)
                logger.info("表 page_data 创建成功")
            else:
                logger.debug("表 page_data 已存在")
        except Exception as e:
            logger.error(f"检查/创建表时出错: {str(e)}")
            # 如果检查失败，尝试直接创建
            try:
                Base.metadata.create_all(self.engine, checkfirst=True)
                logger.info("表创建完成")
            except Exception as e2:
                logger.error(f"创建表失败: {str(e2)}")
                raise
    
    def get_session(self):
        """获取数据库会话"""
        return self.SessionLocal()
    
    def save_page_data(self, url, title, content):
        """
        保存页面数据到数据库
        
        Args:
            url: 页面URL
            title: 页面标题
            content: 页面内容
            
        Returns:
            PageData对象
        """
        session = self.get_session()
        try:
            page_data = PageData(
                url=url,
                title=title,
                content=content,
                created_at=datetime.now()
            )
            session.add(page_data)
            session.commit()
            session.refresh(page_data)
            return page_data
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_all_data(self):
        """获取所有页面数据"""
        session = self.get_session()
        try:
            return session.query(PageData).all()
        finally:
            session.close()
    
    def get_data_by_url(self, url):
        """根据URL获取数据"""
        session = self.get_session()
        try:
            return session.query(PageData).filter(PageData.url == url).first()
        finally:
            session.close()
