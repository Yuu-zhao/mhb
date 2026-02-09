"""
基于requests的网页抓取器
"""
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any
import logging
from .base import BaseScraper

logger = logging.getLogger(__name__)


class RequestsScraper(BaseScraper):
    """基于requests的网页抓取器（支持Session和Cookie）"""
    
    def __init__(self, timeout=10, headers=None, cookies=None, use_session=True):
        """
        初始化抓取器
        
        Args:
            timeout: 请求超时时间（秒）
            headers: 请求头，如果为None则使用默认头
            cookies: Cookie字典或Cookie字符串
            use_session: 是否使用Session保持会话
        """
        self.timeout = timeout
        self.use_session = use_session
        
        # 默认请求头（模拟真实浏览器）
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        # 初始化Session或普通requests
        if use_session:
            self.session = requests.Session()
            self.session.headers.update(self.headers)
            if cookies:
                self._set_cookies(cookies)
        else:
            self.session = None
            self.cookies = cookies
    
    def _set_cookies(self, cookies):
        """设置Cookie"""
        if isinstance(cookies, str):
            # Cookie字符串格式：name1=value1; name2=value2
            cookie_dict = {}
            for item in cookies.split(';'):
                if '=' in item:
                    key, value = item.strip().split('=', 1)
                    cookie_dict[key] = value
            self.session.cookies.update(cookie_dict)
        elif isinstance(cookies, dict):
            self.session.cookies.update(cookies)
    
    def set_cookies(self, cookies):
        """设置Cookie（公开方法）"""
        if self.use_session and self.session:
            self._set_cookies(cookies)
        else:
            self.cookies = cookies
    
    def fetch_page(self, url: str, allow_redirects=True, **kwargs) -> Optional[Dict[str, Any]]:
        """
        抓取网页内容
        
        Args:
            url: 要抓取的URL
            allow_redirects: 是否允许重定向
            **kwargs: 其他参数
            
        Returns:
            包含url、title、content等字段的字典，失败返回None
        """
        try:
            logger.info(f"正在抓取页面: {url}")
            
            if self.use_session and self.session:
                response = self.session.get(
                    url,
                    timeout=self.timeout,
                    allow_redirects=allow_redirects,
                    **kwargs
                )
            else:
                response = requests.get(
                    url,
                    headers=self.headers,
                    cookies=self.cookies,
                    timeout=self.timeout,
                    allow_redirects=allow_redirects,
                    **kwargs
                )
            
            response.raise_for_status()
            response.encoding = response.apparent_encoding or 'utf-8'
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'lxml')
            title = soup.title.string if soup.title else "无标题"
            
            # 提取正文内容
            content = self._extract_content(soup)
            
            logger.info(f"成功抓取页面: {response.url}, 标题: {title}")
            
            return {
                'url': response.url,
                'original_url': url,
                'title': title,
                'content': content,
                'redirected': response.url != url
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"抓取页面失败: {url}, 错误: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"解析页面失败: {url}, 错误: {str(e)}")
            return None
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """提取页面正文内容"""
        # 移除script和style标签
        for script in soup(["script", "style"]):
            script.decompose()
        
        # 尝试提取main、article或body中的文本
        content_selectors = ['main', 'article', '[role="main"]', 'body']
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(separator='\n', strip=True)
                if text and len(text) > 50:
                    return text
        
        body = soup.find('body')
        if body:
            return body.get_text(separator='\n', strip=True)
        
        return ""
    
    def close(self):
        """关闭Session（如果有）"""
        if self.use_session and self.session:
            self.session.close()
