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
import logging
import os
import json

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
db_manager = DatabaseManager()

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
        let currentCookie = null;
        let currentStorageState = null;

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
                // Step 1: 检测是否需要登录
                updateLoading('正在检测登录需求...');
                const checkResult = await fetch('/api/check_login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: url})
                }).then(r => r.json());

                // Step 2: 如果需要登录且没有Cookie，自动获取
                if (checkResult.need_login && !currentCookie && !currentStorageState) {
                    updateLoading('检测到需要登录，正在自动获取Cookie...');
                    showStatus('检测到需要登录，正在自动获取Cookie...', 'warning');
                    
                    const cookieResult = await autoGetCookieInternal(url);
                    if (!cookieResult.success) {
                        showStatus('自动获取Cookie失败: ' + cookieResult.error, 'error');
                        document.getElementById('loading').style.display = 'none';
                        document.querySelector('.btn-primary').disabled = false;
                        return;
                    }
                }

                // Step 3: 开始抓取
                updateLoading('正在抓取页面...');
                const fetchResult = await fetch('/api/fetch', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        url: url,
                        cookie: currentCookie,
                        method: method,
                        storage_state_path: currentStorageState
                    })
                }).then(r => r.json());

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
                    let content = fetchResult.data.content || '无内容';
                    if (content.length > 50000) {
                        content = content.substring(0, 50000) + '\\n\\n... (内容过长，已截断)';
                    }
                    document.getElementById('previewContent').textContent = content;
                    document.getElementById('saveBtn').disabled = false;
                    showStatus(`抓取成功！标题: ${title}, 内容长度: ${fetchResult.data.content?.length || 0} 字符${urlInfo}`, 'success');
                } else {
                    showStatus('抓取失败: ' + fetchResult.error, 'error');
                }
            } catch (error) {
                document.getElementById('loading').style.display = 'none';
                document.querySelector('.btn-primary').disabled = false;
                showStatus('处理失败: ' + error.message, 'error');
            }
        }

        // 自动获取Cookie（内部函数）
        async function autoGetCookieInternal(url) {
            try {
                updateLoading('正在启动浏览器获取Cookie...');
                const result = await fetch('/api/auto_get_cookie', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: url})
                }).then(r => r.json());

                if (result.success) {
                    if (result.cookie) {
                        currentCookie = result.cookie;
                        updateCookieStatus(true, 'Cookie');
                    }
                    if (result.storage_state) {
                        currentStorageState = result.storage_state;
                        updateCookieStatus(true, '登录态');
                    }
                    return {success: true};
                } else {
                    return {success: false, error: result.error};
                }
            } catch (error) {
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
                body: JSON.stringify(currentPageData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showStatus(`数据已保存到数据库！ID: ${data.id}, 标题: ${data.title}`, 'success');
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
                    alert(`详情:\\n\\nURL: ${data.data.url}\\n\\n标题: ${data.data.title || '无标题'}\\n\\n内容: ${data.data.content ? data.data.content.substring(0, 500) + '...' : '无内容'}`);
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

        function clearPreview() {
            document.getElementById('previewTitle').textContent = '暂无数据';
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
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """主页"""
    return render_template_string(HTML_TEMPLATE)

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

@app.route('/api/auto_get_cookie', methods=['POST'])
def api_auto_get_cookie():
    """自动获取Cookie（使用Playwright）"""
    try:
        data = request.json
        url = data.get('url')
        
        if not url:
            return jsonify({'success': False, 'error': 'URL不能为空'})
        
        # 提取域名
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # 生成登录态文件名
        storage_state_path = f"login_state_{domain.replace('.', '_')}.json"
        
        # 使用Playwright自动登录
        scraper = PlaywrightScraper(headless=False)  # 显示浏览器，让用户登录
        try:
            scraper.start()
            
            # 访问登录页面
            login_url = f"{parsed.scheme}://{domain}"
            logger.info(f"正在访问登录页面: {login_url}")
            scraper.page.goto(login_url, wait_until='networkidle', timeout=30000)
            
            # 智能等待用户登录
            logger.info("请在浏览器中完成登录...")
            logger.info("系统会检测登录状态，登录完成后会自动保存")
            
            # 等待登录完成的智能检测
            import time
            max_wait = 300  # 最多等待5分钟
            check_interval = 2  # 每2秒检查一次
            initial_url = scraper.page.url
            initial_cookies_count = len(scraper.get_cookies())
            
            for i in range(int(max_wait / check_interval)):
                time.sleep(check_interval)
                
                current_url = scraper.page.url
                current_cookies = scraper.get_cookies()
                current_cookies_count = len(current_cookies)
                
                # 检测登录完成的标志：
                # 1. URL发生变化（可能跳转到登录后的页面）
                # 2. Cookie数量增加（登录后通常会有新的Cookie）
                # 3. 页面内容变化（检测登录相关的关键词消失）
                
                url_changed = current_url != initial_url
                cookies_increased = current_cookies_count > initial_cookies_count
                
                # 检查是否有登录相关的Cookie（如session、token等）
                has_auth_cookies = any(
                    'session' in c['name'].lower() or 
                    'token' in c['name'].lower() or 
                    'auth' in c['name'].lower() or
                    'login' in c['name'].lower()
                    for c in current_cookies
                )
                
                if (url_changed or cookies_increased or has_auth_cookies) and i > 5:
                    # 再等待几秒确保登录完成
                    time.sleep(3)
                    logger.info("检测到登录完成，正在保存登录态...")
                    break
                
                if i % 10 == 0:  # 每20秒提示一次
                    logger.info(f"等待登录中... ({i * check_interval}秒)")
            
            # 保存登录态
            scraper.context.storage_state(path=storage_state_path)
            logger.info(f"✅ 登录态已保存: {storage_state_path}")
            
            # 获取Cookie
            cookies = scraper.get_cookies()
            cookie_dict = {c['name']: c['value'] for c in cookies}
            cookie_string = CookieHelper.cookie_dict_to_string(cookie_dict)
            
            return jsonify({
                'success': True,
                'cookie': cookie_string,
                'storage_state': storage_state_path,
                'message': 'Cookie获取成功'
            })
            
        finally:
            scraper.close()
            
    except Exception as e:
        logger.error(f"自动获取Cookie失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/fetch', methods=['POST'])
def api_fetch():
    """抓取API"""
    try:
        data = request.json
        url = data.get('url')
        cookie = data.get('cookie', '').strip()
        method = data.get('method', 'playwright')
        storage_state_path = data.get('storage_state_path', '').strip()

        if not url:
            return jsonify({'success': False, 'error': 'URL不能为空'})

        if method == 'playwright':
            if storage_state_path and os.path.exists(storage_state_path):
                scraper = PlaywrightScraper(headless=True, storage_state_path=storage_state_path)
            else:
                scraper = PlaywrightScraper(headless=True)
            try:
                scraper.start()
                page_data = scraper.fetch_page(url, wait_for_url_change=True)
            finally:
                scraper.close()
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
                scraper.close()
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

@app.route('/api/save', methods=['POST'])
def api_save():
    """保存API"""
    try:
        data = request.json
        saved_data = db_manager.save_page_data(
            url=data.get('url'),
            title=data.get('title', '无标题'),
            content=data.get('content', '')
        )
        return jsonify({
            'success': True,
            'id': saved_data.id,
            'title': saved_data.title
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
                return jsonify({
                    'success': True,
                    'data': {
                        'id': data.id,
                        'url': data.url,
                        'title': data.title,
                        'content': data.content,
                        'created_at': data.created_at.strftime('%Y-%m-%d %H:%M:%S') if data.created_at else ''
                    }
                })
        return jsonify({'success': False, 'error': '数据不存在'})
    except Exception as e:
        logger.error(f"获取详情失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("=" * 60)
    print("🌐 网页抓取工具 Web GUI（优化版）")
    print("=" * 60)
    print("📱 访问地址: http://127.0.0.1:5000")
    print("💡 智能检测登录需求，自动获取Cookie")
    print("💡 按 Ctrl+C 停止服务器")
    print("=" * 60)
    app.run(debug=True, host='127.0.0.1', port=5000)
