# Python 实用工具集

## 开发动机

在日常开发中，我们经常需要使用各种库和工具来完成常见任务，如异步编程、文件操作、日志管理等。然而，不同库的 API 设计和使用方式各不相同，增加了开发时的认知负担。

本项目的目标是：
- **统一接口**：为常见任务提供一致的 API，减少学习成本
- **简化使用**：封装复杂的底层实现，提供简单易用的接口
- **提高效率**：提供开箱即用的工具，加速开发流程
- **质量保证**：集成代码质量工具，确保代码规范和可靠性

## 项目概述

这是一个集合了多种实用 Python 工具的项目，涵盖异步编程、文件操作、日志管理、代码生成和代码质量检查等功能。

## 工具列表

| 模块 | 功能描述 | 主要函数 |
|------|----------|----------|
| AsyncTool | 异步任务管理工具 | gather_with_limit, run_batch, run_with_timeout, run_in_processes, run_in_threads, wait_for_condition |
| CodeGen | 代码生成工具 | auto_enum, enhanced_dataclass, retry |
| FileTool | 文件操作工具 | file_download, file_extract, file_read, file_write, file_copy, file_move, file_delete |
| LoggingTool | 日志工具 | setup_logging_intercept, log_ok, log_fail, log_error, log_event, log_debug |
| CodeQualityTool | 代码质量工具 | format, check, test, analyze, setup_pre_commit |

## 安装

### 基础依赖

```bash
pip install httpx loguru
```

### 代码质量工具依赖

```bash
pip install black isort flake8 mypy pytest pytest-cov pylint pre-commit
```

## 使用方法

### 1. 作为模块导入

```python
# 导入特定模块
from AsyncTool import gather_with_limit
from FileTool import file_read, file_write
from LoggingTool import log_ok
from CodeGen import enhanced_dataclass, retry

# 导入整个包
import Python实用工具个人项目 as utils
utils.file_read('config.json')
```

### 2. 命令行使用

#### 代码质量工具

```bash
# 格式化代码
python CodeQualityTool.py format

# 静态检查
python CodeQualityTool.py check

# 运行测试
python CodeQualityTool.py test

# 代码分析
python CodeQualityTool.py analyze

# 设置预提交钩子
python CodeQualityTool.py setup

# 运行所有检查
python CodeQualityTool.py all
```

## 工具详细说明

### AsyncTool - 异步任务管理

**功能**：提供并发控制、超时处理、线程/进程池执行等异步工具。

**设计亮点**：
- 使用信号量实现精确的并发限制，避免系统资源耗尽
- 批处理与并发控制结合，处理大量任务更高效
- 基于 `asyncio.wait_for` 实现优雅的超时控制
- 提供不同级别的执行环境隔离（线程/进程）
- 支持基于条件的异步等待机制

**技术优势**：
- 使用 Python 原生 `asyncio` 库，无额外依赖
- 支持异步生成器和协程的无缝集成
- 完善的错误处理机制，支持异常传递

**使用场景**：
- 大量网络请求的并发控制
- 耗时任务的后台执行
- 定时任务的超时处理

**示例**：
```python
from AsyncTool import gather_with_limit

async def fetch(url):
    async with httpx.AsyncClient() as client:
        return await client.get(url)

# 并发限制为 10
urls = [f'https://example.com/page/{i}' for i in range(100)]
tasks = [fetch(url) for url in urls]
results = await gather_with_limit(tasks, limit=10)
```

### CodeGen - 代码生成

**功能**：提供装饰器来增强 Python 类的功能。

**设计亮点**：
- 采用装饰器模式实现横切关注点，代码侵入性低
- 利用 Python 元编程能力，在运行时动态修改类行为
- 保持 dataclass 的类型提示能力，确保类型安全
- 支持嵌套 dataclass 的序列化和反序列化
- 通过参数控制装饰器行为，灵活可配置

**技术优势**：
- `auto_enum` 自动为枚举添加查找方法，简化枚举使用
- `retry` 装饰器支持指数退避策略，提高网络操作成功率
- `enhanced_dataclass` 支持不可变 dataclass，确保线程安全

