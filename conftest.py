"""
项目根目录 conftest.py
确保 pytest 可以正确导入 comms 包
"""
import sys
import os

# 将项目根目录添加到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
