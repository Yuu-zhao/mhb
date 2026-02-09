"""
基于Playwright的网页抓取器
"""
from .base import BaseScraper
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup
from typing import Optional, Dict
import logging
import time
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlaywrightScraper(BaseScraper):
    """基于Playwright的网页抓取器（支持保存和加载登录态）"""
    
    def __init__(self, headless=True, storage_state_path=None, timeout=30000):
        """
        初始化Playwright抓取器
        
        Args:
            headless: 是否使用无头模式（不显示浏览器窗口）
            storage_state_path: 登录态文件路径（.json），如果提供则自动加载
            timeout: 页面加载超时时间（毫秒），默认30秒
        """
        self.headless = headless
        self.storage_state_path = storage_state_path
        self.timeout = timeout
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
    
    def __enter__(self):
        """上下文管理器入口"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
    
    def start(self):
        """启动浏览器"""
        try:
            self.playwright = sync_playwright().start()
            browser_type = self.playwright.chromium
            
            # 启动浏览器
            try:
                self.browser = browser_type.launch(
                    headless=self.headless,
                    args=['--disable-blink-features=AutomationControlled']
                )
            except Exception as e:
                error_msg = str(e)
                if "Executable doesn't exist" in error_msg or "playwright install" in error_msg.lower():
                    logger.error("=" * 60)
                    logger.error("Playwright浏览器未安装！")
                    logger.error("=" * 60)
                    logger.error("请运行以下命令安装浏览器：")
                    logger.error("  playwright install")
                    logger.error("或者安装Chromium：")
                    logger.error("  playwright install chromium")
                    logger.error("=" * 60)
                    raise Exception("Playwright浏览器未安装，请运行 'playwright install' 安装浏览器")
                else:
                    raise
            
            # 创建浏览器上下文（如果提供了登录态文件，则加载）
            context_options = {
                'viewport': {'width': 1920, 'height': 1080},
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            if self.storage_state_path and os.path.exists(self.storage_state_path):
                # 验证登录态文件是否有效
                try:
                    import json
                    with open(self.storage_state_path, 'r', encoding='utf-8') as f:
                        storage_data = json.load(f)
                    # 检查文件格式
                    if isinstance(storage_data, dict) and ('cookies' in storage_data or 'origins' in storage_data):
                        logger.info(f"加载登录态: {self.storage_state_path}")
                        context_options['storage_state'] = self.storage_state_path
                    else:
                        logger.warning(f"登录态文件格式无效: {self.storage_state_path}，将不使用登录态")
                except (json.JSONDecodeError, Exception) as e:
                    logger.warning(f"登录态文件加载失败: {self.storage_state_path}, 错误: {str(e)}，将不使用登录态")
            
            self.context = self.browser.new_context(**context_options)
            self.page = self.context.new_page()
            
            logger.info("Playwright浏览器启动成功")
        except Exception as e:
            logger.error(f"启动浏览器失败: {str(e)}")
            raise
    
    def close(self):
        """关闭浏览器（安全版本，避免段错误）"""
        # 使用更安全的方式关闭，避免段错误
        # 使用延迟关闭，避免资源竞争
        import time
        import gc
        
        # 分步关闭，每步都有异常保护
        try:
            if self.page:
                try:
                    self.page.close()
                except:
                    pass
                self.page = None
                time.sleep(0.1)
        except:
            pass
        
        try:
            if self.context:
                try:
                    self.context.close()
                except:
                    pass
                self.context = None
                time.sleep(0.15)
        except:
            pass
        
        try:
            if self.browser:
                try:
                    self.browser.close()
                except:
                    pass
                self.browser = None
                time.sleep(0.3)  # 给浏览器进程更多时间完全关闭
        except:
            pass
        
        try:
            if self.playwright:
                try:
                    time.sleep(0.2)
                    self.playwright.stop()
                except:
                    pass
                self.playwright = None
        except:
            pass
        
        # 强制垃圾回收，确保资源释放
        gc.collect()
        time.sleep(0.1)
        
        logger.info("浏览器已关闭")
    
    def login_and_save(self, login_url: str, storage_state_path: str = "login_state.json", wait_seconds=30):
        """
        人工登录并保存登录态
        
        Args:
            login_url: 登录页面URL
            storage_state_path: 保存登录态的文件路径
            wait_seconds: 等待登录的时间（秒）
        """
        if not self.page:
            self.start()
        
        try:
            logger.info(f"正在访问登录页面: {login_url}")
            self.page.goto(login_url, wait_until='networkidle', timeout=self.timeout)
            
            logger.info(f"请在浏览器中完成登录，等待 {wait_seconds} 秒...")
            logger.info("提示：如果已登录，可以直接按回车继续")
            
            # 等待用户完成登录
            input("登录完成后，按回车继续...")
            
            # 额外等待，确保登录完成
            time.sleep(2)
            
            # 保存登录态（包含Cookie、localStorage、sessionStorage）
            self.context.storage_state(path=storage_state_path)
            logger.info(f"✅ 登录态已保存到: {storage_state_path}")
            logger.info("💡 以后可以使用这个文件自动登录")
            
            return True
        except Exception as e:
            logger.error(f"登录并保存失败: {str(e)}")
            return False
    
    def fetch_page(self, url: str, wait_for_selector=None, wait_until='networkidle', 
                   wait_for_url_change=True) -> Optional[Dict[str, str]]:
        """
        抓取网页内容（支持JavaScript渲染和页面跳转）
        
        Args:
            url: 要抓取的URL
            wait_for_selector: 等待的元素选择器（CSS选择器）
            wait_until: 等待条件，可选值：'load', 'domcontentloaded', 'networkidle', 'commit'
            wait_for_url_change: 是否等待URL变化（处理跳转页面）
            
        Returns:
            包含title和content的字典，如果失败返回None
        """
        if not self.page:
            self.start()
        
        try:
            original_url = url
            logger.info(f"正在抓取页面: {url}")
            
            # 访问页面
            self.page.goto(url, wait_until=wait_until, timeout=self.timeout)
            
            # 等待URL变化（处理中间跳转页）
            if wait_for_url_change:
                try:
                    # 等待URL稳定
                    max_wait = 10  # 最多等待10秒
                    check_interval = 0.5
                    last_url = self.page.url
                    stable_count = 0
                    required_stable = 2
                    
                    for _ in range(int(max_wait / check_interval)):
                        time.sleep(check_interval)
                        current_url = self.page.url
                        
                        if current_url != last_url:
                            logger.info(f"检测到URL变化: {last_url} -> {current_url}")
                            stable_count = 0
                            last_url = current_url
                        else:
                            stable_count += 1
                            if stable_count >= required_stable:
                                logger.info(f"URL已稳定: {current_url}")
                                break
                except Exception as e:
                    logger.warning(f"等待URL变化时出错: {str(e)}")
            
            # 等待特定元素（如果指定）
            if wait_for_selector:
                try:
                    self.page.wait_for_selector(wait_for_selector, timeout=self.timeout)
                    logger.info(f"目标元素已加载: {wait_for_selector}")
                except PlaywrightTimeoutError:
                    logger.warning(f"等待元素超时: {wait_for_selector}")
            
            # 等待页面完全加载
            try:
                self.page.wait_for_load_state('networkidle', timeout=self.timeout)
            except PlaywrightTimeoutError:
                logger.warning("等待网络空闲超时，继续处理")
            
            # 额外等待，确保JavaScript执行完成
            time.sleep(1)
            
            # 获取最终URL
            final_url = self.page.url
            if final_url != original_url:
                logger.info(f"页面发生跳转: {original_url} -> {final_url}")
            
            # 获取页面内容（完整HTML，用于数据提取）
            page_content = self.page.content()
            
            # 解析HTML
            soup = BeautifulSoup(page_content, 'lxml')
            
            # 提取标题
            title = self._extract_title(soup)
            
            # 对于需要数据提取的页面（如藏宝阁），返回完整HTML
            # 对于其他页面，可以返回提取的文本内容
            if 'cbg.163.com' in url or 'xyq.cbg.163.com' in url:
                # 藏宝阁页面需要完整HTML结构进行数据提取
                content = page_content
            else:
                # 其他页面返回提取的文本内容
                content = self._extract_content(soup)
            
            logger.info(f"成功抓取页面: {final_url}, 标题: {title}")
            
            return {
                'url': final_url,
                'original_url': original_url,
                'title': title,
                'content': content,
                'redirected': final_url != original_url
            }
            
        except PlaywrightTimeoutError as e:
            logger.error(f"页面加载超时: {url}, 错误: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"抓取页面失败: {url}, 错误: {str(e)}")
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
    
    def save_screenshot(self, filepath: str):
        """保存页面截图"""
        if not self.page:
            logger.warning("页面未初始化，无法截图")
            return
        
        try:
            self.page.screenshot(path=filepath, full_page=True)
            logger.info(f"截图已保存: {filepath}")
        except Exception as e:
            logger.error(f"保存截图失败: {str(e)}")
    
    def get_cookies(self) -> list:
        """获取当前页面的所有Cookie"""
        if not self.context:
            return []
        
        try:
            return self.context.cookies()
        except Exception as e:
            logger.error(f"获取Cookie失败: {str(e)}")
            return []


def login_and_save_state(login_url: str, storage_state_path: str = "login_state.json"):
    """
    便捷函数：登录并保存登录态
    
    Args:
        login_url: 登录页面URL
        storage_state_path: 保存登录态的文件路径
    """
    scraper = PlaywrightScraper(headless=False)  # 显示浏览器窗口
    try:
        scraper.start()
        scraper.login_and_save(login_url, storage_state_path)
    finally:
        scraper.close()


def fetch_with_saved_state(url: str, storage_state_path: str = "login_state.json", 
                           headless: bool = True) -> Optional[Dict[str, str]]:
    """
    便捷函数：使用保存的登录态抓取页面
    
    Args:
        url: 要抓取的URL
        storage_state_path: 登录态文件路径
        headless: 是否使用无头模式
    """
    scraper = PlaywrightScraper(headless=headless, storage_state_path=storage_state_path)
    try:
        scraper.start()
        return scraper.fetch_page(url)
    finally:
        scraper.close()
