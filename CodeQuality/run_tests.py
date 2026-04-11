#!/usr/bin/env python3
"""
自动化测试脚本
使用 pytest 运行测试并生成覆盖率报告
"""

import os
import sys
import subprocess
import argparse


def run_command(cmd):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        return result
    except Exception as e:
        print(f"执行命令失败: {e}")
        return None


def run_tests(test_path, coverage=False, verbose=False):
    """运行测试"""
    print(f"正在运行测试: {test_path}")
    
    # 构建 pytest 命令
    pytest_cmd = ["python", "-m", "pytest"]
    
    # 添加详细输出
    if verbose:
        pytest_cmd.append("-v")
    
    # 添加覆盖率报告
    if coverage:
        pytest_cmd.extend(["--cov", "--cov-report", "term-missing"])
    
    # 添加测试路径
    pytest_cmd.append(test_path)
    
    # 运行测试
    print(f"执行命令: {' '.join(pytest_cmd)}")
    result = run_command(pytest_cmd)
    
    if result:
        print("测试结果:")
        print(result.stdout)
        
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
        
        return result.returncode == 0
    
    return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="使用 pytest 运行测试")
    parser.add_argument("path", nargs="?", default=".", help="测试文件或目录路径 (默认: 当前目录)")
    parser.add_argument("--coverage", action="store_true", help="生成测试覆盖率报告")
    parser.add_argument("--verbose", action="store_true", help="显示详细测试输出")
    
    args = parser.parse_args()
    
    # 检查依赖
    print("检查依赖...")
    dependencies = ["pytest"]
    if args.coverage:
        dependencies.append("pytest-cov")
    
    for dep in dependencies:
        result = run_command(["python", "-m", "pip", "show", dep])
        if result and result.returncode != 0:
            print(f"安装 {dep}...")
            install_result = run_command(["python", "-m", "pip", "install", dep])
            if install_result and install_result.returncode != 0:
                print(f"安装 {dep} 失败: {install_result.stderr}")
                return 1
    
    # 运行测试
    success = run_tests(args.path, coverage=args.coverage, verbose=args.verbose)
    
    if success:
        print("测试通过！")
        return 0
    else:
        print("测试失败！")
        return 1


if __name__ == "__main__":
    sys.exit(main())