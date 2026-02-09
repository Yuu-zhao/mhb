"""
Web应用主文件
"""
from flask import Flask
from .routes import register_routes
from config.settings import WEB_HOST, WEB_PORT, WEB_DEBUG
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def create_app() -> Flask:
    """创建Flask应用"""
    app = Flask(__name__)
    
    # 注册路由
    register_routes(app)
    
    return app


def run_app():
    """运行Web应用"""
    app = create_app()
    
    print("=" * 60)
    print("🌐 网页抓取工具 Web GUI（重构版）")
    print("=" * 60)
    print(f"📱 访问地址: http://{WEB_HOST}:{WEB_PORT}")
    print("💡 智能检测登录需求，自动获取Cookie")
    print("💡 按 Ctrl+C 停止服务器")
    print("=" * 60)
    
    try:
        app.run(debug=WEB_DEBUG, host=WEB_HOST, port=WEB_PORT, use_reloader=False)
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        logger.error(f"服务器运行出错: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_app()
