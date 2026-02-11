"""
道具/法宝信息提取器
从道具标签页提取关键信息
"""
from bs4 import BeautifulSoup
from typing import Dict, Optional, List
import logging
import re

logger = logging.getLogger(__name__)


class EquipExtractor:
    """道具/法宝信息提取器"""
    
    def extract_equip_info(self, html_content: str) -> Dict[str, any]:
        """
        提取道具/法宝信息
        
        Args:
            html_content: HTML内容
            
        Returns:
            包含道具/法宝信息的字典
        """
        soup = BeautifulSoup(html_content, 'lxml')
        result = {
            'equipments': [],      # 装备列表
            'shenqi': [],          # 神器
            'lingbao_equipped': [], # 已装备灵宝
            'lingbao_stored': [],  # 未装备灵宝
            'fabao_equipped': [],  # 已装备法宝
            'fabao_stored': [],    # 未装备法宝
            'currency': {},        # 货币信息
            'bag_expansion': None  # 行囊扩展
        }
        
        try:
            # 提取装备（道具）
            equip_table = soup.find('table', id='RoleUsingEquips')
            if equip_table:
                for img in equip_table.find_all('img', id=re.compile(r'role_using_equip_\d+')):
                    equip_name = img.get('data_equip_name', '')
                    equip_desc = img.get('data_equip_desc', '')
                    equip_type = img.get('data_equip_type', '')
                    equip_level = img.get('data_equip_level', '')
                    equip_type_desc = img.get('data_equip_type_desc', '')
                    if equip_name:
                        result['equipments'].append({
                            'name': equip_name,
                            'desc': equip_desc if equip_desc else '',
                            'type': equip_type,
                            'level': equip_level,
                            'type_desc': equip_type_desc
                        })
            
            # 提取神器
            shenqi_table = soup.find('table', id='RoleStoreShenqi')
            if shenqi_table:
                for td in shenqi_table.find_all('td', class_='shenqi_td'):
                    shenqi_name = td.get('data_equip_name', '')
                    shenqi_desc = td.get('data_equip_desc', '')
                    shenqi_type = td.get('data_equip_type', '')
                    shenqi_level = td.get('data_equip_level', '')
                    if shenqi_name:
                        result['shenqi'].append({
                            'name': shenqi_name,
                            'desc': shenqi_desc if shenqi_desc else '',
                            'type': shenqi_type,
                            'level': shenqi_level
                        })
            
            # 提取已装备灵宝
            lingbao_equipped = soup.find('table', id='RoleUsingLingbao')
            if lingbao_equipped:
                for td in lingbao_equipped.find_all('td'):
                    lingbao_name = td.get('data_equip_name', '')
                    lingbao_desc = td.get('data_equip_desc', '')
                    lingbao_type = td.get('data_equip_type', '')
                    lingbao_level = td.get('data_equip_level', '')
                    if lingbao_name:
                        result['lingbao_equipped'].append({
                            'name': lingbao_name,
                            'desc': lingbao_desc if lingbao_desc else '',
                            'type': lingbao_type,
                            'level': lingbao_level
                        })
            
            # 提取未装备灵宝
            lingbao_stored = soup.find('table', id='RoleNoUsingLingbao')
            if lingbao_stored:
                for td in lingbao_stored.find_all('td'):
                    lingbao_name = td.get('data_equip_name', '')
                    lingbao_desc = td.get('data_equip_desc', '')
                    lingbao_type = td.get('data_equip_type', '')
                    lingbao_level = td.get('data_equip_level', '')
                    if lingbao_name:
                        result['lingbao_stored'].append({
                            'name': lingbao_name,
                            'desc': lingbao_desc if lingbao_desc else '',
                            'type': lingbao_type,
                            'level': lingbao_level
                        })
            
            # 提取已装备法宝
            fabao_equipped = soup.find('table', id='RoleUsingFabao')
            if fabao_equipped:
                for td in fabao_equipped.find_all('td'):
                    fabao_name = td.get('data_equip_name', '')
                    fabao_desc = td.get('data_equip_desc', '')
                    fabao_type = td.get('data_equip_type', '')
                    fabao_level = td.get('data_equip_level', '')
                    if fabao_name:
                        result['fabao_equipped'].append({
                            'name': fabao_name,
                            'desc': fabao_desc if fabao_desc else '',
                            'type': fabao_type,
                            'level': fabao_level
                        })
            
            # 提取未装备法宝
            fabao_stored = soup.find('table', id='RoleStoreFabao')
            if fabao_stored:
                for td in fabao_stored.find_all('td'):
                    fabao_name = td.get('data_equip_name', '')
                    fabao_desc = td.get('data_equip_desc', '')
                    fabao_type = td.get('data_equip_type', '')
                    fabao_level = td.get('data_equip_level', '')
                    if fabao_name:
                        result['fabao_stored'].append({
                            'name': fabao_name,
                            'desc': fabao_desc if fabao_desc else '',
                            'type': fabao_type,
                            'level': fabao_level
                        })
            
            # 提取货币信息
            currency_table = soup.find('table', class_='tb02')
            if currency_table:
                for tr in currency_table.find_all('tr'):
                    th = tr.find('th')
                    td = tr.find('td')
                    if th and td:
                        key = th.get_text(strip=True).replace('：', '').replace(':', '')
                        value = td.get_text(strip=True)
                        if key in ['现金', '存银', '储备', '善恶', '仙玉', '精力']:
                            result['currency'][key] = value
            
            # 提取行囊扩展
            bag_table = soup.find('table', class_='tb02')
            if bag_table:
                for tr in bag_table.find_all('tr'):
                    th = tr.find('th')
                    td = tr.find('td')
                    if th and td:
                        key = th.get_text(strip=True).replace('：', '').replace(':', '')
                        if '行囊扩展' in key:
                            result['bag_expansion'] = td.get_text(strip=True)
            
            logger.info(f"成功提取道具信息: 装备{len(result['equipments'])}个, "
                       f"神器{len(result['shenqi'])}个, 灵宝{len(result['lingbao_equipped'])}个, "
                       f"法宝{len(result['fabao_equipped'])}个")
            
        except Exception as e:
            logger.error(f"提取道具信息失败: {str(e)}")
        
        return result
