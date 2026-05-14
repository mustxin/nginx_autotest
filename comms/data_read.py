"""
数据读取工具模块
封装YAML和配置文件读取逻辑
"""

from pathlib import Path

import yaml
import configparser

_BASE_DIR = Path(__file__).resolve().parent.parent
_DEFAULT_CONFIG = _BASE_DIR / "config" / "config.ini"


def read_yaml(file_path):
    """
    读取YAML测试数据文件

    Args:
        file_path: YAML文件路径（绝对路径或相对于项目根目录的路径）

    Returns:
        dict: 解析后的数据字典
    """
    path = Path(file_path)
    if not path.is_absolute():
        path = _BASE_DIR / path

    if not path.exists():
        raise FileNotFoundError(f"YAML文件不存在: {path}")

    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
        return data if data is not None else {}


def read_config(section, option, config_file=None):
    """
    读取config.ini配置文件中的配置项

    Args:
        section: 配置节名称（如 'nginx'）
        option: 配置项名称（如 'nginx_path'）
        config_file: 配置文件路径，默认为 config/config.ini

    Returns:
        str: 配置项的值
    """
    path = Path(config_file) if config_file else _DEFAULT_CONFIG
    if not path.is_absolute():
        path = _BASE_DIR / path

    if not path.exists():
        raise FileNotFoundError(f"配置文件不存在: {path}")

    config = configparser.ConfigParser()
    config.read(path, encoding='utf-8')

    if not config.has_section(section):
        raise configparser.NoSectionError(section)

    if not config.has_option(section, option):
        raise configparser.NoOptionError(option, section)

    return config.get(section, option)
