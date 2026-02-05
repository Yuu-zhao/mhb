"""
使用Cookie抓取163.com页面的示例
"""
from scraper import WebScraper
from selenium_scraper import SeleniumScraper
from database import DatabaseManager
from cookie_helper import CookieHelper
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 你的Cookie
COOKIES = {
    "is_log_active_stat": "1",
    "fingerprint": "caqu18tw9kcewfik",
    "cur_servername": "%25E6%25A2%25A6%25E5%259B%259E%25E6%259C%259B%25E6%259C%2588",
    "cbg_qrcode": "v2.s.i3yMuhhPa0iXun4a5X7YaP21mpVbfqM9GfbS3GmtupVo-Vw9",
    "area_id": "45",
    "alert_msg_flag": "1",
    "_ns": "NS1.2.1603594620.1728718255",
    "_ga_C6TGHFPQ1H": "GS2.1.s1750218369$o3$g1$t1750218520$j60$l0$h0",
    "_ga": "GA1.1.1466664800.1734602811",
    "_flow_group_v2": "g77",
    "_external_mark": "cbg.163.com",
    "_clck": "8gv7gi%7C2%7Cfwv%7C0%7C1919",
    "__session__": "1",
    "Qs_pv_382223": "3890182994660857300%2C1918653557716756000%2C1899685723721034800%2C1077430685009470700%2C3725720016844696000",
    "Qs_lvt_382223": "1743642752%2C1743643190%2C1750218454",
    "P_INFO": "zzz378282925@163.com|1753680765|0|csa|00&99|zhj&1753671114&csa#zhj&330100#10#0#0|&0|csa&xyq_qrcode&cbg&epay_client|zzz378282925@163.com",
    "NTES_SESS": "ELvz2gnXVETTXQeqWCIAqEc020IEbzWfayXND2sfqefgdWG74r.5xsztdiLZ8GhIVRt58EvSRbutPHsIsBcvZSKtZxBCWW.uHnGquMl2G93kxfrI9gR7ZekJ8ed069u0jyNCtO4pKx8BSg1_qjSl7jFoIDrcvwIVmRdRvPTUw8DvEG4nWAluMqANTGbsdBOgs1cT1OyNc13I7",
    "NTES_P_UTID": "SNJ75ycTgPuYYaJNQk2xhl2Ny34PSZJe|1753680765",
}


def example_requests_method():
    """示例1：使用Requests方法（快速）"""
    print("\n=== 示例1：使用Requests方法 ===")
    
    url = "https://xyq.cbg.163.com/equip?s=150&eid=202505271300113-150-SPP45KPARYKF&client_type=web&view_loc=equip_list|%7B%22tag%22%3A%20%22user%22%2C%20%22is_from_ad_reco%22%3A%200%2C%20%22discover_tag%22%3A%20%22%22%7D&from_shareid=2106102200128-KAMEEZ7UBQNOANF1&reco_request_id=17702606209902k8TR"
    
    scraper = WebScraper(use_session=True)
    
    # 设置Cookie
    scraper.set_cookies(COOKIES)
    
    # 抓取页面
    page_data = scraper.fetch_page(url)
    
    if page_data:
        print(f"✅ 抓取成功！")
        print(f"标题: {page_data.get('title', '无标题')}")
        print(f"内容长度: {len(page_data.get('content', ''))} 字符")
        if page_data.get('redirected'):
            print(f"发生跳转: {page_data.get('original_url')} -> {page_data.get('url')}")
        
        # 保存到数据库
        db = DatabaseManager()
        saved_data = db.save_page_data(
            url=page_data['url'],
            title=page_data.get('title', '无标题'),
            content=page_data.get('content', '')
        )
        print(f"✅ 已保存到数据库，ID: {saved_data.id}")
    else:
        print("❌ 抓取失败")


def example_selenium_method():
    """示例2：使用Selenium方法（支持JavaScript）"""
    print("\n=== 示例2：使用Selenium方法 ===")
    
    url = "https://xyq.cbg.163.com/equip?s=150&eid=202505271300113-150-SPP45KPARYKF&client_type=web&view_loc=equip_list|%7B%22tag%22%3A%20%22user%22%2C%20%22is_from_ad_reco%22%3A%200%2C%20%22discover_tag%22%3A%20%22%22%7D&from_shareid=2106102200128-KAMEEZ7UBQNOANF1&reco_request_id=17702606209902k8TR"
    
    scraper = SeleniumScraper(headless=True)
    
    try:
        # 先访问域名以设置Cookie
        scraper.driver.get("https://xyq.cbg.163.com/")
        
        # 转换为Selenium格式的Cookie
        selenium_cookies = CookieHelper.dict_to_selenium_cookies(COOKIES, domain=".163.com")
        scraper.set_cookies(selenium_cookies)
        
        # 抓取页面（自动处理跳转）
        page_data = scraper.fetch_page(url, wait_for_url_change=True, wait_timeout=15)
        
        if page_data:
            print(f"✅ 抓取成功！")
            print(f"标题: {page_data.get('title', '无标题')}")
            print(f"内容长度: {len(page_data.get('content', ''))} 字符")
            if page_data.get('redirected'):
                print(f"发生跳转: {page_data.get('original_url')} -> {page_data.get('url')}")
            
            # 保存到数据库
            db = DatabaseManager()
            saved_data = db.save_page_data(
                url=page_data['url'],
                title=page_data.get('title', '无标题'),
                content=page_data.get('content', '')
            )
            print(f"✅ 已保存到数据库，ID: {saved_data.id}")
        else:
            print("❌ 抓取失败")
    finally:
        scraper.close()


def save_cookies_to_file():
    """保存Cookie到文件，方便以后使用"""
    print("\n=== 保存Cookie到文件 ===")
    
    CookieHelper.save_cookies_to_file(COOKIES, "cookies_163.json")
    print("✅ Cookie已保存到 cookies_163.json")
    print("💡 以后可以使用以下代码加载：")
    print("   cookies = CookieHelper.load_cookies_from_file('cookies_163.json')")


def convert_cookies_to_string():
    """将Cookie字典转换为字符串格式（用于Web GUI）"""
    print("\n=== Cookie字符串格式（用于Web GUI） ===")
    
    cookie_string = CookieHelper.cookie_dict_to_string(COOKIES)
    print("在Web GUI的Cookie输入框中粘贴以下内容：")
    print("-" * 60)
    print(cookie_string)
    print("-" * 60)


if __name__ == '__main__':
    print("=" * 60)
    print("163.com Cookie使用示例")
    print("=" * 60)
    
    print("\n请选择要运行的示例：")
    print("1. 使用Requests方法抓取（快速）")
    print("2. 使用Selenium方法抓取（支持JavaScript）")
    print("3. 保存Cookie到文件")
    print("4. 转换为Cookie字符串（用于Web GUI）")
    print("5. 全部执行")
    
    choice = input("\n请输入选项 (1-5): ").strip()
    
    if choice == '1':
        example_requests_method()
    elif choice == '2':
        example_selenium_method()
    elif choice == '3':
        save_cookies_to_file()
    elif choice == '4':
        convert_cookies_to_string()
    elif choice == '5':
        save_cookies_to_file()
        convert_cookies_to_string()
        print("\n" + "=" * 60)
        example_requests_method()
        print("\n" + "=" * 60)
        example_selenium_method()
    else:
        print("无效选项")
