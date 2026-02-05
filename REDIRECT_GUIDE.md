# 页面跳转和重定向处理指南

## 问题说明

某些网站在访问时会有中间态的跳转页面，常见情况包括：

1. **HTTP重定向**：301/302状态码跳转
2. **JavaScript跳转**：通过 `window.location` 或 `location.href` 跳转
3. **Meta Refresh跳转**：通过 `<meta http-equiv="refresh">` 跳转
4. **中间加载页**：显示"正在跳转..."等提示页面

## 解决方案

### 自动处理（已实现）

系统已经自动处理了这些情况：

#### 1. Requests方法（HTTP重定向）

- ✅ **自动跟随重定向**：默认 `allow_redirects=True`
- ✅ **跟踪最终URL**：返回最终到达的URL
- ✅ **最大重定向次数**：默认最多10次重定向

```python
from scraper import WebScraper

scraper = WebScraper(use_session=True)
# 自动处理重定向
page_data = scraper.fetch_page(url, allow_redirects=True, max_redirects=10)

# 检查是否发生重定向
if page_data.get('redirected'):
    print(f"原始URL: {page_data.get('original_url')}")
    print(f"最终URL: {page_data.get('url')}")
```

#### 2. Selenium方法（JavaScript跳转）

- ✅ **等待URL稳定**：自动检测URL变化并等待稳定
- ✅ **等待页面加载完成**：检查 `document.readyState`
- ✅ **额外等待时间**：确保JavaScript执行完成

```python
from selenium_scraper import SeleniumScraper

scraper = SeleniumScraper(headless=True)
# 自动等待跳转完成
page_data = scraper.fetch_page(
    url, 
    wait_for_url_change=True,  # 等待URL变化
    wait_timeout=15  # 等待超时时间（秒）
)

# 检查是否发生跳转
if page_data.get('redirected'):
    print(f"原始URL: {page_data.get('original_url')}")
    print(f"最终URL: {page_data.get('url')}")
```

## 在Web GUI中使用

Web界面已经自动启用了跳转处理：

1. **Requests方法**：自动跟随HTTP重定向
2. **Selenium方法**：自动等待JavaScript跳转完成

如果发生跳转，状态提示会显示：
```
抓取成功！标题: xxx, 内容长度: xxx 字符 (已跳转: 原始URL -> 最终URL)
```

## 高级配置

### 自定义等待元素

如果知道目标页面的特定元素，可以等待该元素出现：

```python
# 等待特定元素出现
page_data = scraper.fetch_page(
    url,
    wait_for_element='.main-content',  # CSS选择器
    wait_selector='css'  # 或 'xpath'
)
```

### 禁用重定向（Requests）

如果需要获取重定向前的页面：

```python
page_data = scraper.fetch_page(url, allow_redirects=False)
```

### 调整等待时间（Selenium）

如果跳转较慢，可以增加等待时间：

```python
scraper = SeleniumScraper(wait_time=20)  # 默认10秒，改为20秒
page_data = scraper.fetch_page(url, wait_timeout=20)
```

## 常见问题

### Q: 为什么还是抓取到了中间跳转页？

**A:** 可能的原因：
1. 跳转时间过长，超过了等待时间
2. 使用了Requests方法，但跳转是JavaScript实现的
3. 需要特定的Cookie或参数才能跳转

**解决方案：**
- 使用Selenium方法（支持JavaScript）
- 增加等待时间
- 检查Cookie是否正确

### Q: 如何知道是否发生了跳转？

**A:** 检查返回数据中的 `redirected` 字段：

```python
if page_data.get('redirected'):
    print("发生了跳转")
    print(f"原始: {page_data.get('original_url')}")
    print(f"最终: {page_data.get('url')}")
```

### Q: 跳转后的URL和原始URL有什么区别？

**A:** 
- `original_url`: 你输入的原始URL
- `url`: 最终到达的URL（可能经过多次跳转）
- `redirected`: 布尔值，表示是否发生了跳转

### Q: 如何处理需要登录才能跳转的页面？

**A:** 
1. 确保设置了正确的Cookie
2. 使用Selenium方法（更可靠）
3. 可能需要先访问登录页面，再访问目标页面

## 示例代码

### 示例1：处理163.com的跳转

```python
from selenium_scraper import SeleniumScraper
from cookie_helper import CookieHelper

scraper = SeleniumScraper(headless=True)

# 设置Cookie
cookies = CookieHelper.load_cookies_from_file("cookies.json")
selenium_cookies = CookieHelper.dict_to_selenium_cookies(cookies, domain=".163.com")
scraper.driver.get("https://xyq.cbg.163.com/")
scraper.set_cookies(selenium_cookies)

# 抓取（自动处理跳转）
url = "https://xyq.cbg.163.com/equip?s=150&eid=..."
page_data = scraper.fetch_page(url, wait_for_url_change=True)

if page_data:
    print(f"最终URL: {page_data['url']}")
    if page_data.get('redirected'):
        print(f"发生了跳转: {page_data['original_url']} -> {page_data['url']}")

scraper.close()
```

### 示例2：等待特定内容出现

```python
from selenium_scraper import SeleniumScraper

scraper = SeleniumScraper(headless=True)

# 等待页面中的特定元素出现（表示跳转完成）
page_data = scraper.fetch_page(
    url,
    wait_for_element='.equip-detail',  # 等待装备详情元素
    wait_selector='css',
    wait_for_url_change=True
)

scraper.close()
```

## 技术细节

### Requests重定向处理

- 使用 `allow_redirects=True` 参数
- 自动跟随 Location 头
- 记录重定向历史（`response.history`）
- 返回最终响应

### Selenium跳转检测

1. 访问初始URL
2. 定期检查 `driver.current_url` 是否变化
3. 等待URL稳定（连续2次检查相同）
4. 等待 `document.readyState == 'complete'`
5. 额外等待1秒确保JavaScript执行完成

### 性能优化

- Requests方法：快速，适合HTTP重定向
- Selenium方法：较慢但可靠，适合JavaScript跳转
- 如果知道目标元素，使用 `wait_for_element` 可以更快

## 总结

系统已经自动处理了大部分跳转情况：

- ✅ HTTP重定向（Requests）
- ✅ JavaScript跳转（Selenium）
- ✅ 中间加载页（Selenium等待）
- ✅ URL变化检测（Selenium）

如果遇到特殊问题，可以：
1. 使用Selenium方法
2. 增加等待时间
3. 等待特定元素出现
4. 检查Cookie和参数
