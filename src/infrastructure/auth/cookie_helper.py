"""
Cookie管理工具
用于从浏览器导出Cookie或手动管理Cookie
"""
import json
import logging
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CookieHelper:
    """Cookie管理助手"""
    
    @staticmethod
    def parse_cookie_string(cookie_string: str) -> Dict[str, str]:
        """
        解析Cookie字符串（从浏览器开发者工具复制）
        
        Args:
            cookie_string: Cookie字符串，格式如 "name1=value1; name2=value2"
            
        Returns:
            Cookie字典
        """
        cookies = {}
        for item in cookie_string.split(';'):
            item = item.strip()
            if '=' in item:
                key, value = item.split('=', 1)
                cookies[key.strip()] = value.strip()
        return cookies
    
    @staticmethod
    def cookie_dict_to_string(cookie_dict: Dict[str, str]) -> str:
        """
        将Cookie字典转换为字符串
        
        Args:
            cookie_dict: Cookie字典
            
        Returns:
            Cookie字符串
        """
        return '; '.join([f"{k}={v}" for k, v in cookie_dict.items()])
    
    @staticmethod
    def save_cookies_to_file(cookies: Dict[str, str], filepath: str):
        """
        保存Cookie到文件
        
        Args:
            cookies: Cookie字典
            filepath: 保存路径
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, indent=2, ensure_ascii=False)
            logger.info(f"Cookie已保存到: {filepath}")
        except Exception as e:
            logger.error(f"保存Cookie失败: {str(e)}")
            raise
    
    @staticmethod
    def load_cookies_from_file(filepath: str) -> Dict[str, str]:
        """
        从文件加载Cookie
        
        Args:
            filepath: Cookie文件路径
            
        Returns:
            Cookie字典
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            logger.info(f"Cookie已从文件加载: {filepath}")
            return cookies
        except Exception as e:
            logger.error(f"加载Cookie失败: {str(e)}")
            raise
    
    @staticmethod
    def selenium_cookies_to_dict(selenium_cookies: List[Dict]) -> Dict[str, str]:
        """
        将Selenium格式的Cookie列表转换为字典
        
        Args:
            selenium_cookies: Selenium Cookie列表
            
        Returns:
            Cookie字典
        """
        cookies = {}
        for cookie in selenium_cookies:
            cookies[cookie['name']] = cookie['value']
        return cookies
    
    @staticmethod
    def dict_to_selenium_cookies(cookies: Dict[str, str], domain: str) -> List[Dict]:
        """
        将Cookie字典转换为Selenium格式
        
        Args:
            cookies: Cookie字典
            domain: Cookie域名
            
        Returns:
            Selenium Cookie列表
        """
        selenium_cookies = []
        for name, value in cookies.items():
            selenium_cookies.append({
                'name': name,
                'value': value,
                'domain': domain
            })
        return selenium_cookies


def export_cookies_from_browser():
    """
    从浏览器导出Cookie的说明
    
    方法1：Chrome浏览器
    1. 打开目标网站并登录
    2. 按F12打开开发者工具
    3. 切换到Application/应用程序标签
    4. 左侧选择Cookies -> 选择网站域名
    5. 复制所有Cookie的name和value
    
    方法2：使用浏览器扩展
    可以使用EditThisCookie等扩展导出Cookie
    
    方法3：使用Selenium手动登录后导出
    使用SeleniumScraper登录后，调用get_cookies()方法
    """
    print(export_cookies_from_browser.__doc__)
