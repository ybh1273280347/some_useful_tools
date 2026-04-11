#!/usr/bin/env python3
"""
代码格式化脚本
使用 isort 排序导入，然后使用 black 格式化代码
"""

import argparse
import subprocess
import sys


def run_command(cmd):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        return result
    except Exception as e:
        print(f"执行命令失败: {e}")
        return None


def format_code(path):
    """格式化指定路径的代码"""
    print(f"正在格式化: {path}")

    # 首先运行 isort 排序导入
    print("运行 isort...")
    isort_cmd = ["python", "-m", "isort", path]
    isort_result = run_command(isort_cmd)

    if isort_result and isort_result.returncode != 0:
        print(f"isort 失败: {isort_result.stderr}")
        return False

    # 然后运行 black 格式化代码
    print("运行 black...")
    black_cmd = ["python", "-m", "black", path]
    black_result = run_command(black_cmd)

    if black_result and black_result.returncode != 0:
        print(f"black 失败: {black_result.stderr}")
        return False

    print("格式化完成！")
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="使用 isort 和 black 格式化 Python 代码"
    )
    parser.add_argument(
        "path", nargs="?", default=".", help="要格式化的文件或目录路径 (默认: 当前目录)"
    )
    parser.add_argument("--check", action="store_true", help="只检查格式，不修改文件")

    args = parser.parse_args()

    # 检查依赖
    print("检查依赖...")
    dependencies = ["isort", "black"]
    for dep in dependencies:
        result = run_command(["python", "-m", "pip", "show", dep])
        if result and result.returncode != 0:
            print(f"安装 {dep}...")
            install_result = run_command(["python", "-m", "pip", "install", dep])
            if install_result and install_result.returncode != 0:
                print(f"安装 {dep} 失败: {install_result.stderr}")
                return 1

    # 格式化代码
    if args.check:
        # 只检查格式
        print("检查格式...")
        isort_cmd = ["python", "-m", "isort", "--check", args.path]
        black_cmd = ["python", "-m", "black", "--check", args.path]

        isort_result = run_command(isort_cmd)
        black_result = run_command(black_cmd)

        if isort_result and isort_result.returncode != 0:
            print(f"isort 检查失败: {isort_result.stdout}")
            return 1

        if black_result and black_result.returncode != 0:
            print(f"black 检查失败: {black_result.stdout}")
            return 1

        print("格式检查通过！")
        return 0
    else:
        # 执行格式化
        success = format_code(args.path)
        return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
