# 函数接口

def selector(func1, func2, condition) -> tuple:
    return func1(condition) if condition \
        else func2()
