"""
网页抓取GUI应用
提供可视化的界面来抓取网页并保存到数据库
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
from scraper import WebScraper
from selenium_scraper import SeleniumScraper
from database import DatabaseManager
from cookie_helper import CookieHelper
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebScraperGUI:
    """网页抓取GUI应用"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("网页抓取工具")
        self.root.geometry("900x700")
        
        # 数据存储
        self.current_page_data = None
        self.db_manager = DatabaseManager()
        
        # 创建界面
        self.create_widgets()
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # URL输入区域
        url_frame = ttk.LabelFrame(main_frame, text="URL设置", padding="10")
        url_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(url_frame, text="网页地址:").pack(anchor=tk.W)
        self.url_entry = ttk.Entry(url_frame, width=80)
        self.url_entry.pack(fill=tk.X, pady=(5, 10))
        self.url_entry.insert(0, "https://")
        # 绑定Enter键快速抓取
        self.url_entry.bind('<Return>', lambda e: self.start_fetch())
        
        # Cookie设置区域
        cookie_frame = ttk.LabelFrame(main_frame, text="Cookie设置（可选，用于需要登录的页面）", padding="10")
        cookie_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(cookie_frame, text="Cookie字符串:").pack(anchor=tk.W)
        self.cookie_entry = ttk.Entry(cookie_frame, width=80)
        self.cookie_entry.pack(fill=tk.X, pady=(5, 5))
        
        cookie_btn_frame = ttk.Frame(cookie_frame)
        cookie_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(cookie_btn_frame, text="从文件加载Cookie", 
                  command=self.load_cookie_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(cookie_btn_frame, text="保存Cookie到文件", 
                  command=self.save_cookie_file).pack(side=tk.LEFT)
        
        # 抓取方法选择
        method_frame = ttk.LabelFrame(main_frame, text="抓取方法", padding="10")
        method_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.method_var = tk.StringVar(value="requests")
        ttk.Radiobutton(method_frame, text="Requests + Cookie（快速，推荐）", 
                       variable=self.method_var, value="requests").pack(anchor=tk.W)
        ttk.Radiobutton(method_frame, text="Selenium（支持JavaScript渲染）", 
                       variable=self.method_var, value="selenium").pack(anchor=tk.W)
        
        # 操作按钮区域
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.fetch_btn = ttk.Button(btn_frame, text="开始抓取 (Enter)", 
                                    command=self.start_fetch, width=18)
        self.fetch_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.save_btn = ttk.Button(btn_frame, text="保存到数据库", 
                                  command=self.save_to_database, 
                                  state=tk.DISABLED, width=15)
        self.save_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(btn_frame, text="查看已保存数据", 
                  command=self.view_saved_data, width=15).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(btn_frame, text="清空预览", 
                  command=self.clear_preview, width=15).pack(side=tk.LEFT)
        
        # 预览区域
        preview_frame = ttk.LabelFrame(main_frame, text="数据预览", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题预览
        ttk.Label(preview_frame, text="标题:").pack(anchor=tk.W)
        self.title_text = tk.Text(preview_frame, height=2, wrap=tk.WORD)
        self.title_text.pack(fill=tk.X, pady=(5, 10))
        
        # 内容预览
        ttk.Label(preview_frame, text="内容:").pack(anchor=tk.W)
        self.content_text = scrolledtext.ScrolledText(preview_frame, wrap=tk.WORD, height=15)
        self.content_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(10, 0))
    
    def load_cookie_file(self):
        """从文件加载Cookie"""
        filepath = filedialog.askopenfilename(
            title="选择Cookie文件",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filepath:
            try:
                cookies = CookieHelper.load_cookies_from_file(filepath)
                cookie_string = CookieHelper.cookie_dict_to_string(cookies)
                self.cookie_entry.delete(0, tk.END)
                self.cookie_entry.insert(0, cookie_string)
                self.status_var.set(f"已加载Cookie文件: {filepath}")
                messagebox.showinfo("成功", "Cookie文件加载成功！")
            except Exception as e:
                messagebox.showerror("错误", f"加载Cookie文件失败: {str(e)}")
    
    def save_cookie_file(self):
        """保存Cookie到文件"""
        cookie_string = self.cookie_entry.get().strip()
        if not cookie_string:
            messagebox.showwarning("警告", "请先输入Cookie")
            return
        
        filepath = filedialog.asksaveasfilename(
            title="保存Cookie文件",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filepath:
            try:
                cookies = CookieHelper.parse_cookie_string(cookie_string)
                CookieHelper.save_cookies_to_file(cookies, filepath)
                self.status_var.set(f"Cookie已保存到: {filepath}")
                messagebox.showinfo("成功", "Cookie文件保存成功！")
            except Exception as e:
                messagebox.showerror("错误", f"保存Cookie文件失败: {str(e)}")
    
    def start_fetch(self):
        """开始抓取（在新线程中执行）"""
        url = self.url_entry.get().strip()
        if not url or url == "https://":
            messagebox.showwarning("警告", "请输入有效的URL")
            return
        
        if not url.startswith(('http://', 'https://')):
            messagebox.showerror("错误", "URL必须以http://或https://开头")
            return
        
        # 禁用按钮，显示进度
        self.fetch_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.DISABLED)
        self.progress.start()
        self.status_var.set("正在抓取...")
        
        # 在新线程中执行抓取
        thread = threading.Thread(target=self.fetch_page_thread, args=(url,))
        thread.daemon = True
        thread.start()
    
    def fetch_page_thread(self, url):
        """抓取页面的线程函数"""
        try:
            method = self.method_var.get()
            cookie_string = self.cookie_entry.get().strip()
            
            if method == "selenium":
                page_data = self.fetch_with_selenium(url)
            else:
                page_data = self.fetch_with_requests(url, cookie_string)
            
            # 在主线程中更新UI
            self.root.after(0, self.update_preview, page_data)
            
        except Exception as e:
            logger.error(f"抓取失败: {str(e)}")
            self.root.after(0, self.fetch_error, str(e))
    
    def fetch_with_requests(self, url, cookie_string):
        """使用requests方法抓取"""
        scraper = WebScraper(use_session=True)
        
        if cookie_string:
            scraper.set_cookies(cookie_string)
        
        return scraper.fetch_page(url)
    
    def fetch_with_selenium(self, url):
        """使用Selenium方法抓取"""
        scraper = SeleniumScraper(headless=True)
        try:
            cookie_string = self.cookie_entry.get().strip()
            
            # 如果有Cookie，先设置
            if cookie_string:
                cookies_dict = CookieHelper.parse_cookie_string(cookie_string)
                selenium_cookies = CookieHelper.dict_to_selenium_cookies(
                    cookies_dict, 
                    domain=".163.com" if "163.com" in url else ""
                )
                scraper.driver.get(url.split('/')[0] + '//' + url.split('/')[2])
                scraper.set_cookies(selenium_cookies)
            
            page_data = scraper.fetch_page(url)
            return page_data
        finally:
            scraper.close()
    
    def update_preview(self, page_data):
        """更新预览区域"""
        self.progress.stop()
        self.fetch_btn.config(state=tk.NORMAL)
        
        if page_data is None:
            self.status_var.set("抓取失败")
            messagebox.showerror("错误", "抓取失败，请检查URL和Cookie是否正确")
            return
        
        self.current_page_data = page_data
        
        # 更新标题
        self.title_text.delete(1.0, tk.END)
        self.title_text.insert(1.0, page_data.get('title', '无标题'))
        
        # 更新内容
        self.content_text.delete(1.0, tk.END)
        content = page_data.get('content', '')
        # 限制显示长度，避免界面卡顿
        if len(content) > 50000:
            content = content[:50000] + "\n\n... (内容过长，已截断，完整内容将保存到数据库)"
        self.content_text.insert(1.0, content)
        
        # 启用保存按钮
        self.save_btn.config(state=tk.NORMAL)
        
        # 更新状态
        content_len = len(page_data.get('content', ''))
        self.status_var.set(f"抓取成功！标题: {page_data.get('title', '无标题')}, 内容长度: {content_len} 字符")
        messagebox.showinfo("成功", f"抓取成功！\n标题: {page_data.get('title', '无标题')}\n内容长度: {content_len} 字符")
    
    def fetch_error(self, error_msg):
        """处理抓取错误"""
        self.progress.stop()
        self.fetch_btn.config(state=tk.NORMAL)
        self.status_var.set(f"抓取失败: {error_msg}")
        messagebox.showerror("错误", f"抓取失败:\n{error_msg}")
    
    def save_to_database(self):
        """保存到数据库"""
        if self.current_page_data is None:
            messagebox.showwarning("警告", "没有可保存的数据，请先抓取页面")
            return
        
        try:
            saved_data = self.db_manager.save_page_data(
                url=self.current_page_data['url'],
                title=self.current_page_data.get('title', '无标题'),
                content=self.current_page_data.get('content', '')
            )
            
            self.status_var.set(f"保存成功！ID: {saved_data.id}")
            messagebox.showinfo("成功", f"数据已保存到数据库！\nID: {saved_data.id}\n标题: {saved_data.title}")
            
        except Exception as e:
            logger.error(f"保存失败: {str(e)}")
            messagebox.showerror("错误", f"保存到数据库失败:\n{str(e)}")
    
    def view_saved_data(self):
        """查看已保存的数据"""
        try:
            all_data = self.db_manager.get_all_data()
            
            if not all_data:
                messagebox.showinfo("提示", "数据库中暂无数据")
                return
            
            # 创建新窗口显示数据
            view_window = tk.Toplevel(self.root)
            view_window.title("已保存的数据")
            view_window.geometry("800x500")
            
            # 创建表格
            tree_frame = ttk.Frame(view_window, padding="10")
            tree_frame.pack(fill=tk.BOTH, expand=True)
            
            # 滚动条
            scrollbar = ttk.Scrollbar(tree_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # 树形视图
            tree = ttk.Treeview(tree_frame, columns=("ID", "URL", "Title", "Created"), 
                               show="headings", yscrollcommand=scrollbar.set)
            scrollbar.config(command=tree.yview)
            
            # 设置列
            tree.heading("ID", text="ID")
            tree.heading("URL", text="URL")
            tree.heading("Title", text="标题")
            tree.heading("Created", text="创建时间")
            
            tree.column("ID", width=50)
            tree.column("URL", width=300)
            tree.column("Title", width=200)
            tree.column("Created", width=150)
            
            # 插入数据
            for data in all_data:
                tree.insert("", tk.END, values=(
                    data.id,
                    data.url[:50] + "..." if len(data.url) > 50 else data.url,
                    data.title[:30] + "..." if data.title and len(data.title) > 30 else (data.title or "无标题"),
                    data.created_at.strftime("%Y-%m-%d %H:%M:%S") if data.created_at else ""
                ))
            
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # 双击查看详情
            def on_double_click(event):
                item = tree.selection()[0]
                values = tree.item(item, "values")
                data_id = values[0]
                
                # 查找完整数据
                for data in all_data:
                    if data.id == int(data_id):
                        self.show_data_detail(data)
                        break
            
            tree.bind("<Double-1>", on_double_click)
            
        except Exception as e:
            logger.error(f"查看数据失败: {str(e)}")
            messagebox.showerror("错误", f"查看数据失败:\n{str(e)}")
    
    def show_data_detail(self, data):
        """显示数据详情"""
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"数据详情 - ID: {data.id}")
        detail_window.geometry("700x600")
        
        detail_frame = ttk.Frame(detail_window, padding="10")
        detail_frame.pack(fill=tk.BOTH, expand=True)
        
        # URL
        ttk.Label(detail_frame, text="URL:").pack(anchor=tk.W)
        url_text = tk.Text(detail_frame, height=2, wrap=tk.WORD)
        url_text.insert(1.0, data.url)
        url_text.config(state=tk.DISABLED)
        url_text.pack(fill=tk.X, pady=(5, 10))
        
        # 标题
        ttk.Label(detail_frame, text="标题:").pack(anchor=tk.W)
        title_text = tk.Text(detail_frame, height=2, wrap=tk.WORD)
        title_text.insert(1.0, data.title or "无标题")
        title_text.config(state=tk.DISABLED)
        title_text.pack(fill=tk.X, pady=(5, 10))
        
        # 内容
        ttk.Label(detail_frame, text="内容:").pack(anchor=tk.W)
        content_text = scrolledtext.ScrolledText(detail_frame, wrap=tk.WORD)
        content_text.insert(1.0, data.content or "")
        content_text.config(state=tk.DISABLED)
        content_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # 创建时间
        ttk.Label(detail_frame, text=f"创建时间: {data.created_at.strftime('%Y-%m-%d %H:%M:%S') if data.created_at else '未知'}", 
                 font=("Arial", 9)).pack(anchor=tk.W, pady=(10, 0))
    
    def clear_preview(self):
        """清空预览"""
        self.title_text.delete(1.0, tk.END)
        self.content_text.delete(1.0, tk.END)
        self.current_page_data = None
        self.save_btn.config(state=tk.DISABLED)
        self.status_var.set("已清空预览")


def main():
    """主函数"""
    root = tk.Tk()
    app = WebScraperGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
