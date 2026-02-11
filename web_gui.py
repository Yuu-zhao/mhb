# -*- coding: utf-8 -*-
"""
网页抓取Web GUI应用（优化版）
简化界面，自动化Cookie获取流程
"""
from flask import Flask, render_template_string, request, jsonify
from scraper import WebScraper
from selenium_scraper import SeleniumScraper
from playwright_scraper import PlaywrightScraper
from database import DatabaseManager
from cookie_helper import CookieHelper
from data_extractor import DataExtractor
from login_state_manager import LoginStateManager
from browser_manager import BrowserManager
import sys
from pathlib import Path
# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent))
from src.application.services.multi_tab_scraping_service import MultiTabScrapingService
from src.application.services.data_mapper_service import DataMapperService
from src.infrastructure.database.product_repository import ProductRepository
from src.infrastructure.database.generic_repository import GenericRepository
import logging
import os
import json
import threading
import time as time_module

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
db_manager = DatabaseManager()
data_extractor = DataExtractor()
login_manager = LoginStateManager()  # 中心化登录态管理
browser_manager = BrowserManager()  # 浏览器管理器（单例）
product_repository = ProductRepository()  # 商品数据仓库
data_mapper = DataMapperService()  # 数据映射服务
generic_repository = GenericRepository()  # 泛型数据仓库

