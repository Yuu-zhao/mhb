"""
抓取器模块
提供统一的抓取接口和多种实现
"""

from .base import BaseScraper
from .requests_scraper import RequestsScraper
from .selenium_scraper import SeleniumScraper
from .playwright_scraper import PlaywrightScraper

__all__ = [
    'BaseScraper',
    'RequestsScraper',
    'SeleniumScraper',
    'PlaywrightScraper',
]
