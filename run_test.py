#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nginx白盒测试自动化框架 - 一键执行入口
小白仅需运行此文件，即可一键执行所有测试用例
"""

import os
import sys
import pytest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from comms.data_read import read_config


def main():
    """主函数：读取配置并执行pytest"""

    # 读取报告配置
    try:
        report_path = read_config("report", "report_path")
        report_name = read_config("report", "report_name")
    except Exception as e:
        print(f"警告: 读取报告配置失败，使用默认配置。错误: {str(e)}")
        report_path = "./reports/"
        report_name = "report.html"

    # 获取框架根目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_report_path = os.path.join(base_dir, report_path, report_name)

    # 确保报告目录存在
    full_report_dir = os.path.dirname(full_report_path)
    if not os.path.exists(full_report_dir):
        os.makedirs(full_report_dir)
        print(f"创建报告目录: {full_report_dir}")

    # 测试脚本目录
    test_script_dir = os.path.join(base_dir, "test_script")

    # 检查测试脚本目录是否存在
    if not os.path.exists(test_script_dir):
        print(f"错误: 测试脚本目录不存在: {test_script_dir}")
        print("请确保 test_script/ 目录存在且包含测试脚本文件")
        sys.exit(1)

    # 执行pytest，生成测试报告
    print("=" * 60)
    print("=== 开始执行Nginx白盒自动化测试 ===")
    print("=" * 60)
    print(f"测试脚本目录: {test_script_dir}")
    print(f"测试报告将生成至: {full_report_path}")
    print("-" * 60)

    # pytest执行命令参数
    pytest_args = [
        test_script_dir,           # 执行所有测试脚本
        f"--html={full_report_path}",  # 生成HTML报告
        "--self-contained-html",   # 生成独立HTML文件（包含CSS）
        "-v",                      # 显示详细日志
        "--tb=short",              # 简化报错信息
        "--strict-markers",        # 严格检查marker
    ]

    # 执行pytest
    exit_code = pytest.main(pytest_args)

    print("-" * 60)
    if exit_code == 0:
        print("[OK] 所有测试用例执行通过！")
    elif exit_code == 1:
        print("[FAIL] 部分测试用例执行失败！")
    elif exit_code == 2:
        print("⚠️ 测试执行被中断！")
    elif exit_code == 3:
        print("[FAIL] 测试执行发生内部错误！")
    elif exit_code == 4:
        print("⚠️ pytest命令使用错误！")
    elif exit_code == 5:
        print("⚠️ 未找到任何测试用例！")
    else:
        print(f"⚠️ 测试执行完成，退出码: {exit_code}")

    print("=" * 60)
    print(f"=== 测试执行完成！测试报告已生成：{full_report_path} ===")
    print("=" * 60)
    print("提示：")
    print("  1. 打开HTML报告，可查看详细执行结果（通过/失败/错误）")
    print("  2. 失败用例会显示错误信息和Nginx日志，可对照排查")
    print("  3. 测试完成后，Nginx配置会自动恢复")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
