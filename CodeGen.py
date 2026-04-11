"""
代码生成工具集

提供装饰器来增强 Python 类的功能：
- auto_enum: 为枚举成员自动添加属性和查找方法
- enhanced_dataclass: 为 dataclass 添加序列化/反序列化方法
- retry: 为函数添加自动重试机制
"""

import asyncio
import inspect
import time
from dataclasses import dataclass, fields, is_dataclass
from functools import wraps

# ============================自动枚举============================


def auto_enum(*fields):
    """
    为枚举类自动添加属性和查找方法。

    功能：
        1. 将枚举值中的元素绑定为成员属性
        2. 为每个字段生成 `get_by_{field}` 类方法

    Args:
        *fields: 字段名列表，与枚举值中的元素一一对应

    Returns:
        装饰器函数

    Raises:
        ValueError: 枚举值的元素数量与字段数量不匹配

    Example:
        >>> from enum import Enum
        >>> @auto_enum('label', 'code')
        ... class Status(Enum):
        ...     PENDING = ('pending', 1)
        ...     APPROVED = ('approved', 2)
        ...
        >>> Status.PENDING.label
        'pending'
        >>> Status.PENDING.code
        1
        >>> Status.get_by_label('pending')
        <Status.PENDING: ('pending', 1)>
        >>> Status.get_by_code(1)
        <Status.PENDING: ('pending', 1)>
        >>> Status.get_by_label('unknown') is None
        True

    Note:
        - 避免使用 'name' 和 'value' 作为字段名，它们是 Enum 的内置属性
        - 单字段时枚举值可以是单个值或单元素元组
    """

    def decorator(cls):
        for member in cls:
            args = member.value if isinstance(member.value, tuple) else (member.value,)
            if len(args) != len(fields):
                raise ValueError(f"Expected {len(fields)} arguments, got {len(args)}")
            for field, arg in zip(fields, args):
                setattr(member, field, arg)
        for field in fields:

            @classmethod
            def finder(cls, value, f=field):
                for member in cls:
                    if getattr(member, f) == value:
                        return member
                return None

            setattr(cls, f"get_by_{field}", finder)
        return cls

    return decorator


# ============================ dataclass ==========================


def enhanced_dataclass(recursive=True, frozen=False):
    """
    增强的 dataclass 装饰器，添加序列化/反序列化方法。

    功能：
        1. 保留原生 dataclass 所有功能
        2. 添加 to_dict() 方法：将实例转换为字典
        3. 添加 from_dict() 类方法：从字典创建实例

    Args:
        recursive: 是否递归处理嵌套的 dataclass，默认 True
        frozen: 是否创建不可变的 dataclass，默认 False

    Returns:
        装饰器函数

    Example:
        >>> @enhanced_dataclass()
        ... class Address:
        ...     city: str
        ...     street: str
        ...
        >>> @enhanced_dataclass()
        ... class Person:
        ...     name: str
        ...     age: int
        ...     address: Address
        ...
        >>> addr = Address(city="Beijing", street="Main St")
        >>> person = Person(name="Alice", age=30, address=addr)
        >>> person.to_dict()
        {'name': 'Alice', 'age': 30, 'address': {'city': 'Beijing', 'street': 'Main St'}}
        >>> data = {'name': 'Bob', 'age': 25, 'address': {'city': 'Shanghai', 'street': 'Nanjing Rd'}}
        >>> p = Person.from_dict(data)
        >>> p.address.city
        'Shanghai'

    Note:
        - recursive=False 时，嵌套的 dataclass 不会被转换，保持原对象
        - from_dict() 支持部分字段，缺失字段不会被设置
    """

    def decorator(cls):
        cls = dataclass(cls, frozen=frozen)
        fs = fields(cls)

        def _map(obj, func):
            if isinstance(obj, list):
                return [_map(x, func) for x in obj]
            elif isinstance(obj, tuple):
                return tuple(_map(x, func) for x in obj)
            elif isinstance(obj, set):
                return {_map(x, func) for x in obj}
            elif isinstance(obj, dict):
                return {k: _map(v, func) for k, v in obj.items()}
            else:
                return func(obj)

        def to_dict(self):
            """将 dataclass 实例转换为字典，支持嵌套"""

            def _convert(x):
                return x.to_dict() if is_dataclass(x) else x  # type: ignore

            result = {}
            for f in fs:
                obj = getattr(self, f.name)
                result[f.name] = _map(obj, _convert) if recursive else obj
            return result

        setattr(cls, "to_dict", to_dict)

        @classmethod
        def from_dict(cls, data: dict):
            instance = cls.__new__(cls)
            for f in fs:
                if f.name in data:
                    value = data[f.name]
                    if recursive and is_dataclass(f.type) and isinstance(value, dict):
                        setattr(instance, f.name, f.type.from_dict(value))  # type: ignore
                    else:
                        setattr(instance, f.name, value)
            return instance

        setattr(cls, "from_dict", from_dict)
        return cls

    return decorator


# ========================= retry ==========================


def retry(max_retries=3, delay=1, back_off=2, return_exceptions=False):
    """
    为函数添加自动重试机制，支持同步和异步函数。

    功能：
        1. 自动检测同步/异步函数并使用对应的包装器
        2. 支持指数退避策略
        3. 支持 return_exceptions 模式（失败返回 None 而非抛出异常）
        4. 保留原函数的元信息（__name__, __doc__ 等）

    Args:
        max_retries: 最大重试次数，默认 3
        delay: 初始延迟时间（秒），默认 1
        back_off: 退避倍数，每次重试后 delay *= back_off，默认 2
        return_exceptions: 是否返回异常而非抛出，True 时失败返回 None，默认 False

    Returns:
        装饰器函数

    Example:
        >>> @retry(max_retries=3, delay=0.1)
        ... def flaky_func():
        ...     # 可能失败的操作
        ...     pass
        ...
        >>> @retry(max_retries=3, delay=0.1, back_off=2)
        ... async def async_flaky_func():
        ...     # 异步操作，延迟序列: 0.1s, 0.2s, 0.4s
        ...     pass
        ...
        >>> @retry(max_retries=3, return_exceptions=True)
        ... def may_return_none():
        ...     # 失败时返回 None 而非抛出异常
        ...     pass

    Note:
        - 异步函数使用 asyncio.sleep，同步函数使用 time.sleep
        - back_off=1 时禁用指数退避，使用固定延迟
        - return_exceptions 模式适用于"尝试执行，失败也无妨"的场景
    """

    def decorator(func):
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            _delay = delay
            for i in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i == max_retries - 1:
                        if return_exceptions:
                            return
                        raise e
                    time.sleep(_delay)
                    _delay *= back_off

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            _delay = delay
            for i in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if i == max_retries - 1:
                        if return_exceptions:
                            return
                        raise e
                    await asyncio.sleep(_delay)
                    _delay *= back_off

        return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper

    return decorator
