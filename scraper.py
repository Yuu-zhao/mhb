"""
网页抓取模块
"""
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebScraper:
    """网页抓取器（支持Session和Cookie）"""
    
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
    
    def _set_cookies(self, cookies):
        """设置Cookie"""
        if isinstance(cookies, str):
            # 如果是字符串格式的Cookie，需要解析
            cookie_dict = {}
            for item in cookies.split(';'):
                if '=' in item:
                    key, value = item.strip().split('=', 1)
                    cookie_dict[key] = value
            cookies = cookie_dict
        
        if self.use_session and self.session:
            self.session.cookies.update(cookies)
        else:
            self.cookies = cookies
    
    def set_cookies(self, cookies):
        """
        设置Cookie（可在运行时调用）
        
        Args:
            cookies: Cookie字典或Cookie字符串
        """
        self._set_cookies(cookies)
    
    def set_referer(self, referer):
        """
        设置Referer头
        
        Args:
            referer: Referer URL
        """
        if self.use_session and self.session:
            self.session.headers['Referer'] = referer
        else:
            self.headers['Referer'] = referer
    
    def fetch_page(self, url: str, cookies=None, allow_redirects=True) -> Optional[Dict[str, str]]:
        """
        抓取网页内容（支持处理重定向和跳转）
        
        Args:
            url: 要抓取的URL
            cookies: 可选的Cookie（会临时覆盖已有的Cookie）
            allow_redirects: 是否允许重定向（默认True）
            
        Returns:
            包含title和content的字典，如果失败返回None
        """
        try:
            logger.info(f"正在抓取页面: {url}")
            
            # 设置Referer（如果URL是163.com相关）
            if '163.com' in url:
                self.set_referer('https://xyq.cbg.163.com/')
            
            # 使用Session或普通requests
            if self.use_session and self.session:
                # 如果提供了临时cookies，使用它们
                if cookies:
                    temp_cookies = self.session.cookies.copy()
                    if isinstance(cookies, str):
                        for item in cookies.split(';'):
                            if '=' in item:
                                key, value = item.strip().split('=', 1)
                                temp_cookies[key] = value
                    else:
                        temp_cookies.update(cookies)
                    response = self.session.get(
                        url, 
                        cookies=temp_cookies, 
                        timeout=self.timeout,
                        allow_redirects=allow_redirects
                    )
                else:
                    response = self.session.get(
                        url, 
                        timeout=self.timeout,
                        allow_redirects=allow_redirects
                    )
            else:
                request_cookies = cookies or getattr(self, 'cookies', None)
                response = requests.get(
                    url, 
                    headers=self.headers, 
                    cookies=request_cookies, 
                    timeout=self.timeout,
                    allow_redirects=allow_redirects
                )
            
            # 记录最终URL（可能经过重定向）
            final_url = response.url
            if final_url != url:
                logger.info(f"页面发生重定向: {url} -> {final_url}")
            
            response.raise_for_status()
            
            # 尝试多种编码方式
            if response.encoding is None or response.encoding == 'ISO-8859-1':
                response.encoding = response.apparent_encoding or 'utf-8'
            
            # 检查是否需要登录（通过页面内容判断）
            if self._check_login_required(response.text):
                logger.warning("页面可能需要登录，返回的内容可能不完整")
                logger.info("提示：可以使用SeleniumScraper或手动设置Cookie")
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'lxml')
            
            # 提取标题
            title = self._extract_title(soup)
            
            # 提取正文内容
            content = self._extract_content(soup)
            
            logger.info(f"成功抓取页面: {final_url}, 标题: {title}")
            
            return {
                'url': final_url,  # 返回最终URL
                'original_url': url,  # 保留原始URL
                'title': title,
                'content': content,
                'status_code': response.status_code,
                'cookies': dict(response.cookies) if hasattr(response, 'cookies') else None,
                'redirected': final_url != url  # 是否发生重定向
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {url}, 错误: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"响应状态码: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"解析页面失败: {url}, 错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _check_login_required(self, html_content: str) -> bool:
        """
        检查页面是否需要登录
        
        Args:
            html_content: HTML内容
            
        Returns:
            如果可能需要登录返回True
        """
        login_indicators = [
            '登录', '请登录', '需要登录', 'login', 'sign in',
            '安全提示', '安全验证', '验证码', 'captcha'
        ]
        content_lower = html_content.lower()
        return any(indicator in content_lower for indicator in login_indicators)
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """
        提取页面标题
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            页面标题
        """
        # 优先尝试title标签
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text(strip=True)
        
        # 尝试h1标签
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text(strip=True)
        
        return "无标题"
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """
        提取页面正文内容
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            页面正文内容
        """
        # 移除script和style标签
        for script in soup(["script", "style"]):
            script.decompose()
        
        # 尝试提取main、article或body中的文本
        content_selectors = ['main', 'article', '[role="main"]', 'body']
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(separator='\n', strip=True)
                if text and len(text) > 50:  # 确保有足够的内容
                    return text
        
        # 如果都没找到，返回body的所有文本
        body = soup.find('body')
        if body:
            return body.get_text(separator='\n', strip=True)
        
        return ""
