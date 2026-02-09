"""
登录态管理器
中心化管理登录态的检查、获取、保存和刷新
"""
import os
import json
import logging
from typing import Optional, Dict
from urllib.parse import urlparse
from playwright_scraper import PlaywrightScraper
from cookie_helper import CookieHelper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LoginStateManager:
    """登录态管理器 - 中心化管理所有登录相关操作"""
    
    def __init__(self, base_dir: str = "."):
        """
        初始化登录态管理器
        
        Args:
            base_dir: 存储登录态文件的目录
        """
        self.base_dir = base_dir
        if not os.path.exists(base_dir):
            os.makedirs(base_dir, exist_ok=True)
    
    def _get_storage_state_path(self, domain: str) -> str:
        """获取登录态文件路径"""
        domain_key = domain.replace('.', '_').replace('www_', '')
        return os.path.join(self.base_dir, f"login_state_{domain_key}.json")
    
    def has_valid_state(self, domain: str) -> bool:
        """
        检查是否有有效的登录态
        
        Args:
            domain: 域名（如 'xyq.cbg.163.com'）
            
        Returns:
            如果有有效的登录态返回True，否则返回False
        """
        storage_state_path = self._get_storage_state_path(domain)
        
        if not os.path.exists(storage_state_path):
            logger.debug(f"登录态文件不存在: {storage_state_path}")
            return False
        
        try:
            with open(storage_state_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    logger.debug(f"登录态文件为空: {storage_state_path}")
                    return False
                
                storage_data = json.loads(content)
                if not isinstance(storage_data, dict):
                    logger.debug(f"登录态文件格式无效: {storage_state_path}")
                    return False
                
                # 检查是否有cookies或origins
                if 'cookies' in storage_data or 'origins' in storage_data:
                    logger.info(f"找到有效的登录态文件: {storage_state_path}")
                    return True
                else:
                    logger.debug(f"登录态文件缺少必要字段: {storage_state_path}")
                    return False
        except (json.JSONDecodeError, ValueError, Exception) as e:
            logger.warning(f"读取登录态文件失败: {storage_state_path}, 错误: {str(e)}")
            return False
    
    def get_state(self, domain: str) -> Optional[str]:
        """
        获取登录态文件路径
        
        Args:
            domain: 域名
            
        Returns:
            登录态文件路径，如果不存在返回None
        """
        if self.has_valid_state(domain):
            return self._get_storage_state_path(domain)
        return None
    
    def ensure_login(self, domain: str, url: str) -> str:
        """
        确保已登录（如果未登录则进行登录）
        
        Args:
            domain: 域名
            url: 目标URL（用于登录后重定向）
            
        Returns:
            登录态文件路径
        """
        # 先检查是否已有有效的登录态
        existing_state = self.get_state(domain)
        if existing_state:
            logger.info(f"已有有效的登录态: {existing_state}")
            return existing_state
        
        # 如果没有，进行登录
        logger.info(f"未找到有效登录态，开始登录流程...")
        return self._perform_login(domain, url)
    
    def _perform_login(self, domain: str, url: str) -> str:
        """
        执行登录操作
        
        Args:
            domain: 域名
            url: 目标URL
            
        Returns:
            登录态文件路径
        """
        storage_state_path = self._get_storage_state_path(domain)
        
        logger.info("=" * 60)
        logger.info("准备启动浏览器进行登录...")
        logger.info(f"目标域名: {domain}")
        logger.info(f"目标URL: {url}")
        logger.info("=" * 60)
        
        scraper = PlaywrightScraper(headless=False)  # 显示浏览器
        try:
            scraper.start()
            logger.info("✅ 浏览器启动成功")
            
            # 确定登录URL
            parsed = urlparse(url)
            if 'show_login' in url or 'login' in url.lower():
                login_url = url
                logger.info(f"使用原始URL作为登录页面: {login_url}")
            else:
                login_url = f"{parsed.scheme}://{domain}"
                logger.info(f"使用域名首页作为登录页面: {login_url}")
            
            # 访问登录页面
            logger.info(f"正在导航到登录页面: {login_url}")
            scraper.page.goto(login_url, wait_until='networkidle', timeout=30000)
            logger.info(f"✅ 页面加载完成，当前URL: {scraper.page.url}")
            
            # 等待用户登录
            logger.info("=" * 60)
            logger.info("⚠️  请在弹出的浏览器窗口中完成登录！")
            logger.info("系统会自动检测登录状态，登录完成后会自动保存")
            logger.info("=" * 60)
            
            import time
            max_wait = 300  # 最多等待5分钟
            check_interval = 2  # 每2秒检查一次
            initial_url = scraper.page.url
            initial_cookies_count = len(scraper.get_cookies())
            logger.info(f"初始状态 - URL: {initial_url}, Cookie数量: {initial_cookies_count}")
            
            for i in range(int(max_wait / check_interval)):
                time.sleep(check_interval)
                
                try:
                    current_url = scraper.page.url
                    current_cookies = scraper.get_cookies()
                    current_cookies_count = len(current_cookies)
                except Exception as e:
                    logger.warning(f"获取页面状态时出错: {str(e)}")
                    continue
                
                # 检测登录完成的标志
                url_changed = current_url != initial_url
                cookies_increased = current_cookies_count > initial_cookies_count
                
                has_auth_cookies = any(
                    'session' in c['name'].lower() or 
                    'token' in c['name'].lower() or 
                    'auth' in c['name'].lower() or
                    'login' in c['name'].lower() or
                    'sid' in c['name'].lower() or
                    'sess' in c['name'].lower()
                    for c in current_cookies
                )
                
                is_not_login_page = 'show_login' not in current_url.lower() and 'login' not in current_url.lower()
                
                if i % 5 == 0:  # 每10秒记录一次
                    logger.info(f"等待登录中... ({i * check_interval}秒) | URL变化: {url_changed} | Cookie增加: {cookies_increased} | 有认证Cookie: {has_auth_cookies} | 不在登录页: {is_not_login_page}")
                
                if ((url_changed or cookies_increased or has_auth_cookies) and i > 5) or (is_not_login_page and i > 10):
                    time.sleep(3)
                    logger.info("✅ 检测到登录完成，正在保存登录态...")
                    break
            
            # 保存登录态
            scraper.context.storage_state(path=storage_state_path)
            logger.info(f"✅ 登录态已保存: {storage_state_path}")
            
            return storage_state_path
            
        finally:
            try:
                scraper.close()
                import time
                time.sleep(0.3)
            except Exception as e:
                logger.warning(f"关闭浏览器时出错: {str(e)}")
    
    def refresh_state(self, domain: str, url: str) -> str:
        """
        刷新登录态（重新登录）
        
        Args:
            domain: 域名
            url: 目标URL
            
        Returns:
            新的登录态文件路径
        """
        logger.info(f"刷新登录态: {domain}")
        # 删除旧的登录态文件
        old_state_path = self._get_storage_state_path(domain)
        if os.path.exists(old_state_path):
            try:
                os.remove(old_state_path)
                logger.info(f"已删除旧登录态文件: {old_state_path}")
            except Exception as e:
                logger.warning(f"删除旧登录态文件失败: {str(e)}")
        
        # 重新登录
        return self._perform_login(domain, url)
    
    def get_domain_from_url(self, url: str) -> str:
        """
        从URL中提取域名
        
        Args:
            url: 完整URL
            
        Returns:
            域名（去除www前缀）
        """
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        return domain
