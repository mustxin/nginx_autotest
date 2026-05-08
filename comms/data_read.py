"""
数据读取工具模块
封装YAML和配置文件读取逻辑
"""

import os
import yaml
import configparser
from .platform_utils import get_default_nginx_paths, get_platform


def read_yaml(file_path):
    """
    读取YAML测试数据文件

    Args:
        file_path: YAML文件路径

    Returns:
        dict: 解析后的数据字典

    Raises:
        FileNotFoundError: 文件不存在
        yaml.YAMLError: YAML格式错误
    """
    # 如果传入的是相对路径，转换为绝对路径
    if not os.path.isabs(file_path):
        # 获取当前文件所在目录（common/）的父目录（框架根目录）
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, file_path)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"YAML文件不存在: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = yaml.safe_load(f)
            if data is None:
                return {}
            return data
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"YAML格式错误，请检查文件: {file_path}\n错误信息: {str(e)}")


def read_config(section, option, config_file='config/config.ini'):
    """
    读取config.ini配置文件中的配置项

    支持跨平台：如果配置项不存在，则使用当前平台的默认值

    Args:
        section: 配置节名称（如 'nginx', 'test_env', 'report'）
        option: 配置项名称（如 'nginx_path', 'backup_path'）
        config_file: 配置文件路径，默认为 'config/config.ini'

    Returns:
        str: 配置项的值

    Raises:
        FileNotFoundError: 配置文件不存在
        configparser.NoSectionError: 配置节不存在
        configparser.NoOptionError: 配置项不存在（仅当没有平台默认值时）
    """
    # 如果传入的是相对路径，转换为绝对路径
    if not os.path.isabs(config_file):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_file = os.path.join(base_dir, config_file)

    if not os.path.exists(config_file):
        raise FileNotFoundError(f"配置文件不存在: {config_file}")

    config = configparser.ConfigParser()
    config.read(config_file, encoding='utf-8')

    # 如果是 nginx 相关配置，检查是否存在；如果不存在，使用平台默认值
    if section == 'nginx' and option in get_default_nginx_paths():
        if not config.has_section(section) or not config.has_option(section, option):
            # 使用平台默认值
            default_paths = get_default_nginx_paths()
            return default_paths.get(option)

    if not config.has_section(section):
        raise configparser.NoSectionError(f"配置节不存在: {section}")

    if not config.has_option(section, option):
        raise configparser.NoOptionError(option, section)

    return config.get(section, option)
