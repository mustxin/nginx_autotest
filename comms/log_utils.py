"""
日志工具模块
统一日志输出到文件，不干扰终端显示
"""
import logging
from comms.constants import LOG_DIR, INFO_FILE, ERROR_FILE

_logger = None


def get_logger():
    global _logger
    if _logger is not None:
        return _logger

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    _logger = logging.getLogger("nginx_autotest")
    _logger.setLevel(logging.DEBUG)

    sh2 = logging.FileHandler(filename=INFO_FILE, mode='a', encoding='utf-8')
    sh2.setLevel(logging.INFO)

    sh3 = logging.FileHandler(filename=ERROR_FILE, mode='a', encoding='utf-8')
    sh3.setLevel(logging.ERROR)

    fmt_str = '%(asctime)s - [%(filename)s - %(lineno)d] - %(levelname)s:%(message)s'
    my_fmt = logging.Formatter(fmt_str)

    for handler in (sh2, sh3):
        handler.setFormatter(my_fmt)
        _logger.addHandler(handler)

    return _logger


logger = get_logger()
