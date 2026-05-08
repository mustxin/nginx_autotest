"""
使用常量对路径进行管理
好处：代码使用非绝对路径，可移植性高
"""
import os

# 获取项目路径（项目根目录）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 测试用例执行文件所在路径
CASE_DIR = os.path.join(BASE_DIR, 'test_script')

# 测试数据所在路径
DATA_DIR = os.path.join(BASE_DIR, 'test_data')
DATA_FILE = os.path.join(DATA_DIR, '*.yaml')

# log所在路径
LOG_DIR = os.path.join(BASE_DIR, 'logs')
INFO_FILE = os.path.join(LOG_DIR, 'info.log')
ERROR_FILE = os.path.join(LOG_DIR, 'error.log')

# 配置文件所在路径
CONF_DIR = os.path.join(BASE_DIR, 'config')
CONF_FILE = os.path.join(CONF_DIR, 'config.ini')

# 测试报告路径
REPORT_DIR = os.path.join(BASE_DIR, 'reports')


def get_test_data_path(filename):
    """
    获取测试数据文件的完整路径

    Args:
        filename: 数据文件名（如 'add_header.yaml'）

    Returns:
        str: 完整的文件路径
    """
    return os.path.join(DATA_DIR, filename)


def get_config_path(filename='config.ini'):
    """
    获取配置文件的完整路径

    Args:
        filename: 配置文件名，默认为 'config.ini'

    Returns:
        str: 完整的文件路径
    """
    return os.path.join(CONF_DIR, filename)


def get_log_path(filename):
    """
    获取日志文件的完整路径

    Args:
        filename: 日志文件名

    Returns:
        str: 完整的文件路径
    """
    return os.path.join(LOG_DIR, filename)
