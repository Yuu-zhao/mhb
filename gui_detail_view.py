"""
藏宝阁商品详情展示（可复用：爬取结果预览 / 数据库已录入详情）
使用多 Tab + 每页可滚动，避免单屏无法展示全部字段。
"""
from __future__ import annotations

import json
from typing import Any, Dict, Optional

import tkinter as tk
from tkinter import ttk, scrolledtext

# 与 cbg 分类码对应的中文
PRODUCT_TYPE_ZH = {
    "CHAR": "角色",
    "ITEM": "道具",
    "SUMMON": "召唤兽",
}


def _zh_type(code: Optional[str]) -> str:
    if not code:
        return ""
    return PRODUCT_TYPE_ZH.get(str(code).upper(), str(code))


class GoodsDetailPanel(ttk.Frame):
    """
    将结构化 payload（basic + sections + children）分 Tab 展示。
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._notebook: Optional[ttk.Notebook] = None
        self._build_empty()

    def _build_empty(self):
        self._clear_notebook()
        lab = ttk.Label(self, text="暂无数据，请先爬取或从左侧选择记录。", padding=12)
        lab.pack(fill=tk.BOTH, expand=True)

    def _clear_notebook(self):
        for w in self.winfo_children():
            w.destroy()
        self._notebook = None

    def _add_scroll_tab(self, nb: ttk.Notebook, title: str, text: str, font=("Consolas", 10)) -> None:
        f = ttk.Frame(nb, padding=4)
        nb.add(f, text=title)
        st = scrolledtext.ScrolledText(f, wrap=tk.WORD, font=font, height=12)
        st.pack(fill=tk.BOTH, expand=True)
        st.insert(tk.END, text or "")
        st.config(state=tk.DISABLED)

    def clear(self):
        """清空为占位提示"""
        self._build_empty()

    def set_flat_fallback(self, flat: Dict[str, Any]):
        """无结构化载荷时，将扁平字段单 Tab 展示"""
        if not flat:
            self._build_empty()
            return
        self._clear_notebook()
        nb = ttk.Notebook(self, padding=4)
        nb.pack(fill=tk.BOTH, expand=True)
        self._notebook = nb
        lines = "\n".join(f"{k}: {v}" for k, v in flat.items())
        self._add_scroll_tab(nb, "扁平字段", lines)

    def set_payload(self, payload: Optional[Dict[str, Any]]):
        """
        展示结构化载荷（与 __goods_payload__ / goods_record.payload_json 解析后一致）
        """
        if not payload or not isinstance(payload, dict):
            self._build_empty()
            return

        self._clear_notebook()

        nb = ttk.Notebook(self, padding=4)
        nb.pack(fill=tk.BOTH, expand=True)
        self._notebook = nb

        ptype = payload.get("product_type") or payload.get("category_code")
        gno = payload.get("goods_no") or ""
        title_hint = f"{_zh_type(str(ptype))} · 编号 {gno}"
        ch = payload.get("children")
        ct = payload.get("character_tabs")

        # --- 概览 ---
        lines = [
            title_hint,
            "",
            f"商品类型: {_zh_type(str(ptype))} ({ptype or '-'})",
            f"编号: {gno}",
            f"链接: {payload.get('source_url') or ''}",
            f"子类: {payload.get('sub_category_code') or '-'}",
        ]
        if isinstance(ch, list) and ch:
            lines.append(f"关联商品数: {len(ch)}")
        if isinstance(ct, dict) and ct:
            lines.append(f"角色页签已抓取: {len(ct)} 项")
        self._add_scroll_tab(nb, "概览", "\n".join(lines))

        # --- 基本信息 ---
        basic = payload.get("basic") or {}
        self._add_scroll_tab(nb, "基本信息", json.dumps(basic, ensure_ascii=False, indent=2))

        # --- 角色详情各 Tab（需 Playwright 切换后抓取的数据）---
        if isinstance(ct, dict) and ct:
            sub_nb = ttk.Notebook(nb, padding=2)
            nb.add(sub_nb, text=f"角色页签({len(ct)})")
            for tid, entry in ct.items():
                if not isinstance(entry, dict):
                    continue
                lab = str(entry.get("label") or tid)[:16]
                body = json.dumps(entry, ensure_ascii=False, indent=2)
                self._add_scroll_tab(sub_nb, f"{lab}", body)

        # --- 分块 sections：每块一个 Tab（跳过已单独展示的「角色页签」）---
        sections = payload.get("sections") or {}
        if isinstance(sections, dict):
            for sec_name, sec_val in sections.items():
                if sec_name == "角色页签" and isinstance(ct, dict) and ct:
                    continue
                tab_title = str(sec_name)[:18]
                if isinstance(sec_val, (dict, list)):
                    body = json.dumps(sec_val, ensure_ascii=False, indent=2)
                else:
                    body = str(sec_val)
                self._add_scroll_tab(nb, f"板块·{tab_title}", body)

        # --- 关联商品 ---
        if isinstance(ch, list) and ch:
            sub_nb = ttk.Notebook(nb)
            nb.add(sub_nb, text=f"关联商品({len(ch)})")
            for i, child in enumerate(ch, 1):
                if not isinstance(child, dict):
                    continue
                ctyp = child.get("product_type") or child.get("category_code")
                cno = child.get("goods_no") or ""
                sub_nb.add(self._make_child_frame(child), text=f"{i}.{_zh_type(str(ctyp))[:2]}{cno}")

        # --- 完整 JSON ---
        redacted = {k: v for k, v in payload.items()}
        self._add_scroll_tab(nb, "完整JSON", json.dumps(redacted, ensure_ascii=False, indent=2))

    def _make_child_frame(self, child: Dict[str, Any]) -> ttk.Frame:
        f = ttk.Frame(self, padding=4)
        inner = ttk.Notebook(f)
        inner.pack(fill=tk.BOTH, expand=True)
        self._add_scroll_tab(inner, "概览", json.dumps(
            {
                "类型": _zh_type(str(child.get("product_type") or child.get("category_code"))),
                "编号": child.get("goods_no"),
                "链接": child.get("source_url"),
            },
            ensure_ascii=False,
            indent=2,
        ))
        self._add_scroll_tab(inner, "basic", json.dumps(child.get("basic") or {}, ensure_ascii=False, indent=2))
        self._add_scroll_tab(inner, "sections", json.dumps(child.get("sections") or {}, ensure_ascii=False, indent=2))
        self._add_scroll_tab(inner, "JSON", json.dumps(child, ensure_ascii=False, indent=2))
        return f
