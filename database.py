"""
数据库模型和操作
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()


class PageData(Base):
    """页面数据表（兼容旧版：原始 HTML 摘要 + 扁平 JSON）"""
    __tablename__ = 'page_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(500), nullable=False, index=True)
    title = Column(String(500))
    content = Column(Text)
    extracted_data = Column(Text)  # 核心提取数据 JSON
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<PageData(id={self.id}, url='{self.url}', title='{self.title}')>"


class GoodsCategory(Base):
    """
    商品分类目录（可扩展）
    code 稳定标识；新增类型时插入新行即可。
    """
    __tablename__ = "goods_category"

    code = Column(String(64), primary_key=True)
    parent_code = Column(String(64), nullable=True, index=True)
    name_zh = Column(String(128), nullable=False)
    sort_order = Column(Integer, default=0)


class GoodsRecord(Base):
    """
    商品主表：编号业务唯一 + 链接唯一，分类 + JSON 载荷分块存储
    product_type: 与 category_code 一致语义（CHAR/ITEM/SUMMON），便于查询展示
    parent_goods_no: 角色商品关联的道具/召唤兽等子商品时，指向主角色编号
    """
    __tablename__ = "goods_record"

    id = Column(Integer, primary_key=True, autoincrement=True)
    goods_no = Column(String(128), nullable=False, unique=True, index=True)
    source_url = Column(String(1024), nullable=False, unique=True, index=True)
    category_code = Column(String(64), nullable=False, index=True)
    sub_category_code = Column(String(64), nullable=True, index=True)
    product_type = Column(String(32), nullable=True, index=True)  # CHAR / ITEM / SUMMON
    parent_goods_no = Column(String(128), nullable=True, index=True)
    title = Column(String(500), nullable=True)
    schema_version = Column(Integer, default=1)
    payload_json = Column(Text, nullable=False)  # 完整结构化数据（basic + sections + 分类）
    raw_html_digest = Column(String(64), nullable=True)  # 可选：内容摘要哈希
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<GoodsRecord(id={self.id}, goods_no={self.goods_no}, category={self.category_code})>"


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path='page_data.db'):
        """
        初始化数据库连接
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        # 确保表被创建
        self._ensure_tables_exist()
    
    def _ensure_tables_exist(self):
        """确保数据库表存在，如果不存在则创建"""
        try:
            inspector = inspect(self.engine)
            existing_tables = inspector.get_table_names()
            
            if 'page_data' not in existing_tables:
                logger.info("表 page_data 不存在，正在创建...")
                Base.metadata.create_all(self.engine, checkfirst=True)
                logger.info("表 page_data 创建成功")
            else:
                logger.debug("表 page_data 已存在")
                # 兼容旧表：若无 extracted_data 列则添加
                cols = [c.get('name', getattr(c, 'name', '')) for c in inspector.get_columns('page_data')]
                if 'extracted_data' not in cols:
                    try:
                        with self.engine.connect() as conn:
                            conn.execute(text("ALTER TABLE page_data ADD COLUMN extracted_data TEXT"))
                            conn.commit()
                        logger.info("已添加列 page_data.extracted_data")
                    except Exception as alter_e:
                        logger.warning(f"添加 extracted_data 列失败（可忽略）: {alter_e}")

            # 新表：goods_category / goods_record
            Base.metadata.create_all(self.engine, tables=[GoodsCategory.__table__, GoodsRecord.__table__], checkfirst=True)
            self._migrate_goods_record_columns()
            self._seed_goods_categories()
        except Exception as e:
            logger.error(f"检查/创建表时出错: {str(e)}")
            # 如果检查失败，尝试直接创建
            try:
                Base.metadata.create_all(self.engine, checkfirst=True)
                logger.info("表创建完成")
                self._seed_goods_categories()
            except Exception as e2:
                logger.error(f"创建表失败: {str(e2)}")
                raise

    def _migrate_goods_record_columns(self):
        """SQLite 增量迁移：为旧库添加 product_type / parent_goods_no"""
        try:
            inspector = inspect(self.engine)
            if "goods_record" not in inspector.get_table_names():
                return
            cols = {c["name"] for c in inspector.get_columns("goods_record")}
            with self.engine.connect() as conn:
                if "product_type" not in cols:
                    conn.execute(text("ALTER TABLE goods_record ADD COLUMN product_type VARCHAR(32)"))
                    conn.commit()
                    logger.info("已添加列 goods_record.product_type")
                if "parent_goods_no" not in cols:
                    conn.execute(text("ALTER TABLE goods_record ADD COLUMN parent_goods_no VARCHAR(128)"))
                    conn.commit()
                    logger.info("已添加列 goods_record.parent_goods_no")
            # 回填 product_type
            with self.engine.connect() as conn:
                conn.execute(
                    text(
                        "UPDATE goods_record SET product_type = category_code "
                        "WHERE product_type IS NULL OR product_type = ''"
                    )
                )
                conn.commit()
        except Exception as e:
            logger.warning("goods_record 迁移（可忽略）: %s", e)

    def _seed_goods_categories(self):
        """写入分类目录（仅缺失时插入，便于扩展）"""
        try:
            from cbg_catalog import CATEGORIES
        except Exception as e:
            logger.warning("无法加载 cbg_catalog: %s", e)
            return
        session = self.get_session()
        try:
            for code, parent, name_zh, sort_order in CATEGORIES:
                row = session.query(GoodsCategory).filter(GoodsCategory.code == code).first()
                if not row:
                    session.add(
                        GoodsCategory(
                            code=code,
                            parent_code=parent,
                            name_zh=name_zh,
                            sort_order=sort_order,
                        )
                    )
            session.commit()
        except Exception as e:
            session.rollback()
            logger.warning("分类种子数据写入失败: %s", e)
        finally:
            session.close()
    
    def get_session(self):
        """获取数据库会话"""
        return self.SessionLocal()
    
    def save_page_data(self, url, title, content=None, extracted_data=None):
        """
        保存页面数据到数据库（优化版：优先保存提取的数据）
        
        Args:
            url: 页面URL
            title: 页面标题
            content: 页面内容（可选，如果提供了extracted_data，content可以只保存部分内容）
            extracted_data: 提取的结构化数据（字典或JSON字符串），优先保存
            
        Returns:
            PageData对象
        """
        session = self.get_session()
        try:
            # 将extracted_data转换为JSON字符串
            import json
            extracted_json = None
            if extracted_data:
                if isinstance(extracted_data, dict):
                    extracted_json = json.dumps(extracted_data, ensure_ascii=False, indent=2)
                else:
                    extracted_json = str(extracted_data)
            
            # 如果提供了extracted_data，content可以只保存摘要或为空
            # 这样可以节省数据库空间
            if extracted_data and content:
                # 只保存前10000字符作为参考
                if len(content) > 10000:
                    content = content[:10000] + "\n\n... (内容已截断，关键信息已提取)"
            
            page_data = PageData(
                url=url,
                title=title,
                content=content,
                extracted_data=extracted_json,
                created_at=datetime.now()
            )
            session.add(page_data)
            session.commit()
            session.refresh(page_data)
            return page_data
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_all_data(self):
        """获取所有页面数据"""
        session = self.get_session()
        try:
            return session.query(PageData).all()
        finally:
            session.close()
    
    def get_data_by_url(self, url):
        """根据URL获取数据"""
        session = self.get_session()
        try:
            return session.query(PageData).filter(PageData.url == url).first()
        finally:
            session.close()

    def save_goods_record(self, payload: dict, title: str = None, parent_goods_no: str = None):
        """
        保存/更新规范商品记录（按 goods_no 唯一 upsert）

        Args:
            payload: cbg_extractors.extract_structured_payload 的输出
            title: 页面标题（可选）
            parent_goods_no: 父商品编号（角色关联子商品时使用）；也可在 payload.parent_goods_no 中提供
        """
        import json

        goods_no = (payload or {}).get("goods_no")
        if not goods_no:
            raise ValueError("结构化数据中缺少 goods_no（编号），无法写入 goods_record")

        url = payload.get("source_url") or ""
        cat = payload.get("category_code") or "ITEM"
        sub = payload.get("sub_category_code")
        ptype = (payload.get("product_type") or cat or "ITEM")[:32]
        parent = parent_goods_no or payload.get("parent_goods_no")
        if parent:
            parent = str(parent)
        body = json.dumps(payload, ensure_ascii=False, indent=2)

        session = self.get_session()
        try:
            rec = session.query(GoodsRecord).filter(GoodsRecord.goods_no == str(goods_no)).first()
            now = datetime.now()
            if rec:
                rec.source_url = url
                rec.category_code = cat
                rec.sub_category_code = sub
                rec.product_type = ptype
                if parent is not None:
                    rec.parent_goods_no = parent
                rec.title = title or rec.title
                rec.payload_json = body
                rec.schema_version = int(payload.get("schema_version") or 1)
                rec.updated_at = now
            else:
                rec = GoodsRecord(
                    goods_no=str(goods_no),
                    source_url=url,
                    category_code=cat,
                    sub_category_code=sub,
                    product_type=ptype,
                    parent_goods_no=parent,
                    title=title,
                    schema_version=int(payload.get("schema_version") or 1),
                    payload_json=body,
                    created_at=now,
                    updated_at=now,
                )
                session.add(rec)
            session.commit()
            session.refresh(rec)
            return rec
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def save_goods_bundle(self, main_payload: dict, title: str = None):
        """
        保存主商品（含 payload 内 children 嵌套）并逐条 upsert 子商品行。

        子商品在数据库中单独成行，parent_goods_no 指向主商品 goods_no；
        主商品 payload_json 仍保留完整 children 数组便于展示。
        """
        import json
        import copy

        main = copy.deepcopy(main_payload or {})
        children = main.get("children")
        if not isinstance(children, list):
            children = []

        main_no = main.get("goods_no")
        if not main_no:
            raise ValueError("主商品缺少 goods_no")

        main_rec = self.save_goods_record(main, title=title, parent_goods_no=None)

        for ch in children:
            if not isinstance(ch, dict):
                continue
            cno = ch.get("goods_no")
            if not cno:
                continue
            ch = copy.deepcopy(ch)
            ch["parent_goods_no"] = str(main_no)
            ch.pop("children", None)  # 子行不再嵌套下一层，避免重复入库
            self.save_goods_record(ch, title=title, parent_goods_no=str(main_no))

        return main_rec

    def get_goods_by_no(self, goods_no: str):
        session = self.get_session()
        try:
            return session.query(GoodsRecord).filter(GoodsRecord.goods_no == goods_no).first()
        finally:
            session.close()

    def list_goods_records(self, limit: int = 200, roots_only: bool = True):
        """
        roots_only=True 时仅列出无主商品的记录（主商品列表，避免角色下道具重复刷屏）
        """
        session = self.get_session()
        try:
            q = session.query(GoodsRecord)
            if roots_only:
                q = q.filter(
                    (GoodsRecord.parent_goods_no.is_(None)) | (GoodsRecord.parent_goods_no == "")
                )
            return q.order_by(GoodsRecord.updated_at.desc()).limit(limit).all()
        finally:
            session.close()
