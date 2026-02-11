"""
数据映射服务
将提取的原始数据转换为领域实体
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ...domain.entities.product import Product
from ...domain.entities.character import Character
from ...domain.entities.item import Item
from ...domain.entities.pet import Pet
from ...domain.entities.mount import Mount
from ...domain.entities.appearance import Appearance
from ...domain.entities.home import Home

logger = logging.getLogger(__name__)


class DataMapperService:
    """数据映射服务，将提取的原始数据转换为领域实体"""
    
    def map_to_product(self, extracted_data: Dict[str, Any], url: str) -> Product:
        """
        将提取的数据映射为Product实体
        
        Args:
            extracted_data: 从所有标签页提取的原始数据
            url: 商品URL
            
        Returns:
            Product实体
        """
        basic_info = extracted_data.get('basic_info', {})
        
        # 提取商品基本信息
        product = Product(
            item_id=basic_info.get('编号', ''),
            product_type='角色',  # 默认是角色类型
            url=url,
            price=self._parse_price(basic_info.get('价格', '')),
            seller_id=basic_info.get('卖家ID', ''),
            seller_name=basic_info.get('卖家', ''),
            listed_status=basic_info.get('是否上架', ''),
            bargainable=basic_info.get('是否接受还价', False),
            time_remaining=basic_info.get('出售剩余时间', ''),
            highlights=self._parse_highlights(basic_info.get('亮点', '')),
            extracted_data=extracted_data,
            created_at=datetime.now()
        )
        
        # 映射角色信息
        if basic_info:
            product.character = self._map_to_character(basic_info, extracted_data)
        
        # 映射道具信息
        equip_info = extracted_data.get('equip_info', {})
        if equip_info:
            product.items = self._map_to_items(equip_info)
        
        # 映射召唤兽信息
        pet_info = extracted_data.get('pet_info', {})
        if pet_info:
            product.pets = self._map_to_pets(pet_info)
        
        # 映射坐骑信息
        mount_info = extracted_data.get('mount_info', {})
        if mount_info:
            product.mount = self._map_to_mount(mount_info)
        
        # 映射外观信息
        appearance_info = extracted_data.get('appearance_info', {})
        if appearance_info:
            product.appearance = self._map_to_appearance(appearance_info)
        
        # 映射玩家之家信息
        home_info = extracted_data.get('home_info', {})
        if home_info:
            product.home = self._map_to_home(home_info)
        
        return product
    
    def _map_to_character(self, basic_info: Dict[str, Any], all_data: Dict[str, Any]) -> Character:
        """映射角色信息"""
        skill_info = all_data.get('skill_info', {})
        
        character = Character(
            level=basic_info.get('级别', ''),
            role_name=basic_info.get('角色', ''),
            sect=basic_info.get('门派', ''),
            new_qianyuan_dan_count=basic_info.get('新版乾元丹数量', ''),
            mooncake_zongzi_chance=basic_info.get('月饼粽子机缘', ''),
            ascension_tribulation_sainthood=basic_info.get('飞升/渡劫/化圣', ''),
            achievement_points=basic_info.get('成就点数', ''),
            used_potential_fruit_count=basic_info.get('已用潜能果数量', ''),
            total_experience=basic_info.get('总经验', ''),
            attack_cultivation=basic_info.get('攻击修炼', ''),
            defense_cultivation=basic_info.get('防御修炼', ''),
            magic_cultivation=basic_info.get('法术修炼', ''),
            magic_resistance_cultivation=basic_info.get('抗法修炼', ''),
            hunting_skill_cultivation=basic_info.get('猎术修炼', ''),
            beast_rearing_skill=basic_info.get('育兽术', ''),
            attack_control=basic_info.get('攻击控制力', ''),
            defense_control=basic_info.get('防御控制力', ''),
            magic_control=basic_info.get('法术控制力', ''),
            magic_resistance_control=basic_info.get('抗法控制力', ''),
            school_skills=skill_info.get('school_skills', []),
            life_skills=skill_info.get('life_skills', []),
            story_skills=skill_info.get('story_skills', []),
            story_skill_remaining_points=skill_info.get('story_skill_remaining_points', ''),
            proficiency=skill_info.get('proficiency', {}),
            raw_data=basic_info
        )
        
        return character
    
    def _map_to_items(self, equip_info: Dict[str, Any]) -> List[Item]:
        """映射道具信息"""
        items = []
        
        # 已装备道具
        for equip in equip_info.get('using_equips', []):
            items.append(Item(
                name=equip.get('name', ''),
                item_type=equip.get('type', ''),
                description=equip.get('desc', ''),
                icon_url=equip.get('icon', ''),
                is_equipped=True,
                category='using_equip',
                raw_data=equip
            ))
        
        # 未装备道具
        for equip in equip_info.get('store_equips', []):
            items.append(Item(
                name=equip.get('name', ''),
                item_type=equip.get('type', ''),
                description=equip.get('desc', ''),
                icon_url=equip.get('icon', ''),
                is_equipped=False,
                category='store_equip',
                raw_data=equip
            ))
        
        # 神器
        artifacts = equip_info.get('artifacts', {})
        if artifacts and artifacts.get('name'):
            items.append(Item(
                name=artifacts.get('name', ''),
                item_type=artifacts.get('type', ''),
                description=artifacts.get('desc', ''),
                icon_url=artifacts.get('icon', ''),
                is_equipped=True,
                category='artifact',
                raw_data=artifacts
            ))
        
        # 灵宝
        for lingbao in equip_info.get('using_spirit_treasures', []):
            items.append(Item(
                name=lingbao.get('name', ''),
                item_type=lingbao.get('type', ''),
                description=lingbao.get('desc', ''),
                icon_url=lingbao.get('icon', ''),
                is_equipped=True,
                category='spirit_treasure',
                raw_data=lingbao
            ))
        
        # 法宝
        for fabao in equip_info.get('using_magic_treasures', []):
            items.append(Item(
                name=fabao.get('name', ''),
                item_type=fabao.get('type', ''),
                description=fabao.get('desc', ''),
                icon_url=fabao.get('icon', ''),
                is_equipped=True,
                category='magic_treasure',
                raw_data=fabao
            ))
        
        return items
    
    def _map_to_pets(self, pet_info: Dict[str, Any]) -> List[Pet]:
        """映射召唤兽信息"""
        pets = []
        
        # 召唤兽列表
        for pet_data in pet_info.get('pets', []):
            pet = Pet(
                name=pet_data.get('pet_type', ''),
                pet_type='召唤兽',
                level=str(pet_data.get('level', '')),
                is_baby=pet_data.get('is_baby', False),
                hp=str(pet_data.get('hp', '')),
                mp=str(pet_data.get('mp', '')),
                attack=str(pet_data.get('attack', '')),
                defense=str(pet_data.get('defense', '')),
                speed=str(pet_data.get('speed', '')),
                magic_attack=str(pet_data.get('magic_damage', '')),
                magic_defense=str(pet_data.get('magic_defense', '')),
                growth=str(pet_data.get('growth', '')),
                five_elements=pet_data.get('element', ''),
                aptitude=self._extract_aptitude(pet_data),
                skills=self._extract_pet_skills(pet_data),
                inner_elixirs=pet_data.get('neidans', []),
                raw_data=pet_data
            )
            pets.append(pet)
        
        # 孩子列表
        for child_data in pet_info.get('children', []):
            pet = Pet(
                name=child_data.get('type_id', ''),
                pet_type='孩子',
                raw_data=child_data
            )
            pets.append(pet)
        
        return pets
    
    def _map_to_mount(self, mount_info: Dict[str, Any]) -> Optional[Mount]:
        """映射坐骑信息"""
        mounts = mount_info.get('mounts', [])
        if not mounts:
            return None
        
        mount_data = mounts[0]  # 取第一个坐骑
        
        mount = Mount(
            name=mount_data.get('mount_type', ''),
            mount_type='坐骑',
            level=str(mount_data.get('level', '')),
            main_attribute=mount_data.get('main_attribute', ''),
            growth=str(mount_data.get('growth', '')),
            skills=mount_data.get('skills', []),
            xuanlingzhu=mount_info.get('xuanlingzhu', {}),
            raw_data=mount_data
        )
        
        return mount
    
    def _map_to_appearance(self, appearance_info: Dict[str, Any]) -> Appearance:
        """映射外观信息"""
        dye = appearance_info.get('dye', {})
        jinyi = appearance_info.get('jinyi', {})
        currency = appearance_info.get('currency', {})
        
        appearance = Appearance(
            dyed_fruit_count=str(dye.get('body_dye_count', '')),
            saved_dye_schemes=str(dye.get('wardrobe_saved_count', '')),
            total_dyed_fruit_count=str(dye.get('total_dye_count', '')),
            title_effects=appearance_info.get('title_effects', []),
            spell_attack_effects=appearance_info.get('cast_effects', []),
            bubble_frames=appearance_info.get('bubbles', []),
            avatar_frames=appearance_info.get('avatars', []),
            team_logos=appearance_info.get('decorations', []),
            xianyu_balance=currency.get('xianyu', ''),
            xianyu_points=currency.get('xianyu_jifen', ''),
            qicai_points=currency.get('qicai_jifen', ''),
            total_outfits_count=str(len(jinyi.get('limited', [])) + len(jinyi.get('normal', []))),
            limited_outfits=jinyi.get('limited', []),
            pendants=jinyi.get('accessory', []),
            normal_outfits=jinyi.get('normal', []),
            raw_data=appearance_info
        )
        
        return appearance
    
    def _map_to_home(self, home_info: Dict[str, Any]) -> Home:
        """映射玩家之家信息"""
        home = Home(
            house_level=home_info.get('courtyard_level', ''),
            house_stability='',  # 从原始数据中提取
            house_fengshui='',  # 从原始数据中提取
            house_type=home_info.get('residence', ''),
            furniture_score=str(len(home_info.get('furniture', []))),
            raw_data=home_info
        )
        
        return home
    
    def _parse_price(self, price_str: str) -> Optional[float]:
        """解析价格字符串"""
        if not price_str:
            return None
        try:
            # 移除￥和（元）等字符
            cleaned = price_str.replace('￥', '').replace('（元）', '').replace('元', '').strip()
            return float(cleaned)
        except:
            return None
    
    def _parse_highlights(self, highlights_str: str) -> List[str]:
        """解析亮点字符串"""
        if not highlights_str:
            return []
        if isinstance(highlights_str, list):
            return highlights_str
        # 按|分割
        return [h.strip() for h in highlights_str.split('|') if h.strip()]
    
    def _extract_aptitude(self, pet_data: Dict[str, Any]) -> Dict[str, str]:
        """提取资质信息"""
        aptitude = {}
        for key in ['attack_aptitude', 'defense_aptitude', 'hp_aptitude',
                    'magic_aptitude', 'speed_aptitude', 'dodge_aptitude']:
            value = pet_data.get(key)
            if value:
                aptitude[key] = str(value)
        return aptitude
    
    def _extract_pet_skills(self, pet_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取召唤兽技能"""
        skills = []
        
        # 赐福技能
        for skill in pet_data.get('cifu_skills', []):
            skills.append({
                'name': skill.get('name', ''),
                'type': 'cifu'
            })
        
        # 普通技能
        for skill in pet_data.get('skills', []):
            skills.append({
                'name': skill.get('name', ''),
                'type': 'normal'
            })
        
        return skills
