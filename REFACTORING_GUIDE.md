# 项目重构指南

## 新的项目结构

项目已按照领域驱动设计（DDD）原则重构，结构如下：

```
mhb/
├── src/                          # 源代码目录
│   ├── core/                     # 核心领域层
│   │   ├── scrapers/            # 抓取器（接口和实现）
│   │   │   ├── base.py          # 抽象基类
│   │   │   ├── requests_scraper.py
│   │   │   ├── selenium_scraper.py
│   │   │   └── playwright_scraper.py
│   │   └── extractors/          # 数据提取器
│   │       └── game_equip_extractor.py
│   ├── domain/                   # 领域模型层
│   │   └── entities/            # 实体
│   │       └── page_data.py     # 页面数据实体
│   ├── infrastructure/           # 基础设施层
│   │   ├── database/            # 数据库
│   │   │   ├── models.py        # ORM模型
│   │   │   └── repository.py    # 数据仓库
│   │   ├── browser/             # 浏览器管理
│   │   │   └── browser_manager.py
│   │   └── auth/                # 认证
│   │       ├── login_state_manager.py
│   │       └── cookie_helper.py
│   ├── application/              # 应用服务层
│   │   └── services/            # 业务服务
│   │       ├── scraping_service.py
│   │       └── data_service.py
│   ├── presentation/             # 表现层
│   │   ├── web/                 # Web界面
│   │   ├── cli/                 # 命令行
│   │   └── gui/                 # 桌面GUI
│   └── utils/                    # 工具类
│       └── logger.py
├── config/                       # 配置文件
│   └── settings.py
├── tests/                        # 测试
├── requirements.txt
└── README.md
```

## 架构说明

### 1. 核心领域层 (core)
- **scrapers/**: 抓取器接口和实现
  - `BaseScraper`: 抽象基类，定义统一接口
  - `RequestsScraper`: 基于requests的实现
  - `SeleniumScraper`: 基于Selenium的实现
  - `PlaywrightScraper`: 基于Playwright的实现
- **extractors/**: 数据提取器
  - `DataExtractor`: 游戏装备信息提取器

### 2. 领域模型层 (domain)
- **entities/**: 领域实体
  - `PageData`: 页面数据实体（纯业务对象，不依赖ORM）

### 3. 基础设施层 (infrastructure)
- **database/**: 数据库相关
  - `models.py`: SQLAlchemy ORM模型
  - `repository.py`: 数据仓库实现
- **browser/**: 浏览器管理
- **auth/**: 认证相关

### 4. 应用服务层 (application)
- **services/**: 业务服务
  - `ScrapingService`: 协调抓取和数据提取
  - `DataService`: 处理数据保存和查询

### 5. 表现层 (presentation)
- **web/**: Web界面（Flask）
- **cli/**: 命令行界面
- **gui/**: 桌面GUI

## 使用方式

### 导入示例

```python
# 使用核心领域层
from src.core.scrapers import RequestsScraper, PlaywrightScraper
from src.core.extractors import DataExtractor

# 使用应用服务
from src.application.services import ScrapingService, DataService

# 使用基础设施
from src.infrastructure.database import PageDataRepository
from src.infrastructure.browser import BrowserManager
from src.infrastructure.auth import LoginStateManager

# 使用领域实体
from src.domain.entities import PageData
```

### 服务使用示例

```python
from src.core.scrapers import PlaywrightScraper
from src.application.services import ScrapingService, DataService
from src.infrastructure.browser import BrowserManager

# 创建服务
browser_manager = BrowserManager()
page = browser_manager.get_page(storage_state_path='login_state.json')
scraper = PlaywrightScraper(page=page)  # 需要适配
scraping_service = ScrapingService(scraper)
data_service = DataService()

# 抓取并保存
page_data = scraping_service.scrape_and_extract(url)
if page_data:
    saved_data = data_service.save_page_data(page_data)
```

## 迁移指南

### 旧代码迁移

1. **导入路径更新**:
   - `from scraper import WebScraper` → `from src.core.scrapers import RequestsScraper`
   - `from database import DatabaseManager` → `from src.infrastructure.database import PageDataRepository`
   - `from data_extractor import DataExtractor` → `from src.core.extractors import DataExtractor`

2. **使用服务层**:
   - 不再直接使用 `DatabaseManager`，改用 `DataService`
   - 不再直接组合抓取器和提取器，改用 `ScrapingService`

3. **领域实体**:
   - 使用 `PageData` 实体而不是直接操作ORM模型

## 优势

1. **清晰的职责划分**: 每层都有明确的职责
2. **易于测试**: 接口和实现分离，便于mock
3. **易于扩展**: 新增抓取器只需实现 `BaseScraper`
4. **解耦**: 领域层不依赖基础设施，可以轻松切换数据库或ORM
5. **可维护性**: 代码组织清晰，易于理解和维护
