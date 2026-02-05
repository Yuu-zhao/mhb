"""
Playwright使用示例：登录并保存登录态
"""
from playwright_scraper import PlaywrightScraper, login_and_save_state, fetch_with_saved_state
from database import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_1_login_and_save():
    """示例1：首次登录并保存登录态"""
    print("\n" + "=" * 60)
    print("示例1：首次登录并保存登录态")
    print("=" * 60)
    print("这是第一次使用，需要手动登录一次")
    print("以后就可以自动使用保存的登录态了")
    print()
    
    login_url = "https://xyq.cbg.163.com/"
    storage_state_path = "login_state_163.json"
    
    # 使用便捷函数
    login_and_save_state(login_url, storage_state_path)
    
    print("\n✅ 登录态已保存！")
    print(f"💡 登录态文件: {storage_state_path}")
    print("💡 以后可以直接使用这个文件自动登录")


def example_2_use_saved_state():
    """示例2：使用保存的登录态自动抓取"""
    print("\n" + "=" * 60)
    print("示例2：使用保存的登录态自动抓取")
    print("=" * 60)
    
    storage_state_path = "login_state_163.json"
    url = "https://xyq.cbg.163.com/equip?s=150&eid=202505271300113-150-SPP45KPARYKF&client_type=web&view_loc=equip_list|%7B%22tag%22%3A%20%22user%22%2C%20%22is_from_ad_reco%22%3A%200%2C%20%22discover_tag%22%3A%20%22%22%7D&from_shareid=2106102200128-KAMEEZ7UBQNOANF1&reco_request_id=17702606209902k8TR"
    
    # 使用便捷函数
    page_data = fetch_with_saved_state(url, storage_state_path, headless=True)
    
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
        print("💡 提示：如果登录态过期，请重新运行示例1")


def example_3_manual_control():
    """示例3：手动控制（更灵活）"""
    print("\n" + "=" * 60)
    print("示例3：手动控制")
    print("=" * 60)
    
    storage_state_path = "login_state_163.json"
    url = "https://xyq.cbg.163.com/equip?s=150&eid=202505271300113-150-SPP45KPARYKF&client_type=web&view_loc=equip_list|%7B%22tag%22%3A%20%22user%22%2C%20%22is_from_ad_reco%22%3A%200%2C%20%22discover_tag%22%3A%20%22%22%7D&from_shareid=2106102200128-KAMEEZ7UBQNOANF1&reco_request_id=17702606209902k8TR"
    
    # 使用上下文管理器
    with PlaywrightScraper(headless=True, storage_state_path=storage_state_path) as scraper:
        # 抓取页面
        page_data = scraper.fetch_page(
            url,
            wait_for_selector=None,  # 可以指定等待的元素，如 '.equip-detail'
            wait_until='networkidle',
            wait_for_url_change=True
        )
        
        if page_data:
            print(f"✅ 抓取成功！")
            print(f"标题: {page_data.get('title', '无标题')}")
            
            # 可以保存截图
            scraper.save_screenshot("screenshot.png")
            print("✅ 截图已保存: screenshot.png")
            
            # 保存到数据库
            db = DatabaseManager()
            db.save_page_data(
                url=page_data['url'],
                title=page_data.get('title', '无标题'),
                content=page_data.get('content', '')
            )


def example_4_check_login_state():
    """示例4：检查登录态是否有效"""
    print("\n" + "=" * 60)
    print("示例4：检查登录态是否有效")
    print("=" * 60)
    
    import os
    
    storage_state_path = "login_state_163.json"
    
    if not os.path.exists(storage_state_path):
        print(f"❌ 登录态文件不存在: {storage_state_path}")
        print("💡 请先运行示例1进行登录")
        return
    
    print(f"✅ 登录态文件存在: {storage_state_path}")
    
    # 尝试访问一个需要登录的页面
    test_url = "https://xyq.cbg.163.com/"
    
    with PlaywrightScraper(headless=True, storage_state_path=storage_state_path) as scraper:
        page_data = scraper.fetch_page(test_url)
        
        if page_data:
            # 检查页面内容，判断是否已登录
            content = page_data.get('content', '').lower()
            if '登录' in content or 'login' in content:
                print("⚠️ 登录态可能已过期，请重新登录")
                print("💡 运行示例1重新保存登录态")
            else:
                print("✅ 登录态有效")
        else:
            print("❌ 无法访问页面，登录态可能已过期")


if __name__ == '__main__':
    print("=" * 60)
    print("Playwright 登录态管理示例")
    print("=" * 60)
    print("\n请选择要运行的示例：")
    print("1. 首次登录并保存登录态（需要手动登录）")
    print("2. 使用保存的登录态自动抓取")
    print("3. 手动控制（更灵活）")
    print("4. 检查登录态是否有效")
    print("5. 全部执行（先登录，再抓取）")
    
    choice = input("\n请输入选项 (1-5): ").strip()
    
    if choice == '1':
        example_1_login_and_save()
    elif choice == '2':
        example_2_use_saved_state()
    elif choice == '3':
        example_3_manual_control()
    elif choice == '4':
        example_4_check_login_state()
    elif choice == '5':
        example_1_login_and_save()
        print("\n" + "=" * 60)
        example_2_use_saved_state()
    else:
        print("无效选项")
