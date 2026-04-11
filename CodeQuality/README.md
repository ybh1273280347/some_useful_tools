# 代码质量工具

## 1. 格式化工具

### 功能
- 使用 isort 自动排序导入语句
- 使用 black 自动格式化 Python 代码
- 支持检查模式（只检查格式，不修改文件）
- 自动安装依赖

### 安装

```bash
# 安装依赖
pip install isort black
```

### 使用方法

#### 格式化当前目录
```bash
python CodeQuality/format_code.py
```

#### 格式化指定文件
```bash
python CodeQuality/format_code.py example.py
```

#### 格式化指定目录
```bash
python CodeQuality/format_code.py my_project/
```

#### 只检查格式（不修改文件）
```bash
python CodeQuality/format_code.py --check
```

## 2. 自动化测试工具

### 功能
- 使用 pytest 运行测试
- 支持生成测试覆盖率报告
- 支持详细测试输出
- 自动安装依赖

### 安装

```bash
# 安装依赖
pip install pytest pytest-cov
```

### 使用方法

#### 运行所有测试
```bash
python CodeQuality/run_tests.py
```

#### 运行指定测试文件
```bash
python CodeQuality/run_tests.py tests/test_example.py
```

#### 运行指定测试目录
```bash
python CodeQuality/run_tests.py tests/
```

#### 生成测试覆盖率报告
```bash
python CodeQuality/run_tests.py --coverage
```

#### 显示详细测试输出
```bash
python CodeQuality/run_tests.py --verbose
```

#### 组合使用
```bash
python CodeQuality/run_tests.py --coverage --verbose
```

## 3. 静态代码分析工具

### 功能
- 使用 flake8 检查代码质量
- 支持详细检查输出
- 自动安装依赖

### 安装

```bash
# 安装依赖
pip install flake8
```

### 使用方法

#### 检查当前目录
```bash
python CodeQuality/check_code.py
```

#### 检查指定文件
```bash
python CodeQuality/check_code.py example.py
```

#### 检查指定目录
```bash
python CodeQuality/check_code.py my_project/
```

#### 显示详细输出
```bash
python CodeQuality/check_code.py --verbose
```

## 4. 与 pre-commit 集成

### 配置

项目已包含 `.pre-commit-config.yaml` 文件，集成了所有三个代码质量工具：

```yaml
repos:
-   repo: local
    hooks:
    -   id: format-code
        name: Format code with isort and black
        entry: python CodeQuality/format_code.py
        language: system
        files: \.py$

-   repo: local
    hooks:
    -   id: flake8-check
        name: Check code quality with flake8
        entry: python CodeQuality/check_code.py
        language: system
        files: \.py$

-   repo: local
    hooks:
    -   id: run-tests
        name: Run tests with pytest
        entry: python CodeQuality/run_tests.py
        language: system
        files: \.py$
        pass_filenames: false
```

### 安装和使用

1. **安装 pre-commit**
   ```bash
   pip install pre-commit
   ```

2. **设置 pre-commit 钩子**
   ```bash
   pre-commit install
   ```

3. **手动运行所有钩子**（可选）
   ```bash
   pre-commit run --all-files
   ```

### 工作原理

当你执行 `git commit` 时，pre-commit 会自动：
1. 运行 `format_code.py` 格式化代码
2. 运行 `check_code.py` 检查代码质量
3. 运行 `run_tests.py` 执行测试

只有当所有检查都通过时，提交才会成功。这样可以确保每次提交的代码都符合质量要求。