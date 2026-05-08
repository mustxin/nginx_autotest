"""
server块测试脚本
负责执行server块相关的测试用例
"""

import os
import pytest
from comms.constants import get_test_data_path
from comms.data_read import read_yaml, read_config
from comms.nginx_operate import (
    add_nginx_config,
    check_nginx_config,
    reload_nginx,
    restart_nginx,
    read_nginx_error_log,
)
from comms.cmd_operate import run_cmd


# 读取测试数据
test_data = read_yaml(get_test_data_path("server.yaml"))

# 读取Nginx配置路径
try:
    nginx_path = read_config("nginx", "nginx_path")
    nginx_bin_path = read_config("nginx", "nginx_bin_path")
    nginx_cwd = os.path.dirname(nginx_bin_path)
except Exception as e:
    print(f"警告: 读取Nginx配置路径失败，使用默认路径。错误: {str(e)}")
    nginx_path = "/etc/nginx/nginx.conf"
    nginx_cwd = None


@pytest.mark.parametrize("case_id, case_info", test_data.items())
def test_server(case_id, case_info):
    """
    server块自动化测试用例

    Args:
        case_id: 用例ID
        case_info: 用例信息字典
    """
    print(f"\n{'-' * 60}")
    print(f"执行用例: {case_id}")
    print(f"测试目的: {case_info['test_purpose']}")
    print(f"{'-' * 60}")

    # 打印前置条件
    print("前置条件:")
    for condition in case_info["pre_condition"]:
        print(f"  - {condition}")

    try:
        # 1. 添加Nginx测试配置
        print(f"\n[步骤1] 添加Nginx测试配置...")
        add_nginx_config(nginx_path, case_info["config_content"])
        print("[OK] 配置添加成功")

        # 2. 检查Nginx配置语法
        print(f"\n[步骤2] 检查Nginx配置语法...")
        success, output = check_nginx_config()
        print(f"输出: {output}")
        if not success:
            raise AssertionError(f"Nginx配置语法检查失败: {output}")
        print("[OK] 配置语法检查通过")

        # 3. 重新加载Nginx配置
        print(f"\n[步骤3] 重新加载Nginx配置...")
        success, output = reload_nginx()
        if not success:
            print(f"警告: Nginx重新加载失败: {output}")
            # 尝试重启
            success, output = restart_nginx()
            if not success:
                raise AssertionError(f"Nginx重启失败: {output}")
        print("[OK] Nginx配置重新加载成功")

        # 4. 执行测试命令
        print(f"\n[步骤4] 执行测试命令...")
        all_output = ""
        for cmd in case_info["operate_commands"]:
            print(f"  执行: {cmd}")
            # Nginx命令需要使用完整路径并在Nginx目录下执行
            if cmd.strip().startswith("nginx "):
                # 使用完整路径替换 'nginx'
                full_nginx_bin = read_config("nginx", "nginx_bin_path")
                cmd = cmd.replace("nginx ", f'"{full_nginx_bin}" ')
                result = run_cmd(cmd, cwd=nginx_cwd)
            else:
                result = run_cmd(cmd)
            all_output += result + "\n"
            print(f"  输出: {result[:200]}..." if len(result) > 200 else f"  输出: {result}")

        # 5. 验证结果
        print(f"\n[步骤5] 验证预期结果...")
        for expected in case_info["expected_result"]:
            assert expected in all_output, f"结果验证失败！预期包含: {expected}"
        print("[OK] 所有预期结果验证通过")

        print(f"\n[OK] 用例 {case_id} 执行成功！")

    except AssertionError as e:
        print(f"\n[FAIL] 用例 {case_id} 断言失败: {str(e)}")
        raise

    except Exception as e:
        print(f"\n[FAIL] 用例 {case_id} 执行异常: {str(e)}")
        # 读取Nginx错误日志，辅助排查
        try:
            error_log = read_nginx_error_log(10)
            print(f"\nNginx错误日志（最新10行）:\n{error_log}")
        except Exception as log_error:
            print(f"读取Nginx错误日志失败: {str(log_error)}")
        raise
