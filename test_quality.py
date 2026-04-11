# 测试代码质量检测


def test_function(x, y):
    """测试函数"""
    result = x + y
    print(f"结果: {result}")
    return result


# 测试行长度
long_string = "这是一个很长的字符串，用来测试行长度限制，这是一个很长的字符串，用来测试行长度限制，这是一个很长的字符串，用来测试行长度限制"


def main():
    """主函数"""
    test_function(1, 2)
    test_function("hello", "world")


if __name__ == "__main__":
    main()
