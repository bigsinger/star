# coding:utf-8
# 实现单实例类

class Singleton(type):
    def __init__(self, *args, **kwargs):
        self.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.__instance is None:
            self.__instance = super().__call__(*args, **kwargs)
            return self.__instance
        else:
            return self.__instance


if __name__ == '__main__':
    # Example
    class PathManager(metaclass=Singleton):
        def __init__(self):
            print('Creating PathManager')

    pm1 = PathManager() # Creating PathManager
    pm2 = PathManager() #
    pm3 = PathManager() #

    print(pm1 is pm2)   # True
    print(pm2 is pm3)   # True
