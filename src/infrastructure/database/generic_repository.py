# -*- coding: utf-8 -*-
"""
泛型数据仓库
支持动态创建表并保存数据
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging
import json
import re

logger = logging.getLogger(__name__)

Base = declarative_base()


class GenericDataModel(Base):
    """泛型数据模型基类"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    data_id = Column(Integer, nullable=False, index=True)  # 关联的原始数据ID
    field_name = Column(String(100), nullable=False, index=True)  # 字段名
    field_value = Column(Text)  # 字段值（JSON字符串）
    field_type = Column(String(50))  # 字段类型（string, number, object, array等）
    created_at = Column(DateTime, default=datetime.now)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'data_id': self.data_id,
            'field_name': self.field_name,
            'field_value': json.loads(self.field_value) if self.field_value else None,
            'field_type': self.field_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class GenericRepository:
    """泛型数据仓库"""
    
    def __init__(self, db_path: str = 'scraped_data.db'):
        """
        初始化仓库
        
        Args:
            db_path: 数据库路径
        """
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self._ensure_table_exists()
    
    def _ensure_table_exists(self):
        """确保表存在"""
        try:
            GenericDataModel.metadata.create_all(self.engine)
            logger.info("泛型数据表已创建或已存在")
        except Exception as e:
            logger.error(f"创建泛型数据表失败: {str(e)}")
    
    def _sanitize_table_name(self, name: str) -> str:
        """清理表名，确保符合SQL规范"""
        # 移除特殊字符，只保留字母、数字和下划线
        name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        # 确保以字母或下划线开头
        if name and not name[0].isalpha() and name[0] != '_':
            name = '_' + name
        # 限制长度
        if len(name) > 63:
            name = name[:63]
        return name
    
    def _get_field_type(self, value: Any) -> str:
        """获取字段类型"""
        if value is None:
            return 'null'
        elif isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, int):
            return 'integer'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, str):
            return 'string'
        elif isinstance(value, list):
            return 'array'
        elif isinstance(value, dict):
            return 'object'
        else:
            return 'unknown'
    
    def save_data(self, data_id: int, data: Dict[str, Any]) -> bool:
        """
        保存数据到泛型表
        
        Args:
            data_id: 关联的原始数据ID
            data: 要保存的数据字典
            
        Returns:
            是否保存成功
        """
        session = self.Session()
        try:
            # 先删除该data_id的旧数据
            session.query(GenericDataModel).filter(
                GenericDataModel.data_id == data_id
            ).delete()
            
            # 保存新数据
            for key, value in data.items():
                if value is None:
                    continue
                
                # 将值转换为JSON字符串
                if isinstance(value, (dict, list)):
                    value_str = json.dumps(value, ensure_ascii=False)
                else:
                    value_str = json.dumps(value, ensure_ascii=False)
                
                field_type = self._get_field_type(value)
                
                record = GenericDataModel(
                    data_id=data_id,
                    field_name=str(key),
                    field_value=value_str,
                    field_type=field_type
                )
                session.add(record)
            
            session.commit()
            logger.info(f"成功保存泛型数据，data_id={data_id}, 字段数={len(data)}")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"保存泛型数据失败: {str(e)}")
            return False
        finally:
            session.close()
    
    def get_data(self, data_id: int) -> Optional[Dict[str, Any]]:
        """
        获取数据
        
        Args:
            data_id: 数据ID
            
        Returns:
            数据字典，如果不存在返回None
        """
        session = self.Session()
        try:
            records = session.query(GenericDataModel).filter(
                GenericDataModel.data_id == data_id
            ).all()
            
            if not records:
                return None
            
            result = {}
            for record in records:
                try:
                    value = json.loads(record.field_value) if record.field_value else None
                    result[record.field_name] = value
                except:
                    result[record.field_name] = record.field_value
            
            return result
            
        except Exception as e:
            logger.error(f"获取泛型数据失败: {str(e)}")
            return None
        finally:
            session.close()
    
    def delete_data(self, data_id: int) -> bool:
        """
        删除数据
        
        Args:
            data_id: 数据ID
            
        Returns:
            是否删除成功
        """
        session = self.Session()
        try:
            deleted = session.query(GenericDataModel).filter(
                GenericDataModel.data_id == data_id
            ).delete()
            session.commit()
            logger.info(f"成功删除泛型数据，data_id={data_id}, 删除记录数={deleted}")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"删除泛型数据失败: {str(e)}")
            return False
        finally:
            session.close()
    
    def list_data_ids(self) -> List[int]:
        """
        获取所有数据ID列表
        
        Returns:
            数据ID列表
        """
        session = self.Session()
        try:
            data_ids = session.query(GenericDataModel.data_id).distinct().all()
            return [row[0] for row in data_ids]
        except Exception as e:
            logger.error(f"获取数据ID列表失败: {str(e)}")
            return []
        finally:
            session.close()
