"""
商品数据仓库实现
提供商品及其关联领域实体的持久化接口
"""
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from typing import List, Optional
import logging
import json
from datetime import datetime

from .models import (
    Base, ProductModel, CharacterModel, ItemModel, PetModel,
    MountModel, AppearanceModel, HomeModel, RawPageDataModel
)
from ...domain.entities.product import Product
from ...domain.entities.character import Character
from ...domain.entities.item import Item
from ...domain.entities.pet import Pet
from ...domain.entities.mount import Mount
from ...domain.entities.appearance import Appearance
from ...domain.entities.home import Home

logger = logging.getLogger(__name__)


class ProductRepository:
    """商品数据仓库"""
    
    def __init__(self, db_path='page_data.db'):
        """
        初始化数据仓库
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self._ensure_tables_exist()
    
    def _ensure_tables_exist(self):
        """确保数据库表存在"""
        try:
            inspector = inspect(self.engine)
            existing_tables = inspector.get_table_names()
            
            required_tables = [
                'products', 'characters', 'items', 'pets',
                'mounts', 'appearances', 'homes', 'raw_page_data'
            ]
            
            missing_tables = [t for t in required_tables if t not in existing_tables]
            
            if missing_tables:
                logger.info(f"以下表不存在，正在创建: {missing_tables}")
                Base.metadata.create_all(self.engine, checkfirst=True)
                logger.info("所有表创建成功")
        except Exception as e:
            logger.error(f"检查/创建表时出错: {str(e)}")
            Base.metadata.create_all(self.engine, checkfirst=True)
    
    def save_product(self, product: Product, extracted_data: dict = None) -> Product:
        """
        保存商品及其关联的领域实体
        
        Args:
            product: 商品实体
            extracted_data: 原始提取数据（用于保存到raw_page_data和extracted_data_json）
            
        Returns:
            保存后的商品实体（包含ID）
        """
        session = self.SessionLocal()
        try:
            # 检查是否已存在（根据item_id）
            existing_product = None
            if product.item_id:
                existing_product = session.query(ProductModel).filter(
                    ProductModel.item_id == product.item_id
                ).first()
            
            if existing_product:
                # 更新现有商品
                product_model = existing_product
                product_model.url = product.url
                product_model.price = product.price
                product_model.seller_id = product.seller_id
                product_model.seller_name = product.seller_name
                product_model.listed_status = product.listed_status
                product_model.bargainable = product.bargainable
                product_model.time_remaining = product.time_remaining
                product_model.highlights = json.dumps(product.highlights, ensure_ascii=False) if product.highlights else None
                if extracted_data:
                    product_model.extracted_data_json = json.dumps(extracted_data, ensure_ascii=False, indent=2)
            else:
                # 创建新商品
                product_model = ProductModel(
                    item_id=product.item_id,
                    product_type=product.product_type,
                    url=product.url,
                    price=product.price,
                    seller_id=product.seller_id,
                    seller_name=product.seller_name,
                    listed_status=product.listed_status,
                    bargainable=product.bargainable,
                    time_remaining=product.time_remaining,
                    highlights=json.dumps(product.highlights, ensure_ascii=False) if product.highlights else None,
                    extracted_data_json=json.dumps(extracted_data, ensure_ascii=False, indent=2) if extracted_data else None,
                    created_at=product.created_at
                )
                session.add(product_model)
            
            session.flush()  # 获取product_id
            
            # 保存原始页面数据（如果提供）
            if extracted_data:
                raw_page_data = RawPageDataModel(
                    url=product.url,
                    title="",  # 可以从extracted_data中提取
                    content="",  # 可选：保存完整HTML
                    extracted_data_json=json.dumps(extracted_data, ensure_ascii=False, indent=2),
                    created_at=datetime.now()
                )
                session.add(raw_page_data)
            
            # 保存关联的领域实体
            if hasattr(product, 'character') and product.character:
                self._save_character(session, product_model.product_id, product.character, extracted_data)
            
            if hasattr(product, 'items') and product.items:
                self._save_items(session, product_model.product_id, product.items, extracted_data)
            
            if hasattr(product, 'pets') and product.pets:
                self._save_pets(session, product_model.product_id, product.pets, extracted_data)
            
            if hasattr(product, 'mount') and product.mount:
                self._save_mount(session, product_model.product_id, product.mount, extracted_data)
            
            if hasattr(product, 'appearance') and product.appearance:
                self._save_appearance(session, product_model.product_id, product.appearance, extracted_data)
            
            if hasattr(product, 'home') and product.home:
                self._save_home(session, product_model.product_id, product.home, extracted_data)
            
            session.commit()
            session.refresh(product_model)
            
            # 更新实体的ID
            product.product_id = product_model.product_id
            return product
            
        except Exception as e:
            session.rollback()
            logger.error(f"保存商品失败: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            session.close()
    
    def _save_character(self, session, product_id: int, character: Character, extracted_data: dict = None):
        """保存角色信息"""
        # 删除旧的记录
        session.query(CharacterModel).filter(CharacterModel.product_id == product_id).delete()
        
        character_model = CharacterModel(
            product_id=product_id,
            level=character.level,
            role_name=character.role_name,
            sect=character.sect,
            new_qianyuan_dan_count=character.new_qianyuan_dan_count,
            mooncake_zongzi_chance=character.mooncake_zongzi_chance,
            ascension_tribulation_sainthood=character.ascension_tribulation_sainthood,
            achievement_points=character.achievement_points,
            used_potential_fruit_count=character.used_potential_fruit_count,
            total_experience=character.total_experience,
            attack_cultivation=character.attack_cultivation,
            defense_cultivation=character.defense_cultivation,
            magic_cultivation=character.magic_cultivation,
            magic_resistance_cultivation=character.magic_resistance_cultivation,
            hunting_skill_cultivation=character.hunting_skill_cultivation,
            beast_rearing_skill=character.beast_rearing_skill,
            attack_control=character.attack_control,
            defense_control=character.defense_control,
            magic_control=character.magic_control,
            magic_resistance_control=character.magic_resistance_control,
            school_skills_json=json.dumps(character.school_skills, ensure_ascii=False) if character.school_skills else None,
            life_skills_json=json.dumps(character.life_skills, ensure_ascii=False) if character.life_skills else None,
            story_skills_json=json.dumps(character.story_skills, ensure_ascii=False) if character.story_skills else None,
            story_skill_remaining_points=character.story_skill_remaining_points,
            proficiency_json=json.dumps(character.proficiency, ensure_ascii=False) if character.proficiency else None,
            raw_data_json=json.dumps(character.raw_data, ensure_ascii=False) if character.raw_data else None
        )
        session.add(character_model)
    
    def _save_items(self, session, product_id: int, items: List[Item], extracted_data: dict = None):
        """保存道具信息"""
        # 删除旧的记录
        session.query(ItemModel).filter(ItemModel.product_id == product_id).delete()
        
        for item in items:
            item_model = ItemModel(
                product_id=product_id,
                name=item.name,
                item_type=item.item_type,
                description=item.description,
                icon_url=item.icon_url,
                is_equipped=item.is_equipped,
                category=item.category,
                raw_data_json=json.dumps(item.raw_data, ensure_ascii=False) if item.raw_data else None
            )
            session.add(item_model)
    
    def _save_pets(self, session, product_id: int, pets: List[Pet], extracted_data: dict = None):
        """保存召唤兽信息"""
        # 删除旧的记录
        session.query(PetModel).filter(PetModel.product_id == product_id).delete()
        
        for pet in pets:
            pet_model = PetModel(
                product_id=product_id,
                name=pet.name,
                pet_type=pet.pet_type,
                level=pet.level,
                is_baby=pet.is_baby,
                hp=pet.hp,
                mp=pet.mp,
                attack=pet.attack,
                defense=pet.defense,
                speed=pet.speed,
                magic_attack=pet.magic_attack,
                magic_defense=pet.magic_defense,
                growth=pet.growth,
                five_elements=pet.five_elements,
                aptitude_json=json.dumps(pet.aptitude, ensure_ascii=False) if pet.aptitude else None,
                skills_json=json.dumps(pet.skills, ensure_ascii=False) if pet.skills else None,
                inner_elixirs_json=json.dumps(pet.inner_elixirs, ensure_ascii=False) if pet.inner_elixirs else None,
                equips_json=json.dumps(pet.equips, ensure_ascii=False) if pet.equips else None,
                ornaments_json=json.dumps(pet.ornaments, ensure_ascii=False) if pet.ornaments else None,
                raw_data_json=json.dumps(pet.raw_data, ensure_ascii=False) if pet.raw_data else None
            )
            session.add(pet_model)
    
    def _save_mount(self, session, product_id: int, mount: Mount, extracted_data: dict = None):
        """保存坐骑信息"""
        # 删除旧的记录
        session.query(MountModel).filter(MountModel.product_id == product_id).delete()
        
        mount_model = MountModel(
            product_id=product_id,
            name=mount.name,
            mount_type=mount.mount_type,
            level=mount.level,
            main_attribute=mount.main_attribute,
            growth=mount.growth,
            skills_json=json.dumps(mount.skills, ensure_ascii=False) if mount.skills else None,
            xuanlingzhu_json=json.dumps(mount.xuanlingzhu, ensure_ascii=False) if mount.xuanlingzhu else None,
            auspicious_beast_skill=mount.auspicious_beast_skill,
            raw_data_json=json.dumps(mount.raw_data, ensure_ascii=False) if mount.raw_data else None
        )
        session.add(mount_model)
    
    def _save_appearance(self, session, product_id: int, appearance: Appearance, extracted_data: dict = None):
        """保存外观信息"""
        # 删除旧的记录
        session.query(AppearanceModel).filter(AppearanceModel.product_id == product_id).delete()
        
        appearance_model = AppearanceModel(
            product_id=product_id,
            dyed_fruit_count=appearance.dyed_fruit_count,
            saved_dye_schemes=appearance.saved_dye_schemes,
            total_dyed_fruit_count=appearance.total_dyed_fruit_count,
            title_effects_json=json.dumps(appearance.title_effects, ensure_ascii=False) if appearance.title_effects else None,
            spell_attack_effects_json=json.dumps(appearance.spell_attack_effects, ensure_ascii=False) if appearance.spell_attack_effects else None,
            bubble_frames_json=json.dumps(appearance.bubble_frames, ensure_ascii=False) if appearance.bubble_frames else None,
            avatar_frames_json=json.dumps(appearance.avatar_frames, ensure_ascii=False) if appearance.avatar_frames else None,
            team_logos_json=json.dumps(appearance.team_logos, ensure_ascii=False) if appearance.team_logos else None,
            xianyu_balance=appearance.xianyu_balance,
            xianyu_points=appearance.xianyu_points,
            qicai_points=appearance.qicai_points,
            total_outfits_count=appearance.total_outfits_count,
            limited_outfits_json=json.dumps(appearance.limited_outfits, ensure_ascii=False) if appearance.limited_outfits else None,
            pendants_json=json.dumps(appearance.pendants, ensure_ascii=False) if appearance.pendants else None,
            normal_outfits_json=json.dumps(appearance.normal_outfits, ensure_ascii=False) if appearance.normal_outfits else None,
            raw_data_json=json.dumps(appearance.raw_data, ensure_ascii=False) if appearance.raw_data else None
        )
        session.add(appearance_model)
    
    def _save_home(self, session, product_id: int, home: Home, extracted_data: dict = None):
        """保存玩家之家信息"""
        # 删除旧的记录
        session.query(HomeModel).filter(HomeModel.product_id == product_id).delete()
        
        home_model = HomeModel(
            product_id=product_id,
            house_level=home.house_level,
            house_stability=home.house_stability,
            house_fengshui=home.house_fengshui,
            house_type=home.house_type,
            furniture_score=home.furniture_score,
            raw_data_json=json.dumps(home.raw_data, ensure_ascii=False) if home.raw_data else None
        )
        session.add(home_model)
    
    def find_by_item_id(self, item_id: str) -> Optional[Product]:
        """根据item_id查找商品"""
        session = self.SessionLocal()
        try:
            model = session.query(ProductModel).filter(ProductModel.item_id == item_id).first()
            return self._model_to_entity(model) if model else None
        finally:
            session.close()
    
    def find_all(self) -> List[Product]:
        """获取所有商品"""
        session = self.SessionLocal()
        try:
            models = session.query(ProductModel).all()
            return [self._model_to_entity(m) for m in models]
        finally:
            session.close()
    
    def _model_to_entity(self, model: ProductModel) -> Product:
        """将ORM模型转换为领域实体"""
        highlights = None
        if model.highlights:
            try:
                highlights = json.loads(model.highlights)
            except:
                highlights = model.highlights.split(',') if ',' in model.highlights else [model.highlights]
        
        extracted_data = None
        if model.extracted_data_json:
            try:
                extracted_data = json.loads(model.extracted_data_json)
            except:
                pass
        
        product = Product(
            product_id=model.product_id,
            item_id=model.item_id,
            product_type=model.product_type,
            url=model.url,
            price=model.price,
            seller_id=model.seller_id,
            seller_name=model.seller_name,
            listed_status=model.listed_status,
            bargainable=model.bargainable,
            time_remaining=model.time_remaining,
            highlights=highlights,
            extracted_data=extracted_data,
            created_at=model.created_at
        )
        
        # 加载关联的领域实体（如果需要）
        # 这里可以根据需要加载character, items, pets等
        
        return product
