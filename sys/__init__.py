# coding: utf-8

import os
import sys
import time
import traceback
import subprocess
from subprocess import check_output, CalledProcessError, call


'''
系统相关
import star.sys
star.sys.methodname
'''


#获取本机IP import socket
def getip():
    ip = socket.gethostbyname(socket.gethostname())
    return str(ip)

def getips():
    ips = socket.gethostbyname_ex(socket.gethostname())
    print(ips)

# import ctypes
# import struct
def getmac():
    """ Returns the MAC address of a network host, requires >= WIN2K.
        ref: http://blog.csdn.net/toontong/article/details/7088777
    """
    # Check for api availability
    try:
        SendARP = ctypes.windll.Iphlpapi.SendARP
    except:
        raise NotImplementedError('Usage only on Windows 2000 and above')

    hostip = socket.gethostbyname(socket.gethostname())
    inetaddr = ctypes.windll.wsock32.inet_addr(hostip)

    buffer = ctypes.c_buffer(6)
    addlen = ctypes.c_ulong(ctypes.sizeof(buffer))
    if SendARP(inetaddr, 0, ctypes.byref(buffer), ctypes.byref(addlen)) != 0:
        raise WindowsError('Retreival of mac address(%s) - failed' % hostip)

    # Convert binary data into a string.
    mac = ':'.join('%02X'%i for i in struct.unpack('BBBBBB', buffer))
    return mac


def get_mac():
    '''
    获取uuid或mac
    '''
    import uuid
    mac = uuid.uuid1().hex[-12:]
    return mac


def setclipboard2(s):
    '''
    pip install clipboard
    clipboard.copy('hello')
    :param s: 
    :return: 
    '''
    import pyperclip
    pyperclip.copy(s)

def getclipboard(s):
    import pyperclip
    text = pyperclip.paste()
    return text

def setclipboard2(s):
    import win32clipboard
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(s)
    win32clipboard.CloseClipboard()

def getclipboard2():
    import win32clipboard
    s = None
    win32clipboard.OpenClipboard()
    if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_TEXT):
        s = win32clipboard.GetClipboardData(win32clipboard.CF_TEXT)
    win32clipboard.CloseClipboard()
    return s

#获取当前时间戳，10位
def gettime10():
    return str(int(time.time()))

#获取当前时间戳，13位
def gettime13():
    return "%d" % (time.time() * 1000)

#获取当前时间
def getcurrenttime():
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

def run111(cmd):
    result = os.popen(cmd)
    return result.readlines()

# 直接输出到默认输出，调用者不获取其输出内容.同步调用。
def runS(args):
    p = subprocess.Popen(args, shell=True)
    p.communicate()

def run(args):
    if 'Windows' in platform.system():
        # command = args.encode("utf-8")
        # command = command.decode("utf-8").encode("gbk")
        command = args
    if 'Linux'in platform.system():
        command = args
    p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    # ret = p.wait() #该方法有问题
    ret = p.communicate()
    output = Utils.out2str(p.stdout.readlines())
    error = Utils.out2str(p.stderr.readlines())
    # return output if ret is 0 else error
    return star.commandResult2Str(ret)

def runcmd(adb_cmd):
    """
    Format adb command and execute it in shell
    :param adb_cmd: list adb command to execute
    :return: string '0' and shell command output if successful, otherwise
    raise CalledProcessError exception and return error code
    """
    t = tempfile.TemporaryFile()
    final_adb_cmd = []
    for e in adb_cmd:
        if e != '':  # avoid items with empty string...
            final_adb_cmd.append(e)  # ... so that final command doesn't
            # contain extra spaces
    # print('\n*** Executing: ' + ' '.join(adb_cmd))

    try:
        output = check_output(final_adb_cmd, stderr=t)
    except CalledProcessError as e:
        t.seek(0)
        result = e.returncode, to_str(t.read())
        print(result)
    else:
        result = 0, to_str(output)
        # print('\n' + result[1])

    return result

