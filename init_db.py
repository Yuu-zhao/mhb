"""
数据库初始化脚本
用于手动初始化数据库表
"""
from database import Base, DatabaseManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database(db_path='page_data.db'):
    """
    初始化数据库
    
    Args:
        db_path: 数据库文件路径
    """
    try:
        logger.info(f"正在初始化数据库: {db_path}")
        db_manager = DatabaseManager(db_path)
        logger.info("数据库初始化成功！")
        return True
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        return False


if __name__ == '__main__':
    import sys
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'page_data.db'
    init_database(db_path)
