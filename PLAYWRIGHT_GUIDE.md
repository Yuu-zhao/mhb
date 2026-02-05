# Playwright 使用指南

## 为什么使用 Playwright？

Playwright 是当前最推荐的浏览器自动化方案，相比 Selenium 有以下优势：

- ✅ **更稳定**：基于现代浏览器架构
- ✅ **更快速**：性能更好
- ✅ **保存登录态**：可以保存完整的浏览器状态（Cookie、localStorage、sessionStorage）
- ✅ **一次登录，永久使用**：登录一次后，后续自动使用保存的登录态
- ✅ **更好的 JavaScript 支持**：完美支持现代 Web 应用

## 安装

### Step 1: 安装 Python 包

```bash
pip install playwright
```

### Step 2: 安装浏览器驱动

```bash
playwright install
```

这会自动下载 Chromium、Firefox 和 WebKit 浏览器。

## 快速开始

### 方案一：首次登录并保存登录态（推荐）

**只需要第一次手动登录，以后就全自动了！**

```python
from playwright_scraper import login_and_save_state

# 首次登录并保存登录态
login_and_save_state(
    login_url="https://xyq.cbg.163.com/",
    storage_state_path="login_state_163.json"
)
```

运行后会：
1. 打开浏览器窗口
2. 访问登录页面
3. 等待你完成登录（扫码或输入账号密码）
4. 按回车后自动保存登录态到 `login_state_163.json`

### 方案二：使用保存的登录态自动抓取

```python
from playwright_scraper import fetch_with_saved_state

# 使用保存的登录态自动抓取（完全自动，无需再登录）
page_data = fetch_with_saved_state(
    url="https://xyq.cbg.163.com/equip?s=150&eid=...",
    storage_state_path="login_state_163.json",
    headless=True  # 无头模式，不显示浏览器
)

if page_data:
    print(f"标题: {page_data['title']}")
    print(f"内容: {page_data['content'][:100]}...")
```

## 详细使用

### 示例1：完整流程

```python
from playwright_scraper import PlaywrightScraper
from database import DatabaseManager

# 使用保存的登录态
scraper = PlaywrightScraper(
    headless=True,  # 无头模式
    storage_state_path="login_state_163.json"  # 登录态文件
)

try:
    scraper.start()
    
    # 抓取页面
    page_data = scraper.fetch_page(
        url="https://xyq.cbg.163.com/equip?s=150&eid=...",
        wait_for_selector=None,  # 可选：等待特定元素
        wait_until='networkidle',  # 等待网络空闲
        wait_for_url_change=True  # 等待URL变化（处理跳转）
    )
    
    if page_data:
        print(f"✅ 抓取成功！")
        print(f"标题: {page_data['title']}")
        
        # 保存到数据库
        db = DatabaseManager()
        db.save_page_data(
            url=page_data['url'],
            title=page_data['title'],
            content=page_data['content']
        )
        
        # 保存截图
        scraper.save_screenshot("screenshot.png")
        
finally:
    scraper.close()
```

### 示例2：使用上下文管理器（推荐）

```python
from playwright_scraper import PlaywrightScraper

# 使用上下文管理器，自动管理资源
with PlaywrightScraper(headless=True, storage_state_path="login_state_163.json") as scraper:
    page_data = scraper.fetch_page("https://xyq.cbg.163.com/equip?...")
    
    if page_data:
        print(f"标题: {page_data['title']}")
        scraper.save_screenshot("screenshot.png")
```

### 示例3：检查登录态是否有效

```python
from playwright_scraper import PlaywrightScraper
import os

storage_state_path = "login_state_163.json"

if not os.path.exists(storage_state_path):
    print("❌ 登录态文件不存在，请先登录")
else:
    with PlaywrightScraper(headless=True, storage_state_path=storage_state_path) as scraper:
        # 访问一个需要登录的页面
        page_data = scraper.fetch_page("https://xyq.cbg.163.com/")
        
        if page_data:
            content = page_data['content'].lower()
            if '登录' in content or 'login' in content:
                print("⚠️ 登录态已过期，请重新登录")
            else:
                print("✅ 登录态有效")
```

