# Playwright 安装指南

## 问题说明

如果看到以下错误：
```
Executable doesn't exist at .../chromium-1091/chrome-mac/Chromium.app
Looks like Playwright was just installed or updated.
Please run the following command to download new browsers:
    playwright install
```

这表示 Playwright Python 包已安装，但浏览器驱动未安装。

## 解决方案

### 方法1：安装所有浏览器（推荐）

```bash
playwright install
```

这会安装 Chromium、Firefox 和 WebKit 浏览器。

### 方法2：只安装 Chromium（更快）

```bash
playwright install chromium
```

### 方法3：在虚拟环境中安装

如果使用虚拟环境（如 `.venv`），确保在虚拟环境中运行：

```bash
# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate  # Windows

# 安装浏览器
playwright install
```

## 验证安装

安装完成后，可以运行以下命令验证：

```bash
python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); browser = p.chromium.launch(); browser.close(); p.stop(); print('✅ Playwright安装成功')"
```

## 在Web GUI中检查

Web GUI会在页面加载时自动检查Playwright是否已安装：
- ✅ 如果已安装：正常显示
- ⚠️ 如果未安装：显示警告提示

## 常见问题

### Q: 安装很慢怎么办？

**A:** 可以只安装 Chromium：
```bash
playwright install chromium
```

### Q: 安装失败怎么办？

**A:** 
1. 检查网络连接
2. 尝试使用代理：
```bash
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
playwright install
```

### Q: 在虚拟环境中安装后还是提示未安装？

**A:** 确保在正确的虚拟环境中运行：
```bash
# 检查当前Python路径
which python  # macOS/Linux
where python  # Windows

# 应该指向虚拟环境的Python
# 例如: /path/to/project/.venv/bin/python
```

### Q: 可以使用系统已安装的Chrome吗？

**A:** Playwright需要自己管理的浏览器，不能直接使用系统Chrome。但可以配置使用系统Chrome（需要额外配置）。

## 安装位置

Playwright浏览器默认安装在：
- **macOS**: `~/Library/Caches/ms-playwright/`
- **Linux**: `~/.cache/ms-playwright/`
- **Windows**: `%USERPROFILE%\AppData\Local\ms-playwright\`

## 快速修复

如果遇到问题，可以尝试：

```bash
# 1. 卸载并重新安装
pip uninstall playwright
pip install playwright
playwright install chromium

# 2. 清理缓存后重新安装
rm -rf ~/Library/Caches/ms-playwright/  # macOS
playwright install chromium
```

## 完成安装后

安装完成后，重新启动Web GUI：

```bash
python web_gui.py
```

然后就可以正常使用Playwright功能了！
