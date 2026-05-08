"""
Nginx操作工具模块
封装Nginx核心操作：备份、恢复、检查配置、重启等
"""

import os
import shutil
import time
from .data_read import read_config
from .cmd_operate import run_cmd, run_cmd_with_code
from .platform_utils import (
    get_platform,
    is_windows,
    is_linux,
    is_macos,
    get_nginx_restart_commands,
    get_nginx_cwd,
)


# 全局变量，存储备份文件路径
_backup_file_path = None


def backup_nginx_config():
    """
    备份Nginx原始配置（测试前置操作）

    Returns:
        str: 备份文件路径

    Raises:
        FileNotFoundError: Nginx配置文件不存在
        Exception: 备份失败
    """
    global _backup_file_path

    try:
        nginx_path = read_config("nginx", "nginx_path")
        backup_dir = read_config("nginx", "backup_path")
    except Exception as e:
        # 使用平台默认路径
        from .platform_utils import get_default_nginx_paths
        defaults = get_default_nginx_paths()
        nginx_path = defaults['nginx_path']
        backup_dir = defaults['backup_path']
        print(f"警告: 读取配置失败，使用平台默认路径。错误: {str(e)}")

    # 确保Nginx配置文件存在
    if not os.path.exists(nginx_path):
        raise FileNotFoundError(f"Nginx配置文件不存在: {nginx_path}")

    # 确保备份目录存在
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    # 生成带时间戳的备份文件名
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_filename = f"nginx_backup_{timestamp}.conf"
    _backup_file_path = os.path.join(backup_dir, backup_filename)

    try:
        shutil.copy2(nginx_path, _backup_file_path)
        print(f"[OK] Nginx配置已备份至: {_backup_file_path}")
        return _backup_file_path
    except Exception as e:
        raise Exception(f"备份Nginx配置失败: {str(e)}")


def restore_nginx_config():
    """
    恢复Nginx原始配置（测试后置操作）

    Returns:
        bool: 是否恢复成功

    Raises:
        Exception: 恢复失败
    """
    global _backup_file_path

    if _backup_file_path is None or not os.path.exists(_backup_file_path):
        # 尝试从备份目录中找最新的备份
        try:
            backup_dir = read_config("nginx", "backup_path")
        except Exception:
            from .platform_utils import get_default_nginx_paths
            backup_dir = get_default_nginx_paths()['backup_path']

        if os.path.exists(backup_dir):
            backup_files = [
                f for f in os.listdir(backup_dir)
                if f.startswith("nginx_backup_") and f.endswith(".conf")
            ]
            if backup_files:
                # 按修改时间排序，取最新的
                backup_files.sort(key=lambda x: os.path.getmtime(
                    os.path.join(backup_dir, x)), reverse=True)
                _backup_file_path = os.path.join(backup_dir, backup_files[0])

    if _backup_file_path is None or not os.path.exists(_backup_file_path):
        print("警告: 未找到备份文件，无法恢复Nginx配置")
        return False

    try:
        nginx_path = read_config("nginx", "nginx_path")
    except Exception:
        from .platform_utils import get_default_nginx_paths
        nginx_path = get_default_nginx_paths()['nginx_path']

    try:
        shutil.copy2(_backup_file_path, nginx_path)
        print(f"[OK] Nginx配置已从 {_backup_file_path} 恢复")

        # 恢复后重新加载Nginx
        reload_nginx()

        return True
    except Exception as e:
        raise Exception(f"恢复Nginx配置失败: {str(e)}")


def check_nginx_config():
    """
    执行nginx -t，检查配置语法

    Returns:
        tuple: (是否成功, 输出信息)
    """
    try:
        nginx_bin = read_config("nginx", "nginx_bin_path")
        nginx_path = read_config("nginx", "nginx_path")
    except Exception:
        # 使用平台默认值
        from .platform_utils import get_default_nginx_paths
        defaults = get_default_nginx_paths()
        nginx_bin = defaults['nginx_bin_path']
        nginx_path = defaults['nginx_path']

    # 获取Nginx安装目录作为工作目录（Windows需要）
    nginx_cwd = get_nginx_cwd(nginx_bin)

    cmd = f'"{nginx_bin}" -t -c "{nginx_path}"'
    returncode, output = run_cmd_with_code(cmd, cwd=nginx_cwd)

    return returncode == 0, output


def reload_nginx():
    """
    重新加载Nginx配置（nginx -s reload）

    Returns:
        tuple: (是否成功, 输出信息)
    """
    try:
        nginx_bin = read_config("nginx", "nginx_bin_path")
    except Exception:
        # 使用平台默认值
        from .platform_utils import get_default_nginx_paths
        defaults = get_default_nginx_paths()
        nginx_bin = defaults['nginx_bin_path']

    # 获取Nginx安装目录作为工作目录（Windows需要）
    nginx_cwd = get_nginx_cwd(nginx_bin)

    # Linux/macOS 可能需要 sudo
    if is_linux() or is_macos():
        cmd = f'sudo "{nginx_bin}" -s reload'
    else:
        cmd = f'"{nginx_bin}" -s reload'

    returncode, output = run_cmd_with_code(cmd, cwd=nginx_cwd)

    return returncode == 0, output