## 在 Web GUI 中使用

1. **启动 Web GUI**：
```bash
python web_gui.py
```

2. **选择 Playwright 方法**：
   - 在"抓取方法"中选择"Playwright（推荐，支持保存登录态）"

3. **设置登录态文件（可选）**：
   - 如果已有登录态文件，在"登录态文件"输入框中输入文件路径
   - 或点击"选择文件"按钮选择文件

4. **首次使用需要先登录**：
   - 运行 `python playwright_example.py` 选择选项1
   - 或使用代码：`login_and_save_state("https://xyq.cbg.163.com/", "login_state_163.json")`

5. **开始抓取**：
   - 输入URL
   - 选择登录态文件
   - 点击"开始抓取"

## 运行示例

```bash
python playwright_example.py
```

然后选择：
- 选项 1：首次登录并保存登录态
- 选项 2：使用保存的登录态自动抓取
- 选项 3：手动控制（更灵活）
- 选项 4：检查登录态是否有效
- 选项 5：全部执行

## 登录态文件说明

### 文件格式

登录态文件是 JSON 格式，包含：
- `cookies`: 所有 Cookie
- `origins`: localStorage 和 sessionStorage 数据

### 文件位置

建议保存在项目根目录，如：
- `login_state_163.json`
- `login_state_taobao.json`
- 等等

### 文件安全

⚠️ **重要**：登录态文件包含你的登录信息，请妥善保管：
- 不要提交到 Git 仓库
- 不要分享给他人
- 建议添加到 `.gitignore`

## 常见问题

### Q: 登录态过期了怎么办？

**A:** 重新运行登录流程：
```python
from playwright_scraper import login_and_save_state

login_and_save_state(
    login_url="https://xyq.cbg.163.com/",
    storage_state_path="login_state_163.json"
)
```

### Q: 可以同时保存多个网站的登录态吗？

**A:** 可以，使用不同的文件名：
```python
login_and_save_state("https://site1.com", "login_state_site1.json")
login_and_save_state("https://site2.com", "login_state_site2.json")
```

### Q: Playwright 和 Selenium 有什么区别？

**A:** 
- **Playwright**：更现代、更稳定、支持保存登录态（推荐）
- **Selenium**：传统方案，功能完整但需要手动管理 Cookie

### Q: 无头模式是什么意思？

**A:** 
- `headless=True`：不显示浏览器窗口（后台运行）
- `headless=False`：显示浏览器窗口（可以看到操作过程）

### Q: 如何调试？

**A:** 使用 `headless=False` 可以看到浏览器操作：
```python
scraper = PlaywrightScraper(headless=False)
```

## 最佳实践

1. **首次使用**：运行登录流程，保存登录态
2. **日常使用**：直接使用保存的登录态，全自动
3. **定期检查**：如果抓取失败，检查登录态是否过期
4. **文件管理**：为不同网站使用不同的登录态文件
5. **安全注意**：不要将登录态文件提交到代码仓库

## 优势总结

| 特性 | Playwright | Selenium | Requests |
|------|-----------|----------|----------|
| 保存登录态 | ✅ 完整支持 | ⚠️ 仅Cookie | ❌ 不支持 |
| JavaScript支持 | ✅ 完美 | ✅ 支持 | ❌ 不支持 |
| 性能 | ✅ 快速 | ⚠️ 较慢 | ✅ 最快 |
| 稳定性 | ✅ 高 | ⚠️ 中等 | ✅ 高 |
| 推荐度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |

## 总结

Playwright 是最推荐的方案，特别是对于需要登录的网站：

1. ✅ **一次登录，永久使用**：登录一次后，后续全自动
2. ✅ **完整状态保存**：Cookie、localStorage、sessionStorage 全部保存
3. ✅ **稳定可靠**：基于现代浏览器架构
4. ✅ **易于使用**：API 简洁，文档完善

开始使用 Playwright，享受自动化抓取的便利吧！🚀
