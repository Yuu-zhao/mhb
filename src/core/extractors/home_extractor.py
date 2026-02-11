"""
玩家之家信息提取器
"""
from bs4 import BeautifulSoup
from typing import Dict, Optional, List, Any
import logging
import re

logger = logging.getLogger(__name__)


class HomeExtractor:
    """玩家之家信息提取器"""
    
    def extract_home_info(self, html_content: str) -> Dict[str, Any]:
        """
        提取玩家之家信息
        
        Args:
            html_content: HTML内容
            
        Returns:
            包含玩家之家信息的字典
        """
        soup = BeautifulSoup(html_content, 'lxml')
        result = {
            'marriage_status': None,      # 婚否
            'tongpao_status': None,       # 同袍
            'residence': None,            # 居住房屋
            'is_owner': None,             # 是否产权所有人
            'courtyard_level': None,       # 庭院等级
            'pasture': None,              # 牧场
            'community': None,             # 社区
            'deed': None,                 # 房契
            'window_scenes': [],          # 窗景
            'courtyard_themes': [],       # 庭院主题
            'courtyard_effects': [],      # 庭院特效
            'furniture': []               # 家具
        }
        
        try:
            role_info_box = soup.find('div', id='role_info_box')
            if not role_info_box:
                logger.warning("HomeExtractor: 未找到 role_info_box 元素。")
                return result
            
            # 提取房屋基本信息表
            home_info_table = role_info_box.find('table', class_='tb02')
            if home_info_table:
                for tr in home_info_table.find_all('tr'):
                    tds = tr.find_all('td')
                    for td in tds:
                        text = td.get_text(strip=True)
                        if '婚否：' in text:
                            result['marriage_status'] = text.replace('婚否：', '').strip()
                        elif '同袍：' in text:
                            result['tongpao_status'] = text.replace('同袍：', '').strip()
                        elif '居住房屋：' in text:
                            result['residence'] = text.replace('居住房屋：', '').strip()
                        elif '是否产权所有人：' in text:
                            result['is_owner'] = text.replace('是否产权所有人：', '').strip()
                        elif '庭院等级：' in text:
                            result['courtyard_level'] = text.replace('庭院等级：', '').strip()
                        elif '牧场：' in text:
                            result['pasture'] = text.replace('牧场：', '').strip()
                        elif '社区：' in text:
                            result['community'] = text.replace('社区：', '').strip()
                        elif '房契：' in text:
                            result['deed'] = text.replace('房契：', '').strip()
            
            # 提取窗景
            window_scene_module = role_info_box.find('div', class_='module-jinyi')
            if window_scene_module:
                h4 = window_scene_module.find('h4', string=re.compile('窗景'))
                if h4:
                    p = h4.find_next_sibling('p', class_='jinyi-num')
                    if p:
                        count_text = p.get_text(strip=True)
                        match = re.search(r'(\d+)', count_text)
                        if match:
                            result['window_scenes_count'] = int(match.group(1))
                    ul = h4.find_next_sibling('ul', class_='jinyi-attr-list')
                    if ul:
                        for li in ul.find_all('li', class_='item'):
                            result['window_scenes'].append(li.get_text(strip=True))
            
            # 提取庭院主题
            theme_module = role_info_box.find('div', class_='module-jinyi')
            if theme_module:
                h4 = theme_module.find('h4', string=re.compile('庭院主题'))
                if h4:
                    p = h4.find_next_sibling('p', class_='jinyi-num')
                    if p:
                        count_text = p.get_text(strip=True)
                        match = re.search(r'(\d+)', count_text)
                        if match:
                            result['courtyard_themes_count'] = int(match.group(1))
                    ul = h4.find_next_sibling('ul', class_='jinyi-attr-list')
                    if ul:
                        for li in ul.find_all('li', class_='item'):
                            result['courtyard_themes'].append(li.get_text(strip=True))
            
            # 提取庭院特效
            effect_module = role_info_box.find('div', class_='module-jinyi')
            if effect_module:
                h4 = effect_module.find('h4', string=re.compile('庭院特效'))
                if h4:
                    p = h4.find_next_sibling('p', class_='jinyi-num')
                    if p:
                        count_text = p.get_text(strip=True)
                        match = re.search(r'(\d+)', count_text)
                        if match:
                            result['courtyard_effects_count'] = int(match.group(1))
                    ul = h4.find_next_sibling('ul', class_='jinyi-attr-list')
                    if ul:
                        for li in ul.find_all('li', class_='item'):
                            result['courtyard_effects'].append(li.get_text(strip=True))
            
            # 提取家具
            furniture_module = role_info_box.find('div', class_='module-jinyi')
            if furniture_module:
                h4 = furniture_module.find('h4', string=re.compile('家具'))
                if h4:
                    p = h4.find_next_sibling('p', class_='jinyi-num')
                    if p:
                        count_text = p.get_text(strip=True)
                        match = re.search(r'(\d+)', count_text)
                        if match:
                            result['furniture_count'] = int(match.group(1))
                    ul = h4.find_next_sibling('ul', class_='jinyi-attr-list')
                    if ul:
                        for li in ul.find_all('li', class_='item'):
                            text = li.get_text(strip=True)
                            # 解析 "家具名*数量" 格式
                            match = re.match(r'(.+?)\*(\d+)', text)
                            if match:
                                result['furniture'].append({
                                    'name': match.group(1),
                                    'count': int(match.group(2))
                                })
            
            logger.info(f"成功提取玩家之家信息: 窗景{len(result['window_scenes'])}个, "
                       f"庭院主题{len(result['courtyard_themes'])}个, "
                       f"家具{len(result['furniture'])}种")
            
        except Exception as e:
            logger.error(f"提取玩家之家信息失败: {str(e)}")
        
        return result
