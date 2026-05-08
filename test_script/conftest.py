"""
全局夹具模块（conftest.py）
封装所有测试用例的公共前置/后置操作
"""

import pytest
from comms.constants import DATA_FILE, CONF_FILE
from comms.data_read import read_yaml, read_config
from comms.nginx_operate import (
    add_nginx_config,
    check_nginx_config,
    reload_nginx,
    read_nginx_error_log,
    backup_nginx_config,
    restore_nginx_config,
)


@pytest.fixture(scope="session", autouse=True)
def global_fixture():
    """
    全局前置/后置操作：
    - 所有用例执行前，备份Nginx原始配置
    - 所有用例执行完成后，恢复Nginx原始配置
    """
    print("\n" + "=" * 60)
    print("=== 开始Nginx白盒自动化测试 ===")
    print("=" * 60)

    # 前置操作：备份配置
    try:
        backup_path = backup_nginx_config()
        print(f"[OK] Nginx配置已备份: {backup_path}")
    except Exception as e:
        print(f"[WARN] 警告: Nginx配置备份失败: {str(e)}")
        print("   建议手动备份后再执行测试！")

    yield  # 执行测试用例

    # 后置操作：恢复配置
    print("\n" + "=" * 60)
    print("=== 测试执行完毕，开始清理 ===")
    print("=" * 60)

    try:
        restore_nginx_config()
        print("[OK] Nginx配置已恢复")
    except Exception as e:
        print(f"[ERROR] 错误: Nginx配置恢复失败: {str(e)}")
        print("   请手动恢复Nginx配置！")

    print("=" * 60)
    print("=== 测试会话结束 ===")
    print("=" * 60)


@pytest.fixture(scope="module", autouse=True)
def module_fixture():
    """
    模块级前置/后置操作
    每个测试模块执行前后调用：
    - 前置：恢复到原始配置
    - 后置：恢复到原始配置
    """
    print(f"\n--- 开始执行当前模块测试 ---")
    # 模块前置：恢复原始配置
    try:
        restore_nginx_config()
        reload_nginx()
    except Exception:
        pass

    yield

    # 模块后置：恢复配置
    try:
        restore_nginx_config()
        reload_nginx()
    except Exception:
        pass

    print(f"\n--- 当前模块测试执行完成 ---")


@pytest.fixture(scope="function")
def case_fixture():
    """
    用例级前置/后置操作（可选）
    每个测试用例执行前后调用
    """
    # 用例前置操作
    yield
    # 用例后置操作
    # 可以在这里添加用例级别的清理操作
