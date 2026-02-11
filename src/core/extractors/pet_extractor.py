"""
召唤兽/孩子信息提取器
"""
from bs4 import BeautifulSoup
from typing import Dict, Optional, List, Any
import logging
import re

logger = logging.getLogger(__name__)


class PetExtractor:
    """召唤兽/孩子信息提取器"""
    
    def extract_pet_info(self, html_content: str) -> Dict[str, Any]:
        """
        提取召唤兽/孩子信息
        
        Args:
            html_content: HTML内容
            
        Returns:
            包含召唤兽/孩子信息的字典
        """
        soup = BeautifulSoup(html_content, 'lxml')
        result = {
            'pets': [],           # 召唤兽列表
            'children': [],       # 孩子列表
            'pet_skill_count': None  # 召唤兽心得技能解锁数
        }
        
        try:
            # 提取召唤兽心得技能解锁数
            skill_count_elem = soup.find('td', class_='sbook-skill-val')
            if skill_count_elem:
                skill_text = skill_count_elem.get_text(strip=True)
                # 提取 "44/63" 格式
                match = re.search(r'(\d+)/(\d+)', skill_text)
                if match:
                    result['pet_skill_count'] = f"{match.group(1)}/{match.group(2)}"
            
            # 提取召唤兽详细信息（从pet_detail_panel）
            pet_detail_panel = soup.find('div', id='pet_detail_panel')
            if pet_detail_panel:
                pet_info = self._extract_pet_detail(pet_detail_panel)
                if pet_info:
                    result['pets'].append(pet_info)
            
            # 提取孩子信息
            child_table = soup.find('table', id='RoleChilds')
            if child_table:
                for img in child_table.find_all('img'):
                    child_type = img.get('src', '')
                    # 从图片路径提取孩子类型
                    if child_type:
                        # 提取文件名作为类型标识
                        match = re.search(r'child_icon/(\d+)\.gif', child_type)
                        if match:
                            result['children'].append({
                                'type_id': match.group(1),
                                'icon_url': child_type
                            })
            
            logger.info(f"成功提取召唤兽信息: {len(result['pets'])}个召唤兽, {len(result['children'])}个孩子")
            
        except Exception as e:
            logger.error(f"提取召唤兽信息失败: {str(e)}")
        
        return result
    
    def _extract_pet_detail(self, panel) -> Optional[Dict[str, Any]]:
        """提取单个召唤兽详细信息"""
        try:
            pet_info = {}
            
            # 提取基础属性表
            attr_table = panel.find('table', class_='petZiZhiTb')
            if attr_table:
                for tr in attr_table.find_all('tr'):
                    tds = tr.find_all('td')
                    for td in tds:
                        strong = td.find('strong')
                        if strong:
                            key = strong.get_text(strip=True).replace('：', '').replace(':', '')
                            # 获取值（忽略span等子元素）
                            value_text = td.get_text(strip=True)
                            # 移除key部分
                            value = value_text.replace(key, '').strip()
                            
                            # 映射字段
                            if '类型' in key:
                                pet_info['pet_type'] = value
                            elif '等级' in key:
                                pet_info['level'] = self._parse_int(value)
                            elif '是否宝宝' in key:
                                pet_info['is_baby'] = '是' in value or '否' not in value
                            elif '气血' in key:
                                pet_info['hp'] = self._parse_int(value)
                            elif '魔法' in key:
                                pet_info['mp'] = self._parse_int(value)
                            elif '攻击' in key and '资质' not in key:
                                pet_info['attack'] = self._parse_int(value)
                            elif '防御' in key and '资质' not in key:
                                pet_info['defense'] = self._parse_int(value)
                            elif '速度' in key and '资质' not in key:
                                pet_info['speed'] = self._parse_int(value)
                            elif '法伤' in key:
                                pet_info['magic_damage'] = self._parse_int(value)
                            elif '法防' in key:
                                pet_info['magic_defense'] = self._parse_int(value)
                            elif '体质' in key:
                                pet_info['constitution'] = self._parse_int(value)
                            elif '法力' in key:
                                pet_info['magic_power'] = self._parse_int(value)
                            elif '力量' in key:
                                pet_info['strength'] = self._parse_int(value)
                            elif '耐力' in key:
                                pet_info['endurance'] = self._parse_int(value)
                            elif '敏捷' in key:
                                pet_info['agility'] = self._parse_int(value)
                            elif '潜能' in key:
                                pet_info['potential'] = self._parse_int(value)
                            elif '成长' in key:
                                pet_info['growth'] = self._parse_float(value)
                            elif '攻击资质' in key:
                                pet_info['attack_aptitude'] = self._parse_int(value)
                            elif '防御资质' in key:
                                pet_info['defense_aptitude'] = self._parse_int(value)
                            elif '体力资质' in key:
                                pet_info['hp_aptitude'] = self._parse_int(value)
                            elif '法力资质' in key:
                                pet_info['magic_aptitude'] = self._parse_int(value)
                            elif '速度资质' in key:
                                pet_info['speed_aptitude'] = self._parse_int(value)
                            elif '躲闪资质' in key:
                                pet_info['dodge_aptitude'] = self._parse_int(value)
                            elif '五行' in key:
                                pet_info['element'] = value
                            elif '寿命' in key:
                                pet_info['lifespan'] = self._parse_int(value)
            
            # 提取赐福技能
            cifu_table = panel.find('table', id='RolePetCifu')
            if cifu_table:
                pet_info['cifu_skills'] = []
                for img in cifu_table.find_all('img'):
                    skill_name = img.get('data_equip_name', '')
                    if skill_name:
                        pet_info['cifu_skills'].append({
                            'name': skill_name,
                            'type': 'cifu'
                        })
            
            # 提取普通技能
            skill_table = panel.find('table', id='RolePetSkill')
            if skill_table:
                pet_info['skills'] = []
                for img in skill_table.find_all('img'):
                    skill_name = img.get('data_equip_name', '')
                    if skill_name:
                        pet_info['skills'].append({
                            'name': skill_name,
                            'type': 'normal'
                        })
            
            # 提取内丹
            neidan_table = panel.find('table', id='RolePetNeidan')
            if neidan_table:
                pet_info['neidans'] = []
                for tr in neidan_table.find_all('tr'):
                    th = tr.find('th')
                    td = tr.find('td', string=re.compile(r'\d+层'))
                    if th and td:
                        neidan_name = th.get_text(strip=True)
                        level_text = td.get_text(strip=True)
                        level = self._parse_int(level_text.replace('层', ''))
                        pet_info['neidans'].append({
                            'name': neidan_name,
                            'level': level
                        })
            
            return pet_info if pet_info else None
            
        except Exception as e:
            logger.error(f"提取召唤兽详细信息失败: {str(e)}")
            return None
    
    def _parse_int(self, value: str) -> Optional[int]:
        """解析整数"""
        if not value:
            return None
        try:
            # 移除所有非数字字符（除了负号）
            cleaned = re.sub(r'[^\d-]', '', value)
            return int(cleaned) if cleaned else None
        except:
            return None
    
    def _parse_float(self, value: str) -> Optional[float]:
        """解析浮点数"""
        if not value:
            return None
        try:
            # 移除所有非数字字符（除了小数点和负号）
            cleaned = re.sub(r'[^\d.-]', '', value)
            return float(cleaned) if cleaned else None
        except:
            return None
