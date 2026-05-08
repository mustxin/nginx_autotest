"""
comms 工具包
提供Nginx自动化测试框架的基础工具模块
"""

from comms.constants import (
    BASE_DIR,
    CASE_DIR,
    DATA_DIR,
    DATA_FILE,
    LOG_DIR,
    INFO_FILE,
    ERROR_FILE,
    CONF_DIR,
    CONF_FILE,
    REPORT_DIR,
    get_test_data_path,
    get_config_path,
    get_log_path,
)
from comms.data_read import read_yaml, read_config
from comms.nginx_operate import (
    add_nginx_config,
    check_nginx_config,
    reload_nginx,
    restart_nginx,
    read_nginx_error_log,
    backup_nginx_config,
    restore_nginx_config,
)
from comms.cmd_operate import run_cmd
from comms.log_utils import logger

__all__ = [
    # 路径常量
    'BASE_DIR',
    'CASE_DIR',
    'DATA_DIR',
    'DATA_FILE',
    'LOG_DIR',
    'INFO_FILE',
    'ERROR_FILE',
    'CONF_DIR',
    'CONF_FILE',
    'REPORT_DIR',
    # 路径工具函数
    'get_test_data_path',
    'get_config_path',
    'get_log_path',
    # 数据读取
    'read_yaml',
    'read_config',
    # Nginx操作
    'add_nginx_config',
    'check_nginx_config',
    'reload_nginx',
    'restart_nginx',
    'read_nginx_error_log',
    'backup_nginx_config',
    'restore_nginx_config',
    # 命令操作
    'run_cmd',
    # 日志
    'logger',
]
