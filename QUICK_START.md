# 快速开始指南 - 抓取需要登录的页面

## 针对 163.com 等需要登录的网站

### 方法1：使用Cookie（最简单快速）⭐推荐

#### 步骤1：获取Cookie

1. 在Chrome浏览器中打开并登录目标网站
2. 按 `F12` 打开开发者工具
3. 点击 `Application`（应用程序）标签
4. 左侧展开 `Cookies`，点击网站域名（如 `xyq.cbg.163.com`）
5. 在右侧表格中，复制所有Cookie的 `Name` 和 `Value`
6. 格式化为：`name1=value1; name2=value2; name3=value3`

#### 步骤2：使用Cookie抓取

```bash
python main_with_login.py "https://xyq.cbg.163.com/equip?s=150&eid=..." \
  --method requests \
  --cookie "你的Cookie字符串"
```

#### 步骤3：保存Cookie到文件（可选，方便重复使用）

创建 `cookies.json` 文件：
```json
{
  "cookie_name1": "value1",
  "cookie_name2": "value2"
}
```

然后使用：
```bash
python main_with_login.py "URL" --method requests --cookie-file cookies.json
```

---

### 方法2：使用Selenium（支持JavaScript渲染）

#### 安装ChromeDriver

**macOS:**
```bash
brew install chromedriver
```

**Linux/Windows:**
从 https://chromedriver.chromium.org/ 下载对应版本

#### 使用Selenium抓取

**显示浏览器窗口（可以手动登录）：**
```bash
python main_with_login.py "https://xyq.cbg.163.com/equip?s=150&eid=..." \
  --method selenium \
  --selenium-headless=false
```

程序会打开浏览器，你可以手动登录，然后程序会自动抓取页面。

**无头模式（需要先设置Cookie）：**
```bash
python main_with_login.py "URL" --method selenium
```

---

## 完整示例

### 示例1：使用Cookie字符串

```python
from scraper import WebScraper
from database import DatabaseManager

# 创建抓取器
scraper = WebScraper(use_session=True)

# 设置Cookie（从浏览器复制）
cookie_string = "NTES_SESS=xxx; NTES_PASSPORT=yyy; ..."
scraper.set_cookies(cookie_string)

# 抓取页面
url = "https://xyq.cbg.163.com/equip?s=150&eid=..."
page_data = scraper.fetch_page(url)

if page_data:
    # 保存到数据库
    db = DatabaseManager()
    db.save_page_data(
        url=page_data['url'],
        title=page_data['title'],
        content=page_data['content']
    )
    print("保存成功！")
```

### 示例2：使用Selenium手动登录

```python
from selenium_scraper import SeleniumScraper
from database import DatabaseManager

scraper = SeleniumScraper(headless=False)  # 显示浏览器

try:
    # 访问登录页面
    scraper.driver.get("https://xyq.cbg.163.com/")
    
    # 等待手动登录
    input("请在浏览器中完成登录，然后按回车继续...")
    
    # 抓取目标页面
    target_url = "https://xyq.cbg.163.com/equip?s=150&eid=..."
    page_data = scraper.fetch_page(target_url)
    
    if page_data:
        db = DatabaseManager()
        db.save_page_data(
            url=page_data['url'],
            title=page_data['title'],
            content=page_data['content']
        )
        
        # 保存Cookie供以后使用
        from cookie_helper import CookieHelper
        cookies = scraper.get_cookies()
        CookieHelper.save_cookies_to_file(
            CookieHelper.selenium_cookies_to_dict(cookies),
            "cookies.json"
        )
        print("Cookie已保存！")
finally:
    scraper.close()
```

---

## 常见问题

**Q: Cookie过期了怎么办？**  
A: 重新从浏览器获取Cookie并更新

**Q: 提示"需要登录"但已经设置了Cookie？**  
A: 检查Cookie是否正确，可能需要包含更多Cookie项

**Q: Selenium报错找不到ChromeDriver？**  
A: 确保ChromeDriver在PATH中，或指定路径：
```python
scraper = SeleniumScraper(chrome_driver_path="/path/to/chromedriver")
```

**Q: 页面内容是空的？**  
A: 页面可能是JavaScript渲染的，使用Selenium方法

**Q: 如何查看已保存的数据？**  
A: 
```python
from database import DatabaseManager
db = DatabaseManager()
all_data = db.get_all_data()
for data in all_data:
    print(f"ID: {data.id}, URL: {data.url}, Title: {data.title}")
```

---

## 运行示例代码

查看完整示例：
```bash
python login_example.py
```
