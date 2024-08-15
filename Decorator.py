import time


def logger(func):
    def logger_wrapper(*args, **kwargs):
        start_time = time.time()
        print(f"{func.__name__} started at{time.strftime('%H:%M:%S')}")
        func(*args, **kwargs)
        end_time = time.time()
        delta_time = end_time - start_time
        print(f"{func.__name__} finished in {delta_time:.2f} seconds")
    return logger_wrapper


def matching(func):
    def matching_wrapper(*args, **kwargs):
        start_time = time.time()
        print(f"{func.__name__} started at{time.strftime('%H:%M:%S')}")
        result = func(*args, **kwargs)
        end_time = time.time()
        delta_time = end_time - start_time
        print(f"{func.__name__} finished in {delta_time:.2f} seconds")
        return result
    return matching_wrapper
# 装饰器函数如果要返回值一定别忘了返回
