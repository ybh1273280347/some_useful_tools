# 测试文件
# 故意引入一些代码风格问题


def test_function():
    x = 1  # 缺少空格
    print("Hello World")
    return x


# 行长度超过 79 字符的问题
long_line = "This is a very long line that exceeds the 79 character limit"
long_line += " for Python code style guidelines"


# 空白字符问题
def another_function(x, y):
    return x + y
