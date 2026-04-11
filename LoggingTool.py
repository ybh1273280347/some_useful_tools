"""
日志工具集

基于 Loguru 实现的日志工具，提供统一的日志格式和便捷的日志方法。

核心功能：
- 全局配置：将标准 logging（uvicorn/FastAPI/第三方库）接管到 Loguru
- 统一格式：操作级别的日志函数，包含固定的字段格式
- 便捷方法：成功/失败/异常/事件/调试等场景的专用日志函数

使用流程：
1. 在应用启动时调用 `setup_logging_intercept()` 配置全局日志
2. 在代码中使用 `log_ok()`, `log_fail()`, `log_error()`, `log_event()`, `log_debug()` 记录日志
"""

import logging
import sys
from typing import Any

from loguru import logger

# 全局 Loguru Sink 配置（整个进程只注册一次）
logger.remove()  # 移除默认 sink
logger.add(
    sys.stdout,
    level="INFO",
    colorize=True,
    enqueue=False,
)


class _InterceptHandler(logging.Handler):
    """
    将标准 logging（uvicorn / FastAPI / third-party）接管到 Loguru。

    作用：
        - 捕获标准 logging 的日志
        - 转换为 Loguru 格式
        - 保持原始的调用栈信息
    """

    def emit(self, record: logging.LogRecord):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging_intercept(log_level: str = "INFO"):
    """
    在应用启动时调用一次，配置全局日志。

    将 uvicorn / fastapi / root logger 的输出全部接管到 Loguru，
    保证整个应用的日志格式统一。

    Args:
        log_level: 日志级别，默认 "INFO"

    应用场景：
        - FastAPI/uvicorn 应用启动时
        - 命令行工具启动时
        - 任何需要统一日志格式的 Python 应用

    Example:
        >>> from LoggingTool import setup_logging_intercept
        >>> # 在应用入口调用
        >>> setup_logging_intercept(log_level="INFO")
        >>>
        >>> # 或根据环境变量设置
        >>> import os
        >>> setup_logging_intercept(os.getenv("LOG_LEVEL", "INFO"))
    """
    # 重新配置 Loguru sink 级别，使其与运行时配置一致
    logger.remove()
    logger.add(
        sys.stdout,
        level=log_level.upper(),
        colorize=True,
        enqueue=False,
    )

    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(handlers=[_InterceptHandler()], level=numeric_level, force=True)

    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
        log = logging.getLogger(name)
        log.handlers = [_InterceptHandler()]
        log.propagate = False


def fmt(**fields: Any) -> str:
    """
    将任意 k=v 字段拼接为固定格式的字段后缀。

    Args:
        **fields: 要记录的字段

    Returns:
        格式化后的字段字符串，格式为 " | k=v ..."

    Example:
        >>> fmt(user_id=123, action="login")
        " | user_id=123 action=login"
    """
    if not fields:
        return ""
    parts = " ".join(f"{k}={v}" for k, v in fields.items())
    return f" | {parts}"


def log_ok(op: str, **fields: Any) -> None:
    """
    操作成功（INFO 级别）。

    格式："{op}成功 | k=v ..."

    Args:
        op: 操作名称，如 "登录", "数据同步", "文件上传"
        **fields: 额外字段，如 user_id, item_id 等

    应用场景：
        - 业务操作成功
        - 定时任务完成
        - API 调用成功

    Example:
        >>> log_ok("用户登录", user_id=123, ip="192.168.1.1")
        # 输出: 2024-01-01 12:00:00.000 | INFO     | __main__:123 - 用户登录成功 | user_id=123 ip=192.168.1.1
    """
    logger.opt(depth=1).info(f"{op}成功{fmt(**fields)}")


def log_fail(op: str, error: Any, **fields: Any) -> None:
    """
    操作失败，预期内的可恢复降级（WARNING 级别）。

    格式："{op}失败 | k=v ...: {error}"

    Args:
        op: 操作名称
        error: 错误信息
        **fields: 额外字段

    应用场景：
        - 预期内的错误（如用户输入错误）
        - 可降级的操作（如备用方案）
        - 非致命的业务异常

    Example:
        >>> log_fail("发送邮件", "邮箱格式错误", user_id=123, email="invalid")
        # 输出: 2024-01-01 12:00:00.000 | WARNING  | __main__:123 - 发送邮件失败 | user_id=123 email=invalid: 邮箱格式错误
    """
    logger.opt(depth=1).warning(f"{op}失败{fmt(**fields)}: {error}")


def log_error(op: str, error: Any, **fields: Any) -> None:
    """
    操作异常，非预期的系统故障（ERROR 级别）。

    格式："{op}异常 | k=v ...: {error}"

    Args:
        op: 操作名称
        error: 错误信息
        **fields: 额外字段

    应用场景：
        - 系统级错误
        - 数据库连接失败
        - 第三方服务异常
        - 程序崩溃

    Example:
        >>> try:
        ...     raise Exception("数据库连接失败")
        ... except Exception as e:
        ...     log_error("数据库操作", e, db="users")
        # 输出: 2024-01-01 12:00:00.000 | ERROR    | __main__:123 - 数据库操作异常 | db=users: 数据库连接失败
    """
    logger.opt(depth=1).error(f"{op}异常{fmt(**fields)}: {error}")


def log_event(event: str, **fields: Any) -> None:
    """
    进程或生命周期事件（INFO 级别），不对应具体操作成败。

    格式："{event} | k=v ..."

    Args:
        event: 事件名称，如 "服务启动", "配置加载", "定时任务开始"
        **fields: 额外字段

    应用场景：
        - 服务启动/停止
        - 配置变更
        - 定时任务开始/结束
        - 系统状态变更

    Example:
        >>> log_event("服务启动", version="1.0.0", env="production")
        # 输出: 2024-01-01 12:00:00.000 | INFO     | __main__:123 - 服务启动 | version=1.0.0 env=production
    """
    logger.opt(depth=1).info(f"{event}{fmt(**fields)}")


def log_debug(message, **fields: Any) -> None:
    """
    调试信息（DEBUG 级别）。

    格式："[DEBUG]{message} | k=v"

    Args:
        message: 调试信息
        **fields: 额外字段

    应用场景：
        - 开发调试
        - 详细的内部状态
        - 性能分析

    Example:
        >>> log_debug("计算结果", value=42, input="test")
        # 输出: 2024-01-01 12:00:00.000 | DEBUG    | __main__:123 - [DEBUG]计算结果 | value=42 input=test
    """
    logger.opt(depth=1).debug(f"[DEBUG]{message}{fmt(**fields)}")
