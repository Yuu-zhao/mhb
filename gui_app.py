"""
藏宝阁规则页爬取 - 桌面 GUI
功能：输入 URL → 爬取（可选深度关联）→ 分 Tab 展示 → 保存/更新数据库；
左侧列表展示已录入主商品，点击可查看详情（与爬取后共用详情组件）。
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json
import logging

from scrape_helper import scrape_page
from login_state_manager import LoginStateManager
from database import DatabaseManager
from gui_detail_view import GoodsDetailPanel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("藏宝阁商品爬取 · 数据录入")
        self.root.geometry("1180x780")
        self.root.minsize(900, 560)

        self.login_manager = LoginStateManager()
        self.db_manager = DatabaseManager()

        self.current_page_data = None
        self.current_extracted = None

        self._build_ui()
        self._status_var = tk.StringVar(value="就绪")
        ttk.Label(self.root, textvariable=self._status_var, relief=tk.SUNKEN, anchor=tk.W).pack(
            side=tk.BOTTOM, fill=tk.X
        )
        self._refresh_goods_list()

    def _build_ui(self):
        outer = ttk.Frame(self.root, padding=6)
        outer.pack(fill=tk.BOTH, expand=True)

        paned = ttk.PanedWindow(outer, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # ---------- 左侧：已录入列表 ----------
        left = ttk.Frame(paned, width=300)
        paned.add(left, weight=0)

        lf = ttk.LabelFrame(left, text="已录入商品（主商品）", padding=6)
        lf.pack(fill=tk.BOTH, expand=True)

        cols = ("goods_no", "title", "ptype", "updated")
        self._tree = ttk.Treeview(lf, columns=cols, show="headings", height=22, selectmode="browse")
        self._tree.heading("goods_no", text="编号")
        self._tree.heading("title", text="标题/亮点")
        self._tree.heading("ptype", text="类型")
        self._tree.heading("updated", text="更新时间")
        self._tree.column("goods_no", width=120, stretch=False)
        self._tree.column("title", width=100, stretch=True)
        self._tree.column("ptype", width=52, stretch=False)
        self._tree.column("updated", width=88, stretch=False)

        vsb = ttk.Scrollbar(lf, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self._tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        ttk.Button(left, text="刷新列表", command=self._refresh_goods_list).pack(fill=tk.X, pady=(6, 0))

        # ---------- 右侧 ----------
        right = ttk.Frame(paned, padding=(8, 0))
        paned.add(right, weight=1)

        url_f = ttk.LabelFrame(right, text="页面地址", padding=8)
        url_f.pack(fill=tk.X, pady=(0, 6))
        url_row = ttk.Frame(url_f)
        url_row.pack(fill=tk.X)
        self._url_entry = ttk.Entry(url_row, width=70)
        self._url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self._url_entry.insert(0, "https://")
        self._url_entry.bind("<Return>", lambda e: self._on_start())
        self._fetch_btn = ttk.Button(url_row, text="开始爬取", command=self._on_start, width=12)
        self._fetch_btn.pack(side=tk.RIGHT)

        opt_row = ttk.Frame(url_f)
        opt_row.pack(fill=tk.X, pady=(8, 0))
        self._role_tabs_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            opt_row,
            text="抓取角色全部 Tab（人物/修炼、技能、道具…，需切换页签，较慢）",
            variable=self._role_tabs_var,
        ).pack(anchor=tk.W)
        self._deep_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            opt_row,
            text="深度爬取关联（再抓取子商品详情并入库，最慢）",
            variable=self._deep_var,
        ).pack(anchor=tk.W)

        btn_row = ttk.Frame(right)
        btn_row.pack(fill=tk.X, pady=(0, 6))
        self._save_btn = ttk.Button(
            btn_row, text="保存 / 更新到数据库", command=self._on_save, state=tk.DISABLED, width=22
        )
        self._save_btn.pack(side=tk.LEFT)

        data_f = ttk.LabelFrame(right, text="核心数据（分 Tab 展示，可滚动）", padding=6)
        data_f.pack(fill=tk.BOTH, expand=True)
        self._detail = GoodsDetailPanel(data_f)
        self._detail.pack(fill=tk.BOTH, expand=True)

    def _status(self, msg):
        self._status_var.set(msg)

    def _set_busy(self, busy):
        self._fetch_btn.config(state=tk.DISABLED if busy else tk.NORMAL)

    def _refresh_goods_list(self):
        for iid in self._tree.get_children():
            self._tree.delete(iid)
        try:
            rows = self.db_manager.list_goods_records(limit=300, roots_only=True)
            for r in rows:
                ptype = r.product_type or r.category_code or ""
                zh = {"CHAR": "角色", "ITEM": "道具", "SUMMON": "兽"}.get(ptype, ptype[:4])
                ut = r.updated_at.strftime("%m-%d %H:%M") if r.updated_at else ""
                self._tree.insert(
                    "",
                    tk.END,
                    iid=r.goods_no,
                    values=(r.goods_no, (r.title or "")[:40], zh, ut),
                )
        except Exception as e:
            logger.exception("刷新列表失败: %s", e)

    def _on_tree_select(self, event=None):
        sel = self._tree.selection()
        if not sel:
            return
        goods_no = sel[0]
        try:
            rec = self.db_manager.get_goods_by_no(goods_no)
            if not rec:
                return
            payload = json.loads(rec.payload_json)
            self._detail.set_payload(payload)
            self._status(f"已加载数据库记录: {goods_no}")
        except Exception as e:
            logger.exception("加载记录失败: %s", e)
            messagebox.showerror("错误", f"加载失败: {e}")

    def _show_login_dialog_then_retry(self, url, domain):
        win = tk.Toplevel(self.root)
        win.title("需要登录")
        win.geometry("420x180")
        win.transient(self.root)
        win.grab_set()

        ttk.Label(
            win,
            text="该页面需要登录。点击「打开浏览器登录」后将会弹出浏览器，\n请在浏览器中完成登录，程序检测到登录成功后会继续抓取。",
            justify=tk.LEFT,
            padding=(16, 12),
        ).pack(anchor=tk.W)
        status = tk.StringVar(value="")
        ttk.Label(win, textvariable=status, padding=(16, 0)).pack(anchor=tk.W)

        def do_login_and_retry():
            status.set("正在打开浏览器，请在其中完成登录…")
            win.update()
            try:
                self.login_manager._perform_login(domain, url)
                self.root.after(0, lambda: _close_and_retry())
            except Exception as e:
                logger.exception("登录过程异常: %s", e)
                self.root.after(0, lambda: status.set(f"登录异常: {e}"))

        def _close_and_retry():
            try:
                win.destroy()
            except Exception:
                pass
            self._set_busy(True)
            self._run_scrape_flow(url, use_login_state=True)

        def open_browser():
            for c in win.winfo_children():
                if isinstance(c, ttk.Button) and c.cget("text") == "打开浏览器登录":
                    c.config(state=tk.DISABLED)
                    break
            t = threading.Thread(target=do_login_and_retry, daemon=True)
            t.start()

        btn_f = ttk.Frame(win, padding=16)
        btn_f.pack(fill=tk.X)
        ttk.Button(btn_f, text="打开浏览器登录", command=open_browser).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_f, text="取消", command=win.destroy).pack(side=tk.LEFT)

    def _run_scrape_flow(self, url, use_login_state=False):
        domain = self.login_manager.get_domain_from_url(url)
        storage = self.login_manager.get_state(domain) if use_login_state else None
        deep = self._deep_var.get()
        tabs = self._role_tabs_var.get()

        def work():
            hint = []
            if tabs:
                hint.append("角色Tab")
            if deep:
                hint.append("关联")
            self.root.after(
                0,
                lambda: self._status("正在抓取…" + (f"（{'+'.join(hint)}）" if hint else "")),
            )
            page_data, extracted, need_login = scrape_page(
                url,
                storage_state_path=storage,
                headless=True,
                deep_associated=deep,
                fetch_role_tabs=tabs,
            )
            if need_login and not page_data:
                self.root.after(0, lambda: self._on_need_login(url, domain))
                return
            if need_login and page_data:
                final = (page_data.get("url") or "").lower()
                if "show_login" in final or "act=show_login" in final:
                    self.root.after(0, lambda: self._on_need_login(url, domain))
                    return
            self.root.after(0, lambda: self._on_result(page_data, extracted))

        t = threading.Thread(target=work, daemon=True)
        t.start()

    def _on_need_login(self, url, domain):
        self._set_busy(False)
        self._status("需要登录")
        self._show_login_dialog_then_retry(url, domain)

    def _on_result(self, page_data, extracted):
        self._set_busy(False)
        self.current_page_data = page_data
        self.current_extracted = extracted or {}

        payload = self.current_extracted.get("__goods_payload__")
        if payload:
            self._detail.set_payload(payload)
        else:
            flat = {k: v for k, v in (self.current_extracted or {}).items() if not str(k).startswith("__")}
            if flat:
                self._detail.set_flat_fallback(flat)
            else:
                self._detail.clear()

        self._save_btn.config(state=tk.NORMAL)
        self._status("抓取完成，可保存到数据库")

    def _on_start(self):
        url = self._url_entry.get().strip()
        if not url or url == "https://":
            messagebox.showwarning("提示", "请输入有效 URL")
            return
        if not url.startswith(("http://", "https://")):
            messagebox.showerror("错误", "URL 须以 http:// 或 https:// 开头")
            return

        self._set_busy(True)
        self._save_btn.config(state=tk.DISABLED)
        self._run_scrape_flow(url, use_login_state=True)

    def _on_save(self):
        if not self.current_page_data or self.current_extracted is None:
            messagebox.showwarning("提示", "请先完成一次爬取")
            return
        try:
            title = self.current_page_data.get("title") or "无标题"
            payload = self.current_extracted.get("__goods_payload__")
            if payload:
                if isinstance(payload.get("children"), list) and len(payload["children"]) > 0:
                    gr = self.db_manager.save_goods_bundle(payload, title=title)
                else:
                    gr = self.db_manager.save_goods_record(payload, title=title)
                self._status(f"已写入 goods_record，编号: {gr.goods_no}，类型: {gr.product_type or gr.category_code}")
            clean = {k: v for k, v in self.current_extracted.items() if not str(k).startswith("__")}
            self.db_manager.save_page_data(
                url=self.current_page_data["url"],
                title=title,
                content=self.current_page_data.get("content"),
                extracted_data=clean,
            )
            msg = "保存成功"
            if payload:
                msg += f"\n主商品编号: {payload.get('goods_no')}"
                ch = payload.get("children")
                if isinstance(ch, list) and ch:
                    msg += f"\n已同时写入 {len(ch)} 条关联商品"
            messagebox.showinfo("成功", msg)
            self._refresh_goods_list()
        except Exception as e:
            logger.exception("保存失败: %s", e)
            messagebox.showerror("错误", f"保存失败: {e}")


def main():
    root = tk.Tk()
    app = ScraperGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
