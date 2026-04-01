# 数据库设计（藏宝阁商品）

## 设计原则

- **可扩展分类**：`goods_category` 存目录树，新增业务类型时只插入分类行 + 可选扩展 `cbg_classification` / `kindid` 映射。
- **结构化载荷**：`goods_record.payload_json` 存完整 JSON（`basic` + `sections`），列上只存 **编号、URL、分类** 便于查询与索引。
- **兼容旧数据**：`page_data` 仍保留扁平快照，便于历史兼容。

## 表说明

### `goods_category`

| 字段 | 说明 |
|------|------|
| `code` | 主键，稳定英文编码（如 `CHAR`、`ITEM_WEAPON`） |
| `parent_code` | 父级分类，根节点为 NULL |
| `name_zh` | 中文名 |
| `sort_order` | 排序 |

种子数据来自 `cbg_catalog.py` 的 `CATEGORIES`。

### `goods_record`

| 字段 | 说明 |
|------|------|
| `goods_no` | **业务唯一键**（藏宝阁编号；缺省时用 URL 中 `eid`） |
| `source_url` | 商品链接，唯一 |
| `category_code` | 一级分类（`CHAR` 角色 / `SUMMON` 召唤兽 / `ITEM` 道具） |
| `sub_category_code` | 道具子类（武器、灵饰等），可为空 |
| `product_type` | 与 `category_code` 同语义，便于展示与查询（CHAR/ITEM/SUMMON） |
| `parent_goods_no` | 若本行由**角色详情深度爬取**写入的关联商品（装备/召唤兽等），指向主角色 `goods_no`；主商品此列为空 |
| `payload_json` | 结构化数据：`basic`、`sections`、`classification`（含 `item_name_resolution`：按装备名称枚举解析的大类/细类/子类码）、可选 `character_tabs`、可选 `children` 等 |
| `schema_version` | 载荷版本，便于后续迁移 |

**关联入库**：保存带 `children[]` 的主商品时，调用 `DatabaseManager.save_goods_bundle`：主行一条 + 每个子商品单独 upsert 一行并写入 `parent_goods_no`。

### `page_data`（旧）

保留 `url`、`title`、`content`、`extracted_data`（扁平展示用）。

## 扩展新类型

1. 在 `cbg_catalog.CATEGORIES` 里增加 `(code, parent_code, name_zh, sort_order)`。
2. 若通过 `kindid` 区分：在 `KINDID_TO_ITEM_SUBCATEGORY`（或等价映射）中增加。
3. 若通过 DOM：在 `cbg_classification.classify_cbg_page` 中增加分支。
4. 在 `cbg_extractors.extract_structured_payload` 的 `sections` 中增加对应字段。
