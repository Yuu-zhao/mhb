# 项目结构说明

## 重构后的项目架构

项目已按照**领域驱动设计（DDD）**原则重构，采用分层架构，职责清晰，易于维护和扩展。

## 目录结构

```
mhb/
├── src/                          # 源代码目录
│   ├── core/                     # 核心领域层 - 业务核心逻辑
│   │   ├── scrapers/            # 抓取器模块
│   │   │   ├── base.py          # 抽象基类（接口定义）
│   │   │   ├── requests_scraper.py
│   │   │   ├── selenium_scraper.py
│   │   │   └── playwright_scraper.py
│   │   └── extractors/          # 数据提取器
│   │       └── game_equip_extractor.py
│   │
│   ├── domain/                   # 领域模型层 - 业务实体
│   │   └── entities/            # 领域实体
│   │       └── page_data.py     # 页面数据实体（纯业务对象）
│   │
│   ├── infrastructure/           # 基础设施层 - 技术实现
│   │   ├── database/           # 数据库相关
│   │   │   ├── models.py       # ORM模型（SQLAlchemy）
│   │   │   └── repository.py   # 数据仓库实现
│   │   ├── browser/            # 浏览器管理
│   │   │   └── browser_manager.py
│   │   └── auth/               # 认证相关
│   │       ├── login_state_manager.py
│   │       └── cookie_helper.py
│   │
│   ├── application/              # 应用服务层 - 业务协调
│   │   └── services/            # 业务服务
│   │       ├── scraping_service.py  # 抓取服务
│   │       └── data_service.py      # 数据服务
│   │
│   ├── presentation/             # 表现层 - 用户界面
│   │   ├── web/                 # Web界面（Flask）
│   │   │   ├── app.py          # Flask应用
│   │   │   └── routes.py       # 路由定义
│   │   ├── cli/                # 命令行界面
│   │   │   └── main.py
│   │   └── gui/                # 桌面GUI（可选）
│   │
│   └── utils/                    # 工具类
│       └── logger.py
│
├── config/                       # 配置文件
│   └── settings.py              # 应用配置
│
├── tests/                        # 测试目录
│
├── run.py                        # 项目入口（Web GUI）
├── requirements.txt              # 依赖包
├── README.md                     # 项目说明
├── REFACTORING_GUIDE.md         # 重构指南
└── PROJECT_STRUCTURE.md        # 本文件
```

## 架构层次说明

### 1. 核心领域层 (core)
**职责**: 包含业务核心逻辑，不依赖外部技术实现

- **scrapers/**: 抓取器接口和实现
  - `BaseScraper`: 抽象基类，定义统一的抓取接口
  - `RequestsScraper`: 基于requests的实现
  - `SeleniumScraper`: 基于Selenium的实现
  - `PlaywrightScraper`: 基于Playwright的实现
- **extractors/**: 数据提取器
  - `DataExtractor`: 游戏装备信息提取器

### 2. 领域模型层 (domain)
**职责**: 定义业务实体和值对象，纯业务逻辑，不依赖ORM

- **entities/**: 领域实体
  - `PageData`: 页面数据实体（纯业务对象）

### 3. 基础设施层 (infrastructure)
**职责**: 提供技术实现，如数据库、浏览器管理等

- **database/**: 数据库相关
  - `models.py`: SQLAlchemy ORM模型
  - `repository.py`: 数据仓库实现（实现领域层的接口）
- **browser/**: 浏览器管理
- **auth/**: 认证相关

### 4. 应用服务层 (application)
**职责**: 协调领域对象，实现业务用例

- **services/**: 业务服务
  - `ScrapingService`: 协调抓取器和数据提取器
  - `DataService`: 处理数据保存和查询

### 5. 表现层 (presentation)
**职责**: 处理用户交互，调用应用服务

- **web/**: Web界面（Flask）
- **cli/**: 命令行界面
- **gui/**: 桌面GUI

## 依赖关系

```
presentation → application → domain
                ↓            ↑
            infrastructure
```

- **表现层** 依赖 **应用服务层**
- **应用服务层** 依赖 **领域层** 和 **基础设施层**
- **基础设施层** 实现领域层的接口
- **领域层** 不依赖任何其他层（最核心）

## 使用示例

### 1. 使用应用服务（推荐）

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

### 2. 直接使用核心领域层

```python
from src.core.scrapers import RequestsScraper
from src.core.extractors import DataExtractor

scraper = RequestsScraper()
extractor = DataExtractor()

page_data = scraper.fetch_page(url)
if page_data:
    extracted = extractor.extract_all_info(page_data['content'], url)
```

## 迁移指南

### 旧代码 → 新代码

| 旧代码 | 新代码 |
|--------|--------|
| `from scraper import WebScraper` | `from src.core.scrapers import RequestsScraper` |
| `from database import DatabaseManager` | `from src.infrastructure.database import PageDataRepository` |
| `from data_extractor import DataExtractor` | `from src.core.extractors import DataExtractor` |
| `DatabaseManager().save_page_data(...)` | `DataService().save_page_data(...)` |

## 优势

1. **清晰的职责划分**: 每层都有明确的职责，易于理解
2. **易于测试**: 接口和实现分离，便于单元测试和Mock
3. **易于扩展**: 新增抓取器只需实现 `BaseScraper` 接口
4. **解耦**: 领域层不依赖基础设施，可以轻松切换数据库或ORM
5. **可维护性**: 代码组织清晰，易于维护和重构
6. **业务聚焦**: 领域层专注于业务逻辑，不受技术细节影响

## 运行方式

### Web GUI
```bash
python run.py
# 或
python -m src.presentation.web.app
```

### 命令行
```bash
python -m src.presentation.cli.main <URL> --method playwright
```
