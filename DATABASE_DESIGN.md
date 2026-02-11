# 数据库设计文档

## 设计原则

按照领域驱动设计（DDD）原则，将数据划分为：
- **商品（Product）**：顶层实体，代表一个可交易的商品
- **领域实体**：角色、道具、召唤兽、孩子、坐骑、锦衣、玩家之家等

## 数据库表结构

### 1. 商品表（products）

```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_type VARCHAR(50) NOT NULL,  -- 商品类型：role(角色), equipment(道具), pet(召唤兽), child(孩子), mount(坐骑), appearance(锦衣), home(玩家之家)
    url TEXT NOT NULL UNIQUE,           -- 商品URL
    title VARCHAR(500),                 -- 商品标题
    product_id VARCHAR(100),            -- 商品编号（从页面提取）
    seller VARCHAR(200),                -- 卖家
    seller_id VARCHAR(100),             -- 卖家ID
    price DECIMAL(12, 2),              -- 价格
    is_listed BOOLEAN,                  -- 是否上架
    can_bargain BOOLEAN,                -- 是否接受还价
    time_remaining VARCHAR(50),         -- 出售剩余时间
    highlights TEXT,                    -- 亮点（JSON数组）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. 角色信息表（role_info）

```sql
CREATE TABLE role_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,        -- 关联商品ID
    level INTEGER,                      -- 级别
    role_name VARCHAR(100),            -- 角色名称
    school VARCHAR(50),                -- 门派
    qianyuan_dan_count INTEGER,        -- 新版乾元丹数量
    mooncake_chance VARCHAR(50),        -- 月饼粽子机缘
    ascension_status VARCHAR(50),      -- 飞升/渡劫/化圣
    achievement_points INTEGER,         -- 成就点数
    used_potential_fruit INTEGER,        -- 已用潜能果数量
    total_experience VARCHAR(50),       -- 总经验
    attack_cultivation VARCHAR(50),     -- 攻击修炼
    defense_cultivation VARCHAR(50),    -- 防御修炼
    magic_cultivation VARCHAR(50),      -- 法术修炼
    magic_resistance_cultivation VARCHAR(50), -- 抗法修炼
    hunting_cultivation VARCHAR(50),    -- 猎术修炼
    beast_rearing VARCHAR(50),          -- 育兽术
    attack_control VARCHAR(50),         -- 攻击控制力
    defense_control VARCHAR(50),         -- 防御控制力
    magic_control VARCHAR(50),           -- 法术控制力
    magic_resistance_control VARCHAR(50), -- 抗法控制力
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);
```

### 3. 技能信息表（skill_info）

```sql
CREATE TABLE skill_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,        -- 关联商品ID
    skill_type VARCHAR(50) NOT NULL,    -- 技能类型：school(师门), life(生活), juqing(剧情)
    skill_name VARCHAR(100) NOT NULL,   -- 技能名称
    skill_level INTEGER,                -- 技能等级
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE(product_id, skill_type, skill_name)
);

CREATE TABLE skill_proficiency (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,        -- 关联商品ID
    proficiency_type VARCHAR(100),      -- 熟练度类型（如：打造熟练度）
    proficiency_value VARCHAR(100),     -- 熟练度值
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);
```

### 4. 道具信息表（equipment_info）

```sql
CREATE TABLE equipment_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,        -- 关联商品ID
    equipment_type VARCHAR(50) NOT NULL, -- 道具类型：equipment(装备), shenqi(神器), lingbao(灵宝), fabao(法宝)
    equipment_name VARCHAR(200),       -- 道具名称
    equipment_desc TEXT,                -- 道具描述
    is_equipped BOOLEAN DEFAULT 0,      -- 是否已装备
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE TABLE equipment_currency (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,        -- 关联商品ID
    currency_type VARCHAR(50),         -- 货币类型：现金、存银、储备、善恶、仙玉、精力
    currency_value VARCHAR(100),       -- 货币值
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);
```

### 5. 召唤兽信息表（pet_info）

```sql
CREATE TABLE pet_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,        -- 关联商品ID
    pet_type VARCHAR(100),              -- 类型（如：毗舍童子）
    level INTEGER,                       -- 等级
    is_baby BOOLEAN,                    -- 是否宝宝
    hp INTEGER,                         -- 气血
    mp INTEGER,                         -- 魔法
    attack INTEGER,                     -- 攻击
    defense INTEGER,                    -- 防御
    speed INTEGER,                      -- 速度
    magic_damage INTEGER,               -- 法伤
    magic_defense INTEGER,              -- 法防
    constitution INTEGER,               -- 体质
    magic_power INTEGER,                 -- 法力
    strength INTEGER,                   -- 力量
    endurance INTEGER,                 -- 耐力
    agility INTEGER,                    -- 敏捷
    potential INTEGER,                  -- 潜能
    growth DECIMAL(5, 3),               -- 成长
    attack_aptitude INTEGER,             -- 攻击资质
    defense_aptitude INTEGER,            -- 防御资质
    hp_aptitude INTEGER,                -- 体力资质
    magic_aptitude INTEGER,              -- 法力资质
    speed_aptitude INTEGER,              -- 速度资质
    dodge_aptitude INTEGER,              -- 躲闪资质
    element VARCHAR(10),                 -- 五行
    lifespan INTEGER,                   -- 寿命
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE TABLE pet_skill (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pet_id INTEGER NOT NULL,            -- 关联召唤兽ID
    skill_name VARCHAR(100),            -- 技能名称
    skill_type VARCHAR(50),             -- 技能类型：cifu(赐福), normal(普通)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pet_id) REFERENCES pet_info(id) ON DELETE CASCADE
);

