# 快速开始

## 1. 安装

```bash
pip install -r requirements.txt
playwright install chromium
```

## 2. 启动桌面 GUI

```bash
./run_gui.sh
# 或
python3 gui_app.py
```

## 3. 使用

1. 在「页面地址」输入藏宝阁等规则页 URL，点击 **开始爬取**。
2. 若提示需要登录：点击 **打开浏览器登录**，在弹出浏览器中完成登录，程序会自动保存登录态并继续抓取。
3. 在「爬取后的核心数据」查看抽取结果，需要时点击 **保存到数据库**。

更多说明见 [README.md](README.md)。