def restart_nginx():
    """
    重启Nginx服务

    Returns:
        tuple: (是否成功, 输出信息)

    Note:
        根据不同系统，使用不同的重启命令
    """
    # 获取平台特定的重启命令
    restart_cmds = get_nginx_restart_commands()

    try:
        nginx_bin = read_config("nginx", "nginx_bin_path")
        # Windows 下需要完整路径
        if is_windows():
            restart_cmds.append(f'"{nginx_bin}" -s stop && "{nginx_bin}"')
        else:
            # Linux/macOS 下可能需要 sudo
            restart_cmds.append(f"sudo {nginx_bin} -s stop && sudo {nginx_bin}")
    except Exception:
        if is_windows():
            restart_cmds.append("nginx -s stop && nginx")
        else:
            restart_cmds.append("sudo nginx -s stop && sudo nginx")

    for cmd in restart_cmds:
        returncode, output = run_cmd_with_code(cmd, timeout=10)
        if returncode == 0:
            return True, output

    return False, f"Nginx重启失败，已尝试以下命令: {', '.join(restart_cmds)}"


def _is_server_block_config(config_content):
    """
    判断配置内容是否是 server 块

    Args:
        config_content: 配置内容字符串

    Returns:
        bool: 是否是 server 块配置
    """
    import re
    # 去除前导空白和注释后检查是否以 server { 开头
    lines = config_content.strip().split('\n')
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('#'):
            # 第一个非空非注释行
            return re.match(r'^[\s]*server\s*\{', stripped) is not None
    return False


def _find_http_block_end(content):
    """
    查找 http 块的结束位置（即最后一个 } 的位置）

    Args:
        content: Nginx配置文件内容

    Returns:
        int: http 块结束 } 的索引，如果没有找到返回 None
    """
    http_match = _find_block_range(content, 'http')
    if http_match is None:
        return None
    return http_match[1]  # 返回 } 的位置


def _find_http_block_start(content):
    """
    查找 http 块内容开始位置（即 http { 之后的位置）

    Args:
        content: Nginx配置文件内容

    Returns:
        int: http 块内容开始位置的索引，如果没有找到返回 None
    """
    http_match = _find_block_range(content, 'http')
    if http_match is None:
        return None

    # 找到 http { 后面的位置
    http_start = http_match[0]
    # 从 http_start 向后查找 { 的位置
    brace_pos = content.find('{', http_start)
    if brace_pos == -1:
        return None

    # 返回 { 之后的位置（下一行开始）
    return brace_pos + 1


def _remove_test_config(content):
    """
    移除之前添加的测试配置

    Args:
        content: Nginx配置文件内容

    Returns:
        str: 移除测试配置后的内容
    """
    import re
    # 匹配测试配置块并移除
    pattern = r'\n?\s*# ===== 自动化测试临时配置 =====\n.*?# ===== 自动化测试临时配置结束 =====\n?'
    return re.sub(pattern, '', content, flags=re.DOTALL)


