"""
技能信息提取器
从技能标签页提取关键信息
"""
from bs4 import BeautifulSoup
from typing import Dict, Optional, List
import logging
import re

logger = logging.getLogger(__name__)


class SkillExtractor:
    """技能信息提取器"""
    
    def extract_skill_info(self, html_content: str) -> Dict[str, any]:
        """
        提取技能信息
        
        Args:
            html_content: HTML内容
            
        Returns:
            包含技能信息的字典
        """
        soup = BeautifulSoup(html_content, 'lxml')
        result = {
            'school_skills': [],  # 师门技能
            'life_skills': [],   # 生活技能
            'juqing_skills': [], # 剧情技能
            'proficiency': {}    # 熟练度
        }
        
        try:
            # 提取师门技能
            school_skill_list = soup.find('ul', id='school_skill_lists')
            if school_skill_list:
                for li in school_skill_list.find_all('li'):
                    skill_name = li.find('h5')
                    skill_level = li.find('p')
                    if skill_name and skill_level:
                        result['school_skills'].append({
                            'name': skill_name.get_text(strip=True),
                            'level': skill_level.get_text(strip=True)
                        })
            
            # 提取生活技能
            life_skill_table = soup.find('table', id='life_skill_lists')
            if life_skill_table:
                for td in life_skill_table.find_all('td'):
                    skill_name = td.find('h5')
                    skill_level = td.find('p')
                    if skill_name and skill_level:
                        result['life_skills'].append({
                            'name': skill_name.get_text(strip=True),
                            'level': skill_level.get_text(strip=True)
                        })
            
            # 提取剧情技能
            juqing_skill_table = soup.find('table', id='juqing_skill_lists')
            if juqing_skill_table:
                for td in juqing_skill_table.find_all('td'):
                    skill_name = td.find('h5')
                    skill_level = td.find('p')
                    if skill_name and skill_level:
                        result['juqing_skills'].append({
                            'name': skill_name.get_text(strip=True),
                            'level': skill_level.get_text(strip=True)
                        })
            
            # 提取熟练度
            proficiency_table = soup.find('table', class_='tb02')
            if proficiency_table:
                for tr in proficiency_table.find_all('tr'):
                    th = tr.find('th')
                    td = tr.find('td')
                    if th and td:
                        key = th.get_text(strip=True).replace('：', '').replace(':', '')
                        value = td.get_text(strip=True)
                        result['proficiency'][key] = value
            
            logger.info(f"成功提取技能信息: 师门{len(result['school_skills'])}个, "
                       f"生活{len(result['life_skills'])}个, 剧情{len(result['juqing_skills'])}个")
            
        except Exception as e:
            logger.error(f"提取技能信息失败: {str(e)}")
        
        return result
