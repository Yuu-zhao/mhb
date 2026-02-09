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
            fetch(`/api/detail/${id}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    let detailText = `详情:\\n\\nURL: ${data.data.url}\\n\\n标题: ${data.data.title || '无标题'}\\n\\n`;
                    
                    // 显示提取的关键信息
                    if (data.data.extracted_data && Object.keys(data.data.extracted_data).length > 0) {
                        detailText += '提取的关键信息:\\n';
                        for (const [key, value] of Object.entries(data.data.extracted_data)) {
                            if (value) {
                                detailText += `${key}: ${value}\\n`;
                            }
                        }
                        detailText += '\\n';
                    }
                    
                    detailText += `内容: ${data.data.content ? data.data.content.substring(0, 500) + '...' : '无内容'}`;
                    alert(detailText);
                } else {
                    showStatus('获取详情失败: ' + data.error, 'error');
                }
            })
            .catch(error => {
                showStatus('获取详情失败: ' + error.message, 'error');
            });
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
            
            // 基础信息（人物/修炼）
            if (data.basic_info && Object.keys(data.basic_info).length > 0) {
                html += '<div class="tab-section"><h3 style="color: #667eea; margin-bottom: 10px; padding: 8px; background: #f0f0f0; border-left: 4px solid #667eea;">📊 人物/修炼</h3>';
                html += '<table style="width: 100%; font-size: 12px; border-collapse: collapse; margin-bottom: 15px;">';
                for (const [key, value] of Object.entries(data.basic_info)) {
                    if (value) {
                        html += `<tr><td style="font-weight: bold; padding: 4px 8px; color: #667eea; width: 40%; background: #f5f5f5;">${key}:</td><td style="padding: 4px 8px; background: #fff;">${value}</td></tr>`;
                    }
                }
                html += '</table></div>';
            }
            
            // 技能信息
            if (data.skill_info && Object.keys(data.skill_info).length > 0) {
                html += '<div class="tab-section"><h3 style="color: #667eea; margin-bottom: 10px; padding: 8px; background: #f0f0f0; border-left: 4px solid #667eea;">⚔️ 技能</h3>';
                
                // 师门技能
                if (data.skill_info.school_skills && data.skill_info.school_skills.length > 0) {
                    html += '<div style="margin-bottom: 10px;"><strong>师门技能:</strong><ul style="margin: 5px 0; padding-left: 20px;">';
                    data.skill_info.school_skills.forEach(skill => {
                        html += `<li>${skill.name} (${skill.level}级)</li>`;
                    });
                    html += '</ul></div>';
                }
                
                // 生活技能
                if (data.skill_info.life_skills && data.skill_info.life_skills.length > 0) {
                    html += '<div style="margin-bottom: 10px;"><strong>生活技能:</strong><ul style="margin: 5px 0; padding-left: 20px;">';
                    data.skill_info.life_skills.forEach(skill => {
                        html += `<li>${skill.name} (${skill.level}级)</li>`;
                    });
                    html += '</ul></div>';
                }
                
                // 剧情技能
                if (data.skill_info.juqing_skills && data.skill_info.juqing_skills.length > 0) {
                    html += '<div style="margin-bottom: 10px;"><strong>剧情技能:</strong><ul style="margin: 5px 0; padding-left: 20px;">';
                    data.skill_info.juqing_skills.forEach(skill => {
                        html += `<li>${skill.name} (${skill.level}级)</li>`;
                    });
                    html += '</ul></div>';
                }
                
                // 熟练度
                if (data.skill_info.proficiency && Object.keys(data.skill_info.proficiency).length > 0) {
                    html += '<div style="margin-bottom: 10px;"><strong>熟练度:</strong><ul style="margin: 5px 0; padding-left: 20px;">';
                    for (const [key, value] of Object.entries(data.skill_info.proficiency)) {
                        html += `<li>${key}: ${value}</li>`;
                    }
                    html += '</ul></div>';
                }
                
                html += '</div>';
            }
            
            // 道具/法宝信息
            if (data.equip_info && Object.keys(data.equip_info).length > 0) {
                html += '<div class="tab-section"><h3 style="color: #667eea; margin-bottom: 10px; padding: 8px; background: #f0f0f0; border-left: 4px solid #667eea;">🎒 道具/法宝</h3>';
                
                // 装备数量
                if (data.equip_info.equipments && data.equip_info.equipments.length > 0) {
                    html += `<div style="margin-bottom: 10px;"><strong>装备 (${data.equip_info.equipments.length}件):</strong><ul style="margin: 5px 0; padding-left: 20px;">`;
                    data.equip_info.equipments.forEach(equip => {
                        html += `<li>${equip.name}</li>`;
                    });
                    html += '</ul></div>';
                }
                
                // 神器
                if (data.equip_info.shenqi && data.equip_info.shenqi.length > 0) {
                    html += `<div style="margin-bottom: 10px;"><strong>神器 (${data.equip_info.shenqi.length}件):</strong><ul style="margin: 5px 0; padding-left: 20px;">`;
                    data.equip_info.shenqi.forEach(item => {
                        html += `<li>${item.name}</li>`;
                    });
                    html += '</ul></div>';
                }
                
                // 已装备灵宝
                if (data.equip_info.lingbao_equipped && data.equip_info.lingbao_equipped.length > 0) {
                    html += `<div style="margin-bottom: 10px;"><strong>已装备灵宝 (${data.equip_info.lingbao_equipped.length}件):</strong><ul style="margin: 5px 0; padding-left: 20px;">`;
                    data.equip_info.lingbao_equipped.forEach(item => {
                        html += `<li>${item.name}</li>`;
                    });
                    html += '</ul></div>';
                }
                
                // 已装备法宝
                if (data.equip_info.fabao_equipped && data.equip_info.fabao_equipped.length > 0) {
                    html += `<div style="margin-bottom: 10px;"><strong>已装备法宝 (${data.equip_info.fabao_equipped.length}件):</strong><ul style="margin: 5px 0; padding-left: 20px;">`;
                    data.equip_info.fabao_equipped.forEach(item => {
                        html += `<li>${item.name}</li>`;
                    });
                    html += '</ul></div>';
                }
                
                // 货币信息
                if (data.equip_info.currency && Object.keys(data.equip_info.currency).length > 0) {
                    html += '<div style="margin-bottom: 10px;"><strong>货币:</strong><ul style="margin: 5px 0; padding-left: 20px;">';
                    for (const [key, value] of Object.entries(data.equip_info.currency)) {
                        html += `<li>${key}: ${value}</li>`;
                    }
                    html += '</ul></div>';
                }
                
                // 行囊扩展
                if (data.equip_info.bag_expansion) {
                    html += `<div style="margin-bottom: 10px;"><strong>行囊扩展:</strong> ${data.equip_info.bag_expansion}</div>`;
                }
                
                html += '</div>';
            }
            
            html += '</div>';
            extractedDiv.innerHTML = html;
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
        
        saved_data = db_manager.save_page_data(
            url=url,
            title=data.get('title', '无标题'),
            content=content,
            extracted_data=extracted_data
        )
        
        extracted_count = len([v for v in extracted_data.values() if v]) if extracted_data else 0
        
        return jsonify({
            'success': True,
            'id': saved_data.id,
            'title': saved_data.title,
            'extracted_fields': extracted_count
        })
    except Exception as e:
        logger.error(f"保存失败: {str(e)}")
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
