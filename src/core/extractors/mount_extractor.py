"""
坐骑信息提取器
"""
from bs4 import BeautifulSoup
from typing import Dict, Optional, List, Any
import logging
import re

logger = logging.getLogger(__name__)


class MountExtractor:
    """坐骑信息提取器"""
    
    def extract_mount_info(self, html_content: str) -> Dict[str, Any]:
        """
        提取坐骑信息
        
        Args:
            html_content: HTML内容
            
        Returns:
            包含坐骑信息的字典
        """
        soup = BeautifulSoup(html_content, 'lxml')
        result = {
            'mounts': [],        # 坐骑列表
            'xianrui_limited': [],  # 限量祥瑞
            'xianrui_normal': []    # 普通祥瑞
        }
        
        try:
            # 提取坐骑详细信息
            rider_detail_panel = soup.find('div', id='rider_detail_panel')
            if rider_detail_panel:
                mount_info = self._extract_mount_detail(rider_detail_panel)
                if mount_info:
                    result['mounts'].append(mount_info)
            
            # 提取限量祥瑞
            xianrui_tables = soup.find_all('table', id='RoleXiangRui')
            for table in xianrui_tables:
                # 检查父元素是否有"限量祥瑞"标题
                parent = table.find_parent()
                if parent:
                    prev_h4 = parent.find_previous_sibling('h4')
                    if prev_h4 and '限量祥瑞' in prev_h4.get_text():
                        for tr in table.find_all('tr'):
                            th = tr.find('th')
                            td = tr.find('td')
                            if th and td:
                                xianrui_name = th.get_text(strip=True)
                                skill_text = td.get_text(strip=True)
                                result['xianrui_limited'].append({
                                    'name': xianrui_name,
                                    'skill': skill_text.replace('技能：', '').strip() if '技能：' in skill_text else skill_text
                                })
                    elif prev_h4 and '普通祥瑞' in prev_h4.get_text():
                        for tr in table.find_all('tr'):
                            th = tr.find('th')
                            td = tr.find('td')
                            if th and td:
                                xianrui_name = th.get_text(strip=True)
                                skill_text = td.get_text(strip=True)
                                if '祥瑞总数' not in xianrui_name:
                                    result['xianrui_normal'].append({
                                        'name': xianrui_name,
                                        'skill': skill_text.replace('技能：', '').strip() if '技能：' in skill_text else skill_text
                                    })
            
            # 提取玄灵珠信息
            xuanlingzhu_panel = soup.find('div', id='xuanlingzhu_detail_panel')
            if xuanlingzhu_panel:
                xuanlingzhu_info = self._extract_xuanlingzhu(xuanlingzhu_panel)
                if xuanlingzhu_info:
                    result['xuanlingzhu'] = xuanlingzhu_info
            
            logger.info(f"成功提取坐骑信息: {len(result['mounts'])}个坐骑, "
                       f"{len(result['xianrui_limited'])}个限量祥瑞, "
                       f"{len(result['xianrui_normal'])}个普通祥瑞")
            
        except Exception as e:
            logger.error(f"提取坐骑信息失败: {str(e)}")
        
        return result
    
    def _extract_mount_detail(self, panel) -> Optional[Dict[str, Any]]:
        """提取单个坐骑详细信息"""
        try:
            mount_info = {}
            
            # 提取基础属性
            attr_table = panel.find('table', class_='tb02')
            if attr_table:
                for tr in attr_table.find_all('tr'):
                    ths = tr.find_all('th')
                    tds = tr.find_all('td')
                    for i, th in enumerate(ths):
                        if i < len(tds):
                            key = th.get_text(strip=True).replace('：', '').replace(':', '')
                            value = tds[i].get_text(strip=True)
                            
                            if '类型' in key:
                                mount_info['mount_type'] = value
                            elif '等级' in key:
                                mount_info['level'] = self._parse_int(value)
                            elif '成长' in key:
                                mount_info['growth'] = self._parse_float(value)
                            elif '主属性' in key:
                                mount_info['main_attribute'] = value
            
            # 提取坐骑技能
            skill_table = panel.find('table', id='RoleRiderSkill')
            if skill_table:
                mount_info['skills'] = []
                for img in skill_table.find_all('img'):
                    skill_name = img.get('data_equip_name', '')
                    skill_level_elem = img.find_next_sibling('p')
                    if skill_name:
                        level = self._parse_int(skill_level_elem.get_text(strip=True)) if skill_level_elem else None
                        mount_info['skills'].append({
                            'name': skill_name,
                            'level': level
                        })
            
            return mount_info if mount_info else None
            
        except Exception as e:
            logger.error(f"提取坐骑详细信息失败: {str(e)}")
            return None
    
    def _extract_xuanlingzhu(self, panel) -> Optional[Dict[str, Any]]:
        """提取玄灵珠信息"""
        try:
            xuanlingzhu_info = {}
            
            for tr in panel.find_all('tr'):
                th = tr.find('th')
                td = tr.find('td')
                if th and td:
                    key = th.get_text(strip=True).replace('：', '').replace(':', '')
                    value = td.get_text(strip=True)
                    
                    if '类型' in key:
                        xuanlingzhu_info['type'] = value
                    elif '效果' in key:
                        xuanlingzhu_info['effect'] = value
            
            return xuanlingzhu_info if xuanlingzhu_info else None
            
        except Exception as e:
            logger.error(f"提取玄灵珠信息失败: {str(e)}")
            return None
    
    def _parse_int(self, value: str) -> Optional[int]:
        """解析整数"""
        if not value:
            return None
        try:
            cleaned = re.sub(r'[^\d-]', '', value)
            return int(cleaned) if cleaned else None
        except:
            return None
    
    def _parse_float(self, value: str) -> Optional[float]:
        """解析浮点数"""
        if not value:
            return None
        try:
            cleaned = re.sub(r'[^\d.-]', '', value)
            return float(cleaned) if cleaned else None
        except:
            return None
