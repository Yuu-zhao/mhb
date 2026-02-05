"""
登录示例：演示如何使用不同方法抓取需要登录的页面
"""
from scraper import WebScraper
from selenium_scraper import SeleniumScraper
from database import DatabaseManager
from cookie_helper import CookieHelper
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_1_use_cookie_string():
    """示例1：使用Cookie字符串（从浏览器开发者工具复制）"""
    print("\n=== 示例1：使用Cookie字符串 ===")
    
    # 从浏览器开发者工具复制的Cookie字符串
    # 在Chrome中：F12 -> Application -> Cookies -> 复制所有Cookie
    cookie_string = "your_cookie_name1=value1; your_cookie_name2=value2"
    
    scraper = WebScraper(use_session=True)
    scraper.set_cookies(cookie_string)
    
    url = "https://xyq.cbg.163.com/equip?s=150&eid=202505271300113-150-SPP45KPARYKF"
    page_data = scraper.fetch_page(url)
    
    if page_data:
        print(f"标题: {page_data['title']}")
        print(f"内容长度: {len(page_data['content'])} 字符")
        
        # 保存到数据库
        db = DatabaseManager()
        db.save_page_data(page_data['url'], page_data['title'], page_data['content'])
        print("数据已保存到数据库")


def example_2_use_cookie_file():
    """示例2：使用Cookie文件"""
    print("\n=== 示例2：使用Cookie文件 ===")
    
    # 先保存Cookie到文件（可以从浏览器导出）
    cookies = {
        "cookie_name1": "value1",
        "cookie_name2": "value2"
    }
    CookieHelper.save_cookies_to_file(cookies, "cookies.json")
    
    # 从文件加载Cookie
    cookies = CookieHelper.load_cookies_from_file("cookies.json")
    
    scraper = WebScraper(use_session=True)
    scraper.set_cookies(cookies)
    
    url = "https://xyq.cbg.163.com/equip?s=150&eid=202505271300113-150-SPP45KPARYKF"
    page_data = scraper.fetch_page(url)
    
    if page_data:
        print(f"标题: {page_data['title']}")
        db = DatabaseManager()
        db.save_page_data(page_data['url'], page_data['title'], page_data['content'])


def example_3_use_selenium():
    """示例3：使用Selenium自动化浏览器（支持手动登录）"""
    print("\n=== 示例3：使用Selenium（手动登录） ===")
    
    scraper = SeleniumScraper(headless=False)  # headless=False显示浏览器窗口
    
    try:
        # 访问登录页面
        login_url = "https://xyq.cbg.163.com/"
        scraper.driver.get(login_url)
        
        print("请在浏览器中完成登录，然后按回车继续...")
        input()
        
        # 登录后访问目标页面
        target_url = "https://xyq.cbg.163.com/equip?s=150&eid=202505271300113-150-SPP45KPARYKF"
        page_data = scraper.fetch_page(target_url)
        
        if page_data:
            print(f"标题: {page_data['title']}")
            
            # 保存Cookie供以后使用
            cookies = scraper.get_cookies()
            CookieHelper.save_cookies_to_file(
                CookieHelper.selenium_cookies_to_dict(cookies),
                "selenium_cookies.json"
            )
            print("Cookie已保存到 selenium_cookies.json")
            
            # 保存到数据库
            db = DatabaseManager()
            db.save_page_data(page_data['url'], page_data['title'], page_data['content'])
    finally:
        scraper.close()


def example_4_selenium_with_saved_cookies():
    """示例4：使用Selenium + 已保存的Cookie"""
    print("\n=== 示例4：使用Selenium + 已保存的Cookie ===")
    
    scraper = SeleniumScraper(headless=True)
    
    try:
        # 先访问网站域名以设置Cookie
        scraper.driver.get("https://xyq.cbg.163.com/")
        
        # 加载之前保存的Cookie
        cookies_dict = CookieHelper.load_cookies_from_file("selenium_cookies.json")
        selenium_cookies = CookieHelper.dict_to_selenium_cookies(
            cookies_dict, 
            domain=".163.com"
        )
        scraper.set_cookies(selenium_cookies)
        
        # 访问目标页面
        target_url = "https://xyq.cbg.163.com/equip?s=150&eid=202505271300113-150-SPP45KPARYKF"
        page_data = scraper.fetch_page(target_url)
        
        if page_data:
            print(f"标题: {page_data['title']}")
            db = DatabaseManager()
            db.save_page_data(page_data['url'], page_data['title'], page_data['content'])
    finally:
        scraper.close()


def example_5_custom_login_function():
    """示例5：使用自定义登录函数（需要根据实际网站调整）"""
    print("\n=== 示例5：自定义登录函数 ===")
    
    def custom_login(driver, username=None, password=None):
        """自定义登录函数"""
        # 这里需要根据实际网站的登录流程编写
        # 例如：找到用户名输入框、密码输入框、登录按钮等
        
        # 示例代码（需要根据实际网站调整）：
        # from selenium.webdriver.common.by import By
        # from selenium.webdriver.support.ui import WebDriverWait
        # from selenium.webdriver.support import expected_conditions as EC
        # 
        # wait = WebDriverWait(driver, 10)
        # username_input = wait.until(EC.presence_of_element_located((By.ID, "username")))
        # username_input.send_keys(username)
        # 
        # password_input = driver.find_element(By.ID, "password")
        # password_input.send_keys(password)
        # 
        # login_button = driver.find_element(By.ID, "login-btn")
        # login_button.click()
        # 
        # # 等待登录完成
        # time.sleep(3)
        
        print("请实现自定义登录逻辑")
        input("登录完成后按回车继续...")
    
    scraper = SeleniumScraper(headless=False)
    
    try:
        scraper.login(
            login_url="https://xyq.cbg.163.com/",
            login_func=custom_login,
            username="your_username",
            password="your_password"
        )
        
        target_url = "https://xyq.cbg.163.com/equip?s=150&eid=202505271300113-150-SPP45KPARYKF"
        page_data = scraper.fetch_page(target_url)
        
        if page_data:
            print(f"标题: {page_data['title']}")
            db = DatabaseManager()
            db.save_page_data(page_data['url'], page_data['title'], page_data['content'])
    finally:
        scraper.close()


if __name__ == '__main__':
    print("登录抓取示例")
    print("=" * 50)
    print("请选择要运行的示例：")
    print("1. 使用Cookie字符串")
    print("2. 使用Cookie文件")
    print("3. 使用Selenium手动登录")
    print("4. 使用Selenium + 已保存的Cookie")
    print("5. 自定义登录函数")
    
    choice = input("\n请输入选项 (1-5): ")
    
    if choice == '1':
        example_1_use_cookie_string()
    elif choice == '2':
        example_2_use_cookie_file()
    elif choice == '3':
        example_3_use_selenium()
    elif choice == '4':
        example_4_selenium_with_saved_cookies()
    elif choice == '5':
        example_5_custom_login_function()
    else:
        print("无效选项")
