# 规则页爬取工具

抓取藏宝阁等规则页（如 `html/rule` 下示例页）的页面数据，通过桌面 GUI 输入 URL、自动处理登录、展示核心抽取结果并支持落库。

## 功能

- **桌面 GUI**：左侧 **已录入主商品列表**（点击加载详情）；右侧输入 URL → **可选「抓取角色全部 Tab」**（Playwright 依次点「人物/修炼、技能、道具/法宝…」并结构化落库）→ **可选「深度爬取关联」**（再抓子商品详情）→ **分 Tab 可滚动展示** → **保存/更新**（同编号 upsert）
- **登录处理**：若检测到需要登录，弹窗提示后打开浏览器，手动登录后自动保存登录态并继续抓取
- **核心数据**：按规则从页面抽取（编号、价格、门派、亮点、修炼等）；角色类可带 `children[]` 关联子商品
- **落库**：`goods_record` 含 `product_type`、`parent_goods_no`；主商品带关联时调用 `save_goods_bundle` 写入主行 + 子行；兼容表 `page_data` 仍存扁平快照；详见 [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)
- **分类与扩展**：参考 `html/` 下各类型示例（`rule/` 角色、`zhaohuanshou/` 召唤兽、`daoju/` 武器、`lingshi/` 灵饰等），在 `cbg_catalog` / `cbg_classification` / `cbg_extractors` 中扩展新类型；关联 URL 抽取见 `character_links.py`

## 环境要求

- Python 3.8+
- 依赖见 `requirements.txt`

## 安装

### macOS（Homebrew Python 常见：无 tkinter）

若用 `brew install python@3.13` 装的 Python，默认**没有** Tk 图形库，运行 GUI 会报 `No module named '_tkinter'`。请先安装带 Tk 的解释器，并用它**重建**虚拟环境：

```bash
brew install python-tk@3.13
cd /path/to/mhb
rm -rf .venv
"$(brew --prefix python-tk@3.13)/bin/python3" -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

也可改用 [python.org](https://www.python.org/downloads/) 官方 macOS 安装包（自带 tkinter），再 `python3 -m venv .venv`。

### 通用

```bash
pip install -r requirements.txt
playwright install chromium
```

## 使用

### 启动桌面 GUI（推荐）

```bash
./run_gui.sh
```

或：

```bash
python3 gui_app.py
```

### 操作步骤

1. 在「页面地址」输入目标 URL（如藏宝阁商品页），按需勾选 **深度爬取关联（角色）**，回车或点击 **开始爬取**。
2. 若需登录：会弹出「需要登录」窗口，点击 **打开浏览器登录**，在浏览器中完成登录，程序检测到登录成功后会保存登录态并自动再次抓取。
3. 抓取完成后在右侧 **分 Tab 区域** 查看概览、基本信息、各板块、关联商品与完整 JSON（内容多时可滚动）。
4. 点击 **保存 / 更新到数据库**；同一 `goods_no` 会更新。左侧列表可点选已保存主商品查看详情（与爬取后共用同一展示组件）。

### 数据库

- 文件：`page_data.db`（首次保存时自动创建）
- **`goods_category`**：商品分类目录（角色 / 召唤兽 / 道具及子类），启动时从 `cbg_catalog.py` 种子数据写入
- **`goods_record`**：主表，`goods_no` 唯一；列含 `product_type`、`parent_goods_no`（关联子商品指向主角色）；`payload_json` 存 `basic` + `sections` + 可选 `children`
- **`page_data`**：兼容旧用法，存 `url`、`title`、`content`、`extracted_data`（扁平 JSON）

查看示例：

```bash
sqlite3 page_data.db "SELECT goods_no, product_type, parent_goods_no, category_code, sub_category_code, updated_at FROM goods_record;"
sqlite3 page_data.db "SELECT id, url, title, created_at FROM page_data;"
```

## 项目结构（核心）

```
mhb/
├── gui_app.py              # 桌面 GUI（列表 + 详情 + 保存）
├── gui_detail_view.py      # 可复用：分 Tab 商品详情展示
├── scrape_helper.py        # 抓取 + 规则抽取 + 可选角色关联深度爬取
├── character_links.py      # 从角色页 HTML 提取 equip 子链接
├── role_tabs.py            # 角色详情 div.tabs：切换各 li#role_* 并调用抽取器
├── item_name_catalog.py    # 灵饰/武器/装备名称枚举 → 类型属性（大类、细类、ITEM_* 子码）
├── login_state_manager.py  # 登录态管理（打开浏览器、保存/加载登录态）
├── playwright_scraper.py   # Playwright 抓取（支持登录态）
├── data_extractor.py       # 规则页数据抽取（infoList.goodsInfo、role_info_box 等）
├── cbg_catalog.py          # 分类目录定义（可扩展）
├── cbg_classification.py # 页面类型判定（DOM / kindid）
├── cbg_extractors.py       # 分类型结构化抽取（角色/召唤兽/道具）
├── database.py             # 数据库模型与保存（含 goods_record）
├── html/                   # 各类型页面样式样例（供抽取规则参考）
│   ├── daoju/              # 道具·武器等新模板（类型/状态/li.names + equip_desc_panel）
│   └── lingshi/            # 灵饰模板（类型：耳饰 等 + 展示ID=标准名）
├── DATABASE_SCHEMA.md      # 表结构与扩展说明
├── cookie_helper.py        # Cookie 工具（登录态内部使用）
├── run_gui.sh              # GUI 启动脚本
├── requirements.txt
└── page_data.db            # SQLite（运行后生成）
```

## 注意事项

- 请遵守目标站点的使用条款与访问频率，避免滥用。
- **登录态与 Cookie**：登录成功后会写入项目目录下的 `login_state_<域名>.json`（Playwright `storage_state`，内含 Cookie 及站点存储），下次「开始爬取」会自动加载，无需再手动贴 Cookie。
- 若登录态过期，会再次被重定向到登录页，按提示重新在浏览器中登录一次即可覆盖该文件。
- 桌面 GUI 依赖 **tkinter**；若报错 `_tkinter`，见上文「macOS（Homebrew Python 常见：无 tkinter）」。
