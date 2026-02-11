"""
数据库模型（SQLAlchemy ORM）
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

Base = declarative_base()


# ==============================================================================
# 原始页面数据模型 (Raw Page Data Model)
# 用于存储原始抓取到的页面内容，作为历史记录和调试用途
# ==============================================================================
class RawPageDataModel(Base):
    """原始页面数据表模型（ORM）"""
    __tablename__ = 'raw_page_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(500), nullable=False, index=True)
    title = Column(String(500))
    content = Column(Text)
    extracted_data_json = Column(Text)  # JSON格式的提取数据，存储所有标签页的原始提取结果
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<RawPageDataModel(id={self.id}, url='{self.url}', title='{self.title}')>"


# 向后兼容：保留旧名称的别名
PageDataModel = RawPageDataModel


# ==============================================================================
# 领域模型 (Domain Models)
# 对应用户定义的领域划分：商品、角色、道具、召唤兽、坐骑、锦衣/外观、玩家之家
# ==============================================================================

class ProductModel(Base):
    """商品表模型"""
    __tablename__ = 'products'

    product_id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(String(100), nullable=False, unique=True, index=True) # 对应藏宝阁的编号eid
    product_type = Column(String(50), nullable=False) # 角色, 道具, 召唤兽等
    url = Column(String(500), nullable=False)
    price = Column(Float)
    seller_id = Column(String(100))
    seller_name = Column(String(100))
    listed_status = Column(String(50))
    bargainable = Column(Boolean)
    time_remaining = Column(String(100))
    highlights = Column(Text) # 存储JSON字符串或逗号分隔
    extracted_data_json = Column(Text) # 存储所有原始提取数据，JSON格式
    created_at = Column(DateTime, default=datetime.now)

    # 建立与子领域模型的关系
    character = relationship("CharacterModel", back_populates="product", uselist=False, cascade="all, delete-orphan")
    items = relationship("ItemModel", back_populates="product", cascade="all, delete-orphan")
    pets = relationship("PetModel", back_populates="product", cascade="all, delete-orphan")
    mounts = relationship("MountModel", back_populates="product", cascade="all, delete-orphan")
    appearance = relationship("AppearanceModel", back_populates="product", uselist=False, cascade="all, delete-orphan")
    home = relationship("HomeModel", back_populates="product", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ProductModel(product_id={self.product_id}, type='{self.product_type}', item_id='{self.item_id}')>"


class CharacterModel(Base):
    """角色信息表模型"""
    __tablename__ = 'characters'

    character_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.product_id'), unique=True, nullable=False)
    
    level = Column(String(50))
    role_name = Column(String(100))
    sect = Column(String(100))
    new_qianyuan_dan_count = Column(String(50))
    mooncake_zongzi_chance = Column(String(50))
    ascension_tribulation_sainthood = Column(String(50))
    achievement_points = Column(String(50))
    used_potential_fruit_count = Column(String(50))
    total_experience = Column(String(100))
    attack_cultivation = Column(String(50))
    defense_cultivation = Column(String(50))
    magic_cultivation = Column(String(50))
    magic_resistance_cultivation = Column(String(50))
    hunting_skill_cultivation = Column(String(50))
    beast_rearing_skill = Column(String(50))
    attack_control = Column(String(50))
    defense_control = Column(String(50))
    magic_control = Column(String(50))
    magic_resistance_control = Column(String(50))
    
    school_skills_json = Column(Text) # JSON存储师门技能列表
    life_skills_json = Column(Text) # JSON存储生活技能列表
    story_skills_json = Column(Text) # JSON存储剧情技能列表
    story_skill_remaining_points = Column(String(50))
    proficiency_json = Column(Text) # JSON存储熟练度字典
    
    raw_data_json = Column(Text) # 存储原始提取数据，JSON格式

    product = relationship("ProductModel", back_populates="character")

    def __repr__(self):
        return f"<CharacterModel(character_id={self.character_id}, level='{self.level}', role='{self.role_name}')>"


class ItemModel(Base):
    """道具信息表模型"""
    __tablename__ = 'items'

    item_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    
    name = Column(String(255))
    item_type = Column(String(100)) # e.g., "戒指", "耳饰", "项链", "神器", "灵宝", "法宝"
    description = Column(Text)
    icon_url = Column(String(500))
    is_equipped = Column(Boolean)
    category = Column(String(100)) # e.g., "using_equip", "artifact", "spirit_treasure", "magic_treasure"
    
    raw_data_json = Column(Text) # 存储原始提取数据，JSON格式

    product = relationship("ProductModel", back_populates="items")

    def __repr__(self):
        return f"<ItemModel(item_id={self.item_id}, name='{self.name}', type='{self.item_type}')>"


class PetModel(Base):
    """召唤兽/孩子信息表模型"""
    __tablename__ = 'pets'

    pet_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    
    name = Column(String(255))
    pet_type = Column(String(50)) # e.g., "召唤兽", "孩子", "特殊宠物"
    level = Column(String(50))
    is_baby = Column(Boolean)
    hp = Column(String(50))
    mp = Column(String(50))
    attack = Column(String(50))
    defense = Column(String(50))
    speed = Column(String(50))
    magic_attack = Column(String(50))
    magic_defense = Column(String(50))
    growth = Column(String(50))
    five_elements = Column(String(50))
    
    aptitude_json = Column(Text) # JSON存储资质
    skills_json = Column(Text) # JSON存储技能 (赐福技能, 普通技能)
    inner_elixirs_json = Column(Text) # JSON存储内丹
    equips_json = Column(Text) # JSON存储装备
    ornaments_json = Column(Text) # JSON存储饰品
    
    raw_data_json = Column(Text) # 存储原始提取数据，JSON格式

    product = relationship("ProductModel", back_populates="pets")

    def __repr__(self):
        return f"<PetModel(pet_id={self.pet_id}, name='{self.name}', type='{self.pet_type}')>"


class MountModel(Base):
    """坐骑信息表模型"""
    __tablename__ = 'mounts'

    mount_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.product_id'), unique=True, nullable=False)
    
    name = Column(String(255))
    mount_type = Column(String(50)) # e.g., "坐骑", "限量祥瑞", "普通祥瑞"
    level = Column(String(50))
    main_attribute = Column(String(50))
    growth = Column(String(50))
    
    skills_json = Column(Text) # JSON存储坐骑技能
    xuanlingzhu_json = Column(Text) # JSON存储携带玄灵珠
    auspicious_beast_skill = Column(String(255)) # 祥瑞技能
    
    raw_data_json = Column(Text) # 存储原始提取数据，JSON格式

    product = relationship("ProductModel", back_populates="mounts")

    def __repr__(self):
        return f"<MountModel(mount_id={self.mount_id}, name='{self.name}', type='{self.mount_type}')>"


class AppearanceModel(Base):
    """锦衣/外观信息表模型"""
    __tablename__ = 'appearances'

    appearance_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.product_id'), unique=True, nullable=False)
    
    dyed_fruit_count = Column(String(50))
    saved_dye_schemes = Column(String(50))
    total_dyed_fruit_count = Column(String(50))
    
    title_effects_json = Column(Text) # JSON存储称谓特效
    spell_attack_effects_json = Column(Text) # JSON存储施法/攻击特效
    bubble_frames_json = Column(Text) # JSON存储冒泡框
    avatar_frames_json = Column(Text) # JSON存储头像框
    team_logos_json = Column(Text) # JSON存储彩饰-队标
    
    xianyu_balance = Column(String(50))
    xianyu_points = Column(String(50))
    qicai_points = Column(String(50))
    total_outfits_count = Column(String(50))
    
    limited_outfits_json = Column(Text) # JSON存储限量锦衣
    pendants_json = Column(Text) # JSON存储挂件
    normal_outfits_json = Column(Text) # JSON存储普通锦衣
    
    raw_data_json = Column(Text) # 存储原始提取数据，JSON格式

    product = relationship("ProductModel", back_populates="appearance")

    def __repr__(self):
        return f"<AppearanceModel(appearance_id={self.appearance_id}, total_outfits='{self.total_outfits_count}')>"


class HomeModel(Base):
    """玩家之家信息表模型"""
    __tablename__ = 'homes'

    home_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.product_id'), unique=True, nullable=False)
    
    house_level = Column(String(50))
    house_stability = Column(String(50))
    house_fengshui = Column(String(50))
    house_type = Column(String(50))
    furniture_score = Column(String(50))
    
    raw_data_json = Column(Text) # 存储原始提取数据，JSON格式

    product = relationship("ProductModel", back_populates="home")

    def __repr__(self):
        return f"<HomeModel(home_id={self.home_id}, level='{self.house_level}', fengshui='{self.house_fengshui}')>"
