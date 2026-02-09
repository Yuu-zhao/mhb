#!/usr/bin/env python3
"""
项目入口文件
"""
import sys
from pathlib import Path

# 添加src目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.presentation.web.app import run_app

if __name__ == '__main__':
    run_app()
