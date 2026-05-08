"""
跨平台配置适配模块
自动检测操作系统并提供相应的默认配置
"""

import os
import platform
import sys


def get_platform():
    """
    获取当前操作系统平台

    Returns:
        str: 'windows', 'linux', 或 'darwin' (macOS)
    """
    system = platform.system().lower()
    if system == 'windows':
        return 'windows'
    elif system == 'linux':
        return 'linux'
    elif system == 'darwin':
        return 'darwin'
    else:
        return 'unknown'


def is_windows():
    """检查是否为 Windows 系统"""
    return get_platform() == 'windows'


def is_linux():
    """检查是否为 Linux 系统"""
    return get_platform() == 'linux'


def is_macos():
    """检查是否为 macOS 系统"""
    return get_platform() == 'darwin'


def get_default_nginx_paths():
    """
    获取当前平台的默认 Nginx 路径

    Returns:
        dict: 包含 nginx_path, nginx_bin_path, backup_path, error_log_path 的字典
    """
    plat = get_platform()

    if plat == 'windows':
        # Windows 默认路径
        return {
            'nginx_path': r'D:\Tools\nginx-1.30.0\conf\nginx.conf',
            'nginx_bin_path': r'D:\Tools\nginx-1.30.0\nginx.exe',
            'backup_path': r'D:\Tools\nginx-1.30.0\backup',
            'error_log_path': r'D:\Tools\nginx-1.30.0\logs\error.log',
        }
    elif plat == 'darwin':
        # macOS 默认路径 (Homebrew 安装)
        return {
            'nginx_path': '/usr/local/etc/nginx/nginx.conf',
            'nginx_bin_path': '/usr/local/bin/nginx',
            'backup_path': '/usr/local/etc/nginx/backup/',
            'error_log_path': '/usr/local/var/log/nginx/error.log',
        }
    else:
        # Linux 默认路径
        return {
            'nginx_path': '/etc/nginx/nginx.conf',
            'nginx_bin_path': '/usr/sbin/nginx',
            'backup_path': '/etc/nginx/backup/',
            'error_log_path': '/var/log/nginx/error.log',
        }


def get_nginx_restart_commands():
    """
    获取当前平台的 Nginx 重启命令列表

    Returns:
        list: 重启命令列表
    """
    plat = get_platform()

    if plat == 'windows':
        return [
            "systemctl restart nginx",
            "service nginx restart",
            "/etc/init.d/nginx restart",
        ]
    else:
        # Linux/macOS
        return [
            "sudo systemctl restart nginx",
            "sudo service nginx restart",
            "sudo /etc/init.d/nginx restart",
            "sudo nginx -s stop && sudo nginx",
        ]


def adapt_path_for_platform(path):
    """
    将路径适配为当前平台的格式

    Args:
        path: 原始路径

    Returns:
        str: 适配后的路径
    """
    if not path:
        return path

    plat = get_platform()

    if plat == 'windows':
        # Windows: 确保使用反斜杠
        return path.replace('/', '\\')
    else:
        # Linux/macOS: 确保使用正斜杠
        return path.replace('\\', '/')


def check_nginx_installed():
    """
    检查 Nginx 是否已安装

    Returns:
        tuple: (是否安装, 版本信息或错误信息)
    """
    import subprocess

    try:
        if is_windows():
            result = subprocess.run(['nginx', '-v'], capture_output=True, text=True, shell=True)
        else:
            result = subprocess.run(['nginx', '-v'], capture_output=True, text=True)

        if result.returncode == 0:
            return True, result.stderr.strip()  # nginx -v 输出到 stderr
        else:
            return False, result.stderr.strip()
    except FileNotFoundError:
        return False, "Nginx 未找到，请确保 Nginx 已安装并添加到系统 PATH"
    except Exception as e:
        return False, str(e)


def get_platform_info():
    """
    获取详细的平台信息

    Returns:
        dict: 包含平台详细信息的字典
    """
    return {
        'system': platform.system(),
        'platform': get_platform(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': sys.version,
    }


# 便捷函数：获取当前平台的 nginx 工作目录
def get_nginx_cwd(nginx_bin_path):
    """
    获取 Nginx 命令执行时的工作目录

    Args:
        nginx_bin_path: Nginx 可执行文件路径

    Returns:
        str: 工作目录路径，Windows 下需要返回 nginx 安装目录
    """
    if is_windows():
        return os.path.dirname(nginx_bin_path)
    return None  # Linux/macOS 不需要特别设置工作目录
