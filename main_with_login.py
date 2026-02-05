"""
主程序：支持登录的网页抓取并保存到数据库
"""
import sys
import argparse
from scraper import WebScraper
from selenium_scraper import SeleniumScraper
from database import DatabaseManager
from cookie_helper import CookieHelper
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def scrape_with_cookie(url: str, cookie_string: str = None, cookie_file: str = None, db_path: str = 'page_data.db'):
    """
    使用Cookie抓取网页并保存到数据库
    
    Args:
        url: 要抓取的网页URL
        cookie_string: Cookie字符串（从浏览器复制）
        cookie_file: Cookie文件路径（JSON格式）
        db_path: 数据库文件路径
    """
    # 初始化抓取器和数据库管理器
    scraper = WebScraper(use_session=True)
    db_manager = DatabaseManager(db_path)
    
    # 加载Cookie
    cookies = None
    if cookie_file:
        cookies = CookieHelper.load_cookies_from_file(cookie_file)
        logger.info(f"从文件加载Cookie: {cookie_file}")
    elif cookie_string:
        cookies = CookieHelper.parse_cookie_string(cookie_string)
        logger.info("从字符串解析Cookie")
    
    if cookies:
        scraper.set_cookies(cookies)
    
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


def scrape_with_selenium(url: str, headless: bool = True, db_path: str = 'page_data.db'):
    """
    使用Selenium抓取网页并保存到数据库（支持JavaScript渲染）
    
    Args:
        url: 要抓取的网页URL
        headless: 是否使用无头模式
        db_path: 数据库文件路径
    """
    scraper = None
    try:
        # 初始化Selenium抓取器
        scraper = SeleniumScraper(headless=headless)
        db_manager = DatabaseManager(db_path)
        
        # 抓取网页
        logger.info("使用Selenium抓取页面（支持JavaScript渲染）")
        page_data = scraper.fetch_page(url)
        
        if page_data is None:
            logger.error(f"无法抓取页面: {url}")
            return False
        
        # 保存到数据库
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
        logger.error(f"抓取失败: {str(e)}")
        return False
    finally:
        if scraper:
            scraper.close()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='网页抓取工具（支持登录）')
    parser.add_argument('url', help='要抓取的网页URL')
    parser.add_argument('--method', choices=['requests', 'selenium'], default='requests',
                       help='抓取方法：requests（使用Cookie）或selenium（自动化浏览器）')
    parser.add_argument('--cookie', type=str, help='Cookie字符串（从浏览器开发者工具复制）')
    parser.add_argument('--cookie-file', type=str, help='Cookie文件路径（JSON格式）')
    parser.add_argument('--selenium-headless', action='store_true', default=True,
                       help='Selenium是否使用无头模式（默认True）')
    parser.add_argument('--db', type=str, default='page_data.db', help='数据库文件路径')
    
    args = parser.parse_args()
    
    url = args.url
    
    # 验证URL格式
    if not url.startswith(('http://', 'https://')):
        logger.error("URL必须以http://或https://开头")
        sys.exit(1)
    
    logger.info(f"开始处理URL: {url}")
    logger.info(f"使用方法: {args.method}")
    
    if args.method == 'selenium':
        success = scrape_with_selenium(url, headless=args.selenium_headless, db_path=args.db)
    else:
        if not args.cookie and not args.cookie_file:
            logger.warning("使用requests方法但未提供Cookie，可能无法访问需要登录的页面")
        success = scrape_with_cookie(url, cookie_string=args.cookie, 
                                     cookie_file=args.cookie_file, db_path=args.db)
    
    if success:
        logger.info("处理完成！")
        sys.exit(0)
    else:
        logger.error("处理失败！")
        sys.exit(1)


if __name__ == '__main__':
    main()
