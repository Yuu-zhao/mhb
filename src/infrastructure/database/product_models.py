"""
商品相关数据库模型（按照领域划分）
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, DECIMAL, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database.models import Base


class Product(Base):
    """商品表"""
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_type = Column(String(50), nullable=False, index=True)  # role, equipment, pet, child, mount, appearance, home
    url = Column(String(1000), nullable=False, unique=True, index=True)
    title = Column(String(500))
    product_id = Column(String(100))  # 商品编号
    seller = Column(String(200))
    seller_id = Column(String(100), index=True)
    price = Column(DECIMAL(12, 2))
    is_listed = Column(Boolean)
    can_bargain = Column(Boolean)
    time_remaining = Column(String(50))
    highlights = Column(Text)  # JSON数组
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    role_info = relationship("RoleInfo", back_populates="product", cascade="all, delete-orphan", uselist=False)
    skill_infos = relationship("SkillInfo", back_populates="product", cascade="all, delete-orphan")
    skill_proficiencies = relationship("SkillProficiency", back_populates="product", cascade="all, delete-orphan")
    equipment_infos = relationship("EquipmentInfo", back_populates="product", cascade="all, delete-orphan")
    equipment_currencies = relationship("EquipmentCurrency", back_populates="product", cascade="all, delete-orphan")
    pet_infos = relationship("PetInfo", back_populates="product", cascade="all, delete-orphan")
    child_infos = relationship("ChildInfo", back_populates="product", cascade="all, delete-orphan")
    mount_infos = relationship("MountInfo", back_populates="product", cascade="all, delete-orphan")
    mount_xianruis = relationship("MountXianrui", back_populates="product", cascade="all, delete-orphan")
    appearance_infos = relationship("AppearanceInfo", back_populates="product", cascade="all, delete-orphan")
    appearance_dye = relationship("AppearanceDye", back_populates="product", cascade="all, delete-orphan", uselist=False)
    home_info = relationship("HomeInfo", back_populates="product", cascade="all, delete-orphan", uselist=False)


class RoleInfo(Base):
    """角色信息表"""
    __tablename__ = 'role_info'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    level = Column(Integer)
    role_name = Column(String(100))
    school = Column(String(50))
    qianyuan_dan_count = Column(Integer)
    mooncake_chance = Column(String(50))
    ascension_status = Column(String(50))
    achievement_points = Column(Integer)
    used_potential_fruit = Column(Integer)
    total_experience = Column(String(50))
    attack_cultivation = Column(String(50))
    defense_cultivation = Column(String(50))
    magic_cultivation = Column(String(50))
    magic_resistance_cultivation = Column(String(50))
    hunting_cultivation = Column(String(50))
    beast_rearing = Column(String(50))
    attack_control = Column(String(50))
    defense_control = Column(String(50))
    magic_control = Column(String(50))
    magic_resistance_control = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    product = relationship("Product", back_populates="role_info")


class SkillInfo(Base):
    """技能信息表"""
    __tablename__ = 'skill_info'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    skill_type = Column(String(50), nullable=False)  # school, life, juqing
    skill_name = Column(String(100), nullable=False)
    skill_level = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    
    product = relationship("Product", back_populates="skill_infos")
    
    __table_args__ = (
        UniqueConstraint('product_id', 'skill_type', 'skill_name', name='uq_skill'),
        Index('idx_skill_type', 'skill_type'),
    )


class SkillProficiency(Base):
    """熟练度表"""
    __tablename__ = 'skill_proficiency'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    proficiency_type = Column(String(100))
    proficiency_value = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)
    
    product = relationship("Product", back_populates="skill_proficiencies")


class EquipmentInfo(Base):
    """道具信息表"""
    __tablename__ = 'equipment_info'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    equipment_type = Column(String(50), nullable=False)  # equipment, shenqi, lingbao, fabao
    equipment_name = Column(String(200))
    equipment_desc = Column(Text)
    is_equipped = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    
    product = relationship("Product", back_populates="equipment_infos")
    
    __table_args__ = (
        Index('idx_equipment_type', 'equipment_type'),
    )


class EquipmentCurrency(Base):
    """道具货币表"""
    __tablename__ = 'equipment_currency'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    currency_type = Column(String(50))
    currency_value = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)
    
    product = relationship("Product", back_populates="equipment_currencies")


class PetInfo(Base):
    """召唤兽信息表"""
    __tablename__ = 'pet_info'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    pet_type = Column(String(100))
    level = Column(Integer)
    is_baby = Column(Boolean)
    hp = Column(Integer)
    mp = Column(Integer)
    attack = Column(Integer)
    defense = Column(Integer)
    speed = Column(Integer)
    magic_damage = Column(Integer)
    magic_defense = Column(Integer)
    constitution = Column(Integer)
    magic_power = Column(Integer)
    strength = Column(Integer)
    endurance = Column(Integer)
    agility = Column(Integer)
    potential = Column(Integer)
    growth = Column(DECIMAL(5, 3))
    attack_aptitude = Column(Integer)
    defense_aptitude = Column(Integer)
    hp_aptitude = Column(Integer)
    magic_aptitude = Column(Integer)
    speed_aptitude = Column(Integer)
    dodge_aptitude = Column(Integer)
    element = Column(String(10))
    lifespan = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    product = relationship("Product", back_populates="pet_infos")
    skills = relationship("PetSkill", back_populates="pet", cascade="all, delete-orphan")
    neidans = relationship("PetNeidan", back_populates="pet", cascade="all, delete-orphan")


class PetSkill(Base):
    """召唤兽技能表"""
    __tablename__ = 'pet_skill'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pet_id = Column(Integer, ForeignKey('pet_info.id', ondelete='CASCADE'), nullable=False, index=True)
    skill_name = Column(String(100))
    skill_type = Column(String(50))  # cifu, normal
    created_at = Column(DateTime, default=datetime.now)
    
    pet = relationship("PetInfo", back_populates="skills")


class PetNeidan(Base):
    """召唤兽内丹表"""
    __tablename__ = 'pet_neidan'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pet_id = Column(Integer, ForeignKey('pet_info.id', ondelete='CASCADE'), nullable=False, index=True)
    neidan_name = Column(String(100))
    neidan_level = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    
    pet = relationship("PetInfo", back_populates="neidans")


class ChildInfo(Base):
    """孩子信息表"""
    __tablename__ = 'child_info'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    child_type = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)
    
    product = relationship("Product", back_populates="child_infos")


class MountInfo(Base):
    """坐骑信息表"""
    __tablename__ = 'mount_info'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    mount_type = Column(String(100))
    level = Column(Integer)
    growth = Column(DECIMAL(8, 4))
    main_attribute = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)
    
    product = relationship("Product", back_populates="mount_infos")
    skills = relationship("MountSkill", back_populates="mount", cascade="all, delete-orphan")


class MountSkill(Base):
    """坐骑技能表"""
    __tablename__ = 'mount_skill'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    mount_id = Column(Integer, ForeignKey('mount_info.id', ondelete='CASCADE'), nullable=False, index=True)
    skill_name = Column(String(100))
    skill_level = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    
    mount = relationship("MountInfo", back_populates="skills")


class MountXianrui(Base):
    """坐骑祥瑞表"""
    __tablename__ = 'mount_xianrui'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    xianrui_type = Column(String(50))  # limited, normal
    xianrui_name = Column(String(100))
    xianrui_skill = Column(String(200))
    created_at = Column(DateTime, default=datetime.now)
    
    product = relationship("Product", back_populates="mount_xianruis")


class AppearanceInfo(Base):
    """锦衣信息表"""
    __tablename__ = 'appearance_info'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    appearance_type = Column(String(50))  # jinyi, title_effect, cast_effect, bubble, avatar, decoration
    appearance_name = Column(String(200))
    appearance_category = Column(String(100))  # 限量、挂件、普通锦衣等
    created_at = Column(DateTime, default=datetime.now)
    
    product = relationship("Product", back_populates="appearance_infos")


class AppearanceDye(Base):
    """锦衣染色表"""
    __tablename__ = 'appearance_dye'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    body_dye_count = Column(Integer)
    wardrobe_saved_count = Column(Integer)
    total_dye_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    
    product = relationship("Product", back_populates="appearance_dye")


class HomeInfo(Base):
    """玩家之家信息表"""
    __tablename__ = 'home_info'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    home_level = Column(Integer)
    home_type = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)
    
    product = relationship("Product", back_populates="home_info")
