"""
代码质量工具

集成多种代码质量工具，提供统一的命令行接口。

依赖：
- black: 代码格式化
- isort: 导入排序
- flake8: 代码检查
- mypy: 类型检查
- pytest: 测试运行
- pytest-cov: 测试覆盖率
- pylint: 代码分析
- pre-commit: 预提交钩子

安装：
pip install black isort flake8 mypy pytest pytest-cov pylint pre-commit
"""

import subprocess
from pathlib import Path
from typing import List, Optional


class CodeQualityTool:
    """
    代码质量工具类
    """

    def __init__(self, project_root: Optional[str] = None):
        """
        初始化代码质量工具

        Args:
            project_root: 项目根目录，默认当前目录
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()

    def _run_command(
        self, cmd: List[str], cwd: Optional[Path] = None
    ) -> subprocess.CompletedProcess:
        """
        运行命令

        Args:
            cmd: 命令列表
            cwd: 工作目录

        Returns:
            命令执行结果
        """
        cwd = cwd or self.project_root
        result = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8"
        )
        return result

    def format(self, paths: Optional[List[str]] = None) -> bool:
        """
        自动格式化代码

        Args:
            paths: 要格式化的文件/目录列表，默认整个项目

        Returns:
            是否成功
        """
        print("=== 开始格式化代码 ===")

        # 处理路径
        targets = paths or [str(self.project_root)]

        # 运行 isort 排序导入
        print("运行 isort...")
        result = self._run_command(["isort"] + targets)
        if result.returncode != 0:
            print(f"isort 失败: {result.stderr}")
            return False

        # 运行 black 格式化代码
        print("运行 black...")
        result = self._run_command(["black"] + targets)
        if result.returncode != 0:
            print(f"black 失败: {result.stderr}")
            return False

        print("格式化完成！")
        return True

    def check(self, paths: Optional[List[str]] = None) -> bool:
        """
        静态检查代码

        Args:
            paths: 要检查的文件/目录列表，默认整个项目

        Returns:
            是否通过检查
        """
        print("=== 开始静态检查 ===")

        # 处理路径
        targets = paths or [str(self.project_root)]

        # 运行 flake8 检查
        print("运行 flake8...")
        result = self._run_command(["flake8"] + targets)
        if result.returncode != 0:
            print(f"flake8 检查失败:\n{result.stdout}")
            return False

        # 运行 mypy 类型检查
        print("运行 mypy...")
        result = self._run_command(["mypy"] + targets)
        if result.returncode != 0:
            print(f"mypy 检查失败:\n{result.stdout}")
            return False

        print("静态检查通过！")
        return True

    def test(
        self, test_paths: Optional[List[str]] = None, cov_report: bool = True
    ) -> bool:
        """
        运行测试并生成覆盖率报告

        Args:
            test_paths: 测试文件/目录列表，默认 "tests" 目录
            cov_report: 是否生成覆盖率报告

        Returns:
            是否通过测试
        """
        print("=== 开始运行测试 ===")

        # 处理测试路径
        targets = test_paths or ["tests"]

        # 构建 pytest 命令
        cmd = ["pytest"]
        if cov_report:
            cmd.extend(
                [
                    "--cov",
                    str(self.project_root),
                    "--cov-report",
                    "term-missing",
                    "--cov-report",
                    "html:cov_html",
                ]
            )
        cmd.extend(targets)

        # 运行测试
        result = self._run_command(cmd)
        if result.returncode != 0:
            print(f"测试失败:\n{result.stdout}")
            return False

        print("测试通过！")
        if cov_report:
            print(f"覆盖率报告已生成到: {self.project_root / 'cov_html'}")
        return True

    def analyze(self, paths: Optional[List[str]] = None) -> bool:
        """
        代码分析（使用 pylint）

        Args:
            paths: 要分析的文件/目录列表，默认整个项目

        Returns:
            是否通过分析
        """
        print("=== 开始代码分析 ===")

        # 处理路径
        targets = paths or [str(self.project_root)]

        # 运行 pylint
        result = self._run_command(["pylint"] + targets)
        if result.returncode != 0:
            print(f"pylint 分析结果:\n{result.stdout}")
            return False

        print("代码分析通过！")
        return True

    def setup_pre_commit(self) -> bool:
        """
        设置预提交钩子

        Returns:
            是否成功
        """
        print("=== 设置预提交钩子 ===")

        # 创建 pre-commit 配置文件
        config_content = """
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files

-   repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
    -   id: isort

-   repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
    -   id: black

-   repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
    -   id: flake8

-   repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
    -   id: mypy
"""

        config_path = self.project_root / ".pre-commit-config.yaml"
        config_path.write_text(config_content)

        # 安装预提交钩子
        result = self._run_command(["pre-commit", "install"])
        if result.returncode != 0:
            print(f"预提交钩子安装失败: {result.stderr}")
            return False

        print("预提交钩子设置成功！")
        print("现在每次 git commit 前都会自动运行代码质量检查")
        return True

    def run_all(self, paths: Optional[List[str]] = None) -> bool:
        """
        运行所有代码质量检查

        Args:
            paths: 要检查的文件/目录列表，默认整个项目

        Returns:
            是否全部通过
        """
        print("=== 运行全部代码质量检查 ===")

        steps = [
            ("格式化", self.format),
            ("静态检查", self.check),
            ("测试", self.test),
            ("代码分析", self.analyze),
        ]

        all_passed = True
        for step_name, step_func in steps:
            print(f"\n--- {step_name} ---")
            if not step_func(paths):
                all_passed = False

        if all_passed:
            print("\n🎉 所有代码质量检查通过！")
        else:
            print("\n❌ 部分代码质量检查失败！")

        return all_passed


# 命令行接口
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="代码质量工具")
    parser.add_argument("--root", default=None, help="项目根目录")
    parser.add_argument("--paths", nargs="*", help="要处理的文件/目录列表")

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # format 命令
    subparsers.add_parser("format", help="格式化代码")

    # check 命令
    subparsers.add_parser("check", help="静态检查")

    # test 命令
    test_parser = subparsers.add_parser("test", help="运行测试")
    test_parser.add_argument("--no-cov", action="store_true", help="不生成覆盖率报告")
    test_parser.add_argument("test_paths", nargs="*", help="测试文件/目录")

    # analyze 命令
    subparsers.add_parser("analyze", help="代码分析")

    # setup 命令
    subparsers.add_parser("setup", help="设置预提交钩子")

    # all 命令
    subparsers.add_parser("all", help="运行所有检查")

    args = parser.parse_args()

    tool = CodeQualityTool(args.root)

    if args.command == "format":
        tool.format(args.paths)
    elif args.command == "check":
        tool.check(args.paths)
    elif args.command == "test":
        test_paths = args.test_paths or ["tests"]
        tool.test(test_paths, not args.no_cov)
    elif args.command == "analyze":
        tool.analyze(args.paths)
    elif args.command == "setup":
        tool.setup_pre_commit()
    elif args.command == "all":
        tool.run_all(args.paths)
    else:
        parser.print_help()
