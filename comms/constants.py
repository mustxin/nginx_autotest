"""
路径常量管理模块
基于 pathlib 统一管理项目目录结构，确保可移植性
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "test_data"
LOG_DIR = BASE_DIR / "logs"

INFO_FILE = LOG_DIR / "info.log"
ERROR_FILE = LOG_DIR / "error.log"


def get_test_data_path(filename: str) -> Path:
    """获取测试数据文件的完整路径"""
    return DATA_DIR / filename
