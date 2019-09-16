# coding: utf-8

import os
import sys
import time
import logging
import traceback

'''
调试相关
'''

'''
获取用户输入
x = input('please input: ')
'''


'''
示例：
star.initlogging()
logging.debug(u"%s %d", u"哈", 1)
'''
def initlogging(logFile = u"log.txt", toFile = False):
    '''
    binPath = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), "bin")
    pid = '%d' % (os.getpid())
    logging.basicConfig(level=logging.DEBUG,
            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            filename=u'%s%swrap_%s.log' % (binPath, os.sep, pid),
            filemode='a')
    #################################################################################################
    #定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    #################################################################################################
    '''
    if toFile is False:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)-6s %(filename)20s:%(lineno)-4d  %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            stream=sys.stdout,
        )
    else:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)-6s %(filename)20s:%(lineno)-4d  %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            filename=logFile,
            filemode='a',
        )

'''
把一段内容作为日志保存到当前目录下的log.txt文件中，每次重新创建，不追加！追加模式请使用loga函数。
s：      将要被输出到日志文件的bytes内容，字符串不可用。如果是字符串请用with open(file, 'w')
file：   默认为log.txt，也可以指定路径。
mode：   日志文件的打开方式，默认为读写重新创建，也可以重新指定。
'''
def log(s, file = 'log.txt', mode = os.O_RDWR | os.O_CREAT):
    result = False
    fd = os.open(file, mode)
    if fd > 0 and s:
        try:
            os.write(fd, bytes(s, 'UTF-8'))
            result = True
        except Exception as e:
            print(e)
            print('can not access file: ' + file + ' open with os.O_RDWR?')
        finally:
            os.close(fd)
    else:
        print('open file error: ' + file)
        print(fd)
    return result

'''
追加的形式写日志，其他同log函数。
'''
def loga(s, file = 'log.txt'):
    return log(s, file, os.O_RDWR | os.O_APPEND)

# 命令行下暂停
def pause():
    os.system('pause')


"""
时间记录的函数和装饰器
"""
class TimeRecorder:
    def __init__(self, name):
        print(name + u" start")
        self.name = name
        self.startTime = time.time()
    def __del__(self):
        print(u"%s end, time used: %.1f s", self.name, time.time() - self.startTime)

"""
def scan1():
    t = TimeRecorder(scan1.func_name)
    time.sleep(1)
    return 1

print scan1()
"""


# 函数装饰器，让函数打印耗时
def logtime(func):
    def wrapper(*args, **kwargs):
        print(func.func_name + u" start")
        startTime = time.time()
        ret = func(*args, **kwargs)
        print(u"%s end, time used: %.1f s" % (func.func_name, time.time() - startTime))
        return ret
    return wrapper

# 指定一个名称
def logtimewithname(name = None):
    def wrapper(func):
        def wrapper2(*args, **kwargs):
            _name = name
            if name is None:
                _name = func.func_name
            else:
                _name = name
            print(_name + u" start")
            startTime = time.time()
            res = func(*args, **kwargs)
            print(u"%s end, time used: %.1f s" % (_name, time.time() - startTime))
            return res
        return wrapper2
    return wrapper


# 函数限定时间运行
def timelimit(interval):
    def time_out():
        raise Exception("time out")

    def wrapper(func):
        def wrapper2(*args, **kwargs):
            print(func.func_name + u" start")
            timer = Timer(interval, time_out)
            timer.start()
            startTime = time.time()
            res = func(*args, **kwargs)
            timer.cancel()
            print(u"{0} end time: {1}".format(func.func_name, time.time() - startTime))
            return res
        return wrapper2
    return wrapper




class TimeoutException(Exception):
    pass

# 函数限定时间运行
def timelimited(timeout):
    def decorator(func):
        def decorator2(*args,**kwargs):
            class TimeLimited(Thread):
                def __init__(self):
                    Thread.__init__(self)
                    self._error = None
                    self._result = None

                def run(self):
                    try:
                        print(func.func_name + u" start")
                        startTime = time.time()
                        self._result = func(*args, **kwargs)
                        print(u"{0} end time: {1}".format(func.func_name, time.time() - startTime))
                    except Exception as e:
                        self._error = e

                def _stop(self):
                    if self.isAlive():
                        Thread._Thread__stop(self)

            t = TimeLimited()
            t.start()
            t.join(timeout)

            if t.isAlive():
                t._stop()
                raise TimeoutException('timeout for %s' % (repr(func)))

            if isinstance(t._error, TimeoutException):
                t._stop()
                raise TimeoutException('timeout for %s' % (repr(func)))

            if t._error is None:
                return t._result

        return decorator2
    return decorator

"""
@logtime
def scan1(p1, p2):
    time.sleep(1)
    return 1
print scan1(1, 2)

# @logtimewithname()
@logtimewithname(u"扫描")
def scan2(p1, p2):
    time.sleep(1)
    return 2

print scan2(1, 2)

@timelimited(2)
def scan3():
    time.sleep(3)

scan3()
"""

class logger:
    '''
    日志输出函数，使用示例：
    import star.debug
    logger = star.debug.logger().getlogger()
    logger.error('error')
    '''
    def __init__(self, name = 'log'):
        self.log = logging.getLogger(name)
        self.log.setLevel(logging.DEBUG)

        fmt = '%(asctime)s %(thread)d|%(threadName)s %(filename)s:%(lineno)s %(levelname)s %(name)s :%(message)s'
        formatter = logging.Formatter(fmt)

        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        ch.setLevel(logging.DEBUG)
        fh = logging.FileHandler(name + '.log')
        fh.setFormatter(formatter)
        fh.setLevel(logging.DEBUG)

        self.log.addHandler(fh)
        self.log.addHandler(ch)
    def getlogger(self):
        return self.log


class timer:
    '''
    时间记录者，使用示例：
    timer = star.debug.timer()
    do something..
    print u'耗时：' + str(timer.stop()) + ' s'
    '''
    def __init__(self):
        self.begintime = datetime.datetime.now()
        self.endtime = self.begintime
    def start(self):
        self.begintime = datetime.datetime.now()
    def stop(self):
        self.endtime = datetime.datetime.now()
        cost = self.endtime - self.begintime
        return cost.seconds
