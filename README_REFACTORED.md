# 网页抓取工具 - 重构版

## 📁 项目结构

项目已按照**领域驱动设计（DDD）**原则重构，采用清晰的分层架构：

```
mhb/
├── src/                          # 源代码
│   ├── core/                     # 核心领域层
│   │   ├── scrapers/            # 抓取器（接口+实现）
│   │   └── extractors/          # 数据提取器
│   ├── domain/                   # 领域模型层
│   │   └── entities/            # 业务实体
│   ├── infrastructure/           # 基础设施层
│   │   ├── database/            # 数据库
│   │   ├── browser/             # 浏览器管理
│   │   └── auth/                # 认证
│   ├── application/              # 应用服务层
│   │   └── services/            # 业务服务
│   ├── presentation/             # 表现层
│   │   ├── web/                 # Web界面
│   │   └── cli/                 # 命令行
│   └── utils/                    # 工具类
├── config/                       # 配置
└── tests/                        # 测试
```

## 🚀 快速开始

### Web GUI（推荐）

```bash
python run.py
```

访问：http://127.0.0.1:5000

### 命令行

```bash
python -m src.presentation.cli.main <URL> --method playwright
```

## 📦 模块说明

### 核心领域层 (core)

**职责**: 业务核心逻辑，不依赖外部技术

- `scrapers/`: 抓取器接口和实现
  - `BaseScraper`: 抽象基类
  - `RequestsScraper`: requests实现
  - `SeleniumScraper`: Selenium实现
  - `PlaywrightScraper`: Playwright实现
- `extractors/`: 数据提取器
  - `DataExtractor`: 游戏装备信息提取

### 领域模型层 (domain)

**职责**: 业务实体定义

- `entities/PageData`: 页面数据实体（纯业务对象）

### 基础设施层 (infrastructure)

**职责**: 技术实现

- `database/`: 数据库（ORM模型 + Repository）
- `browser/`: 浏览器管理（BrowserManager）
- `auth/`: 认证（LoginStateManager, CookieHelper）

### 应用服务层 (application)

**职责**: 业务协调

- `services/ScrapingService`: 抓取服务
- `services/DataService`: 数据服务

### 表现层 (presentation)

**职责**: 用户界面

- `web/`: Web界面（Flask）
- `cli/`: 命令行界面

## 💡 使用示例

### 使用应用服务（推荐）

```python
from src.core.scrapers import PlaywrightScraper
from src.application.services import ScrapingService, DataService
from src.infrastructure.database import PageDataRepository
from src.infrastructure.browser import BrowserManager

# 创建服务
browser_manager = BrowserManager()
page = browser_manager.get_page(storage_state_path='login_state.json')
scraper = PlaywrightScraper(page=page)
scraping_service = ScrapingService(scraper)
data_service = DataService(PageDataRepository())

# 抓取并保存
page_data = scraping_service.scrape_and_extract(url)
if page_data:
    saved_data = data_service.save_page_data(page_data)
```

## 🔄 迁移指南

### 旧代码迁移

| 旧代码 | 新代码 |
|--------|--------|
| `from scraper import WebScraper` | `from src.core.scrapers import RequestsScraper` |
| `from database import DatabaseManager` | `from src.infrastructure.database import PageDataRepository` |
| `DatabaseManager().save_page_data(...)` | `DataService().save_page_data(...)` |

详细迁移指南请参考 `REFACTORING_GUIDE.md`

## ✨ 架构优势

1. **清晰的职责划分**: 每层职责明确
2. **易于测试**: 接口和实现分离
3. **易于扩展**: 新增功能只需实现接口
4. **解耦**: 领域层不依赖基础设施
5. **可维护性**: 代码组织清晰

## 📚 文档

- `PROJECT_STRUCTURE.md`: 详细的项目结构说明
- `REFACTORING_GUIDE.md`: 重构指南和迁移说明
- `README.md`: 原始文档（保留）
