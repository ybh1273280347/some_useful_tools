"""
设计模式工具集

提供常用的设计模式实现：
- Singleton: 单例模式
- ObjectPool: 对象池模式
- RegistryFactory: 注册表工厂模式
"""

from abc import ABC, abstractmethod


class Singleton:
    """
    单例模式

    确保一个类只有一个实例，并提供全局访问点。

    使用示例:
        class MySingleton(Singleton):
            def __init__(self):
                self.value = 0

        s1 = MySingleton()
        s2 = MySingleton()
        assert s1 is s2  # True
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        创建新实例或返回已存在的实例

        Args:
            *args: 传递给构造函数的位置参数
            **kwargs: 传递给构造函数的关键字参数

        Returns:
            cls: 单例实例
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


class ObjectPool(ABC):
    """
    对象池模式

    管理对象的复用，避免频繁创建和销毁对象，提高性能。

    使用示例:
        class ConnectionPool(ObjectPool):
            def _create(self):
                return DatabaseConnection()

            def _destroy(self, obj):
                obj.close()

        with ConnectionPool(max_size=10) as pool:
            conn = pool.get()
            conn.query("SELECT * FROM users")
            pool.release(conn)
    """

    def __init__(self, max_size=10):
        """
        初始化对象池

        Args:
            max_size: 对象池最大容量，默认 10
        """
        self._pool = []
        self.max_size = max_size

    def get(self):
        """
        从池中获取一个对象

        如果池中有可用对象则直接返回，否则创建新对象

        Returns:
            object: 池中的对象或新创建的对象
        """
        if self._pool:
            return self._pool.pop()
        return self._create()

    def release(self, obj):
        """
        将对象放回池中

        如果池未满则放入池中，否则销毁对象

        Args:
            obj: 要释放的对象
        """
        if len(self._pool) < self.max_size:
            self._pool.append(obj)
        else:
            self._destroy(obj)

    def close(self):
        """
        关闭对象池，销毁所有池中对象
        """
        for obj in self._pool:
            self._destroy(obj)
        self._pool.clear()

    @abstractmethod
    def _create(self):
        """
        创建新对象（子类必须实现）

        Returns:
            object: 新创建的对象
        """
        pass

    @abstractmethod
    def _destroy(self, obj):
        """
        销毁对象（子类必须实现）

        Args:
            obj: 要销毁的对象
        """
        pass

    def __enter__(self):
        """
        上下文管理器入口

        Returns:
            ObjectPool: 对象池实例
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        上下文管理器出口，自动关闭对象池

        Args:
            exc_type: 异常类型
            exc_val: 异常值
            exc_tb: 异常回溯
        """
        self.close()


class RegistryFactory:
    """
    注册表工厂模式

    自动注册子类，通过名称创建对象实例。

    使用示例:
        class BaseShape(RegistryFactory):
            @abstractmethod
            def draw(self):
                pass

        class Circle(BaseShape):
            def draw(self):
                print("画圆")

        class Rectangle(BaseShape):
            def draw(self):
                print("画矩形")

        # 通过名称创建对象
        circle = BaseShape.create("Circle")
        circle.draw()
    """

    _registry = {}

    def __init_subclass__(cls, **kwargs):
        """
        子类初始化钩子，自动注册子类

        Args:
            **kwargs: 其他关键字参数
        """
        super().__init_subclass__(**kwargs)
        cls._registry = {}

        if RegistryFactory in cls.__bases__:
            RegistryFactory._registry[cls.__name__] = cls
        else:
            for base in cls.__bases__:
                if hasattr(base, "_registry"):
                    base._registry[cls.__name__] = cls

    @classmethod
    def create(cls, name, *args, **kwargs):
        """
        通过名称创建对象实例

        Args:
            name: 子类名称
            *args: 传递给构造函数的位置参数
            **kwargs: 传递给构造函数的关键字参数

        Returns:
            object: 创建的对象实例

        Raises:
            ValueError: 如果名称未注册
        """
        if name not in cls._registry:
            raise ValueError(
                f"{name} is not registered, you can only use {list(cls._registry.keys())}"
            )
        return cls._registry[name](*args, **kwargs)
