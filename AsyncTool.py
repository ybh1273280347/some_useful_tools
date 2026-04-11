"""
异步工具集

提供异步任务管理、并发控制、超时处理等常用异步工具。

应用场景：
- gather_with_limit: 大量并发任务需要控制并发数，避免资源耗尽
- run_batch: 任务数量特别大，分批执行降低内存压力
- run_with_timeout: 防止协程卡死，设置超时时间
- run_in_threads: 调用阻塞同步函数，避免阻塞事件循环
- run_in_processes: CPU 密集型任务，利用多核性能
- wait_for_condition: 轮询等待某个条件满足
"""

import asyncio
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import Callable, List, Tuple


async def gather_with_limit(
    tasks: List, limit: int = 5, return_exceptions: bool = False
):
    """
    带并发限制的 asyncio.gather。

    使用 Semaphore 控制同时运行的协程数量，避免资源耗尽。

    Args:
        tasks: 协程对象列表
        limit: 最大并发数，默认 5
        return_exceptions: 是否返回异常而非抛出，默认 False

    Returns:
        结果列表，顺序与 tasks 一致

    应用场景：
        - 大量网络请求、API 调用
        - 避免同时打开太多连接/文件
        - 控制并发量防止服务器限流

    Example:
        >>> async def fetch(url):
        ...     async with httpx.AsyncClient() as client:
        ...         return await client.get(url)
        ...
        >>> urls = [f'https://example.com/page/{i}' for i in range(100)]
        >>> tasks = [fetch(url) for url in urls]
        >>> results = await gather_with_limit(tasks, limit=10)
    """
    semaphore = asyncio.Semaphore(limit)

    async def run_task(task):
        async with semaphore:
            return await task

    return await asyncio.gather(
        *[run_task(task) for task in tasks], return_exceptions=return_exceptions
    )


async def run_batch(tasks: List, batch_size: int = 100, limit: int = 10):
    """
    分批执行大量异步任务。

    当任务数量特别大时，避免一次性创建所有协程导致内存压力。

    Args:
        tasks: 协程对象列表
        batch_size: 每批执行的任务数，默认 100
        limit: 每批的最大并发数，默认 10

    Returns:
        所有结果的列表，顺序与 tasks 一致

    应用场景：
        - 任务数量 > 1000
        - 避免一次性创建大量协程
        - 更精细的内存控制

    Example:
        >>> tasks = [my_task(i) for i in range(10000)]
        >>> results = await run_batch(tasks, batch_size=200, limit=20)
    """
    results = []
    for i in range(0, len(tasks), batch_size):
        batch_tasks = tasks[i:i + batch_size]
        batch_results = await gather_with_limit(batch_tasks, limit)
        results.extend(batch_results)
    return results


async def run_with_timeout(coro, timeout, default=None):
    """
    带超时的协程执行。

    Args:
        coro: 协程对象
        timeout: 超时时间（秒）
        default: 超时时返回的默认值，默认 None

    Returns:
        协程结果或 default

    应用场景：
        - 网络请求设置超时
        - 防止某个协程卡死导致整体挂起
        - 优雅处理超时而非抛出异常

    Example:
        >>> async def slow_operation():
        ...     await asyncio.sleep(10)
        ...     return "done"
        ...
        >>> result = await run_with_timeout(slow_operation(), timeout=2, default="timeout")
        >>> result
        'timeout'
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        return default


async def run_in_processes(
    func, args_list: List[Tuple], max_workers: int = 4, **kwargs
):
    """
    在进程池中执行同步函数。

    利用多个 CPU 核心处理 CPU 密集型任务，避免阻塞事件循环。

    Args:
        func: 同步函数
        args_list: 参数元组列表，每个元组对应一次调用
        max_workers: 最大进程数，默认 CPU 核心数
        **kwargs: 传递给 gather_with_limit 的参数

    Returns:
        结果列表

    应用场景：
        - CPU 密集型计算（加密、图像处理、数据计算）
        - 避免 GIL 限制
        - 利用多核性能

    Note:
        - func 和参数必须可序列化（pickle）
        - 进程创建开销较大，适合耗时较长的任务

    Example:
        >>> def heavy_calc(x, y):
        ...     return sum(range(x * y))
        ...
        >>> args_list = [(1000, 1000), (2000, 2000), (3000, 3000)]
        >>> results = await run_in_processes(heavy_calc, args_list, max_workers=4)
    """
    loop = asyncio.get_event_loop()
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        tasks = [loop.run_in_executor(executor, func, *args) for args in args_list]
        return await gather_with_limit(tasks, **kwargs)


async def run_in_threads(
    func: Callable, args_list: List[Tuple], max_workers: int = 4, **kwargs
):
    """
    在线程池中执行同步函数。

    用于调用阻塞的同步函数（如文件 IO、某些数据库驱动），避免阻塞事件循环。

    Args:
        func: 同步函数
        args_list: 参数元组列表，每个元组对应一次调用
        max_workers: 最大线程数，默认 4
        **kwargs: 传递给 gather_with_limit 的参数

    Returns:
        结果列表

    应用场景：
        - 阻塞 IO（文件读写、同步数据库驱动）
        - 调用不支持异步的第三方库
        - 比进程池更轻量

    Example:
        >>> def blocking_read(file):
        ...     with open(file, 'r') as f:
        ...         return f.read()
        ...
        >>> args_list = [('file1.txt',), ('file2.txt',), ('file3.txt',)]
        >>> results = await run_in_threads(blocking_read, args_list)
    """
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        tasks = [loop.run_in_executor(executor, func, *args) for args in args_list]
        return await gather_with_limit(tasks, **kwargs)


async def wait_for_condition(
    condition: Callable[[], bool], timeout: float = 30, interval: float = 0.5
) -> bool:
    """
    轮询等待某个条件满足。

    Args:
        condition: 条件判断函数，返回 True/False
        timeout: 最大等待时间（秒），默认 30
        interval: 轮询间隔（秒），默认 0.5

    Returns:
        条件满足返回 True，超时返回 False

    应用场景：
        - 等待外部服务启动
        - 等待文件生成
        - 等待某个状态变化

    Example:
        >>> import os
        >>> await wait_for_condition(lambda: os.path.exists('output.txt'), timeout=10)
        True
    """
    start = asyncio.get_event_loop().time()
    while True:
        if condition():
            return True
        if asyncio.get_event_loop().time() - start > timeout:
            return False
        await asyncio.sleep(interval)
