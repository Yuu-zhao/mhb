# 网页抓取与数据库存储工具

这是一个用于抓取网页内容并存储到数据库的Python工具。

## 功能特性

- 自动抓取网页内容（标题和正文）
- 将数据存储到SQLite数据库
- 支持自定义请求头
- **支持需要登录的页面（Cookie和Selenium两种方式）**
- **支持JavaScript渲染的页面（Selenium）**
- 完善的错误处理和日志记录

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本使用（无需登录的页面）

```bash
python main.py <URL>
```

示例：
```bash
python main.py https://www.example.com
```

### 需要登录的页面

#### 方法1：使用Cookie（推荐，速度快）

**步骤1：从浏览器获取Cookie**
1. 在浏览器中打开目标网站并登录
2. 按 `F12` 打开开发者工具
3. 切换到 `Application`（应用程序）标签
4. 左侧选择 `Cookies` -> 选择网站域名
5. 复制所有Cookie的name和value，格式如：`name1=value1; name2=value2`

**步骤2：使用Cookie抓取**

```bash
# 使用Cookie字符串
python main_with_login.py <URL> --method requests --cookie "name1=value1; name2=value2"

# 使用Cookie文件（JSON格式）
python main_with_login.py <URL> --method requests --cookie-file cookies.json
```

示例：
```bash
python main_with_login.py "https://xyq.cbg.163.com/equip?s=150&eid=..." --method requests --cookie "your_cookie_string"
```

#### 方法2：使用Selenium（支持JavaScript渲染）

**安装ChromeDriver：**
```bash
# macOS
brew install chromedriver

# 或从官网下载：https://chromedriver.chromium.org/
```

**使用Selenium抓取：**
```bash
# 无头模式（不显示浏览器）
python main_with_login.py <URL> --method selenium

# 显示浏览器窗口（可以手动登录）
python main_with_login.py <URL> --method selenium --selenium-headless=false
```

示例：
```bash
python main_with_login.py "https://xyq.cbg.163.com/equip?s=150&eid=..." --method selenium
```

### 在代码中使用

#### 基本使用（无需登录）

```python
from scraper import WebScraper
from database import DatabaseManager

# 创建抓取器和数据库管理器
scraper = WebScraper()
db_manager = DatabaseManager()

# 抓取网页
page_data = scraper.fetch_page('https://www.example.com')

if page_data:
    # 保存到数据库
    db_manager.save_page_data(
        url=page_data['url'],
        title=page_data['title'],
        content=page_data['content']
    )
```

#### 使用Cookie（需要登录的页面）

```python
from scraper import WebScraper
from database import DatabaseManager
from cookie_helper import CookieHelper

# 创建抓取器（使用Session）
scraper = WebScraper(use_session=True)

# 设置Cookie（从浏览器复制）
cookie_string = "name1=value1; name2=value2"
scraper.set_cookies(cookie_string)

# 或者从文件加载Cookie
cookies = CookieHelper.load_cookies_from_file("cookies.json")
scraper.set_cookies(cookies)

# 抓取需要登录的页面
page_data = scraper.fetch_page('https://xyq.cbg.163.com/equip?...')

if page_data:
    db_manager = DatabaseManager()
    db_manager.save_page_data(
        url=page_data['url'],
        title=page_data['title'],
        content=page_data['content']
    )
```

#### 使用Selenium（支持JavaScript渲染）

```python
from selenium_scraper import SeleniumScraper
from database import DatabaseManager

# 创建Selenium抓取器
scraper = SeleniumScraper(headless=True)

try:
    # 如果需要登录，先访问登录页面
    scraper.driver.get("https://xyq.cbg.163.com/")
    # 手动登录或使用自定义登录函数
    input("请完成登录后按回车...")
    
    # 抓取目标页面
    page_data = scraper.fetch_page('https://xyq.cbg.163.com/equip?...')
    
    if page_data:
        db_manager = DatabaseManager()
        db_manager.save_page_data(
            url=page_data['url'],
            title=page_data['title'],
            content=page_data['content']
        )
finally:
    scraper.close()
```

更多示例请查看 `login_example.py`

## 项目结构

```
mhb/
├── main.py              # 主程序入口（基本抓取）
├── main_with_login.py   # 支持登录的主程序
├── scraper.py           # 网页抓取模块（支持Cookie）
├── selenium_scraper.py  # Selenium抓取模块（支持JavaScript）
├── cookie_helper.py     # Cookie管理工具
├── database.py          # 数据库模型和操作
├── login_example.py     # 登录使用示例
├── requirements.txt     # 依赖包列表
├── README.md            # 说明文档
└── page_data.db         # SQLite数据库文件（运行后自动生成）
```

## 数据库结构

数据存储在SQLite数据库 `page_data.db` 中，表结构如下：

- `id`: 主键，自增
- `url`: 页面URL
- `title`: 页面标题
- `content`: 页面正文内容
- `created_at`: 创建时间

## 查看数据库内容

可以使用SQLite命令行工具查看数据：

```bash
sqlite3 page_data.db
SELECT * FROM page_data;
```

或者使用Python：

```python
from database import DatabaseManager

db = DatabaseManager()
all_data = db.get_all_data()
for data in all_data:
    print(f"ID: {data.id}, URL: {data.url}, Title: {data.title}")
```

## 注意事项

1. **请遵守网站的robots.txt和使用条款**
2. **不要过于频繁地请求同一网站，避免被封IP**
3. **使用Cookie时，注意Cookie的有效期，过期后需要重新获取**
4. **使用Selenium时，需要安装Chrome浏览器和ChromeDriver**
5. **某些网站有反爬虫机制，可能需要：**
   - 设置更完整的请求头
   - 使用代理IP
   - 添加请求延迟
   - 使用更真实的User-Agent

## 获取Cookie的方法

### 方法1：从Chrome浏览器获取

1. 打开目标网站并登录
2. 按 `F12` 打开开发者工具
3. 切换到 `Application` 标签（或 `存储`）
4. 左侧展开 `Cookies`，选择网站域名
5. 复制所有Cookie的name和value

### 方法2：使用浏览器扩展

安装 `EditThisCookie` 或类似扩展，可以一键导出所有Cookie

### 方法3：使用Selenium自动获取

运行 `login_example.py` 示例3，手动登录后会自动保存Cookie

## 常见问题

**Q: 提示"需要登录"怎么办？**  
A: 使用 `main_with_login.py` 并提供Cookie，或使用Selenium方法

**Q: 页面内容是空的或只有JavaScript代码？**  
A: 使用Selenium方法，它可以执行JavaScript并渲染页面

**Q: Cookie过期了怎么办？**  
A: 重新从浏览器获取Cookie并更新

**Q: Selenium报错找不到ChromeDriver？**  
A: 确保已安装Chrome浏览器，并下载对应版本的ChromeDriver
