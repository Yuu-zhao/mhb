"""
应用配置
"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

# 数据库配置
DATABASE_PATH = os.getenv('DATABASE_PATH', str(BASE_DIR / 'page_data.db'))

# 浏览器配置
BROWSER_HEADLESS = os.getenv('BROWSER_HEADLESS', 'true').lower() == 'true'
BROWSER_TIMEOUT = int(os.getenv('BROWSER_TIMEOUT', '30000'))

# 登录态配置
LOGIN_STATE_DIR = os.getenv('LOGIN_STATE_DIR', str(BASE_DIR))
LOGIN_STATE_IDLE_TIMEOUT = int(os.getenv('LOGIN_STATE_IDLE_TIMEOUT', '300'))  # 5分钟

# Web服务器配置
WEB_HOST = os.getenv('WEB_HOST', '127.0.0.1')
WEB_PORT = int(os.getenv('WEB_PORT', '5000'))
WEB_DEBUG = os.getenv('WEB_DEBUG', 'true').lower() == 'true'

# 日志配置
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
