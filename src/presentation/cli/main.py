"""
命令行主程序
"""
import sys
import argparse
from typing import Optional

from ...application.services import ScrapingService, DataService
from ...core.scrapers import RequestsScraper, SeleniumScraper, PlaywrightScraper
from ...infrastructure.database import PageDataRepository
from ...utils.logger import setup_logger
from config.settings import DATABASE_PATH

logger = setup_logger(__name__)


def main():
    """命令行主函数"""
    parser = argparse.ArgumentParser(description='网页抓取工具')
    parser.add_argument('url', help='要抓取的URL')
    parser.add_argument('--method', choices=['requests', 'selenium', 'playwright'], 
                       default='requests', help='抓取方法')
    parser.add_argument('--cookie', help='Cookie字符串')
    parser.add_argument('--cookie-file', help='Cookie文件路径')
    parser.add_argument('--headless', action='store_true', help='无头模式')
    parser.add_argument('--db', default=DATABASE_PATH, help='数据库路径')
    
    args = parser.parse_args()
    
    # 创建抓取器
    scraper = None
    if args.method == 'requests':
        scraper = RequestsScraper()
        if args.cookie:
            scraper.set_cookies(args.cookie)
    elif args.method == 'selenium':
        scraper = SeleniumScraper(headless=args.headless)
    elif args.method == 'playwright':
        scraper = PlaywrightScraper(headless=args.headless)
    
    if not scraper:
        logger.error("无法创建抓取器")
        sys.exit(1)
    
    # 创建服务
    scraping_service = ScrapingService(scraper)
    data_service = DataService(PageDataRepository(args.db))
    
    try:
        # 抓取并提取
        page_data = scraping_service.scrape_and_extract(args.url)
        
        if page_data:
            # 保存到数据库
            saved_data = data_service.save_page_data(page_data)
            logger.info(f"成功保存数据，ID: {saved_data.id}")
            logger.info(f"标题: {saved_data.title}")
            if saved_data.extracted_data:
                logger.info(f"提取了 {len([v for v in saved_data.extracted_data.values() if v])} 个字段")
        else:
            logger.error("抓取失败")
            sys.exit(1)
    finally:
        scraping_service.close()


if __name__ == '__main__':
    main()
