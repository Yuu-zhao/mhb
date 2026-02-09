"""
浏览器管理器 - 维护长期运行的浏览器实例池
支持浏览器实例复用，避免频繁启动/关闭浏览器
"""
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from typing import Optional, Dict
import logging
import time
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BrowserManager:
    """浏览器管理器 - 单例模式，维护浏览器实例池"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(BrowserManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.playwright = None
        self.browser_pool: Dict[str, Browser] = {}  # key: storage_state_path or 'default', value: Browser
        self.context_pool: Dict[str, BrowserContext] = {}  # key: storage_state_path or 'default', value: Context
        self.page_pool: Dict[str, Page] = {}  # key: storage_state_path or 'default', value: Page
        self.last_used: Dict[str, float] = {}  # 记录最后使用时间
        self.idle_timeout = 300  # 5分钟无使用则关闭浏览器
        self._lock = threading.Lock()
        
        logger.info("浏览器管理器已初始化")
    
    def get_playwright(self):
        """获取或创建Playwright实例"""
        if self.playwright is None:
            try:
                logger.info("正在启动Playwright...")
                self.playwright = sync_playwright().start()
                logger.info("Playwright实例已创建")
            except Exception as e:
                logger.error(f"启动Playwright失败: {str(e)}")
                raise
        return self.playwright
    
    def get_browser(self, storage_state_path: Optional[str] = None, headless: bool = True) -> Browser:
        """
        获取或创建浏览器实例
        
        Args:
            storage_state_path: 登录态文件路径，用于区分不同的登录状态
            headless: 是否使用无头模式
            
        Returns:
            Browser实例
        """
        key = storage_state_path or 'default'
        
        # 先检查是否已有浏览器实例
        browser = None
        with self._lock:
            if key in self.browser_pool:
                browser = self.browser_pool[key]
        
        # 在锁外检查浏览器是否仍然有效（避免阻塞）
        if browser:
            try:
                if browser.is_connected():
                    with self._lock:
                        self.last_used[key] = time.time()
                    logger.info(f"复用浏览器实例: {key}")
                    return browser
                else:
                    # 浏览器已断开，清理并重新创建
                    logger.warning(f"浏览器实例已断开，清理: {key}")
                    with self._lock:
                        self._cleanup_key(key)
            except Exception as e:
                logger.warning(f"检查浏览器连接状态失败: {str(e)}")
                with self._lock:
                    self._cleanup_key(key)
        
        # 创建新的浏览器实例（在锁外创建，避免阻塞）
        logger.info(f"创建新的浏览器实例: {key} (headless={headless})")
        try:
            playwright = self.get_playwright()
            logger.info(f"正在启动Chromium浏览器...")
            browser = playwright.chromium.launch(
                headless=headless,
                args=['--disable-blink-features=AutomationControlled'],
                timeout=30000  # 30秒超时
            )
            logger.info(f"浏览器实例创建成功: {key}")
            
            # 创建成功后，在锁内添加到池中
            with self._lock:
                self.browser_pool[key] = browser
                self.last_used[key] = time.time()
            
            return browser
        except Exception as e:
            logger.error(f"创建浏览器实例失败: {key}, 错误: {str(e)}")
            raise
    
    def get_context(self, storage_state_path: Optional[str] = None, headless: bool = True) -> BrowserContext:
        """
        获取或创建浏览器上下文
        
        Args:
            storage_state_path: 登录态文件路径
            headless: 是否使用无头模式
            
        Returns:
            BrowserContext实例
        """
        key = storage_state_path or 'default'
        
        # 先检查是否已有上下文
        context = None
        with self._lock:
            if key in self.context_pool:
                context = self.context_pool[key]
        
        # 在锁外检查上下文是否仍然有效
        if context:
            try:
                if context.browser.is_connected():
                    with self._lock:
                        self.last_used[key] = time.time()
                    logger.info(f"复用浏览器上下文: {key}")
                    return context
                else:
                    logger.warning(f"浏览器已断开，清理上下文: {key}")
                    with self._lock:
                        self._cleanup_key(key)
            except Exception as e:
                logger.warning(f"检查上下文状态失败: {str(e)}")
                with self._lock:
                    self._cleanup_key(key)
        
        # 创建新的上下文（在锁外创建，避免阻塞）
        logger.info(f"创建新的浏览器上下文: {key}")
        try:
            browser = self.get_browser(storage_state_path, headless)
            
            context_options = {}
            if storage_state_path:
                import json
                import os
                if os.path.exists(storage_state_path):
                    try:
                        logger.info(f"正在加载登录态文件: {storage_state_path}")
                        with open(storage_state_path, 'r', encoding='utf-8') as f:
                            storage_data = json.load(f)
                        if isinstance(storage_data, dict) and ('cookies' in storage_data or 'origins' in storage_data):
                            context_options['storage_state'] = storage_state_path
                            logger.info(f"登录态文件加载成功: {storage_state_path}")
                        else:
                            logger.warning(f"登录态文件格式无效: {storage_state_path}")
                    except Exception as e:
                        logger.warning(f"加载登录态失败: {str(e)}")
            
            logger.info(f"正在创建浏览器上下文...")
            context = browser.new_context(**context_options)
            logger.info(f"浏览器上下文创建成功: {key}")
            
            # 创建成功后，在锁内添加到池中
            with self._lock:
                self.context_pool[key] = context
                self.last_used[key] = time.time()
            
            return context
        except Exception as e:
            logger.error(f"创建浏览器上下文失败: {key}, 错误: {str(e)}")
            raise
    
    def get_page(self, storage_state_path: Optional[str] = None, headless: bool = True) -> Page:
        """
        获取或创建页面实例
        
        Args:
            storage_state_path: 登录态文件路径
            headless: 是否使用无头模式
            
        Returns:
            Page实例
        """
        key = storage_state_path or 'default'
        
        # 先检查是否已有页面
        page = None
        with self._lock:
            if key in self.page_pool:
                page = self.page_pool[key]
        
        # 在锁外检查页面是否仍然有效
        if page:
            try:
                if not page.is_closed() and page.context.browser.is_connected():
                    with self._lock:
                        self.last_used[key] = time.time()
                    logger.info(f"复用页面实例: {key}")
                    return page
                else:
                    logger.warning(f"页面已关闭或浏览器已断开，清理: {key}")
                    with self._lock:
                        self._cleanup_key(key)
            except Exception as e:
                logger.warning(f"检查页面状态失败: {str(e)}")
                with self._lock:
                    self._cleanup_key(key)
        
        # 创建新的页面（在锁外创建，避免阻塞）
        logger.info(f"创建新的页面实例: {key}")
        try:
            context = self.get_context(storage_state_path, headless)
            logger.info(f"正在创建新页面...")
            page = context.new_page()
            logger.info(f"页面实例创建成功: {key}")
            
            # 创建成功后，在锁内添加到池中
            with self._lock:
                self.page_pool[key] = page
                self.last_used[key] = time.time()
            
            return page
        except Exception as e:
            logger.error(f"创建页面实例失败: {key}, 错误: {str(e)}")
            raise
    
    def _cleanup_key(self, key: str):
        """清理指定key的所有资源"""
        try:
            if key in self.page_pool:
                try:
                    self.page_pool[key].close()
                except:
                    pass
                del self.page_pool[key]
            
            if key in self.context_pool:
                try:
                    self.context_pool[key].close()
                except:
                    pass
                del self.context_pool[key]
            
            if key in self.browser_pool:
                try:
                    self.browser_pool[key].close()
                except:
                    pass
                del self.browser_pool[key]
            
            if key in self.last_used:
                del self.last_used[key]
            
            logger.info(f"已清理资源: {key}")
        except Exception as e:
            logger.warning(f"清理资源时出错: {str(e)}")
    
    def cleanup_idle(self):
        """清理长时间未使用的浏览器实例"""
        current_time = time.time()
        keys_to_cleanup = []
        
        with self._lock:
            for key, last_time in self.last_used.items():
                if current_time - last_time > self.idle_timeout:
                    keys_to_cleanup.append(key)
            
            for key in keys_to_cleanup:
                logger.info(f"清理空闲浏览器实例: {key} (空闲 {int(current_time - self.last_used[key])} 秒)")
                self._cleanup_key(key)
    
    def close_all(self):
        """关闭所有浏览器实例"""
        with self._lock:
            keys = list(self.browser_pool.keys())
            for key in keys:
                self._cleanup_key(key)
            
            if self.playwright:
                try:
                    self.playwright.stop()
                except:
                    pass
                self.playwright = None
            
            logger.info("所有浏览器实例已关闭")
    
    def __del__(self):
        """析构函数，确保资源清理"""
        try:
            self.close_all()
        except:
            pass
