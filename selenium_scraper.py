"""
基于Selenium的网页抓取模块（支持JavaScript渲染和登录）
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
from typing import Optional, Dict, Callable
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SeleniumScraper:
    """基于Selenium的网页抓取器（支持登录和JavaScript渲染）"""
    
    def __init__(self, headless=True, wait_time=10, chrome_driver_path=None):
        """
        初始化Selenium抓取器
        
        Args:
            headless: 是否使用无头模式（不显示浏览器窗口）
            wait_time: 页面加载等待时间（秒）
            chrome_driver_path: ChromeDriver路径，如果为None则使用系统PATH中的
        """
        self.headless = headless
        self.wait_time = wait_time
        self.driver = None
        self.chrome_driver_path = chrome_driver_path
        self._init_driver()
    
    def _init_driver(self):
        """初始化Chrome驱动"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            if self.chrome_driver_path:
                service = Service(self.chrome_driver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                self.driver = webdriver.Chrome(options=chrome_options)
            
            self.driver.set_page_load_timeout(self.wait_time)
            logger.info("Chrome驱动初始化成功")
        except WebDriverException as e:
            logger.error(f"初始化Chrome驱动失败: {str(e)}")
            logger.error("请确保已安装Chrome浏览器和ChromeDriver")
            raise
    
    def login(self, login_url: str, login_func: Optional[Callable] = None, **kwargs):
        """
        执行登录操作
        
        Args:
            login_url: 登录页面URL
            login_func: 自定义登录函数，接收driver作为参数
            **kwargs: 登录相关参数（如username, password等）
        """
        try:
            logger.info(f"正在访问登录页面: {login_url}")
            self.driver.get(login_url)
            time.sleep(2)  # 等待页面加载
            
            if login_func:
                # 使用自定义登录函数
                logger.info("使用自定义登录函数")
                login_func(self.driver, **kwargs)
            else:
                # 默认登录流程（需要根据实际网站调整）
                logger.warning("未提供登录函数，请手动登录或提供login_func")
                logger.info("等待30秒，请手动完成登录...")
                time.sleep(30)
            
            logger.info("登录完成")
        except Exception as e:
            logger.error(f"登录失败: {str(e)}")
            raise
    
    def fetch_page(self, url: str, wait_for_element=None, wait_selector=None, 
                   wait_for_url_change=True, wait_timeout=None) -> Optional[Dict[str, str]]:
        """
        抓取网页内容（支持JavaScript渲染和页面跳转）
        
        Args:
            url: 要抓取的URL
            wait_for_element: 等待的元素选择器（CSS选择器或XPath）
            wait_selector: 等待的选择器类型（'css' 或 'xpath'），默认为CSS
            wait_for_url_change: 是否等待URL变化（处理跳转页面），默认True
            wait_timeout: 等待超时时间（秒），如果为None则使用self.wait_time
            
        Returns:
            包含title和content的字典，如果失败返回None
        """
        try:
            logger.info(f"正在抓取页面: {url}")
            original_url = url
            self.driver.get(url)
            
            # 等待URL变化（处理中间跳转页）
            if wait_for_url_change:
                timeout = wait_timeout or self.wait_time
                try:
                    # 等待URL稳定（不再变化）
                    max_wait = timeout
                    check_interval = 0.5
                    last_url = self.driver.current_url
                    stable_count = 0
                    required_stable = 2  # URL需要稳定2次检查才认为完成
                    
                    for _ in range(int(max_wait / check_interval)):
                        time.sleep(check_interval)
                        current_url = self.driver.current_url
                        
                        if current_url != last_url:
                            logger.info(f"检测到URL变化: {last_url} -> {current_url}")
                            stable_count = 0
                            last_url = current_url
                        else:
                            stable_count += 1
                            if stable_count >= required_stable:
                                logger.info(f"URL已稳定: {current_url}")
                                break
                    
                    final_url = self.driver.current_url
                    if final_url != original_url:
                        logger.info(f"页面发生跳转: {original_url} -> {final_url}")
                    
                except Exception as e:
                    logger.warning(f"等待URL变化时出错: {str(e)}")
            
            # 等待页面加载完成（通过document.readyState）
            try:
                WebDriverWait(self.driver, self.wait_time).until(
                    lambda driver: driver.execute_script('return document.readyState') == 'complete'
                )
                logger.info("页面加载完成")
            except TimeoutException:
                logger.warning("等待页面加载超时，继续处理")
            
            # 额外等待一小段时间，确保JavaScript执行完成
            time.sleep(1)
            
            # 等待特定元素（如果指定）
            if wait_for_element:
                try:
                    wait = WebDriverWait(self.driver, self.wait_time)
                    if wait_selector == 'xpath':
                        wait.until(EC.presence_of_element_located((By.XPATH, wait_for_element)))
                    else:
                        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_element)))
                    logger.info("目标元素已加载")
                except TimeoutException:
                    logger.warning("等待元素超时，继续处理页面内容")
            else:
                # 默认等待页面基本加载完成
                time.sleep(1)
            
            # 获取最终URL
            final_url = self.driver.current_url
            
            # 获取页面源码
            page_source = self.driver.page_source
            
            # 解析HTML
            soup = BeautifulSoup(page_source, 'lxml')
            
            # 提取标题
            title = self._extract_title(soup)
            
            # 提取正文内容
            content = self._extract_content(soup)
            
            logger.info(f"成功抓取页面: {final_url}, 标题: {title}")
            
            return {
                'url': final_url,  # 返回最终URL
                'original_url': original_url,  # 保留原始URL
                'title': title,
                'content': content,
                'redirected': final_url != original_url  # 是否发生跳转
            }
            
        except WebDriverException as e:
            logger.error(f"抓取页面失败: {url}, 错误: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"解析页面失败: {url}, 错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """提取页面标题"""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text(strip=True)
        
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text(strip=True)
        
        return "无标题"
    
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
    
    def get_cookies(self) -> dict:
        """获取当前浏览器的所有Cookie"""
        return self.driver.get_cookies()
    
    def set_cookies(self, cookies: list):
        """
        设置Cookie
        
        Args:
            cookies: Cookie列表，格式如 [{'name': 'xxx', 'value': 'yyy', 'domain': '...'}, ...]
        """
        for cookie in cookies:
            try:
                self.driver.add_cookie(cookie)
            except Exception as e:
                logger.warning(f"设置Cookie失败: {cookie.get('name', 'unknown')}, 错误: {str(e)}")
    
    def save_screenshot(self, filepath: str):
        """保存页面截图"""
        try:
            self.driver.save_screenshot(filepath)
            logger.info(f"截图已保存: {filepath}")
        except Exception as e:
            logger.error(f"保存截图失败: {str(e)}")
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            logger.info("浏览器已关闭")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
