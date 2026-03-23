#!/bin/bash
# GUI 启动脚本：检测 tkinter 后再启动

set -e
cd "$(dirname "$0")"

# 优先使用 venv / PATH 中的 python
if command -v python &>/dev/null; then
  PY=python
elif command -v python3 &>/dev/null; then
  PY=python3
else
  echo "未找到 python 或 python3，请先安装 Python。"
  exit 1
fi

if ! "$PY" -c "import tkinter" 2>/dev/null; then
  echo "错误：当前 Python 未包含 tkinter（_tkinter），无法启动桌面界面。"
  echo ""
  echo "若使用 Homebrew 的 python@3.13，请安装带 Tk 的版本并用它重建虚拟环境，例如："
  echo "  brew install python-tk@3.13"
  echo "  rm -rf .venv"
  echo "  \"\$(brew --prefix python-tk@3.13)/bin/python3\" -m venv .venv"
  echo "  source .venv/bin/activate"
  echo "  pip install -r requirements.txt && playwright install chromium"
  echo ""
  echo "详见 README.md「安装」一节。"
  exit 1
fi

exec "$PY" gui_app.py "$@"
