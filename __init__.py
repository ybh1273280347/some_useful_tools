"""
Python 实用工具包

包含各种实用工具模块：
- AsyncTool: 异步任务管理工具
- CodeGen: 代码生成工具
- ClassMode: 设计模式工具
- FileTool: 文件操作工具
- LoggingTool: 日志工具
- CodeQuality: 代码质量工具
"""

from .AsyncTool import (
    gather_with_limit,
    run_batch,
    run_in_processes,
    run_in_threads,
    run_with_timeout,
    wait_for_condition,
)
from .ClassMode import ObjectPool, RegistryFactory, Singleton
from .CodeGen import auto_enum, enhanced_dataclass, retry
from .FileTool import (
    file_compress,
    file_copy,
    file_delete,
    file_download,
    file_download_and_extract,
    file_download_batch,
    file_extract,
    file_find,
    file_move,
    file_read,
    file_size,
    file_write,
)
from .LoggingTool import (
    log_debug,
    log_error,
    log_event,
    log_fail,
    log_ok,
    setup_logging_intercept,
)

__all__ = [
    # AsyncTool
    "gather_with_limit",
    "run_batch",
    "run_with_timeout",
    "run_in_processes",
    "run_in_threads",
    "wait_for_condition",
    # CodeGen
    "auto_enum",
    "enhanced_dataclass",
    "retry",
    # ClassMode
    "Singleton",
    "ObjectPool",
    "RegistryFactory",
    # FileTool
    "file_download",
    "file_download_batch",
    "file_extract",
    "file_download_and_extract",
    "file_find",
    "file_read",
    "file_write",
    "file_size",
    "file_compress",
    "file_copy",
    "file_move",
    "file_delete",
    # LoggingTool
    "setup_logging_intercept",
    "log_ok",
    "log_fail",
    "log_error",
    "log_event",
    "log_debug",
]

# CodeQuality 工具通过脚本方式使用，不通过模块导入
# 运行方式: python CodeQuality/format_code.py
#          python CodeQuality/run_tests.py
#          python CodeQuality/check_code.py
