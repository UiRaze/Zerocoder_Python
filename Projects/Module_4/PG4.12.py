def greeting_decorator(func):
    def wrapper():
        print("Привет! Это здорово, что ты изучаешь Python.")
        func()
        print("Пока")
    return wrapper

@greeting_decorator
def say_hello():
    print("Hello, world!")

say_hello()