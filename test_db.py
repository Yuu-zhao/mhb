"""
测试数据库连接和表创建
"""
from database import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_database():
    """测试数据库功能"""
    try:
        logger.info("正在测试数据库...")
        db_manager = DatabaseManager()
        logger.info("数据库管理器创建成功")
        
        # 测试保存数据
        test_data = db_manager.save_page_data(
            url="https://test.example.com",
            title="测试标题",
            content="测试内容"
        )
        logger.info(f"测试数据保存成功，ID: {test_data.id}")
        
        # 测试查询数据
        all_data = db_manager.get_all_data()
        logger.info(f"查询到 {len(all_data)} 条记录")
        
        logger.info("数据库测试通过！")
        return True
    except Exception as e:
        logger.error(f"数据库测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    test_database()
