import time

def time_it_decorator(function):
    def time_it(*args, **kwargs):
        before = time.time()
        result = function(*args, **kwargs)
        after = time.time()
        return (result, after - before)

    return time_it

@time_it_decorator
def test_this(a):
    return a
    
