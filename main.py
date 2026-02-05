"""
主程序：抓取网页并保存到数据库
"""
import sys
from scraper import WebScraper
from database import DatabaseManager
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def scrape_and_save(url: str, db_path: str = 'page_data.db'):
    """
    抓取网页并保存到数据库
    
    Args:
        url: 要抓取的网页URL
        db_path: 数据库文件路径
    """
    # 初始化抓取器和数据库管理器
    scraper = WebScraper()
    db_manager = DatabaseManager(db_path)
    
    # 抓取网页
    page_data = scraper.fetch_page(url)
    
    if page_data is None:
        logger.error(f"无法抓取页面: {url}")
        return False
    
    # 保存到数据库
    try:
        saved_data = db_manager.save_page_data(
            url=page_data['url'],
            title=page_data['title'],
            content=page_data['content']
        )
        logger.info(f"成功保存数据到数据库，ID: {saved_data.id}")
        logger.info(f"标题: {saved_data.title}")
        logger.info(f"内容长度: {len(saved_data.content)} 字符")
        return True
    except Exception as e:
        logger.error(f"保存数据失败: {str(e)}")
        return False


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python main.py <URL>")
        print("示例: python main.py https://www.example.com")
        sys.exit(1)
    
    url = sys.argv[1]
    
    # 验证URL格式
    if not url.startswith(('http://', 'https://')):
        logger.error("URL必须以http://或https://开头")
        sys.exit(1)
    
    logger.info(f"开始处理URL: {url}")
    success = scrape_and_save(url)
    
    if success:
        logger.info("处理完成！")
        sys.exit(0)
    else:
        logger.error("处理失败！")
        sys.exit(1)


if __name__ == '__main__':
    main()