def runcmd2(adb_cmd):
    """
    Format adb command and execute it in shell
    :param adb_cmd: list adb command to execute
    :return: string '0' and shell command output if successful, otherwise
    raise CalledProcessError exception and return error code
    """
    t = tempfile.TemporaryFile()
    final_adb_cmd = []
    for e in adb_cmd:
        if e != '':  # avoid items with empty string...
            final_adb_cmd.append(e)  # ... so that final command doesn't
            # contain extra spaces
    # print('\n*** Executing ' + ' '.join(adb_cmd) + ' ' + 'command')

    try:
        p = subprocess.Popen(final_adb_cmd, stdout=subprocess.PIPE, shell=True)
        s = p.stdout.read()
        p.stdout.close()
        retval = p.wait()
        return retval,str(s,"utf-8")
    except CalledProcessError as e:
        t.seek(0)
        result = e.returncode, str(t.read(),"utf-8")
        print(result)
    else:
        result = 0, str(output,"utf-8")
        # print('\n' + result[1])

    return result

def run_cmd_asyn(adb_cmd):
    ret = 0
    msg = None
    """
    Format adb command and execute it in shell
    :param adb_cmd: list adb command to execute
    :return: string '0' and shell command output if successful, otherwise
    raise CalledProcessError exception and return error code
    """
    final_adb_cmd = []
    for e in adb_cmd:
        if e != '':  # avoid items with empty string...
            final_adb_cmd.append(e)  # ... so that final command doesn't
            # contain extra spaces
    # print('\n*** Executing: ' + ' '.join(adb_cmd))
    print('\n*** Executing: ' + " ".join('%s' % id for id in adb_cmd))

    try:
        print(final_adb_cmd)
        p = subprocess.Popen(final_adb_cmd, stdout=subprocess.PIPE, shell=False)
        # s = p.stdout.read()
        # p.stdout.close()
        # retval = p.wait()
        # return retval,s
    except Exception as e:
        ret = -1
        msg = traceback.format_exc()
        pass
    return ret, msg

def runcmd2file(adb_cmd, dest_file_handler):
    """
    Format adb command and execute it in shell and redirects to a file
    :param adb_cmd: list adb command to execute
    :param dest_file_handler: file handler to which output will be redirected
    :return: string '0' and writes shell command output to file if successful, otherwise
    raise CalledProcessError exception and return error code
    """
    t = tempfile.TemporaryFile()
    final_adb_cmd = []
    for e in adb_cmd:
        if e != '':  # avoid items with empty string...
            final_adb_cmd.append(e)  # ... so that final command doesn't
            # contain extra spaces
    print('\n*** Executing ' + ' '.join(adb_cmd) + ' ' + 'command')

    try:
        output = call(final_adb_cmd, stdout=dest_file_handler, stderr=t)
    except CalledProcessError as e:
        t.seek(0)
        result = e.returncode, t.read()
    else:
        result = output
        dest_file_handler.close()

    return result


def MultiProcess():
    '''
    多进程运行
    :return: 
    '''
    from multiprocessing import Process
    for _ in range(5):
        p = Process(target=core.Main, args=(url, proxy, headers, level, cookie, method))
        p.start()
        p.join()

def redirect_std(file_name): 
    '''
    重定向标准输入输出流, eg.
    import star.sys
    star.sys.redirect_std('log.txt')
    print('test')
    :param file_name: 
    :return: 
    '''
    f = open(file_name, 'a')
    # denature std fd's
    os.dup2(f.fileno(), sys.stdin.fileno())
    os.dup2(f.fileno(), sys.stdout.fileno())
    os.dup2(f.fileno(), sys.stderr.fileno())
    f.close()
    

def load_modules():
    """
    Read the INDEX_FILE and load all modules. Used by client and server.
    """
    # a text file named INDEX_FILE is created during the build process that
    # lists the names of all the modules in the modules/ directory. this file
    # is needed because the package has no way to know the names of the modules
    # to load otherwise. it can't use os.listdir('modules') because in
    # production, this is executing in a zip file, so the modules aren't on the
    # filesystem
    import pkg_resources
    from importlib import import_module
    
    for fname in pkg_resources.resource_string(__name__, 'modindex.txt').split():
        fname = fname.decode()
        print(fname)
        if fname.endswith('.py'):
            mod = os.path.splitext(fname)[0]

            # __init__ isn't a command, but we need it for modules to work correctly
            if mod == '__init__':
                continue
            else:
                ...

            import_module('modules.' + mod)
            # TODO : validate module structure for required functions

def _loading():
    import itertools
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if loading == True:
            break
        sys.stdout.write('\rLoading...' + c)
        sys.stdout.flush()
        time.sleep(0.1)
        
def loading():
    import threading
    t = threading.Thread(target=_loading)
    t.start()