# 数据浏览页面模板
DATA_VIEW_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>数据详情 - {{ title }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f5f5f5;
            padding: 20px;
            line-height: 1.6;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 {
            font-size: 24px;
            margin: 0;
        }
        .header .back-btn {
            background: rgba(255,255,255,0.2);
            color: white;
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }
        .header .back-btn:hover {
            background: rgba(255,255,255,0.3);
        }
        .content {
            padding: 30px;
            display: flex;
            gap: 30px;
        }
        .content-left {
            flex: 1;
            min-width: 0;
        }
        .content-right {
            width: 50%;
            min-width: 400px;
        }
        .goods-info-card {
            background: #fff;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        .goods-info-header {
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 20px;
            margin-bottom: 20px;
        }
        .goods-info-header .price {
            font-size: 36px;
            color: #ff6600;
            font-weight: bold;
            margin: 15px 0;
        }
        .highlights {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 15px;
        }
        .highlight-tag {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
            color: white;
            padding: 6px 14px;
            border-radius: 16px;
            font-size: 13px;
            font-weight: 500;
        }
        .goods-info-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        .goods-info-list li {
            padding: 12px 0;
            border-bottom: 1px solid #f5f5f5;
            display: flex;
            align-items: center;
        }
        .goods-info-list li:last-child {
            border-bottom: none;
        }
        .goods-info-list li strong {
            color: #333;
            min-width: 140px;
            font-weight: 600;
        }
        .goods-info-list li span {
            color: #666;
            flex: 1;
        }
        .tab-container {
            margin-top: 30px;
        }
        .tab-buttons {
            display: flex;
            gap: 10px;
            border-bottom: 2px solid #e0e0e0;
            margin-bottom: 25px;
            flex-wrap: wrap;
        }
        .tab-button {
            padding: 12px 24px;
            background: transparent;
            border: none;
            border-bottom: 3px solid transparent;
            cursor: pointer;
            font-size: 15px;
            color: #666;
            transition: all 0.3s;
            font-weight: 500;
        }
        .tab-button:hover {
            color: #667eea;
        }
        .tab-button.active {
            color: #667eea;
            border-bottom-color: #667eea;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .info-section {
            background: #fafafa;
            border: 1px solid #e8e8e8;
            border-radius: 6px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .info-section h4 {
            color: #333;
            margin-bottom: 15px;
            font-size: 18px;
            font-weight: 600;
            border-left: 4px solid #667eea;
            padding-left: 12px;
        }
        .skill-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .skill-item {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            padding: 15px;
            text-align: center;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .skill-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .skill-item .skill-name {
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
            font-size: 15px;
        }
        .skill-item .skill-level {
            color: #667eea;
            font-size: 16px;
            font-weight: 600;
        }
        .equip-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .equip-item {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            padding: 15px;
            text-align: center;
            position: relative;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .equip-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .equip-item.equipped::before {
            content: "已装备";
            position: absolute;
            top: 8px;
            right: 8px;
            background: #28a745;
            color: white;
            font-size: 11px;
            padding: 3px 8px;
            border-radius: 12px;
        }
        .pet-card {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .pet-card h5 {
            color: #333;
            margin-bottom: 15px;
            font-size: 18px;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 10px;
        }
        .pet-attr-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
            gap: 12px;
            margin-top: 15px;
        }
        .pet-attr-item {
            background: #f8f9fa;
            padding: 12px;
            border-radius: 6px;
            text-align: center;
        }
        .pet-attr-item .attr-label {
            font-size: 13px;
            color: #666;
            margin-bottom: 6px;
        }
        .pet-attr-item .attr-value {
            font-size: 16px;
            font-weight: 600;
            color: #333;
        }
        .meta-info {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
            font-size: 14px;
            color: #666;
        }
        .meta-info span {
            margin-right: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 数据详情</h1>
            <a href="/" class="back-btn">← 返回首页</a>
        </div>
        <div class="content">
            <div class="content-left">
                <div class="meta-info">
                    <span><strong>ID:</strong> {{ data_id }}</span>
                    <span><strong>创建时间:</strong> {{ created_at }}</span>
                    <span><strong>URL:</strong> <a href="{{ url }}" target="_blank">{{ url[:60] }}{% if url|length > 60 %}...{% endif %}</a></span>
                </div>
                
                {% if extracted_data %}
                <!-- 标签页容器 -->
                <div class="tab-container">
                    <div class="tab-buttons">
                        {% if extracted_data.basic_info %}
                            <button class="tab-button active" onclick="switchTab('basic')">👤 人物/修炼</button>
                        {% endif %}
                        {% if extracted_data.skill_info %}
                            <button class="tab-button" onclick="switchTab('skill')">⚔️ 技能</button>
                        {% endif %}
                        {% if extracted_data.equip_info %}
                            <button class="tab-button" onclick="switchTab('equip')">🎒 道具/法宝</button>
                        {% endif %}
                        {% if extracted_data.pet_info %}
                            <button class="tab-button" onclick="switchTab('pet')">🐉 召唤兽/孩子</button>
                        {% endif %}
                        {% if extracted_data.mount_info %}
                            <button class="tab-button" onclick="switchTab('mount')">🐴 坐骑</button>
                        {% endif %}
                        {% if extracted_data.appearance_info %}
                            <button class="tab-button" onclick="switchTab('appearance')">👗 锦衣/外观</button>
                        {% endif %}
                        {% if extracted_data.home_info %}
                            <button class="tab-button" onclick="switchTab('home')">🏠 玩家之家</button>
                        {% endif %}
                    </div>
                    
                    <!-- 人物/修炼标签页 -->
                    {% if extracted_data.basic_info %}
                        <div class="tab-content active" id="tab-basic">
                            {% set basic = extracted_data.basic_info %}
                            <div class="info-section">
                                <h4>角色属性</h4>
                                <ul class="goods-info-list">
                                    {% if basic.get('级别') %}<li><strong>级别：</strong><span>{{ basic['级别'] }}</span></li>{% endif %}
                                    {% if basic.get('角色') %}<li><strong>角色：</strong><span>{{ basic['角色'] }}</span></li>{% endif %}
                                    {% if basic.get('门派') %}<li><strong>门派：</strong><span>{{ basic['门派'] }}</span></li>{% endif %}
                                    {% if basic.get('新版乾元丹数量') %}<li><strong>新版乾元丹数量：</strong><span>{{ basic['新版乾元丹数量'] }}</span></li>{% endif %}
                                    {% if basic.get('月饼粽子机缘') %}<li><strong>月饼粽子机缘：</strong><span>{{ basic['月饼粽子机缘'] }}</span></li>{% endif %}
                                    {% if basic.get('飞升/渡劫/化圣') %}<li><strong>飞升/渡劫/化圣：</strong><span>{{ basic['飞升/渡劫/化圣'] }}</span></li>{% endif %}
                                    {% if basic.get('成就点数') %}<li><strong>成就点数：</strong><span>{{ basic['成就点数'] }}</span></li>{% endif %}
                                    {% if basic.get('已用潜能果数量') %}<li><strong>已用潜能果数量：</strong><span>{{ basic['已用潜能果数量'] }}</span></li>{% endif %}
                                    {% if basic.get('总经验') %}<li><strong>总经验：</strong><span>{{ basic['总经验'] }}</span></li>{% endif %}
                                </ul>
                            </div>
                            <div class="info-section">
                                <h4>修炼</h4>
                                <ul class="goods-info-list">
                                    {% if basic.get('攻击修炼') %}<li><strong>攻击修炼：</strong><span>{{ basic['攻击修炼'] }}</span></li>{% endif %}
                                    {% if basic.get('防御修炼') %}<li><strong>防御修炼：</strong><span>{{ basic['防御修炼'] }}</span></li>{% endif %}
                                    {% if basic.get('法术修炼') %}<li><strong>法术修炼：</strong><span>{{ basic['法术修炼'] }}</span></li>{% endif %}
                                    {% if basic.get('抗法修炼') %}<li><strong>抗法修炼：</strong><span>{{ basic['抗法修炼'] }}</span></li>{% endif %}
                                    {% if basic.get('猎术修炼') %}<li><strong>猎术修炼：</strong><span>{{ basic['猎术修炼'] }}</span></li>{% endif %}
                                    {% if basic.get('育兽术') %}<li><strong>育兽术：</strong><span>{{ basic['育兽术'] }}</span></li>{% endif %}
                                </ul>
                            </div>
                            <div class="info-section">
                                <h4>控制力</h4>
                                <ul class="goods-info-list">
                                    {% if basic.get('攻击控制力') %}<li><strong>攻击控制力：</strong><span>{{ basic['攻击控制力'] }}</span></li>{% endif %}
                                    {% if basic.get('防御控制力') %}<li><strong>防御控制力：</strong><span>{{ basic['防御控制力'] }}</span></li>{% endif %}
                                    {% if basic.get('法术控制力') %}<li><strong>法术控制力：</strong><span>{{ basic['法术控制力'] }}</span></li>{% endif %}
                                    {% if basic.get('抗法控制力') %}<li><strong>抗法控制力：</strong><span>{{ basic['抗法控制力'] }}</span></li>{% endif %}
                                </ul>
                            </div>
                        </div>
                    {% endif %}
                    
                    <!-- 技能标签页 -->
                    {% if extracted_data.skill_info %}
                        <div class="tab-content" id="tab-skill">
                            {% set skill = extracted_data.skill_info %}
                            {% if skill.get('school_skills') %}
                                <div class="info-section">
                                    <h4>师门技能</h4>
                                    <div class="skill-grid">
                                        {% for s in skill['school_skills'] %}
                                            <div class="skill-item">
                                                <div class="skill-name">{{ s.get('name', '未知') }}</div>
                                                <div class="skill-level">{{ s.get('level', '0') }}级</div>
                                            </div>
                                        {% endfor %}
                                    </div>
                                </div>
                            {% endif %}
                            {% if skill.get('life_skills') %}
                                <div class="info-section">
                                    <h4>生活技能</h4>
                                    <div class="skill-grid">
                                        {% for s in skill['life_skills'] %}
                                            <div class="skill-item">
                                                <div class="skill-name">{{ s.get('name', '未知') }}</div>
                                                <div class="skill-level">{{ s.get('level', '0') }}级</div>
                                            </div>
                                        {% endfor %}
                                    </div>
                                </div>
                            {% endif %}
                            {% if skill.get('story_skills') %}
                                <div class="info-section">
                                    <h4>剧情技能</h4>
                                    <div class="skill-grid">
                                        {% for s in skill['story_skills'] %}
                                            <div class="skill-item">
                                                <div class="skill-name">{{ s.get('name', '未知') }}</div>
                                                <div class="skill-level">{{ s.get('level', '0') }}级</div>
                                            </div>
                                        {% endfor %}
                                    </div>
                                    {% if skill.get('story_skill_remaining_points') %}
                                        <div style="margin-top: 15px; color: #666;">剩余技能点：{{ skill['story_skill_remaining_points'] }}</div>
                                    {% endif %}
                                </div>
                            {% endif %}
                            {% if skill.get('proficiency') %}
                                <div class="info-section">
                                    <h4>熟练度</h4>
                                    <ul class="goods-info-list">
                                        {% for key, value in skill['proficiency'].items() %}
                                            <li><strong>{{ key }}：</strong><span>{{ value }}</span></li>
                                        {% endfor %}
                                    </ul>
                                </div>
                            {% endif %}
                        </div>
                    {% endif %}
                    
                    <!-- 道具/法宝标签页 -->
                    {% if extracted_data.equip_info %}
                        <div class="tab-content" id="tab-equip">
                            {% set equip = extracted_data.equip_info %}
                            {% if equip.get('equipments') %}
                                <div class="info-section">
                                    <h4>已装备道具</h4>
                                    <div class="equip-grid">
                                        {% for item in equip['equipments'] %}
                                            <div class="equip-item equipped">
                                                <div class="skill-name">{{ item.get('name', '未知') }}</div>
                                                {% if item.get('level') %}
                                                    <div style="font-size: 12px; color: #666; margin-top: 5px;">等级: {{ item['level'] }}</div>
                                                {% endif %}
                                                {% if item.get('type_desc') %}
                                                    <div style="font-size: 11px; color: #999; margin-top: 3px;">{{ item['type_desc'] }}</div>
                                                {% endif %}
                                            </div>
                                        {% endfor %}
                                    </div>
                                </div>
                            {% endif %}
                            {% if equip.get('shenqi') %}
                                <div class="info-section">
                                    <h4>神器</h4>
                                    <div class="equip-grid">
                                        {% for item in equip['shenqi'] %}
                                            <div class="equip-item equipped">
                                                <div class="skill-name">{{ item.get('name', '未知') }}</div>
                                                {% if item.get('level') %}
                                                    <div style="font-size: 12px; color: #666; margin-top: 5px;">等级: {{ item['level'] }}</div>
                                                {% endif %}
                                            </div>
                                        {% endfor %}
                                    </div>
                                </div>
                            {% endif %}
                            {% if equip.get('lingbao_equipped') %}
                                <div class="info-section">
                                    <h4>已装备灵宝</h4>
                                    <div class="equip-grid">
                                        {% for item in equip['lingbao_equipped'] %}
                                            <div class="equip-item equipped">
                                                <div class="skill-name">{{ item.get('name', '未知') }}</div>
                                                {% if item.get('level') %}
                                                    <div style="font-size: 12px; color: #666; margin-top: 5px;">等级: {{ item['level'] }}</div>
                                                {% endif %}
                                            </div>
                                        {% endfor %}
                                    </div>
                                </div>
                            {% endif %}
                            {% if equip.get('fabao_equipped') %}
                                <div class="info-section">
                                    <h4>已装备法宝</h4>
                                    <div class="equip-grid">
                                        {% for item in equip['fabao_equipped'] %}
                                            <div class="equip-item equipped">
                                                <div class="skill-name">{{ item.get('name', '未知') }}</div>
                                                {% if item.get('level') %}
                                                    <div style="font-size: 12px; color: #666; margin-top: 5px;">等级: {{ item['level'] }}</div>
                                                {% endif %}
                                            </div>
                                        {% endfor %}
                                    </div>
                                </div>
                            {% endif %}
                            {% if equip.get('currency') %}
                                <div class="info-section">
                                    <h4>货币</h4>
                                    <ul class="goods-info-list">
                                        {% for key, value in equip['currency'].items() %}
                                            <li><strong>{{ key }}：</strong><span>{{ value }}</span></li>
                                        {% endfor %}
                                    </ul>
                                </div>
                            {% endif %}
                        </div>
                    {% endif %}
                    
                    <!-- 召唤兽/孩子标签页 -->
                    {% if extracted_data.pet_info %}
                        <div class="tab-content" id="tab-pet">
                            {% set pet = extracted_data.pet_info %}
                            {% if pet.get('pets') %}
                                {% for p in pet['pets'] %}
                                    <div class="pet-card">
                                        <h5>召唤兽 {{ loop.index }}{% if p.get('pet_type') %} - {{ p['pet_type'] }}{% endif %}</h5>
                                        <div class="pet-attr-grid">
                                            {% if p.get('level') %}
                                                <div class="pet-attr-item">
                                                    <div class="attr-label">等级</div>
                                                    <div class="attr-value">{{ p['level'] }}</div>
                                                </div>
                                            {% endif %}
                                            {% if p.get('hp') %}
                                                <div class="pet-attr-item">
                                                    <div class="attr-label">气血</div>
                                                    <div class="attr-value">{{ p['hp'] }}</div>
                                                </div>
                                            {% endif %}
                                            {% if p.get('attack') %}
                                                <div class="pet-attr-item">
                                                    <div class="attr-label">攻击</div>
                                                    <div class="attr-value">{{ p['attack'] }}</div>
                                                </div>
                                            {% endif %}
                                            {% if p.get('defense') %}
                                                <div class="pet-attr-item">
                                                    <div class="attr-label">防御</div>
                                                    <div class="attr-value">{{ p['defense'] }}</div>
                                                </div>
                                            {% endif %}
                                            {% if p.get('speed') %}
                                                <div class="pet-attr-item">
                                                    <div class="attr-label">速度</div>
                                                    <div class="attr-value">{{ p['speed'] }}</div>
                                                </div>
                                            {% endif %}
                                            {% if p.get('growth') %}
                                                <div class="pet-attr-item">
                                                    <div class="attr-label">成长</div>
                                                    <div class="attr-value">{{ p['growth'] }}</div>
                                                </div>
                                            {% endif %}
                                        </div>
                                    </div>
                                {% endfor %}
                            {% endif %}
                            {% if pet.get('children') %}
                                <div class="info-section">
                                    <h4>孩子</h4>
                                    <p>共有 {{ pet['children']|length }} 个孩子</p>
                                </div>
                            {% endif %}
                        </div>
                    {% endif %}
                    
                    <!-- 坐骑标签页 -->
                    {% if extracted_data.mount_info %}
                        <div class="tab-content" id="tab-mount">
                            {% set mount = extracted_data.mount_info %}
                            {% if mount.get('mounts') %}
                                {% for m in mount['mounts'] %}
                                    <div class="info-section">
                                        <h4>坐骑 {{ loop.index }}{% if m.get('mount_type') %} - {{ m['mount_type'] }}{% endif %}</h4>
                                        <ul class="goods-info-list">
                                            {% if m.get('level') %}<li><strong>等级：</strong><span>{{ m['level'] }}</span></li>{% endif %}
                                            {% if m.get('growth') %}<li><strong>成长：</strong><span>{{ m['growth'] }}</span></li>{% endif %}
                                            {% if m.get('main_attribute') %}<li><strong>主属性：</strong><span>{{ m['main_attribute'] }}</span></li>{% endif %}
                                        </ul>
                                    </div>
                                {% endfor %}
                            {% endif %}
                        </div>
                    {% endif %}
                    
                    <!-- 锦衣/外观标签页 -->
                    {% if extracted_data.appearance_info %}
                        <div class="tab-content" id="tab-appearance">
                            {% set appearance = extracted_data.appearance_info %}
                            {% if appearance.get('jinyi') %}
                                {% if appearance['jinyi'].get('limited') %}
                                    <div class="info-section">
                                        <h4>限量锦衣</h4>
                                        <div class="equip-grid">
                                            {% for item in appearance['jinyi']['limited'] %}
                                                <div class="equip-item">
                                                    <div class="skill-name">{{ item }}</div>
                                                </div>
                                            {% endfor %}
                                        </div>
                                    </div>
                                {% endif %}
                                {% if appearance['jinyi'].get('normal') %}
                                    <div class="info-section">
                                        <h4>普通锦衣</h4>
                                        <div class="equip-grid">
                                            {% for item in appearance['jinyi']['normal'] %}
                                                <div class="equip-item">
                                                    <div class="skill-name">{{ item }}</div>
                                                </div>
                                            {% endfor %}
                                        </div>
                                    </div>
                                {% endif %}
                            {% endif %}
                        </div>
                    {% endif %}
                    
                    <!-- 玩家之家标签页 -->
                    {% if extracted_data.home_info %}
                        <div class="tab-content" id="tab-home">
                            {% set home = extracted_data.home_info %}
                            <div class="info-section">
                                <h4>房屋信息</h4>
                                <ul class="goods-info-list">
                                    {% if home.get('house_level') %}<li><strong>房屋等级：</strong><span>{{ home['house_level'] }}</span></li>{% endif %}
                                    {% if home.get('house_type') %}<li><strong>房屋类型：</strong><span>{{ home['house_type'] }}</span></li>{% endif %}
                                    {% if home.get('house_fengshui') %}<li><strong>房屋风水：</strong><span>{{ home['house_fengshui'] }}</span></li>{% endif %}
                                    {% if home.get('furniture_score') %}<li><strong>家具评分：</strong><span>{{ home['furniture_score'] }}</span></li>{% endif %}
                                </ul>
                            </div>
                        </div>
                    {% endif %}
                </div>
                {% else %}
                    <div class="info-section">
                        <p style="color: #999; text-align: center;">暂无提取数据</p>
                    </div>
                {% endif %}
            </div>
            
            <div class="content-right">
                {% if extracted_data %}
                    {% if extracted_data.basic_info %}
                        <!-- 商品基本信息卡片 -->
                        <div class="goods-info-card">
                            <div class="goods-info-header">
                                {% if extracted_data.basic_info.get('价格') %}
                                    <div class="price">{{ extracted_data.basic_info['价格'] }}</div>
                                {% endif %}
                                {% if extracted_data.basic_info.get('亮点') %}
                                    <div class="highlights">
                                        {% set highlights = extracted_data.basic_info['亮点'] %}
                                        {% if highlights is string %}
                                            {% set highlight_list = highlights.split('|') %}
                                        {% else %}
                                            {% set highlight_list = highlights %}
                                        {% endif %}
                                        {% for highlight in highlight_list %}
                                            {% if highlight and highlight.strip() %}
                                                <span class="highlight-tag">{{ highlight.strip() }}</span>
                                            {% endif %}
                                        {% endfor %}
                                    </div>
                                {% endif %}
                            </div>
                            <ul class="goods-info-list">
                                {% if extracted_data.basic_info.get('编号') %}
                                    <li><strong>编号：</strong><span>{{ extracted_data.basic_info['编号'] }}</span></li>
                                {% endif %}
                                {% if extracted_data.basic_info.get('卖家') %}
                                    <li><strong>卖家：</strong><span>{{ extracted_data.basic_info['卖家'] }}</span></li>
                                {% endif %}
                                {% if extracted_data.basic_info.get('卖家ID') %}
                                    <li><strong>卖家ID：</strong><span>{{ extracted_data.basic_info['卖家ID'] }}</span></li>
                                {% endif %}
                                {% if extracted_data.basic_info.get('是否上架') %}
                                    <li><strong>是否上架：</strong><span>{{ extracted_data.basic_info['是否上架'] }}</span></li>
                                {% endif %}
                                {% if extracted_data.basic_info.get('是否接受还价') %}
                                    <li><strong>是否接受还价：</strong><span>{{ '是' if extracted_data.basic_info['是否接受还价'] else '否' }}</span></li>
                                {% endif %}
                                {% if extracted_data.basic_info.get('出售剩余时间') %}
                                    <li><strong>出售剩余时间：</strong><span>{{ extracted_data.basic_info['出售剩余时间'] }}</span></li>
                                {% endif %}
                            </ul>
                        </div>
                    {% endif %}
                {% endif %}
            </div>
        </div>
    </div>
    
    <script>
        function switchTab(tabId) {
            // 隐藏所有标签内容
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // 移除所有按钮的active状态
            document.querySelectorAll('.tab-button').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // 显示选中的标签内容
            const tabContent = document.getElementById('tab-' + tabId);
            if (tabContent) {
                tabContent.classList.add('active');
            }
            
            // 激活对应的按钮
            event.target.classList.add('active');
        }
    </script>
</body>
</html>
"""

# 简化的HTML模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>网页抓取工具</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .content {
            padding: 30px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .left-panel, .right-panel {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        .section {
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .section h2 {
            color: #333;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: 500;
        }
        input[type="text"], select {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn-group {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        button {
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s;
            flex: 1;
            min-width: 120px;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .btn-success {
            background: #28a745;
            color: white;
        }
        .btn-success:hover {
            background: #218838;
        }
        .btn-info {
            background: #17a2b8;
            color: white;
        }
        .btn-info:hover {
            background: #138496;
        }
        .btn-warning {
            background: #ffc107;
            color: #333;
        }
        .btn-warning:hover {
            background: #e0a800;
        }
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .preview-box {
            background: white;
            border: 2px solid #ddd;
            border-radius: 6px;
            padding: 15px;
            max-height: 500px;
            overflow-y: auto;
            font-size: 13px;
            line-height: 1.6;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .status {
            padding: 10px;
            border-radius: 6px;
            margin-bottom: 15px;
            display: none;
        }
        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .status.info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        .status.warning {
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
        }
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .cookie-status {
            padding: 10px;
            border-radius: 6px;
            margin-top: 10px;
            font-size: 0.9em;
        }
        .cookie-status.has-cookie {
            background: #d4edda;
            color: #155724;
        }
        .cookie-status.no-cookie {
            background: #fff3cd;
            color: #856404;
        }
        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        .data-table th, .data-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        .data-table th {
            background: #f8f9fa;
            font-weight: 600;
            color: #333;
        }
        .data-table tr:hover {
            background: #f8f9fa;
        }
        /* 藏宝阁风格样式 */
        .goods-info-card {
            background: #fff;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .goods-info-header {
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 15px;
            margin-bottom: 15px;
        }
        .goods-info-header .price {
            font-size: 28px;
            color: #ff6600;
            font-weight: bold;
            margin: 10px 0;
        }
        .goods-info-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        .goods-info-list li {
            padding: 8px 0;
            border-bottom: 1px solid #f5f5f5;
            display: flex;
            align-items: center;
        }
        .goods-info-list li:last-child {
            border-bottom: none;
        }
        .goods-info-list li strong {
            color: #333;
            min-width: 120px;
            font-weight: 600;
        }
        .goods-info-list li span {
            color: #666;
            flex: 1;
        }
        .highlights {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 5px;
        }
        .highlight-tag {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }
        .tab-container {
            margin-top: 20px;
        }
        .tab-buttons {
            display: flex;
            gap: 10px;
            border-bottom: 2px solid #e0e0e0;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .tab-button {
            padding: 10px 20px;
            background: transparent;
            border: none;
            border-bottom: 3px solid transparent;
            cursor: pointer;
            font-size: 14px;
            color: #666;
            transition: all 0.3s;
            font-weight: 500;
        }
        .tab-button:hover {
            color: #667eea;
        }
        .tab-button.active {
            color: #667eea;
            border-bottom-color: #667eea;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .info-section {
            background: #fafafa;
            border: 1px solid #e8e8e8;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 15px;
        }
        .info-section h4 {
            color: #333;
            margin-bottom: 12px;
            font-size: 16px;
            font-weight: 600;
            border-left: 4px solid #667eea;
            padding-left: 10px;
        }
        .skill-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }
        .skill-item {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            padding: 10px;
            text-align: center;
        }
        .skill-item .skill-name {
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }
        .skill-item .skill-level {
            color: #667eea;
            font-size: 14px;
        }
        .equip-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }
        .equip-item {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            padding: 10px;
            text-align: center;
            position: relative;
        }
        .equip-item.equipped::before {
            content: "已装备";
            position: absolute;
            top: 5px;
            right: 5px;
            background: #28a745;
            color: white;
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 3px;
        }
        .pet-card {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        }
        .pet-card h5 {
            color: #333;
            margin-bottom: 10px;
            font-size: 16px;
        }
        .pet-attr-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            gap: 8px;
            margin-top: 10px;
        }
        .pet-attr-item {
            background: #f8f9fa;
            padding: 8px;
            border-radius: 4px;
            text-align: center;
        }
        .pet-attr-item .attr-label {
            font-size: 12px;
            color: #666;
            margin-bottom: 4px;
        }
        .pet-attr-item .attr-value {
            font-size: 14px;
            font-weight: 600;
            color: #333;
        }
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
        }
        .modal-content {
            background: white;
            margin: 5% auto;
            padding: 30px;
            border-radius: 10px;
            width: 80%;
            max-width: 800px;
            max-height: 80vh;
            overflow-y: auto;
        }
        .close {
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }
        .close:hover {
            color: #000;
        }
        @media (max-width: 768px) {
            .content {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🕷️ 网页抓取工具</h1>
            <p>智能抓取，自动登录</p>
        </div>
        <div class="content">
            <!-- 左侧面板 -->
            <div class="left-panel">
                <!-- 1. 地址输入 -->
                <div class="section">
                    <h2>📍 地址输入</h2>
                    <div class="form-group">
                        <label for="url">网页地址:</label>
                        <input type="text" id="url" placeholder="https://example.com" value="https://">
                    </div>
                    <div class="btn-group">
                        <button class="btn-primary" onclick="startWorkflow()">开始抓取</button>
                        <button class="btn-success" onclick="startMultiTabWorkflow()" style="margin-left: 10px;">多标签页抓取</button>
                    </div>
                </div>

                <!-- 2. Cookie管理 -->
                <div class="section">
                    <h2>🍪 Cookie管理</h2>
                    <div id="cookieStatus" class="cookie-status no-cookie">
                        ⚠️ 未检测到Cookie，将自动获取
                    </div>
                    <div class="btn-group">
                        <button class="btn-warning" onclick="autoGetCookie()">自动获取Cookie</button>
                        <button class="btn-info" onclick="loadCookieFile()">从文件加载</button>
                        <button class="btn-info" onclick="saveCookieFile()">保存到文件</button>
                        <input type="file" id="cookieFileInput" accept=".json" style="display:none" onchange="handleCookieFileSelect(event)">
                    </div>
                    <div style="margin-top: 10px; font-size: 0.9em; color: #666;">
                        💡 首次使用会自动检测登录需求并获取Cookie
                    </div>
                </div>

                <!-- 3. 爬取模式 -->
                <div class="section">
                    <h2>⚙️ 爬取模式</h2>
                    <div class="form-group">
                        <label for="method">选择模式:</label>
                        <select id="method">
                            <option value="playwright">Playwright（推荐，自动登录）</option>
                            <option value="selenium">Selenium（支持JavaScript）</option>
                            <option value="requests">Requests（快速，需Cookie）</option>
                        </select>
                    </div>
                    <div style="margin-top: 10px; font-size: 0.9em; color: #666;">
                        <div>✅ Playwright: 自动保存登录态，一次登录永久使用</div>
                        <div>✅ Selenium: 支持复杂JavaScript页面</div>
                        <div>✅ Requests: 最快，适合简单页面</div>
                    </div>
                </div>

                <!-- 4. 操作 -->
                <div class="section">
                    <h2>🎯 操作</h2>
                    <div class="btn-group">
                        <button class="btn-success" id="saveBtn" onclick="saveToDatabase()" disabled>保存到数据库</button>
                        <button class="btn-info" onclick="viewSavedData()">查看已保存</button>
                        <button class="btn-secondary" onclick="clearPreview()">清空预览</button>
                    </div>
                </div>
            </div>

            <!-- 右侧面板 -->
            <div class="right-panel">
                <!-- 5. 浏览 -->
                <div class="section" style="flex: 1;">
                    <h2>👀 数据预览</h2>
                    <div class="form-group">
                        <label>标题:</label>
                        <div class="preview-box" id="previewTitle">暂无数据</div>
                    </div>
                    <div class="form-group">
                        <label>提取的关键信息:</label>
                        <div class="preview-box" id="previewExtracted" style="max-height: 200px; font-size: 12px; overflow-y: auto;">暂无提取数据</div>
                    </div>
                    <div class="form-group">
                        <label>内容:</label>
                        <div class="preview-box" id="previewContent">暂无数据</div>
                    </div>
                </div>
            </div>
        </div>

        <div id="status" class="status"></div>
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p style="margin-top: 10px;" id="loadingText">正在处理...</p>
        </div>
    </div>

    <!-- 数据列表模态框 -->
    <div id="dataModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal()">&times;</span>
            <h2>已保存的数据</h2>
            <div id="dataList"></div>
        </div>
    </div>

    <script>
        let currentPageData = null;
        // 不再在前端持久化Cookie和storage_state，由后端LoginStateManager统一管理

        function showStatus(message, type) {
            const statusDiv = document.getElementById('status');
            statusDiv.textContent = message;
            statusDiv.className = 'status ' + type;
            statusDiv.style.display = 'block';
            setTimeout(() => {
                statusDiv.style.display = 'none';
            }, 5000);
        }

        function updateLoading(text) {
            document.getElementById('loadingText').textContent = text;
        }

        // 多标签页抓取工作流程
        async function startMultiTabWorkflow() {
            const url = document.getElementById('url').value.trim();
            if (!url || url === 'https://') {
                showStatus('请输入有效的URL', 'error');
                return;
            }

            if (!url.startsWith('http://') && !url.startsWith('https://')) {
                showStatus('URL必须以http://或https://开头', 'error');
                return;
            }

            const method = document.getElementById('method').value;
            
            if (method !== 'playwright') {
                showStatus('多标签页抓取仅支持Playwright方法，请先切换抓取方法', 'error');
                return;
            }
            
            document.getElementById('loading').style.display = 'block';
            updateLoading('正在抓取所有标签页（人物/修炼、技能、道具/法宝）...');
            document.querySelector('.btn-primary').disabled = true;
            document.querySelector('.btn-success').disabled = true;
            document.getElementById('saveBtn').disabled = true;

            try {
                const fetchResult = await fetch('/api/fetch_all_tabs', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        url: url,
                        method: method
                    })
                }).then(r => r.json());

                document.getElementById('loading').style.display = 'none';
                document.querySelector('.btn-primary').disabled = false;
                document.querySelector('.btn-success').disabled = false;

                if (!fetchResult.success) {
                    showStatus('抓取失败: ' + (fetchResult.error || '未知错误'), 'error');
                    return;
                }

                if (fetchResult.success) {
                    currentPageData = fetchResult.data;
                    let title = fetchResult.data.title || '无标题';
                    document.getElementById('previewTitle').textContent = title;
                    
                    // 显示多标签页提取的关键信息
                    if (fetchResult.data.extracted_data) {
                        displayExtractedData(fetchResult.data.extracted_data);
                        currentPageData.extracted_data = fetchResult.data.extracted_data;
                        
                        // 统计提取的字段数
                        let totalFields = 0;
                        if (fetchResult.data.extracted_data.basic_info) {
                            totalFields += Object.keys(fetchResult.data.extracted_data.basic_info).filter(k => fetchResult.data.extracted_data.basic_info[k]).length;
                        }
                        if (fetchResult.data.extracted_data.skill_info) {
                            totalFields += Object.keys(fetchResult.data.extracted_data.skill_info).filter(k => fetchResult.data.extracted_data.skill_info[k]).length;
                        }
                        if (fetchResult.data.extracted_data.equip_info) {
                            totalFields += Object.keys(fetchResult.data.extracted_data.equip_info).filter(k => fetchResult.data.extracted_data.equip_info[k]).length;
                        }
                        
                        showStatus(`✅ 多标签页抓取成功！标题: ${title}, 共提取了 ${totalFields} 个关键字段`, 'success');
                    } else {
                        showStatus(`抓取成功！标题: ${title}`, 'success');
                    }
                    
                    // 内容预览
                    document.getElementById('previewContent').textContent = '已提取所有标签页的关键信息，完整内容未保存（节省空间）';
                    
                    document.getElementById('saveBtn').disabled = false;
                }
            } catch (error) {
                document.getElementById('loading').style.display = 'none';
                document.querySelector('.btn-primary').disabled = false;
                document.querySelector('.btn-success').disabled = false;
                showStatus('处理失败: ' + error.message, 'error');
            }
        }

        // 主工作流程：智能抓取
        async function startWorkflow() {
            const url = document.getElementById('url').value.trim();
            if (!url || url === 'https://') {
                showStatus('请输入有效的URL', 'error');
                return;
            }

            if (!url.startsWith('http://') && !url.startsWith('https://')) {
                showStatus('URL必须以http://或https://开头', 'error');
                return;
            }

            const method = document.getElementById('method').value;
            
            document.getElementById('loading').style.display = 'block';
            document.querySelector('.btn-primary').disabled = true;
            document.getElementById('saveBtn').disabled = true;

            try {
                // Step 1: 直接抓取（使用已有登录态，如果有的话）
                updateLoading('正在抓取页面...');
                let fetchResult = await fetch('/api/fetch_and_extract', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        url: url,
                        method: method
                        // 不再传递cookie和storage_state_path，由后端LoginStateManager统一管理
                    })
                }).then(r => r.json());

                // Step 2: 如果抓取失败且提示需要登录，提示用户先获取cookie
                console.log('检查登录需求，fetchResult:', fetchResult);
                if (!fetchResult.success && (fetchResult.need_login || (fetchResult.error && (fetchResult.error.includes('登录') || fetchResult.error.includes('login'))))) {
                    console.log('检测到需要登录');
                    document.getElementById('loading').style.display = 'none';
                    document.querySelector('.btn-primary').disabled = false;
                    showStatus('页面需要登录，请先点击"自动获取Cookie"按钮获取最新登录态，然后再进行抓取', 'warning');
                    return;
                }

                // 如果仍然失败，显示错误
                if (!fetchResult.success) {
                    document.getElementById('loading').style.display = 'none';
                    document.querySelector('.btn-primary').disabled = false;
                    showStatus('抓取失败: ' + (fetchResult.error || '未知错误'), 'error');
                    return;
                }

                document.getElementById('loading').style.display = 'none';
                document.querySelector('.btn-primary').disabled = false;

                if (fetchResult.success) {
                    currentPageData = fetchResult.data;
                    let title = fetchResult.data.title || '无标题';
                    let urlInfo = '';
                    if (fetchResult.data.redirected && fetchResult.data.original_url) {
                        urlInfo = ` (已跳转: ${fetchResult.data.original_url} -> ${fetchResult.data.url})`;
                    }
                    document.getElementById('previewTitle').textContent = title;
                    
                    // 直接显示提取的关键信息
                    if (fetchResult.data.extracted_data) {
                        displayExtractedData(fetchResult.data.extracted_data);
                        currentPageData.extracted_data = fetchResult.data.extracted_data;
                        const extractedCount = Object.keys(fetchResult.data.extracted_data).filter(k => fetchResult.data.extracted_data[k]).length;
                        showStatus(`抓取成功！标题: ${title}, 提取了 ${extractedCount} 个关键字段${urlInfo}`, 'success');
                    } else {
                        showStatus(`抓取成功！标题: ${title}${urlInfo}`, 'success');
                    }
                    
                    // 内容预览（可选，显示部分内容）
                    if (fetchResult.data.content) {
                        let content = fetchResult.data.content;
                        if (content.length > 10000) {
                            content = content.substring(0, 10000) + '\\n\\n... (内容过长，已截断，仅显示提取的关键信息)';
                        }
                        document.getElementById('previewContent').textContent = content;
                    } else {
                        document.getElementById('previewContent').textContent = '已提取关键信息，完整内容未保存';
                    }
                    
                    document.getElementById('saveBtn').disabled = false;
                } else {
                    showStatus('抓取失败: ' + fetchResult.error, 'error');
                }
            } catch (error) {
                document.getElementById('loading').style.display = 'none';
                document.querySelector('.btn-primary').disabled = false;
                showStatus('处理失败: ' + error.message, 'error');
            }
        }

        // 自动获取Cookie（内部函数）- 简化版，不再管理状态
        async function autoGetCookieInternal(url) {
            try {
                console.log('开始调用 autoGetCookieInternal，URL:', url);
                updateLoading('正在启动浏览器获取Cookie...');
                showStatus('正在启动浏览器，请在弹出的窗口中完成登录...', 'info');
                
                const response = await fetch('/api/auto_get_cookie', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: url})
                });
                
                console.log('收到响应，状态:', response.status);
                const result = await response.json();
                console.log('解析结果:', result);

                if (result.success) {
                    // 登录态已由后端LoginStateManager保存，前端只需确认成功
                    updateCookieStatus(true, '登录态');
                    return {
                        success: true,
                        storage_state: result.storage_state  // 仅用于返回，不持久化
                    };
                } else {
                    console.error('登录失败:', result.error);
                    return {success: false, error: result.error};
                }
            } catch (error) {
                console.error('登录过程出错:', error);
                return {success: false, error: error.message};
            }
        }

        // 自动获取Cookie（用户触发）
        async function autoGetCookie() {
            const url = document.getElementById('url').value.trim();
            if (!url || url === 'https://') {
                showStatus('请先输入URL', 'error');
                return;
            }

            document.getElementById('loading').style.display = 'block';
            updateLoading('正在获取Cookie...');
            
            const result = await autoGetCookieInternal(url);
            
            document.getElementById('loading').style.display = 'none';
            
            if (result.success) {
                showStatus('Cookie获取成功！', 'success');
            } else {
                showStatus('Cookie获取失败: ' + result.error, 'error');
            }
        }

        // 更新Cookie状态显示
        function updateCookieStatus(hasCookie, type) {
            const statusDiv = document.getElementById('cookieStatus');
            if (hasCookie) {
                statusDiv.className = 'cookie-status has-cookie';
                statusDiv.textContent = `✅ 已获取${type}，可以开始抓取`;
            } else {
                statusDiv.className = 'cookie-status no-cookie';
                statusDiv.textContent = '⚠️ 未检测到Cookie，将自动获取';
            }
        }

        function saveToDatabase() {
            if (!currentPageData) {
                showStatus('没有可保存的数据，请先抓取页面', 'error');
                return;
            }

            fetch('/api/save', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    url: currentPageData.url,
                    title: currentPageData.title,
                    content: currentPageData.content,
                    extracted_data: currentPageData.extracted_data
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    let msg = `数据已保存到数据库！ID: ${data.id}, 标题: ${data.title}`;
                    if (data.extracted_fields > 0) {
                        msg += `, 提取了 ${data.extracted_fields} 个字段`;
                    }
                    showStatus(msg, 'success');
                } else {
                    showStatus('保存失败: ' + data.error, 'error');
                }
            })
            .catch(error => {
                showStatus('保存失败: ' + error.message, 'error');
            });
        }

        function viewSavedData() {
            fetch('/api/list')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    displayDataList(data.data);
                } else {
                    showStatus('获取数据失败: ' + data.error, 'error');
                }
            })
            .catch(error => {
                showStatus('获取数据失败: ' + error.message, 'error');
            });
        }

        function displayDataList(dataList) {
            const modal = document.getElementById('dataModal');
            const listDiv = document.getElementById('dataList');

            if (dataList.length === 0) {
                listDiv.innerHTML = '<p>数据库中暂无数据</p>';
            } else {
                let html = '<table class="data-table"><thead><tr><th>ID</th><th>URL</th><th>标题</th><th>创建时间</th><th>操作</th></tr></thead><tbody>';
                dataList.forEach(item => {
                    html += `<tr>
                        <td>${item.id}</td>
                        <td>${item.url.length > 50 ? item.url.substring(0, 50) + '...' : item.url}</td>
                        <td>${item.title ? (item.title.length > 30 ? item.title.substring(0, 30) + '...' : item.title) : '无标题'}</td>
                        <td>${item.created_at || ''}</td>
                        <td><button class="btn-info" onclick="viewDetail(${item.id})">查看详情</button></td>
                    </tr>`;
                });
                html += '</tbody></table>';
                listDiv.innerHTML = html;
            }

            modal.style.display = 'block';
        }

        function viewDetail(id) {
            // 跳转到数据浏览页面
            window.open(`/view/${id}`, '_blank');
        }

        function closeModal() {
            document.getElementById('dataModal').style.display = 'none';
        }

        function displayExtractedData(extractedData) {
            const extractedDiv = document.getElementById('previewExtracted');
            if (!extractedData || Object.keys(extractedData).length === 0) {
                extractedDiv.textContent = '暂无提取数据';
                return;
            }
            
            // 检查是否是多标签页数据
            if (extractedData.basic_info || extractedData.skill_info || extractedData.equip_info) {
                displayMultiTabData(extractedData);
                return;
            }
            
            // 单标签页数据展示
            let html = '<div class="extracted-data-container">';
            html += '<table style="width: 100%; font-size: 12px; border-collapse: collapse; margin-bottom: 10px;">';
            for (const [key, value] of Object.entries(extractedData)) {
                if (value) {
                    html += `<tr><td style="font-weight: bold; padding: 4px 8px; color: #667eea; width: 40%; background: #f5f5f5;">${key}:</td><td style="padding: 4px 8px; background: #fff;">${value}</td></tr>`;
                }
            }
            html += '</table></div>';
            extractedDiv.innerHTML = html;
        }

        function displayMultiTabData(data) {
            const extractedDiv = document.getElementById('previewExtracted');
            let html = '<div class="multi-tab-data-container">';
            
            // 商品基本信息卡片（参考藏宝阁样式）
            if (data.basic_info && Object.keys(data.basic_info).length > 0) {
                const basic = data.basic_info;
                html += '<div class="goods-info-card">';
                html += '<div class="goods-info-header">';
                
                // 价格（突出显示）
                if (basic['价格']) {
                    html += `<div class="price">${basic['价格']}</div>`;
                }
                
                // 亮点
                if (basic['亮点']) {
                    const highlights = Array.isArray(basic['亮点']) ? basic['亮点'] : basic['亮点'].split('|');
                    html += '<div class="highlights">';
                    highlights.forEach(h => {
                        if (h && h.trim()) {
                            html += `<span class="highlight-tag">${h.trim()}</span>`;
                        }
                    });
                    html += '</div>';
                }
                
                html += '</div>';
                
                // 商品信息列表
                html += '<ul class="goods-info-list">';
                const infoFields = [
                    {key: '编号', label: '编号'},
                    {key: '卖家', label: '卖家'},
                    {key: '卖家ID', label: '卖家ID'},
                    {key: '是否上架', label: '是否上架'},
                    {key: '是否接受还价', label: '是否接受还价', format: (v) => v ? '是' : '否'},
                    {key: '出售剩余时间', label: '出售剩余时间'}
                ];
                
                infoFields.forEach(field => {
                    if (basic[field.key]) {
                        const value = field.format ? field.format(basic[field.key]) : basic[field.key];
                        html += `<li><strong>${field.label}：</strong><span>${value}</span></li>`;
                    }
                });
                html += '</ul>';
                html += '</div>';
            }
            
            // 标签页容器
            html += '<div class="tab-container">';
            html += '<div class="tab-buttons">';
            const tabs = [];
            if (data.basic_info) tabs.push({id: 'basic', label: '人物/修炼', icon: '👤'});
            if (data.skill_info) tabs.push({id: 'skill', label: '技能', icon: '⚔️'});
            if (data.equip_info) tabs.push({id: 'equip', label: '道具/法宝', icon: '🎒'});
            if (data.pet_info) tabs.push({id: 'pet', label: '召唤兽/孩子', icon: '🐉'});
            if (data.mount_info) tabs.push({id: 'mount', label: '坐骑', icon: '🐴'});
            if (data.appearance_info) tabs.push({id: 'appearance', label: '锦衣/外观', icon: '👗'});
            if (data.home_info) tabs.push({id: 'home', label: '玩家之家', icon: '🏠'});
            
            tabs.forEach((tab, index) => {
                html += `<button class="tab-button ${index === 0 ? 'active' : ''}" onclick="switchTab('${tab.id}')">${tab.icon} ${tab.label}</button>`;
            });
            html += '</div>';
            
            // 人物/修炼标签页
            if (data.basic_info) {
                html += `<div class="tab-content ${tabs[0]?.id === 'basic' ? 'active' : ''}" id="tab-basic">`;
                html += displayCharacterInfo(data.basic_info);
                html += '</div>';
            }
            
            // 技能标签页
            if (data.skill_info) {
                html += `<div class="tab-content" id="tab-skill">`;
                html += displaySkillInfo(data.skill_info);
                html += '</div>';
            }
            
            // 道具/法宝标签页
            if (data.equip_info) {
                html += `<div class="tab-content" id="tab-equip">`;
                html += displayEquipInfo(data.equip_info);
                html += '</div>';
            }
            
            // 召唤兽/孩子标签页
            if (data.pet_info) {
                html += `<div class="tab-content" id="tab-pet">`;
                html += displayPetInfo(data.pet_info);
                html += '</div>';
            }
            
            // 坐骑标签页
            if (data.mount_info) {
                html += `<div class="tab-content" id="tab-mount">`;
                html += displayMountInfo(data.mount_info);
                html += '</div>';
            }
            
            // 锦衣/外观标签页
            if (data.appearance_info) {
                html += `<div class="tab-content" id="tab-appearance">`;
                html += displayAppearanceInfo(data.appearance_info);
                html += '</div>';
            }
            
            // 玩家之家标签页
            if (data.home_info) {
                html += `<div class="tab-content" id="tab-home">`;
                html += displayHomeInfo(data.home_info);
                html += '</div>';
            }
            
            html += '</div></div>';
            extractedDiv.innerHTML = html;
        }
        
        // 显示角色信息
        function displayCharacterInfo(basic) {
            let html = '<div class="info-section"><h4>角色属性</h4>';
            html += '<ul class="goods-info-list">';
            const charFields = [
                {key: '级别', label: '级别'},
                {key: '角色', label: '角色'},
                {key: '门派', label: '门派'},
                {key: '新版乾元丹数量', label: '新版乾元丹数量'},
                {key: '月饼粽子机缘', label: '月饼粽子机缘'},
                {key: '飞升/渡劫/化圣', label: '飞升/渡劫/化圣'},
                {key: '成就点数', label: '成就点数'},
                {key: '已用潜能果数量', label: '已用潜能果数量'},
                {key: '总经验', label: '总经验'}
            ];
            charFields.forEach(field => {
                if (basic[field.key]) {
                    html += `<li><strong>${field.label}：</strong><span>${basic[field.key]}</span></li>`;
                }
            });
            html += '</ul></div>';
            
            html += '<div class="info-section"><h4>修炼</h4>';
            html += '<ul class="goods-info-list">';
            const cultivationFields = [
                {key: '攻击修炼', label: '攻击修炼'},
                {key: '防御修炼', label: '防御修炼'},
                {key: '法术修炼', label: '法术修炼'},
                {key: '抗法修炼', label: '抗法修炼'},
                {key: '猎术修炼', label: '猎术修炼'},
                {key: '育兽术', label: '育兽术'}
            ];
            cultivationFields.forEach(field => {
                if (basic[field.key]) {
                    html += `<li><strong>${field.label}：</strong><span>${basic[field.key]}</span></li>`;
                }
            });
            html += '</ul></div>';
            
            html += '<div class="info-section"><h4>控制力</h4>';
            html += '<ul class="goods-info-list">';
            const controlFields = [
                {key: '攻击控制力', label: '攻击控制力'},
                {key: '防御控制力', label: '防御控制力'},
                {key: '法术控制力', label: '法术控制力'},
                {key: '抗法控制力', label: '抗法控制力'}
            ];
            controlFields.forEach(field => {
                if (basic[field.key]) {
                    html += `<li><strong>${field.label}：</strong><span>${basic[field.key]}</span></li>`;
                }
            });
            html += '</ul></div>';
            
            return html;
        }
        
        // 显示技能信息
        function displaySkillInfo(skillInfo) {
            let html = '';
            
            if (skillInfo.school_skills && skillInfo.school_skills.length > 0) {
                html += '<div class="info-section"><h4>师门技能</h4>';
                html += '<div class="skill-grid">';
                skillInfo.school_skills.forEach(skill => {
                    html += `<div class="skill-item">
                        <div class="skill-name">${skill.name || '未知'}</div>
                        <div class="skill-level">${skill.level || '0'}级</div>
                    </div>`;
                });
                html += '</div></div>';
            }
            
            if (skillInfo.life_skills && skillInfo.life_skills.length > 0) {
                html += '<div class="info-section"><h4>生活技能</h4>';
                html += '<div class="skill-grid">';
                skillInfo.life_skills.forEach(skill => {
                    html += `<div class="skill-item">
                        <div class="skill-name">${skill.name || '未知'}</div>
                        <div class="skill-level">${skill.level || '0'}级</div>
                    </div>`;
                });
                html += '</div></div>';
            }
            
            if (skillInfo.story_skills && skillInfo.story_skills.length > 0) {
                html += '<div class="info-section"><h4>剧情技能</h4>';
                html += '<div class="skill-grid">';
                skillInfo.story_skills.forEach(skill => {
                    html += `<div class="skill-item">
                        <div class="skill-name">${skill.name || '未知'}</div>
                        <div class="skill-level">${skill.level || '0'}级</div>
                    </div>`;
                });
                html += '</div></div>';
                if (skillInfo.story_skill_remaining_points) {
                    html += `<div style="margin-top: 10px; color: #666;">剩余技能点：${skillInfo.story_skill_remaining_points}</div>`;
                }
            }
            
            if (skillInfo.proficiency && Object.keys(skillInfo.proficiency).length > 0) {
                html += '<div class="info-section"><h4>熟练度</h4>';
                html += '<ul class="goods-info-list">';
                for (const [key, value] of Object.entries(skillInfo.proficiency)) {
                    html += `<li><strong>${key}：</strong><span>${value}</span></li>`;
                }
                html += '</ul></div>';
            }
            
            return html || '<div class="info-section"><p style="color: #999; text-align: center;">暂无技能信息</p></div>';
        }
        
        // 显示道具/法宝信息
        function displayEquipInfo(equipInfo) {
            let html = '';
            
            if (equipInfo.using_equips && equipInfo.using_equips.length > 0) {
                html += '<div class="info-section"><h4>已装备道具</h4>';
                html += '<div class="equip-grid">';
                equipInfo.using_equips.forEach(equip => {
                    html += `<div class="equip-item equipped">
                        <div class="skill-name">${equip.name || '未知'}</div>
                    </div>`;
                });
                html += '</div></div>';
            }
            
            if (equipInfo.artifacts && equipInfo.artifacts.name) {
                html += '<div class="info-section"><h4>神器</h4>';
                html += `<div class="equip-item equipped">
                    <div class="skill-name">${equipInfo.artifacts.name}</div>
                </div></div>`;
            }
            
            if (equipInfo.using_spirit_treasures && equipInfo.using_spirit_treasures.length > 0) {
                html += '<div class="info-section"><h4>已装备灵宝</h4>';
                html += '<div class="equip-grid">';
                equipInfo.using_spirit_treasures.forEach(item => {
                    html += `<div class="equip-item equipped">
                        <div class="skill-name">${item.name || '未知'}</div>
                    </div>`;
                });
                html += '</div></div>';
            }
            
            if (equipInfo.using_magic_treasures && equipInfo.using_magic_treasures.length > 0) {
                html += '<div class="info-section"><h4>已装备法宝</h4>';
                html += '<div class="equip-grid">';
                equipInfo.using_magic_treasures.forEach(item => {
                    html += `<div class="equip-item equipped">
                        <div class="skill-name">${item.name || '未知'}</div>
                    </div>`;
                });
                html += '</div></div>';
            }
            
            if (equipInfo.currency && Object.keys(equipInfo.currency).length > 0) {
                html += '<div class="info-section"><h4>货币</h4>';
                html += '<ul class="goods-info-list">';
                for (const [key, value] of Object.entries(equipInfo.currency)) {
                    html += `<li><strong>${key}：</strong><span>${value}</span></li>`;
                }
                html += '</ul></div>';
            }
            
            return html || '<div class="info-section"><p style="color: #999; text-align: center;">暂无道具信息</p></div>';
        }
        
        // 显示召唤兽信息
        function displayPetInfo(petInfo) {
            let html = '';
            
            if (petInfo.pets && petInfo.pets.length > 0) {
                petInfo.pets.forEach((pet, index) => {
                    html += `<div class="pet-card">
                        <h5>召唤兽 ${index + 1}${pet.pet_type ? ' - ' + pet.pet_type : ''}</h5>
                        <div class="pet-attr-grid">`;
                    
                    const attrs = [
                        {key: 'level', label: '等级'},
                        {key: 'hp', label: '气血'},
                        {key: 'mp', label: '魔法'},
                        {key: 'attack', label: '攻击'},
                        {key: 'defense', label: '防御'},
                        {key: 'speed', label: '速度'},
                        {key: 'growth', label: '成长'}
                    ];
                    
                    attrs.forEach(attr => {
                        if (pet[attr.key]) {
                            html += `<div class="pet-attr-item">
                                <div class="attr-label">${attr.label}</div>
                                <div class="attr-value">${pet[attr.key]}</div>
                            </div>`;
                        }
                    });
                    
                    html += '</div></div>';
                });
            }
            
            if (petInfo.children && petInfo.children.length > 0) {
                html += '<div class="info-section"><h4>孩子</h4>';
                html += `<p>共有 ${petInfo.children.length} 个孩子</p></div>`;
            }
            
            return html || '<div class="info-section"><p style="color: #999; text-align: center;">暂无召唤兽信息</p></div>';
        }
        
        // 显示坐骑信息
        function displayMountInfo(mountInfo) {
            let html = '';
            
            if (mountInfo.mounts && mountInfo.mounts.length > 0) {
                mountInfo.mounts.forEach((mount, index) => {
                    html += `<div class="info-section">
                        <h4>坐骑 ${index + 1}${mount.mount_type ? ' - ' + mount.mount_type : ''}</h4>
                        <ul class="goods-info-list">`;
                    
                    if (mount.level) html += `<li><strong>等级：</strong><span>${mount.level}</span></li>`;
                    if (mount.growth) html += `<li><strong>成长：</strong><span>${mount.growth}</span></li>`;
                    if (mount.main_attribute) html += `<li><strong>主属性：</strong><span>${mount.main_attribute}</span></li>`;
                    
                    html += '</ul></div>';
                });
            }
            
            return html || '<div class="info-section"><p style="color: #999; text-align: center;">暂无坐骑信息</p></div>';
        }
        
        // 显示外观信息
        function displayAppearanceInfo(appearanceInfo) {
            let html = '';
            
            if (appearanceInfo.jinyi) {
                if (appearanceInfo.jinyi.limited && appearanceInfo.jinyi.limited.length > 0) {
                    html += '<div class="info-section"><h4>限量锦衣</h4>';
                    html += '<div class="equip-grid">';
                    appearanceInfo.jinyi.limited.forEach(item => {
                        html += `<div class="equip-item"><div class="skill-name">${item}</div></div>`;
                    });
                    html += '</div></div>';
                }
                
                if (appearanceInfo.jinyi.normal && appearanceInfo.jinyi.normal.length > 0) {
                    html += '<div class="info-section"><h4>普通锦衣</h4>';
                    html += '<div class="equip-grid">';
                    appearanceInfo.jinyi.normal.forEach(item => {
                        html += `<div class="equip-item"><div class="skill-name">${item}</div></div>`;
                    });
                    html += '</div></div>';
                }
            }
            
            return html || '<div class="info-section"><p style="color: #999; text-align: center;">暂无外观信息</p></div>';
        }
        
        // 显示玩家之家信息
        function displayHomeInfo(homeInfo) {
            let html = '<div class="info-section"><h4>房屋信息</h4>';
            html += '<ul class="goods-info-list">';
            
            if (homeInfo.house_level) html += `<li><strong>房屋等级：</strong><span>${homeInfo.house_level}</span></li>`;
            if (homeInfo.house_type) html += `<li><strong>房屋类型：</strong><span>${homeInfo.house_type}</span></li>`;
            if (homeInfo.house_fengshui) html += `<li><strong>房屋风水：</strong><span>${homeInfo.house_fengshui}</span></li>`;
            if (homeInfo.furniture_score) html += `<li><strong>家具评分：</strong><span>${homeInfo.furniture_score}</span></li>`;
            
            html += '</ul></div>';
            
            return html || '<div class="info-section"><p style="color: #999; text-align: center;">暂无玩家之家信息</p></div>';
        }
        
        // 切换标签页
        function switchTab(tabId) {
            // 隐藏所有标签内容
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // 移除所有按钮的active状态
            document.querySelectorAll('.tab-button').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // 显示选中的标签内容
            const tabContent = document.getElementById(`tab-${tabId}`);
            if (tabContent) {
                tabContent.classList.add('active');
            }
            
            // 激活对应的按钮
            event.target.classList.add('active');
        }

        function clearPreview() {
            document.getElementById('previewTitle').textContent = '暂无数据';
            document.getElementById('previewExtracted').textContent = '暂无提取数据';
            document.getElementById('previewContent').textContent = '暂无数据';
            currentPageData = null;
            document.getElementById('saveBtn').disabled = true;
        }

        function loadCookieFile() {
            document.getElementById('cookieFileInput').click();
        }

        function handleCookieFileSelect(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    try {
                        const data = JSON.parse(e.target.result);
                        // 判断是Cookie文件还是登录态文件
                        if (data.cookies || data.origins) {
                            // 登录态文件
                            currentStorageState = file.name;
                            updateCookieStatus(true, '登录态');
                            showStatus('登录态文件加载成功', 'success');
                        } else {
                            // Cookie文件
                            const cookieString = Object.entries(data).map(([k, v]) => `${k}=${v}`).join('; ');
                            currentCookie = cookieString;
                            updateCookieStatus(true, 'Cookie');
                            showStatus('Cookie文件加载成功', 'success');
                        }
                    } catch (error) {
                        showStatus('加载文件失败: ' + error.message, 'error');
                    }
                };
                reader.readAsText(file);
            }
        }

        function saveCookieFile() {
            if (!currentCookie && !currentStorageState) {
                showStatus('没有可保存的Cookie或登录态', 'error');
                return;
            }

            // 这里可以保存Cookie或登录态文件
            showStatus('保存功能开发中，请使用自动获取功能', 'info');
        }

        // URL输入框按Enter键快速抓取
        document.getElementById('url').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                startWorkflow();
            }
        });

        // 检查Playwright是否已安装
        function checkPlaywrightInstalled() {
            fetch('/api/check_playwright')
            .then(response => response.json())
            .then(data => {
                if (!data.installed) {
                    document.getElementById('playwright_warning').style.display = 'block';
                    document.getElementById('playwright_desc').style.color = '#856404';
                    document.getElementById('playwright_desc').textContent = '⚠️ Playwright: 浏览器未安装，请先运行 playwright install';
                }
            })
            .catch(error => {
                console.error('检查Playwright状态失败:', error);
            });
        }

        // 页面加载时检查
        window.addEventListener('load', function() {
            checkPlaywrightInstalled();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """主页"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/check_playwright', methods=['GET'])
def api_check_playwright():
    """检查Playwright是否已安装（安全版本，只检查文件，不启动浏览器）"""
    try:
        # 使用文件检查方式，避免启动浏览器导致崩溃
        from pathlib import Path
        
        # 检查Playwright浏览器是否存在（macOS路径）
        home = Path.home()
        playwright_cache = home / "Library" / "Caches" / "ms-playwright"
        
        if not playwright_cache.exists():
            return jsonify({
                'success': True,
                'installed': False,
                'message': 'Playwright浏览器未安装，请运行 playwright install'
            })
        
        # 检查是否有chromium（不实际启动，只检查文件）
        chromium_dirs = list(playwright_cache.glob("chromium-*"))
        if chromium_dirs:
            # 检查是否有可执行文件
            for chromium_dir in chromium_dirs:
                chrome_mac = chromium_dir / "chrome-mac" / "Chromium.app" / "Contents" / "MacOS" / "Chromium"
                if chrome_mac.exists():
                    return jsonify({
                        'success': True,
                        'installed': True,
                        'message': 'Playwright已安装'
                    })
        
        return jsonify({
            'success': True,
            'installed': False,
            'message': 'Playwright浏览器未安装，请运行 playwright install'
        })
            
    except Exception as e:
        logger.error(f"检查Playwright失败: {str(e)}")
        # 发生错误时默认返回未安装，避免崩溃
        return jsonify({
            'success': True,
            'installed': False,
            'message': 'Playwright浏览器未安装，请运行 playwright install'
        })

@app.route('/api/check_login', methods=['POST'])
def api_check_login():
    """检测是否需要登录"""
    try:
        data = request.json
        url = data.get('url')
        
        if not url:
            return jsonify({'success': False, 'error': 'URL不能为空'})
        
        # 尝试访问页面，检测是否需要登录
        scraper = WebScraper(use_session=True)
        page_data = scraper.fetch_page(url, allow_redirects=True)
        
        if page_data:
            # 检查页面内容，判断是否需要登录
            content = page_data.get('content', '').lower()
            title = page_data.get('title', '').lower()
            
            login_indicators = [
                '登录', '请登录', '需要登录', 'login', 'sign in',
                '安全提示', '安全验证', '验证码', 'captcha',
                '扫码登录', '账号登录'
            ]
            
            need_login = any(indicator in content or indicator in title 
                           for indicator in login_indicators)
            
            return jsonify({
                'success': True,
                'need_login': need_login,
                'title': page_data.get('title', '')
            })
        else:
            return jsonify({
                'success': True,
                'need_login': True,  # 如果无法访问，假设需要登录
                'title': ''
            })
            
    except Exception as e:
        logger.error(f"检测登录需求失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

def check_playwright_installed():
    """检查Playwright是否已安装浏览器（安全版本，避免段错误）"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False
    
    playwright = None
    browser = None
    
    try:
        # 使用超时和更安全的启动方式
        playwright = sync_playwright().start()
        browser_type = playwright.chromium
        
        # 尝试启动浏览器（headless模式，快速检查）
        # 使用更短的超时时间，避免长时间等待
        browser = browser_type.launch(
            headless=True,
            timeout=5000  # 5秒超时
        )
        
        # 立即关闭，不等待
        if browser:
            browser.close()
            browser = None
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        # 检查是否是浏览器未安装的错误
        if "Executable doesn't exist" in error_msg or "playwright install" in error_msg.lower():
            return False
        # 其他错误（包括超时）也返回False，避免崩溃
        logger.debug(f"Playwright检查出错: {str(e)}")
        return False
    finally:
        # 确保资源被正确清理，使用更安全的方式
        try:
            if browser:
                try:
                    browser.close()
                except:
                    pass
        except:
            pass
        
        try:
            if playwright:
                try:
                    playwright.stop()
                except:
                    pass
        except:
            pass

@app.route('/api/auto_get_cookie', methods=['POST'])
def api_auto_get_cookie():
    """自动获取Cookie（使用LoginStateManager）"""
    try:
        data = request.json
        url = data.get('url')
        
        if not url:
            return jsonify({'success': False, 'error': 'URL不能为空'})
        
        # 检查Playwright是否已安装
        if not check_playwright_installed():
            error_msg = (
                "Playwright浏览器未安装！\n\n"
                "请运行以下命令安装：\n"
                "  playwright install\n\n"
                "或者安装Chromium：\n"
                "  playwright install chromium"
            )
            return jsonify({'success': False, 'error': error_msg})
        
        # 使用LoginStateManager进行登录（强制刷新，因为这是用户主动触发的获取Cookie操作）
        domain = login_manager.get_domain_from_url(url)
        logger.info(f"用户主动触发获取Cookie，强制刷新登录态: {domain}")
        storage_state_path = login_manager.refresh_state(domain, url)
        
        # 从保存的登录态文件中读取Cookie（避免再次启动浏览器）
        cookie_string = None
        try:
            import json
            if storage_state_path and os.path.exists(storage_state_path):
                with open(storage_state_path, 'r', encoding='utf-8') as f:
                    storage_data = json.load(f)
                    if 'cookies' in storage_data:
                        cookie_dict = {c['name']: c['value'] for c in storage_data['cookies']}
                        cookie_string = CookieHelper.cookie_dict_to_string(cookie_dict)
                        logger.info(f"从登录态文件中提取了 {len(cookie_dict)} 个Cookie")
        except Exception as e:
            logger.warning(f"从登录态文件读取Cookie失败: {str(e)}")
            cookie_string = None
        
        return jsonify({
            'success': True,
            'cookie': cookie_string,
            'storage_state': storage_state_path,
            'message': 'Cookie获取成功，已保存到本地文件'
        })
            
    except Exception as e:
        logger.error(f"自动获取Cookie失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/check_local_cookie', methods=['POST'])
def api_check_local_cookie():
    """检查本地Cookie文件"""
    try:
        data = request.json
        url = data.get('url', '')
        
        if not url:
            return jsonify({'success': False, 'error': 'URL不能为空'})
        
        # 从URL中提取域名
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        
        # 查找对应的登录态文件
        storage_state_path = f"login_state_{domain.replace('.', '_')}.json"
        
        if os.path.exists(storage_state_path):
            # 验证文件是否有效
            try:
                import json
                with open(storage_state_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        storage_data = json.loads(content)
                        if isinstance(storage_data, dict) and ('cookies' in storage_data or 'origins' in storage_data):
                            logger.info(f"找到有效的本地Cookie文件: {storage_state_path}")
                            return jsonify({
                                'success': True,
                                'storage_state_path': storage_state_path,
                                'message': '找到本地Cookie文件'
                            })
            except Exception as e:
                logger.warning(f"Cookie文件无效: {str(e)}")
        
        return jsonify({
            'success': False,
            'storage_state_path': None,
            'message': '未找到有效的本地Cookie文件'
        })
    except Exception as e:
        logger.error(f"检查本地Cookie失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/fetch_and_extract', methods=['POST'])
def api_fetch_and_extract():
    """抓取页面并直接提取关键信息（重构版：使用LoginStateManager）"""
    try:
        data = request.json
        url = data.get('url')
        method = data.get('method', 'playwright')

        if not url:
            return jsonify({'success': False, 'error': 'URL不能为空'})

        # 提取域名
        domain = login_manager.get_domain_from_url(url)
        logger.info(f"处理URL: {url}, 域名: {domain}")

        # 获取登录态（如果存在）
        storage_state_path = None
        if method == 'playwright':
            # 只使用已有的登录态，不自动创建
            if login_manager.has_valid_state(domain):
                storage_state_path = login_manager.get_state(domain)
                logger.info(f"使用已有登录态: {storage_state_path}")
            else:
                logger.info(f"未找到登录态文件，将尝试无登录态抓取")
                storage_state_path = None

        page_data = None
        extracted_data = None
        need_login = False

        if method == 'playwright':
            # 检查Playwright是否已安装
            if not check_playwright_installed():
                return jsonify({
                    'success': False, 
                    'error': 'Playwright浏览器未安装，请运行 "playwright install" 安装浏览器，或选择其他抓取方法'
                })
            
            try:
                # 使用BrowserManager获取页面实例（复用浏览器，不关闭）
                page = browser_manager.get_page(storage_state_path=storage_state_path, headless=True)
                
                # 直接使用page对象抓取页面
                from bs4 import BeautifulSoup
                
                original_url = url
                logger.info(f"正在抓取页面: {url}")
                
                # 访问页面
                page.goto(url, wait_until='networkidle', timeout=30000)
                
                # 等待URL稳定
                max_wait = 10
                check_interval = 0.5
                last_url = page.url
                stable_count = 0
                required_stable = 2
                
                for _ in range(int(max_wait / check_interval)):
                    time_module.sleep(check_interval)
                    current_url = page.url
                    if current_url != last_url:
                        logger.info(f"检测到URL变化: {last_url} -> {current_url}")
                        stable_count = 0
                        last_url = current_url
                    else:
                        stable_count += 1
                        if stable_count >= required_stable:
                            logger.info(f"URL已稳定: {current_url}")
                            break
                
                # 等待页面完全加载
                try:
                    page.wait_for_load_state('networkidle', timeout=30000)
                except:
                    logger.warning("等待网络空闲超时，继续处理")
                
                # 额外等待，确保JavaScript执行完成
                time_module.sleep(1)
                
                # 获取最终URL
                final_url = page.url
                if final_url != original_url:
                    logger.info(f"页面发生跳转: {original_url} -> {final_url}")
                
                # 获取页面内容（完整HTML）
                page_content = page.content()
                
                # 解析HTML
                soup = BeautifulSoup(page_content, 'lxml')
                
                # 提取标题
                title_tag = soup.find('title')
                title = title_tag.get_text(strip=True) if title_tag else "无标题"
                
                # 对于藏宝阁页面，返回完整HTML
                if 'cbg.163.com' in url or 'xyq.cbg.163.com' in url:
                    content = page_content
                else:
                    # 其他页面提取文本内容
                    for script in soup(["script", "style"]):
                        script.decompose()
                    body = soup.find('body')
                    content = body.get_text(separator='\n', strip=True) if body else ""
                
                page_data = {
                    'url': final_url,
                    'original_url': original_url,
                    'title': title,
                    'content': content,
                    'redirected': final_url != original_url
                }
                
                logger.info(f"成功抓取页面: {final_url}, 标题: {title}")
                
                # 检查是否需要登录（通过URL判断）
                if page_data:
                    page_url = page_data.get('url', '')
                    # 检查URL是否包含登录相关路径
                    if 'show_login' in page_url or 'login' in page_url.lower():
                        need_login = True
                        logger.info(f"检测到页面需要登录（通过URL判断）: {page_url}")
                        # 如果使用了登录态但仍然需要登录，说明登录态已过期，需要删除过期文件
                        if storage_state_path:
                            logger.warning(f"登录态已过期，删除过期文件: {storage_state_path}")
                            try:
                                if os.path.exists(storage_state_path):
                                    os.remove(storage_state_path)
                                    logger.info(f"✅ 已删除过期登录态文件: {storage_state_path}")
                                    # 清理对应的浏览器实例
                                    browser_manager._cleanup_key(storage_state_path)
                            except Exception as e:
                                logger.warning(f"删除过期登录态文件失败: {str(e)}")
                    elif page_data.get('content'):
                        # 直接提取关键信息
                        extracted_data = data_extractor.extract_all_info(page_data['content'], url)
                        extracted_count = len([v for v in extracted_data.values() if v])
                        logger.info(f"提取了 {extracted_count} 个字段")
                        
                        # 如果提取失败，保存HTML用于调试
                        if extracted_count == 0:
                            try:
                                debug_file = 'debug_extract_failed.html'
                                with open(debug_file, 'w', encoding='utf-8') as f:
                                    f.write(page_data['content'])
                                logger.warning(f"提取失败，已保存页面内容到 {debug_file} 用于调试")
                                
                                # 检查HTML中是否包含关键元素
                                from bs4 import BeautifulSoup
                                soup = BeautifulSoup(page_data['content'], 'lxml')
                                goods_info = None
                                for div in soup.find_all('div', class_=True):
                                    classes = div.get('class', [])
                                    if isinstance(classes, str):
                                        classes = [classes]
                                    if 'infoList' in classes and 'goodsInfo' in classes:
                                        goods_info = div
                                        break
                                
                                if not goods_info:
                                    logger.warning("HTML中未找到 infoList goodsInfo，可能是页面结构不同或需要等待JavaScript加载")
                                    # 检查是否有类似的元素
                                    all_divs = soup.find_all('div', class_=True)
                                    infoList_divs = [d for d in all_divs if 'infoList' in str(d.get('class', []))]
                                    goodsInfo_divs = [d for d in all_divs if 'goodsInfo' in str(d.get('class', []))]
                                    logger.info(f"找到 {len(infoList_divs)} 个包含'infoList'的div, {len(goodsInfo_divs)} 个包含'goodsInfo'的div")
                            except Exception as e:
                                logger.warning(f"保存调试文件失败: {str(e)}")
                    else:
                        need_login = True
                        logger.info("页面内容为空，可能需要登录")
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Playwright抓取失败: {str(e)}")
                import traceback
                traceback.print_exc()
                
                # 检查是否是严重错误（如UnboundLocalError、AttributeError等），需要停止服务
                if isinstance(e, (UnboundLocalError, NameError, AttributeError, ImportError)):
                    logger.critical(f"检测到严重错误: {type(e).__name__}: {str(e)}")
                    logger.critical("程序将停止运行，请检查代码错误")
                    # 清理资源
                    try:
                        browser_manager.close_all()
                    except:
                        pass
                    # 停止Flask服务器
                    import sys
                    import os
                    os._exit(1)  # 强制退出
                
                # 检查是否是登录相关错误
                if '登录' in error_msg or 'login' in error_msg.lower() or 'redirect' in error_msg.lower():
                    need_login = True
                else:
                    return jsonify({'success': False, 'error': f'抓取失败: {str(e)}', 'need_login': need_login})
            # 注意：不再关闭浏览器，保持浏览器实例运行以便复用
        elif method == 'selenium':
            scraper = SeleniumScraper(headless=True)
            try:
                if cookie:
                    cookies_dict = CookieHelper.parse_cookie_string(cookie)
                    selenium_cookies = CookieHelper.dict_to_selenium_cookies(
                        cookies_dict,
                        domain=".163.com" if "163.com" in url else ""
                    )
                    scraper.driver.get(url.split('/')[0] + '//' + url.split('/')[2])
                    scraper.set_cookies(selenium_cookies)
                
                page_data = scraper.fetch_page(url, wait_for_url_change=True, wait_timeout=15)
                
                # 直接提取关键信息
                if page_data and page_data.get('content'):
                    extracted_data = data_extractor.extract_all_info(page_data['content'], url)
                    logger.info(f"提取了 {len([v for v in extracted_data.values() if v])} 个字段")
            finally:
                try:
                    scraper.close()
                    time_module.sleep(0.2)
                except Exception as e:
                    logger.warning(f"关闭浏览器时出错: {str(e)}")
        else:
            scraper = WebScraper(use_session=True)
            if cookie:
                scraper.set_cookies(cookie)
            page_data = scraper.fetch_page(url, allow_redirects=True)
            
            # 直接提取关键信息
            if page_data and page_data.get('content'):
                extracted_data = data_extractor.extract_all_info(page_data['content'], url)
                logger.info(f"提取了 {len([v for v in extracted_data.values() if v])} 个字段")

        if page_data is None:
            return jsonify({
                'success': False, 
                'error': '抓取失败，未获取到页面数据',
                'need_login': need_login
            })

        # 如果需要登录，返回提示（提示用户先获取cookie）
        if need_login:
            return jsonify({
                'success': False,
                'error': '页面需要登录，请先点击"自动获取Cookie"按钮获取最新登录态，然后再进行抓取',
                'need_login': True,
                'original_url': url  # 保存原始URL，登录后可以重定向回来
            })

        # 返回提取的数据，不返回完整HTML内容（节省空间）
        return jsonify({
            'success': True,
            'data': {
                'url': page_data.get('url', url),
                'title': page_data.get('title', '无标题'),
                'content': page_data.get('content', '')[:5000] if page_data.get('content') else '',  # 只返回前5000字符作为预览
                'extracted_data': extracted_data,
                'redirected': page_data.get('redirected', False),
                'original_url': page_data.get('original_url', url)
            }
        })
    except Exception as e:
        logger.error(f"抓取失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/fetch_all_tabs', methods=['POST'])
def api_fetch_all_tabs():
    """多标签页抓取：依次抓取人物/修炼、技能、道具/法宝"""
    try:
        data = request.json
        url = data.get('url')
        method = data.get('method', 'playwright')

        if not url:
            return jsonify({'success': False, 'error': 'URL不能为空'})

        # 只支持Playwright（需要页面交互）
        if method != 'playwright':
            return jsonify({
                'success': False,
                'error': '多标签页抓取仅支持Playwright方法'
            })

        # 检查Playwright是否已安装
        if not check_playwright_installed():
            return jsonify({
                'success': False,
                'error': 'Playwright浏览器未安装，请运行 "playwright install" 安装浏览器'
            })

        # 提取域名
        domain = login_manager.get_domain_from_url(url)
        logger.info(f"开始多标签页抓取: {url}, 域名: {domain}")

        # 获取登录态
        storage_state_path = None
        if login_manager.has_valid_state(domain):
            storage_state_path = login_manager.get_state(domain)
            logger.info(f"使用已有登录态: {storage_state_path}")

        try:
            # 使用BrowserManager获取页面实例
            page = browser_manager.get_page(storage_state_path=storage_state_path, headless=True)
            
            # 创建PlaywrightScraper包装器（使用已有的page）
            class PageWrapper:
                def __init__(self, page):
                    self.page = page
                    self.headless = True
                    self.storage_state_path = storage_state_path
                
                def fetch_page(self, url, **kwargs):
                    """使用已有page抓取"""
                    from bs4 import BeautifulSoup
                    self.page.goto(url, wait_until='networkidle', timeout=30000)
                    time_module.sleep(1)
                    content = self.page.content()
                    soup = BeautifulSoup(content, 'lxml')
                    title = soup.find('title')
                    return {
                        'url': self.page.url,
                        'title': title.get_text(strip=True) if title else '无标题',
                        'content': content
                    }
            
            wrapper = PageWrapper(page)
            
            # 创建多标签页抓取服务（需要先初始化，检查page属性）
            try:
                multi_tab_service = MultiTabScrapingService(wrapper)
            except ValueError as e:
                logger.error(f"创建多标签页抓取服务失败: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': f'创建抓取服务失败: {str(e)}'
                })
            
            # 执行多标签页抓取
            page_data = multi_tab_service.scrape_all_tabs(url)
            
            if not page_data:
                return jsonify({
                    'success': False,
                    'error': '多标签页抓取失败'
                })
            
            # 返回结果
            return jsonify({
                'success': True,
                'data': {
                    'url': page_data.url,
                    'title': page_data.title,
                    'extracted_data': page_data.extracted_data,
                    'tabs': {
                        'basic': '人物/修炼',
                        'skill': '技能',
                        'equip': '道具/法宝'
                    }
                }
            })
            
        except Exception as e:
            logger.error(f"多标签页抓取失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': f'抓取失败: {str(e)}'
            })
            
    except Exception as e:
        logger.error(f"多标签页抓取异常: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/fetch', methods=['POST'])
def api_fetch():
    """抓取API"""
    try:
        data = request.json
        url = data.get('url')
        cookie = (data.get('cookie') or '').strip() if data.get('cookie') else ''
        method = data.get('method', 'playwright')
        storage_state_path = (data.get('storage_state_path') or '').strip() if data.get('storage_state_path') else ''

        if not url:
            return jsonify({'success': False, 'error': 'URL不能为空'})

        if method == 'playwright':
            # 检查Playwright是否已安装
            if not check_playwright_installed():
                return jsonify({
                    'success': False, 
                    'error': 'Playwright浏览器未安装，请运行 "playwright install" 安装浏览器，或选择其他抓取方法'
                })
            
            scraper = None
            try:
                # 验证登录态文件
                valid_storage_state = None
                if storage_state_path and os.path.exists(storage_state_path):
                    try:
                        import json
                        with open(storage_state_path, 'r', encoding='utf-8') as f:
                            content = f.read().strip()
                            if content:
                                storage_data = json.loads(content)
                                if isinstance(storage_data, dict) and ('cookies' in storage_data or 'origins' in storage_data):
                                    valid_storage_state = storage_state_path
                                else:
                                    logger.warning(f"登录态文件格式无效，将不使用登录态")
                            else:
                                logger.warning(f"登录态文件为空，将不使用登录态")
                    except (json.JSONDecodeError, ValueError, Exception) as e:
                        logger.warning(f"登录态文件加载失败: {str(e)}，将不使用登录态")
                
                scraper = PlaywrightScraper(headless=True, storage_state_path=valid_storage_state)
                scraper.start()
                page_data = scraper.fetch_page(url, wait_for_url_change=True)
            except Exception as e:
                logger.error(f"Playwright抓取失败: {str(e)}")
                import traceback
                traceback.print_exc()
                return jsonify({'success': False, 'error': f'抓取失败: {str(e)}'})
            finally:
                if scraper:
                    try:
                        # 使用更安全的方式关闭，避免段错误
                        scraper.close()
                        time_module.sleep(0.2)  # 延迟确保资源释放
                    except Exception as e:
                        logger.warning(f"关闭浏览器时出错: {str(e)}")
                        # 继续运行，不影响程序
                        # 短暂延迟，确保资源完全释放
                        time_module.sleep(0.2)
                    except Exception as close_error:
                        logger.warning(f"关闭浏览器时出错: {str(close_error)}")
                        # 即使出错也继续，不影响程序运行
        elif method == 'selenium':
            scraper = SeleniumScraper(headless=True)
            try:
                if cookie:
                    cookies_dict = CookieHelper.parse_cookie_string(cookie)
                    selenium_cookies = CookieHelper.dict_to_selenium_cookies(
                        cookies_dict,
                        domain=".163.com" if "163.com" in url else ""
                    )
                    scraper.driver.get(url.split('/')[0] + '//' + url.split('/')[2])
                    scraper.set_cookies(selenium_cookies)
                
                page_data = scraper.fetch_page(url, wait_for_url_change=True, wait_timeout=15)
            finally:
                try:
                    scraper.close()
                    time_module.sleep(0.2)  # 延迟确保资源释放
                except Exception as e:
                    logger.warning(f"关闭浏览器时出错: {str(e)}")
                    # 继续运行，不影响程序
        else:
            scraper = WebScraper(use_session=True)
            if cookie:
                scraper.set_cookies(cookie)
            page_data = scraper.fetch_page(url, allow_redirects=True)

        if page_data:
            return jsonify({'success': True, 'data': page_data})
        else:
            return jsonify({'success': False, 'error': '抓取失败，请检查URL和Cookie'})

    except Exception as e:
        logger.error(f"抓取失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/extract', methods=['POST'])
def api_extract():
    """提取数据API"""
    try:
        data = request.json
        url = data.get('url', '')
        content = data.get('content', '')
        
        if not content:
            return jsonify({'success': False, 'error': '内容为空'})
        
        # 提取结构化信息
        extracted_data = data_extractor.extract_all_info(content, url)
        extracted_count = len([v for v in extracted_data.values() if v])
        
        logger.info(f"提取了 {extracted_count} 个字段")
        
        return jsonify({
            'success': True,
            'data': extracted_data,
            'count': extracted_count
        })
    except Exception as e:
        logger.error(f"提取数据失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/save', methods=['POST'])
def api_save():
    """保存API"""
    try:
        data = request.json
        url = data.get('url', '')
        content = data.get('content', '')
        
        # 提取结构化信息（如果还没有提取）
        extracted_data = data.get('extracted_data')
        if not extracted_data and content and url:
            try:
                extracted_data = data_extractor.extract_all_info(content, url)
                logger.info(f"提取了 {len([v for v in extracted_data.values() if v])} 个字段")
            except Exception as e:
                logger.warning(f"提取数据时出错: {str(e)}")
        
        # 检查是否是多标签页数据（包含basic_info, skill_info等）
        is_multi_tab_data = extracted_data and isinstance(extracted_data, dict) and (
            'basic_info' in extracted_data or 
            'skill_info' in extracted_data or 
            'equip_info' in extracted_data
        )
        
        if is_multi_tab_data:
            # 使用新的ProductRepository保存
            try:
                product = data_mapper.map_to_product(extracted_data, url)
                saved_product = product_repository.save_product(product, extracted_data)
                
                # 同时保存到泛型表
                try:
                    generic_repository.save_data(saved_product.product_id, extracted_data)
                    logger.info(f"已保存到泛型表，product_id={saved_product.product_id}")
                except Exception as e:
                    logger.warning(f"保存到泛型表失败: {str(e)}")
                
                # 统计提取的字段数
                extracted_count = 0
                if extracted_data:
                    for tab_name, tab_data in extracted_data.items():
                        if isinstance(tab_data, dict):
                            extracted_count += len([v for v in tab_data.values() if v])
                
                return jsonify({
                    'success': True,
                    'id': saved_product.product_id,
                    'title': f"商品 {saved_product.item_id}",
                    'extracted_fields': extracted_count,
                    'product_type': saved_product.product_type
                })
            except Exception as e:
                logger.error(f"使用ProductRepository保存失败，回退到旧方式: {str(e)}")
                import traceback
                traceback.print_exc()
                # 回退到旧的保存方式
                is_multi_tab_data = False
        
        if not is_multi_tab_data:
            # 使用旧的PageDataRepository保存（向后兼容）
            saved_data = db_manager.save_page_data(
                url=url,
                title=data.get('title', '无标题'),
                content=content,
                extracted_data=extracted_data
            )
            
            # 同时保存到泛型表
            if extracted_data:
                try:
                    generic_repository.save_data(saved_data.id, extracted_data)
                    logger.info(f"已保存到泛型表，data_id={saved_data.id}")
                except Exception as e:
                    logger.warning(f"保存到泛型表失败: {str(e)}")
            
            extracted_count = len([v for v in extracted_data.values() if v]) if extracted_data else 0
            
            return jsonify({
                'success': True,
                'id': saved_data.id,
                'title': saved_data.title,
                'extracted_fields': extracted_count
            })
            
    except Exception as e:
        logger.error(f"保存失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/list', methods=['GET'])
def api_list():
    """列表API"""
    try:
        all_data = db_manager.get_all_data()
        data_list = []
        for data in all_data:
            data_list.append({
                'id': data.id,
                'url': data.url,
                'title': data.title,
                'created_at': data.created_at.strftime('%Y-%m-%d %H:%M:%S') if data.created_at else ''
            })
        return jsonify({'success': True, 'data': data_list})
    except Exception as e:
        logger.error(f"获取列表失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/detail/<int:data_id>', methods=['GET'])
def api_detail(data_id):
    """详情API"""
    try:
        all_data = db_manager.get_all_data()
        for data in all_data:
            if data.id == data_id:
                # 解析提取的数据
                extracted_data = None
                if data.extracted_data:
                    try:
                        extracted_data = json.loads(data.extracted_data)
                    except:
                        pass
                
                return jsonify({
                    'success': True,
                    'data': {
                        'id': data.id,
                        'url': data.url,
                        'title': data.title,
                        'content': data.content,
                        'extracted_data': extracted_data,
                        'created_at': data.created_at.strftime('%Y-%m-%d %H:%M:%S') if data.created_at else ''
                    }
                })
        return jsonify({'success': False, 'error': '数据不存在'})
    except Exception as e:
        logger.error(f"获取详情失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/view/<int:data_id>')
def view_data_page(data_id):
    """数据浏览页面"""
    try:
        all_data = db_manager.get_all_data()
        for data in all_data:
            if data.id == data_id:
                # 解析提取的数据
                extracted_data = None
                if data.extracted_data:
                    try:
                        extracted_data = json.loads(data.extracted_data)
                    except:
                        pass
                
                # 渲染展示页面
                return render_template_string(DATA_VIEW_TEMPLATE, 
                    data_id=data.id,
                    url=data.url,
                    title=data.title or '无标题',
                    extracted_data=extracted_data or {},
                    created_at=data.created_at.strftime('%Y-%m-%d %H:%M:%S') if data.created_at else ''
                )
        return "数据不存在", 404
    except Exception as e:
        logger.error(f"获取详情失败: {str(e)}")
        return f"获取数据失败: {str(e)}", 500

if __name__ == '__main__':
    import warnings
    import signal
    import sys
    
    # 忽略urllib3的OpenSSL警告（不影响功能，已知问题）
    warnings.filterwarnings('ignore', category=UserWarning, module='urllib3')
    
    # 全局异常处理，防止程序意外退出
    def handle_exception(exc_type, exc_value, exc_traceback):
        """全局异常处理"""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        # 对于段错误等严重错误，记录但不退出
        logger.error("未捕获的异常:", exc_info=(exc_type, exc_value, exc_traceback))
        # 不调用sys.exit()，让程序继续运行
    
    sys.excepthook = handle_exception
    
    # 定期清理空闲浏览器的后台任务
    def cleanup_idle_browsers():
        """定期清理空闲浏览器"""
        while True:
            try:
                time_module.sleep(60)  # 每分钟检查一次
                browser_manager.cleanup_idle()
            except Exception as e:
                logger.warning(f"清理空闲浏览器时出错: {str(e)}")
    
    cleanup_thread = threading.Thread(target=cleanup_idle_browsers, daemon=True)
    cleanup_thread.start()
    logger.info("已启动浏览器清理任务")
    
    # 程序退出时清理所有浏览器
    def cleanup_on_exit():
        """程序退出时清理资源"""
        logger.info("正在关闭所有浏览器实例...")
        browser_manager.close_all()
    
    signal.signal(signal.SIGINT, lambda s, f: cleanup_on_exit() or sys.exit(0))
    signal.signal(signal.SIGTERM, lambda s, f: cleanup_on_exit() or sys.exit(0))
    
    # 设置信号处理，捕获段错误信号（如果可能）
    try:
        def sigsegv_handler(signum, frame):
            """处理段错误信号"""
            logger.error("收到段错误信号 (SIGSEGV)，但程序将继续运行")
            # 不退出，让程序继续运行
        
        signal.signal(signal.SIGSEGV, sigsegv_handler)
    except (ValueError, OSError):
        # 在某些系统上可能无法设置SIGSEGV处理
        pass
    
    # 信号处理，优雅退出
    def signal_handler(sig, frame):
        print("\n正在关闭服务器...")
        browser_manager.close_all()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("=" * 60)
    print("🌐 网页抓取工具 Web GUI（优化版）")
    print("=" * 60)
    print("📱 访问地址: http://127.0.0.1:5000")
    print("💡 智能检测登录需求，自动获取Cookie")
    print("💡 按 Ctrl+C 停止服务器")
    print("=" * 60)
    
    try:
        # 使用use_reloader=False可以减少资源泄漏警告和避免环境变量问题
        app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        logger.error(f"服务器运行出错: {str(e)}")
        import traceback
        traceback.print_exc()
        # 即使出错也尝试继续运行
        print("尝试重新启动服务器...")
        app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)