**主要装饰器**：
- `auto_enum`：为枚举成员自动添加属性和查找方法
- `enhanced_dataclass`：为 dataclass 添加序列化/反序列化方法
- `retry`：为函数添加自动重试机制

**示例**：
```python
from CodeGen import enhanced_dataclass, retry

@enhanced_dataclass(frozen=True)
class User:
    name: str
    age: int
    email: str

# 序列化
tom = User(name="Tom", age=20, email="tom@example.com")
data = tom.to_dict()

# 反序列化
user = User.from_dict(data)

@retry(max_attempts=3, delay=1, return_exceptions=True)
async def fetch_data(url):
    async with httpx.AsyncClient() as client:
        return await client.get(url)
```

### FileTool - 文件操作

**功能**：提供下载、解压、读写、复制、移动、删除等文件操作。

**设计亮点**：
- 提供一致的文件操作接口，简化文件处理
- 支持异步下载，不阻塞主线程
- 完善的异常处理机制，提供清晰的错误信息
- 自动处理路径拼接和规范化，跨平台兼容

**技术优势**：
- 使用 `httpx` 实现高效的异步下载
- 支持多种压缩格式的解压（zip、tar.gz 等）
- 文件操作函数名统一添加 `file_` 前缀，提高可读性

**使用场景**：
- 文件下载与解压
- 配置文件读写
- 批量文件处理

**示例**：
```python
from FileTool import file_download, file_extract, file_read, file_write

# 下载文件
await file_download('https://example.com/file.zip', 'downloads/')

# 解压文件
file_extract('downloads/file.zip', 'output/')

# 读写文件
content = file_read('config.json')
file_write('output.txt', 'Hello World')
```

### LoggingTool - 日志工具

**功能**：基于 Loguru 实现的统一日志工具。

**设计亮点**：
- 接管全局日志配置，包括标准库日志
- 使用字典形式记录日志，支持结构化分析
- 提供不同级别的日志函数，语义清晰
- 自动添加时间戳、进程 ID 等上下文信息

**技术优势**：
- 基于 `Loguru` 实现，API 简洁易用
- 支持日志文件轮转和压缩
- 与标准 `logging` 库完全兼容

**使用场景**：
- 应用日志管理
- 操作结果记录
- 错误追踪

**示例**：
```python
from LoggingTool import setup_logging_intercept, log_ok, log_error

# 配置全局日志
setup_logging_intercept(log_level="INFO")

# 记录操作成功
log_ok("用户登录", user_id=123, ip="192.168.1.1")

# 记录错误
try:
    raise Exception("数据库连接失败")
except Exception as e:
    log_error("数据库操作", e, db="users")
```

### CodeQualityTool - 代码质量工具

**功能**：集成多种代码质量工具，提供统一的命令行接口。

**设计亮点**：
- 统一封装多种代码质量工具，提供一致的接口
- 支持命令行参数解析，使用简单
- 自动设置 git 预提交钩子，确保代码质量
- 统一处理和展示不同工具的检查结果

**技术优势**：
- 支持自定义配置文件（`pyproject.toml`）
- 自动处理编码问题，支持中文输出
- 提供详细的检查结果和错误信息

**使用场景**：
- 代码提交前检查
- CI/CD 流程中的质量控制
- 团队代码规范管理

**配置**：
- 支持 `pyproject.toml` 配置文件
- 可自定义检查规则

## 项目结构

```
Python实用工具个人项目/
├── AsyncTool.py          # 异步工具
├── CodeGen.py           # 代码生成工具
├── FileTool.py          # 文件操作工具
├── LoggingTool.py       # 日志工具
├── CodeQualityTool.py   # 代码质量工具
├── __init__.py          # 包初始化文件
├── README.md            # 项目说明
└── README_CodeQualityTool.md  # 代码质量工具说明
```

## 开发指南

### 代码风格
- 使用 black 进行代码格式化
- 使用 isort 进行导入排序
- 遵循 PEP 8 代码风格

### 测试
- 为新功能添加测试用例
- 确保所有测试通过
- 运行代码质量检查

### 提交规范
- 每次提交前运行 `python CodeQualityTool.py setup` 设置预提交钩子
- 确保代码符合质量要求
- 提交信息清晰明了

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 许可证

MIT License
