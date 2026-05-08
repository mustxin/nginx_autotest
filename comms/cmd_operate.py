"""
命令执行工具模块
封装系统命令执行，捕获输出和异常
"""

import subprocess


def run_cmd(cmd, timeout=30, shell=True, cwd=None):
    """
    执行指定命令，返回命令输出结果

    Args:
        cmd: 要执行的命令字符串
        timeout: 命令执行超时时间（秒），默认30秒
        shell: 是否使用shell执行，默认为True
        cwd: 命令执行的工作目录，默认为None（当前目录）

    Returns:
        str: 命令的输出结果（stdout + stderr）

    Raises:
        subprocess.TimeoutExpired: 命令执行超时
        subprocess.SubprocessError: 命令执行失败
    """
    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8',
            errors='replace',
            cwd=cwd
        )

        # 合并stdout和stderr
        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += "\n" + result.stderr if output else result.stderr

        return output.strip()

    except subprocess.TimeoutExpired as e:
        raise subprocess.TimeoutExpired(
            cmd, timeout,
            f"命令执行超时（超过{timeout}秒）: {cmd}\n部分输出: {e.stdout if e.stdout else '无'}"
        )
    except Exception as e:
        raise subprocess.SubprocessError(f"命令执行失败: {cmd}\n错误信息: {str(e)}")


def check_cmd_result(cmd, expected, timeout=30):
    """
    执行命令并检查输出是否包含预期结果

    Args:
        cmd: 要执行的命令字符串
        expected: 预期的结果字符串或字符串列表
        timeout: 命令执行超时时间（秒），默认30秒

    Returns:
        tuple: (是否匹配, 实际输出)

    Raises:
        subprocess.TimeoutExpired: 命令执行超时
        subprocess.SubprocessError: 命令执行失败
    """
    output = run_cmd(cmd, timeout)

    if isinstance(expected, str):
        expected_list = [expected]
    else:
        expected_list = expected

    for exp in expected_list:
        if exp not in output:
            return False, output

    return True, output


def run_cmd_with_code(cmd, timeout=30, shell=True, cwd=None):
    """
    执行命令并返回返回码和输出

    Args:
        cmd: 要执行的命令字符串
        timeout: 命令执行超时时间（秒），默认30秒
        shell: 是否使用shell执行，默认为True
        cwd: 命令执行的工作目录，默认为None（当前目录）

    Returns:
        tuple: (返回码, 输出结果)
    """
    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8',
            errors='replace',
            cwd=cwd
        )

        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += "\n" + result.stderr if output else result.stderr

        return result.returncode, output.strip()

    except subprocess.TimeoutExpired:
        return -1, f"命令执行超时（超过{timeout}秒）: {cmd}"
    except Exception as e:
        return -1, f"命令执行失败: {cmd}\n错误信息: {str(e)}"