CREATE TABLE pet_neidan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pet_id INTEGER NOT NULL,            -- 关联召唤兽ID
    neidan_name VARCHAR(100),          -- 内丹名称
    neidan_level INTEGER,               -- 内丹等级
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pet_id) REFERENCES pet_info(id) ON DELETE CASCADE
);
```

### 6. 孩子信息表（child_info）

```sql
CREATE TABLE child_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,        -- 关联商品ID
    child_type VARCHAR(100),            -- 孩子类型
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);
```

### 7. 坐骑信息表（mount_info）

```sql
CREATE TABLE mount_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,        -- 关联商品ID
    mount_type VARCHAR(100),           -- 坐骑类型（如：披甲战狼）
    level INTEGER,                      -- 等级
    growth DECIMAL(8, 4),               -- 成长
    main_attribute VARCHAR(50),        -- 主属性
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE TABLE mount_skill (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mount_id INTEGER NOT NULL,          -- 关联坐骑ID
    skill_name VARCHAR(100),            -- 技能名称
    skill_level INTEGER,                 -- 技能等级
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mount_id) REFERENCES mount_info(id) ON DELETE CASCADE
);

CREATE TABLE mount_xianrui (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,        -- 关联商品ID
    xianrui_type VARCHAR(50),           -- 祥瑞类型：limited(限量), normal(普通)
    xianrui_name VARCHAR(100),          -- 祥瑞名称
    xianrui_skill VARCHAR(200),         -- 祥瑞技能
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);
```

### 8. 锦衣信息表（appearance_info）

```sql
CREATE TABLE appearance_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,        -- 关联商品ID
    appearance_type VARCHAR(50),       -- 外观类型：jinyi(锦衣), title_effect(称谓特效), cast_effect(施法特效), bubble(冒泡框), avatar(头像框), decoration(彩饰)
    appearance_name VARCHAR(200),       -- 外观名称
    appearance_category VARCHAR(100),   -- 分类（如：限量、挂件、普通锦衣）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE TABLE appearance_dye (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,        -- 关联商品ID
    body_dye_count INTEGER,              -- 身上染色折算彩果数
    wardrobe_saved_count INTEGER,       -- 衣柜已保存染色方案
    total_dye_count INTEGER,            -- 所有染色折算彩果数
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);
```

### 9. 玩家之家信息表（home_info）

```sql
CREATE TABLE home_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,        -- 关联商品ID
    home_level INTEGER,                  -- 房屋等级
    home_type VARCHAR(100),             -- 房屋类型
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);
```

## 索引设计

```sql
-- 商品表索引
CREATE INDEX idx_products_type ON products(product_type);
CREATE INDEX idx_products_url ON products(url);
CREATE INDEX idx_products_seller_id ON products(seller_id);

-- 角色信息索引
CREATE INDEX idx_role_info_product_id ON role_info(product_id);

-- 技能信息索引
CREATE INDEX idx_skill_info_product_id ON skill_info(product_id);
CREATE INDEX idx_skill_info_type ON skill_info(skill_type);

-- 道具信息索引
CREATE INDEX idx_equipment_info_product_id ON equipment_info(product_id);
CREATE INDEX idx_equipment_info_type ON equipment_info(equipment_type);

-- 召唤兽信息索引
CREATE INDEX idx_pet_info_product_id ON pet_info(product_id);
CREATE INDEX idx_pet_skill_pet_id ON pet_skill(pet_id);
```

## 数据关系图

```
products (商品)
├── role_info (角色信息)
│   └── skill_info (技能信息)
│   └── skill_proficiency (熟练度)
├── equipment_info (道具信息)
│   └── equipment_currency (货币信息)
├── pet_info (召唤兽信息)
│   ├── pet_skill (召唤兽技能)
│   └── pet_neidan (内丹)
├── child_info (孩子信息)
├── mount_info (坐骑信息)
│   ├── mount_skill (坐骑技能)
│   └── mount_xianrui (祥瑞)
├── appearance_info (锦衣信息)
│   └── appearance_dye (染色信息)
└── home_info (玩家之家信息)
```
