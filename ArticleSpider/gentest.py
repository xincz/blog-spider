def my_gen():
    yield 1
    yield 2
    yield 3
    return 4

def my_fun():
    return 4

print(my_gen())

for data in my_gen():
    print(data)

next(my_gen())
next(my_gen())

# 可以停止的函数
gen = my_gen()
next(gen)
next(gen)
next(gen)


# 遇到url可以立即交给scrapy进行下载
# Scrapy 是异步 IO 框架，没有多线程
# 基于回调模式的框架只有单线程，单线程就可以完成高并发
# 没有引入消息队列