def add_nginx_config(nginx_path, config_content):
    """
    向Nginx配置文件添加测试配置

    根据配置内容类型智能选择插入位置：
    - 如果配置内容是 server 块，则插入到 http 块内（不在另一个 server 块内）
    - 如果配置内容是 location 块或其他指令，则插入到最后一个 server 块内

    Args:
        nginx_path: Nginx配置文件路径
        config_content: 要添加的配置内容

    Returns:
        bool: 是否添加成功

    Raises:
        FileNotFoundError: Nginx配置文件不存在
        Exception: 写入失败
    """
    if not os.path.exists(nginx_path):
        raise FileNotFoundError(f"Nginx配置文件不存在: {nginx_path}")

    try:
        # 读取原始配置
        with open(nginx_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        # 移除之前可能残留的测试配置
        original_content = _remove_test_config(original_content)

        # 判断配置内容类型
        is_server_block = _is_server_block_config(config_content)

        if is_server_block:
            # 配置内容是 server 块，需要插入到 http 块开头（确保优先匹配）
            http_block_start = _find_http_block_start(original_content)
            if http_block_start is None:
                raise Exception("Nginx配置文件格式错误：未找到http块")

            insert_index = http_block_start
            test_config = f"""

# ===== 自动化测试临时配置 =====
{config_content}
# ===== 自动化测试临时配置结束 =====
"""
        else:
            # 配置内容是 location 块或其他指令，插入到最后一个 server 块内
            server_block_end = _find_last_server_block_end(original_content)

            if server_block_end is not None:
                # 在最后一个 server 块的 } 之前插入配置
                insert_index = server_block_end
                # 为配置内容添加缩进（8个空格，与 server 块内的其他指令对齐）
                indented_config = '\n'.join('        ' + line if line.strip() else line
                                              for line in config_content.split('\n'))
                test_config = f"""

        # ===== 自动化测试临时配置 =====
{indented_config}
        # ===== 自动化测试临时配置结束 =====
"""
            else:
                # 没有找到 server 块，在 http 块内创建一个新的 server 块
                http_block_end = _find_http_block_end(original_content)
                if http_block_end is None:
                    raise Exception("Nginx配置文件格式错误：未找到http块")

                insert_index = http_block_end
                # 为配置内容添加缩进（8个空格）
                indented_config = '\n'.join('        ' + line if line.strip() else line
                                              for line in config_content.split('\n'))
                test_config = f"""

    # ===== 自动化测试临时配置 =====
    server {{
        listen 80;
        server_name localhost;
{indented_config}
    }}
    # ===== 自动化测试临时配置结束 =====
"""

        # 插入测试配置
        new_content = (
            original_content[:insert_index] +
            test_config +
            original_content[insert_index:]
        )

        # 写回文件
        with open(nginx_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
            f.flush()
            import time
            time.sleep(0.1)

        print(f"[OK] 测试配置已添加至: {nginx_path}")
        return True

    except Exception as e:
        raise Exception(f"添加Nginx配置失败: {str(e)}")


def _find_last_server_block_end(content):
    """
    查找最后一个 server 块的结束位置（即最后一个 } 的位置）

    Args:
        content: Nginx配置文件内容

    Returns:
        int: 最后一个 server 块结束 } 的索引，如果没有找到返回 None
    """
    # 简单的括号匹配算法，找到最后一个 server 块
    # 从后向前查找 "server {" 然后匹配对应的 }

    # 先找到 http 块的范围
    http_match = _find_block_range(content, 'http')
    if http_match is None:
        return None

    http_start, http_end = http_match
    http_content = content[http_start:http_end]

    # 在 http 块内找最后一个 server 块
    server_match = _find_last_block_in_range(http_content, 'server')
    if server_match is None:
        return None

    # 返回在原始内容中的位置
    return http_start + server_match[1]


def _find_block_range(content, block_name):
    """
    查找指定配置块的范围

    Args:
        content: 配置内容
        block_name: 块名称，如 'http', 'server'

    Returns:
        tuple: (开始位置, 结束位置) 或 None
    """
    import re
    # 查找 block_name {，但排除注释行（行首有#）
    # 使用多行模式，确保 block_name 前面是行首或空白字符
    pattern = re.compile(r'^[ \t]*' + block_name + r'\s*\{', re.MULTILINE)
    match = pattern.search(content)
    if not match:
        return None

    start = match.start()
    brace_start = match.end() - 1  # { 的位置

    # 从 { 开始匹配到对应的 }
    brace_count = 0
    pos = brace_start
    while pos < len(content):
        if content[pos] == '{':
            brace_count += 1
        elif content[pos] == '}':
            brace_count -= 1
            if brace_count == 0:
                return (start, pos)  # 返回pos（}的位置），不是pos+1
        pos += 1

    return None


def _find_last_block_in_range(content, block_name):
    """
    在指定范围内查找最后一个配置块

    Args:
        content: 配置内容
        block_name: 块名称

    Returns:
        tuple: (开始位置, 结束位置) 或 None
    """
    import re
    # 使用多行模式，排除注释行（行首有#）
    pattern = re.compile(r'^[ \t]*' + block_name + r'\s*\{', re.MULTILINE)
    matches = list(pattern.finditer(content))

    if not matches:
        return None

    # 取最后一个匹配
    last_match = matches[-1]
    start = last_match.start()
    brace_start = last_match.end() - 1

    # 匹配对应的 }
    brace_count = 0
    pos = brace_start
    while pos < len(content):
        if content[pos] == '{':
            brace_count += 1
        elif content[pos] == '}':
            brace_count -= 1
            if brace_count == 0:
                return (start, pos)  # 返回pos（}的位置），不是pos+1
        pos += 1

    return None


def read_nginx_error_log(lines=10):
    """
    读取Nginx错误日志

    Args:
        lines: 读取最后多少行，默认10行

    Returns:
        str: 错误日志内容
    """
    try:
        error_log_path = read_config("nginx", "error_log_path")
    except Exception:
        from .platform_utils import get_default_nginx_paths
        error_log_path = get_default_nginx_paths()['error_log_path']

    if not os.path.exists(error_log_path):
        return f"错误日志文件不存在: {error_log_path}"

    try:
        # 使用tail命令读取最后N行
        cmd = f"tail -n {lines} {error_log_path}"
        return run_cmd(cmd)
    except Exception as e:
        # 如果tail命令失败，直接读取文件
        try:
            with open(error_log_path, 'r', encoding='utf-8', errors='replace') as f:
                all_lines = f.readlines()
                return ''.join(all_lines[-lines:])
        except Exception as e2:
            return f"读取错误日志失败: {str(e)}, {str(e2)}"


def get_nginx_version():
    """
    获取Nginx版本信息

    Returns:
        str: Nginx版本信息
    """
    try:
        nginx_bin = read_config("nginx", "nginx_bin_path")
    except Exception:
        from .platform_utils import get_default_nginx_paths
        nginx_bin = get_default_nginx_paths()['nginx_bin_path']

    cmd = f'"{nginx_bin}" -v'
    try:
        return run_cmd(cmd)
    except Exception as e:
        return f"获取Nginx版本失败: {str(e)}"
