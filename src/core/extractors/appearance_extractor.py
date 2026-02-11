"""
锦衣/外观信息提取器
"""
from bs4 import BeautifulSoup
from typing import Dict, Optional, List, Any
import logging
import re

logger = logging.getLogger(__name__)


class AppearanceExtractor:
    """锦衣/外观信息提取器"""
    
    def extract_appearance_info(self, html_content: str) -> Dict[str, Any]:
        """
        提取锦衣/外观信息
        
        Args:
            html_content: HTML内容
            
        Returns:
            包含锦衣/外观信息的字典
        """
        soup = BeautifulSoup(html_content, 'lxml')
        result = {
            'dye': {},           # 染色信息
            'title_effects': [],  # 称谓特效
            'cast_effects': [],   # 施法/攻击特效
            'bubbles': [],       # 冒泡框
            'avatars': [],       # 头像框
            'decorations': [],   # 彩饰-队标
            'jinyi': {          # 锦衣
                'limited': [],   # 限量
                'accessory': [], # 挂件
                'normal': []     # 普通
            },
            'currency': {}       # 仙玉、积分等
        }
        
        try:
            # 提取染色信息
            dye_table = soup.find('table', class_='tb02')
            if dye_table:
                for tr in dye_table.find_all('tr'):
                    th = tr.find('th')
                    td = tr.find('td')
                    if th and td:
                        key = th.get_text(strip=True).replace('：', '').replace(':', '')
                        value = td.get_text(strip=True)
                        
                        if '身上染色折算彩果数' in key:
                            result['dye']['body_dye_count'] = self._parse_int(value)
                        elif '衣柜已保存染色方案' in key:
                            result['dye']['wardrobe_saved_count'] = self._parse_int(value)
                        elif '所有染色折算彩果数' in key:
                            result['dye']['total_dye_count'] = self._parse_int(value)
            
            # 提取称谓特效
            title_module = soup.find('div', class_='module-jinyi')
            if title_module:
                h4 = title_module.find('h4', string=re.compile('称谓特效'))
                if h4:
                    ul = h4.find_next_sibling('ul', class_='jinyi-attr-list')
                    if ul:
                        for li in ul.find_all('li', class_='item'):
                            result['title_effects'].append(li.get_text(strip=True))
            
            # 提取施法/攻击特效
            cast_module = soup.find('div', class_='module-jinyi')
            if cast_module:
                h4 = cast_module.find('h4', string=re.compile('施法/攻击特效'))
                if h4:
                    ul = h4.find_next_sibling('ul', class_='jinyi-attr-list')
                    if ul:
                        for li in ul.find_all('li', class_='item'):
                            result['cast_effects'].append(li.get_text(strip=True))
            
            # 提取冒泡框
            bubble_module = soup.find('div', class_='module-jinyi')
            if bubble_module:
                h4 = bubble_module.find('h4', string=re.compile('冒泡框'))
                if h4:
                    ul = h4.find_next_sibling('ul', class_='jinyi-attr-list')
                    if ul:
                        for li in ul.find_all('li', class_='item'):
                            result['bubbles'].append(li.get_text(strip=True))
            
            # 提取头像框
            avatar_module = soup.find('div', class_='module-jinyi')
            if avatar_module:
                h4 = avatar_module.find('h4', string=re.compile('头像框'))
                if h4:
                    ul = h4.find_next_sibling('ul', class_='jinyi-attr-list')
                    if ul:
                        for li in ul.find_all('li', class_='item'):
                            result['avatars'].append(li.get_text(strip=True))
            
            # 提取彩饰-队标
            decoration_module = soup.find('div', class_='module-jinyi')
            if decoration_module:
                h4 = decoration_module.find('h4', string=re.compile('彩饰-队标'))
                if h4:
                    ul = h4.find_next_sibling('ul', class_='jinyi-attr-list')
                    if ul:
                        for li in ul.find_all('li', class_='item'):
                            result['decorations'].append(li.get_text(strip=True))
            
            # 提取锦衣列表
            jinyi_list = soup.find('div', class_='new-jinyi-list')
            if jinyi_list:
                # 限量锦衣
                limited_module = jinyi_list.find('div', class_=re.compile('module-jinyi—0'))
                if limited_module:
                    ul = limited_module.find('ul', class_='jinyi-attr-list')
                    if ul:
                        for li in ul.find_all('li', class_='item'):
                            result['jinyi']['limited'].append(li.get_text(strip=True))
                
                # 挂件
                accessory_module = jinyi_list.find('div', class_=re.compile('module-jinyi—1'))
                if accessory_module:
                    ul = accessory_module.find('ul', class_='jinyi-attr-list')
                    if ul:
                        for li in ul.find_all('li', class_='item'):
                            result['jinyi']['accessory'].append(li.get_text(strip=True))
                
                # 普通锦衣
                normal_module = jinyi_list.find('div', class_=re.compile('module-jinyi—2'))
                if normal_module:
                    ul = normal_module.find('ul', class_='jinyi-attr-list')
                    if ul:
                        for li in ul.find_all('li', class_='item'):
                            result['jinyi']['normal'].append(li.get_text(strip=True))
            
            # 提取货币信息
            xianyu_wrap = soup.find('ul', class_='xianyu-wrap')
            if xianyu_wrap:
                for li in xianyu_wrap.find_all('li'):
                    text = li.get_text(strip=True)
                    if '仙玉:' in text:
                        result['currency']['xianyu'] = text.replace('仙玉:', '').strip()
                    elif '仙玉积分:' in text:
                        result['currency']['xianyu_jifen'] = text.replace('仙玉积分:', '').strip()
                    elif '七彩积分:' in text:
                        result['currency']['qicai_jifen'] = text.replace('七彩积分:', '').strip()
            
            logger.info(f"成功提取外观信息: 称谓特效{len(result['title_effects'])}个, "
                       f"冒泡框{len(result['bubbles'])}个, 头像框{len(result['avatars'])}个, "
                       f"锦衣{len(result['jinyi']['limited']) + len(result['jinyi']['normal'])}件")
            
        except Exception as e:
            logger.error(f"提取外观信息失败: {str(e)}")
        
        return result
    
    def _parse_int(self, value: str) -> Optional[int]:
        """解析整数"""
        if not value:
            return None
        try:
            import re
            cleaned = re.sub(r'[^\d-]', '', value)
            return int(cleaned) if cleaned else None
        except:
            return None
