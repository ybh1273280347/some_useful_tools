# CodeQualityTool 使用指南

## 功能概述

CodeQualityTool 是一个集成了多种代码质量工具的统一命令行工具，支持：
- 代码自动格式化（black + isort）
- 静态代码检查（flake8 + mypy）
- 测试运行与覆盖率报告（pytest + pytest-cov）
- 代码分析（pylint）
- 预提交钩子设置

## 安装依赖

首先安装所需的依赖包：

```bash
pip install black isort flake8 mypy pytest pytest-cov pylint pre-commit
```

## 基本使用

### 1. 格式化代码

```bash
# 格式化整个项目
python CodeQualityTool.py format

# 格式化指定文件/目录
python CodeQualityTool.py format --paths src/ tests/
```

### 2. 静态检查

```bash
# 检查整个项目
python CodeQualityTool.py check

# 检查指定文件/目录
python CodeQualityTool.py check --paths src/utils.py
```

### 3. 运行测试

```bash
# 运行测试并生成覆盖率报告
python CodeQualityTool.py test

# 运行指定测试文件
python CodeQualityTool.py test tests/test_utils.py

# 不生成覆盖率报告
python CodeQualityTool.py test --no-cov
```

### 4. 代码分析

```bash
# 分析整个项目
python CodeQualityTool.py analyze

# 分析指定文件/目录
python CodeQualityTool.py analyze --paths src/
```

### 5. 设置预提交钩子

```bash
# 设置 git 预提交钩子
python CodeQualityTool.py setup
```

设置后，每次 `git commit` 前都会自动运行代码质量检查。

### 6. 运行所有检查

```bash
# 运行所有代码质量检查
python CodeQualityTool.py all

# 针对指定文件/目录运行所有检查
python CodeQualityTool.py all --paths src/
```

## 高级使用

### 指定项目根目录

如果工具不在项目根目录运行，可以通过 `--root` 参数指定：

```bash
python CodeQualityTool.py --root /path/to/project format
```

### 集成到 CI/CD

在 CI/CD 流程中，可以添加以下步骤：

```bash
# 运行所有代码质量检查
python CodeQualityTool.py all

# 仅运行测试和覆盖率检查
python CodeQualityTool.py test
```

### 配置文件

工具会使用项目中现有的配置文件：
- `pyproject.toml`：black、isort、mypy 配置
- `.flake8`：flake8 配置
- `pytest.ini`：pytest 配置
- `.pylintrc`：pylint 配置

## 示例

### 示例 1：格式化并检查代码

```bash
# 格式化代码
python CodeQualityTool.py format

# 检查代码
python CodeQualityTool.py check
```

### 示例 2：运行测试并查看覆盖率

```bash
# 运行测试
python CodeQualityTool.py test

# 查看覆盖率报告
# 报告生成在 cov_html 目录中，打开 index.html 查看
```

### 示例 3：设置预提交钩子

```bash
# 设置预提交钩子
python CodeQualityTool.py setup

# 测试钩子（尝试提交代码时会自动运行检查）
git add .
git commit -m "test commit"
```

## 常见问题

### 1. 依赖安装失败

如果依赖安装失败，可以尝试使用国内镜像：

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple black isort flake8 mypy pytest pytest-cov pylint pre-commit
```

### 2. 预提交钩子不生效

确保已经运行了 `python CodeQualityTool.py setup`，并且 git 仓库已经初始化。

### 3. 覆盖率报告为空

确保测试文件以 `test_` 开头，并且测试函数以 `test_` 开头。

### 4. 类型检查失败

为项目添加类型注解，或在 `pyproject.toml` 中配置 mypy 忽略特定错误。

## 总结

CodeQualityTool 提供了一个统一的接口来管理代码质量，帮助团队保持代码风格一致，及时发现潜在问题，提高代码质量和可维护性。
