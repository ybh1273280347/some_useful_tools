#!/usr/bin/env python3
"""
静态代码分析脚本
使用 flake8 检查代码质量
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


def run_flake8(path, verbose=False):
    """运行 flake8 检查"""
    print(f"正在检查: {path}")

    # 构建 flake8 命令
    flake8_cmd = ["python", "-m", "flake8"]

    # 添加详细输出
    if verbose:
        flake8_cmd.append("--verbose")

    # 添加检查路径
    flake8_cmd.append(path)

    # 运行检查
    print(f"执行命令: {' '.join(flake8_cmd)}")
    result = run_command(flake8_cmd)

    if result:
        print("检查结果:")
        print(result.stdout)

        if result.stderr:
            print("错误输出:")
            print(result.stderr)

        return result.returncode == 0

    return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="使用 flake8 检查代码质量")
    parser.add_argument(
        "path", nargs="?", default=".", help="要检查的文件或目录路径 (默认: 当前目录)"
    )
    parser.add_argument("--verbose", action="store_true", help="显示详细检查输出")

    args = parser.parse_args()

    # 检查依赖
    print("检查依赖...")
    dependencies = ["flake8"]
    for dep in dependencies:
        result = run_command(["python", "-m", "pip", "show", dep])
        if result and result.returncode != 0:
            print(f"安装 {dep}...")
            install_result = run_command(["python", "-m", "pip", "install", dep])
            if install_result and install_result.returncode != 0:
                print(f"安装 {dep} 失败: {install_result.stderr}")
                return 1

    # 运行检查
    success = run_flake8(args.path, verbose=args.verbose)

    if success:
        print("代码质量检查通过！")
        return 0
    else:
        print("代码质量检查失败！")
        return 1


if __name__ == "__main__":
    sys.exit(main())
