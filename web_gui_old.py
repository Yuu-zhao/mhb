"""
网页抓取Web GUI应用
基于Flask的Web界面，不依赖系统GUI库
"""
from flask import Flask, render_template_string, request, jsonify
from scraper import WebScraper
from selenium_scraper import SeleniumScraper
from playwright_scraper import PlaywrightScraper
from database import DatabaseManager
from cookie_helper import CookieHelper
import logging
import os
import threading

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
db_manager = DatabaseManager()

# HTML模板
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
            max-width: 1200px;
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
        }
        .section {
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .section h2 {
            color: #333;
            margin-bottom: 15px;
            font-size: 1.3em;
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
        input[type="text"], textarea, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        textarea {
            resize: vertical;
            min-height: 80px;
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
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        .btn-secondary:hover {
            background: #5a6268;
        }
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .preview-section {
            margin-top: 30px;
        }
        .preview-box {
            background: white;
            border: 2px solid #ddd;
            border-radius: 6px;
            padding: 15px;
            margin-top: 10px;
            max-height: 400px;
            overflow-y: auto;
        }
        .preview-title {
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }
        .preview-content {
            color: #666;
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
        .radio-group {
            display: flex;
            gap: 20px;
            margin-top: 10px;
        }
        .radio-item {
            display: flex;
            align-items: center;
        }
        .radio-item input {
            width: auto;
            margin-right: 5px;
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
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🕷️ 网页抓取工具</h1>
            <p>轻松抓取网页内容并保存到数据库</p>
        </div>
        <div class="content">
            <div id="status" class="status"></div>
            
            <div class="section">
                <h2>📝 URL设置</h2>
                <div class="form-group">
                    <label for="url">网页地址:</label>
                    <input type="text" id="url" placeholder="https://example.com" value="https://">
                </div>
            </div>

            <div class="section">
                <h2>🍪 Cookie设置（可选，用于需要登录的页面）</h2>
                <div class="form-group">
                    <label for="cookie">Cookie字符串:</label>
                    <textarea id="cookie" placeholder="从浏览器开发者工具复制Cookie，格式: name1=value1; name2=value2"></textarea>
                </div>
                <div class="btn-group">
                    <button class="btn-secondary" onclick="loadCookieFile()">从文件加载Cookie</button>
                    <button class="btn-secondary" onclick="saveCookieFile()">保存Cookie到文件</button>
                    <input type="file" id="cookieFileInput" accept=".json" style="display:none" onchange="handleCookieFileSelect(event)">
                </div>
            </div>

            <div class="section">
                <h2>⚙️ 抓取方法</h2>
                <div class="radio-group">
                    <div class="radio-item">
                        <input type="radio" id="method_requests" name="method" value="requests" checked>
                        <label for="method_requests">Requests + Cookie（快速，推荐）</label>
                    </div>
                    <div class="radio-item">
                        <input type="radio" id="method_selenium" name="method" value="selenium">
                        <label for="method_selenium">Selenium（支持JavaScript渲染）</label>
                    </div>
                    <div class="radio-item">
                        <input type="radio" id="method_playwright" name="method" value="playwright">
                        <label for="method_playwright">Playwright（推荐，支持保存登录态）</label>
                    </div>
                </div>
                <div style="margin-top: 10px; padding: 10px; background: #e7f3ff; border-radius: 6px; font-size: 0.9em;">
                    <strong>💡 Playwright提示：</strong>
                    <div style="margin-top: 5px;">
                        <label for="storageStateFile">登录态文件（可选）:</label>
                        <input type="text" id="storageStateFile" placeholder="login_state.json" style="width: 200px; margin-left: 5px;">
                        <button class="btn-secondary" onclick="selectStorageStateFile()" style="margin-left: 5px; padding: 5px 10px;">选择文件</button>
                        <input type="file" id="storageStateFileInput" accept=".json" style="display:none" onchange="handleStorageStateFileSelect(event)">
                    </div>
                    <div style="margin-top: 5px; color: #666;">
                        首次使用需要先登录并保存登录态，以后就可以自动使用了
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>🎯 操作</h2>
                <div class="btn-group">
                    <button class="btn-primary" onclick="startFetch()">开始抓取</button>
                    <button class="btn-success" id="saveBtn" onclick="saveToDatabase()" disabled>保存到数据库</button>
                    <button class="btn-info" onclick="viewSavedData()">查看已保存数据</button>
                    <button class="btn-secondary" onclick="clearPreview()">清空预览</button>
                </div>
            </div>

            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p style="margin-top: 10px;">正在抓取，请稍候...</p>
            </div>

            <div class="section preview-section">
                <h2>👀 数据预览</h2>
                <div class="form-group">
                    <label>标题:</label>
                    <div class="preview-box" id="previewTitle">暂无数据</div>
                </div>
                <div class="form-group">
                    <label>内容:</label>
                    <div class="preview-box" id="previewContent" style="max-height: 300px;">暂无数据</div>
                </div>
            </div>
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

        function showStatus(message, type) {
            const statusDiv = document.getElementById('status');
            statusDiv.textContent = message;
            statusDiv.className = 'status ' + type;
            statusDiv.style.display = 'block';
            setTimeout(() => {
                statusDiv.style.display = 'none';
            }, 5000);
        }

        function startFetch() {
            const url = document.getElementById('url').value.trim();
            if (!url || url === 'https://') {
                showStatus('请输入有效的URL', 'error');
                return;
            }

            if (!url.startsWith('http://') && !url.startsWith('https://')) {
                showStatus('URL必须以http://或https://开头', 'error');
                return;
            }

            const cookie = document.getElementById('cookie').value.trim();
            const method = document.querySelector('input[name="method"]:checked').value;
            const storageStateFile = document.getElementById('storageStateFile').value.trim();

            document.getElementById('loading').style.display = 'block';
            document.querySelector('.btn-primary').disabled = true;
            document.getElementById('saveBtn').disabled = true;

            fetch('/api/fetch', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: url,
                    cookie: cookie,
                    method: method,
                    storage_state_path: storageStateFile
                })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('loading').style.display = 'none';
                document.querySelector('.btn-primary').disabled = false;

                if (data.success) {
                    currentPageData = data.data;
                    let title = data.data.title || '无标题';
                    let urlInfo = '';
                    if (data.data.redirected && data.data.original_url) {
                        urlInfo = ` (已跳转: ${data.data.original_url} -> ${data.data.url})`;
                    }
                    document.getElementById('previewTitle').textContent = title;
                    let content = data.data.content || '无内容';
                    if (content.length > 50000) {
                        content = content.substring(0, 50000) + '\\n\\n... (内容过长，已截断，完整内容将保存到数据库)';
                    }
                    document.getElementById('previewContent').textContent = content;
                    document.getElementById('saveBtn').disabled = false;
                    showStatus(`抓取成功！标题: ${title}, 内容长度: ${data.data.content?.length || 0} 字符${urlInfo}`, 'success');
                } else {
                    showStatus('抓取失败: ' + data.error, 'error');
                }
            })
            .catch(error => {
                document.getElementById('loading').style.display = 'none';
                document.querySelector('.btn-primary').disabled = false;
                showStatus('抓取失败: ' + error.message, 'error');
            });
        }

        function saveToDatabase() {
            if (!currentPageData) {
                showStatus('没有可保存的数据，请先抓取页面', 'error');
                return;
            }

            fetch('/api/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
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
                        const cookies = JSON.parse(e.target.result);
                        const cookieString = Object.entries(cookies).map(([k, v]) => `${k}=${v}`).join('; ');
                        document.getElementById('cookie').value = cookieString;
                        showStatus('Cookie文件加载成功', 'success');
                    } catch (error) {
                        showStatus('加载Cookie文件失败: ' + error.message, 'error');
                    }
                };
                reader.readAsText(file);
            }
        }

        function saveCookieFile() {
            const cookie = document.getElementById('cookie').value.trim();
            if (!cookie) {
                showStatus('请先输入Cookie', 'error');
                return;
            }

            try {
                const cookies = {};
                cookie.split(';').forEach(item => {
                    const [key, value] = item.trim().split('=');
                    if (key && value) {
                        cookies[key] = value;
                    }
                });

                const blob = new Blob([JSON.stringify(cookies, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'cookies.json';
                a.click();
                URL.revokeObjectURL(url);
                showStatus('Cookie文件已保存', 'success');
            } catch (error) {
                showStatus('保存Cookie文件失败: ' + error.message, 'error');
            }
        }

        // 点击模态框外部关闭
        window.onclick = function(event) {
            const modal = document.getElementById('dataModal');
            if (event.target == modal) {
                modal.style.display = 'none';
            }
        }

        // URL输入框按Enter键快速抓取
        document.getElementById('url').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                startFetch();
            }
        });

        function selectStorageStateFile() {
            document.getElementById('storageStateFileInput').click();
        }

        function handleStorageStateFileSelect(event) {
            const file = event.target.files[0];
            if (file) {
                document.getElementById('storageStateFile').value = file.name;
                showStatus('已选择登录态文件: ' + file.name, 'info');
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """主页"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/fetch', methods=['POST'])
def api_fetch():
    """抓取API"""
    try:
        data = request.json
        url = data.get('url')
        cookie = data.get('cookie', '').strip()
        method = data.get('method', 'requests')

        if not url:
            return jsonify({'success': False, 'error': 'URL不能为空'})

        if method == 'selenium':
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
                
                # 启用URL变化等待，处理中间跳转页
                page_data = scraper.fetch_page(url, wait_for_url_change=True, wait_timeout=15)
            finally:
                scraper.close()
        else:
            scraper = WebScraper(use_session=True)
            if cookie:
                scraper.set_cookies(cookie)
            # 允许重定向，处理中间跳转页
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
    print("🌐 网页抓取工具 Web GUI")
    print("=" * 60)
    print("📱 访问地址: http://127.0.0.1:5000")
    print("💡 按 Ctrl+C 停止服务器")
    print("=" * 60)
    app.run(debug=True, host='127.0.0.1', port=5000)
