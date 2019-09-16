# coding: utf-8

import os
import sys
import shutil
import traceback


def get_this_path():
    '''
    :return: 返回当前脚本所在目录的全路径，末尾不带\
    在使用os.path.join函数时，后面的路径也不能以\开头，例如：
    os.path.join(getthispath(), 'tools\\tools.exe')     √
    os.path.join(getthispath(), '\\tools\\tools.exe')   ×
    或者直接调用 os.path.abspath(os.path.dirname(__file__))，例如在F:\osopen\studypython\Main.py中调用则返回F:\osopen\studypython；
    若调用os.path.dirname(__file__)则返回F:/osopen/studypython
    '''
    path = sys.path[0]
    #判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.split(path)[0]

def get_parent_path(filepath):
    '''
    相当于os.path.dirname的改进版，filepath末尾是否带反斜杠都可以正确获取
    :param filepath:
    :return: 获取路径的父目录，末尾不带\
    '''
    if not filepath:
        return None
    lsPath = os.path.split(filepath)
    # print(lsPath)
    # print("lsPath[1] = %s" %lsPath[1])
    if lsPath[1]:
        return lsPath[0]
    lsPath = os.path.split(lsPath[0])
    return lsPath[0]

def get_dirname(filepath):
    '''
    仅获取
    :param filepath:
    :return: 仅获取文件夹的名字（非全路径）, 无论是否带\都可以准确获取
    '''
    if not filepath:
        return None
    lsPath = os.path.split(filepath)
    if lsPath[1]:
        return lsPath[1]
    else:
        return os.path.split(lsPath[0])[1]

# 获取文件的目录、名称、扩展名
def get_dir_name_ext(filen_path):
    (dir, file_name) = os.path.split(filen_path)
    (name, ext) = os.path.splitext(file_name)
    return dir, name, ext


def get_desktop_path():
    '''
    返回桌面全路径，末尾不带\
    '''
    import winreg
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
    return winreg.QueryValueEx(key, 'Desktop')[0]

def get_desktop_path2():
    '''
    返回桌面全路径，末尾不带\
    '''
    from win32com.shell import shell
    from win32com.shell import shellcon

    result = None
    try:
        from win32com.shell import shell
        from win32com.shell import shellcon
        desktop_path = shell.SHGetPathFromIDList(shell.SHGetSpecialFolderLocation(0, shellcon.CSIDL_DESKTOP))
        result = desktop_path.decode()
    except:
        print(traceback.format_exc())
        result = None
    return result

def makedirs(to_create_path):
    '''
    创建多级目录，比如c:\\test1\\test2,如果test1 test2都不存在，都将被创建
    :param to_create_path:
    :return:
    '''
    path_create = to_create_path
    if os.sep == '\\':
        path_create = path_create.replace('/', os.sep)
    dirs = path_create.split(os.sep)
    path = ''
    for dir in dirs:
        dir += os.sep
        path = os.path.join(path, dir)
        if not os.path.exists(path):
            os.mkdir(path, 0o777)

    if not os.path.exists(to_create_path):
        return False
    return True

def deletedirs(to_del_dirs):
    '''
    删除目录
    :param to_del_dirs:
    :return:
    '''
    if os.path.exists(to_del_dirs):
        shutil.rmtree(to_del_dirs)
        return os.path.exists(to_del_dirs) is False
    else:
        return True

def get_filesize(f):
    '''
    获取一个文件的大小
    :param f:
    :return:
    '''
    return os.path.getsize(f)

def getdirsize(path):
    '''
    目录下文件大小累加
    :param path:
    :return:
    '''
    size = 0
    for root, dirs, files in os.walk(path, True):
        size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
        return size

def deletefile(to_del_file):
    if os.path.exists(to_del_file):
         os.remove(to_del_file)
         return os.path.exists(to_del_file) is False
    else:
        return True

def copyfile(sourceDir, destDir):
    if deletefile(destDir):
        shutil.copy(sourceDir, destDir)
        return os.path.exists(destDir)
    else:
        return False

def movefile(sourceDir, destDir):
    if deletefile(destDir):
        shutil.move(sourceDir, destDir)
        return os.path.exists(destDir)
    else:
        return False
    

def isendwith(file, *endstring):
    '''
    判断一个文件路径名是否为某某结尾，这个可以测试文件是否为指定类型的文件
    print(star.file.isendwith(filename, "txt", "apk"))
    :param file: 
    :param endstring: 
    :return: 
    '''
    return True in map(file.endswith, endstring)


# filelist = Utils.getfilenamelistformdir(metainfPath, ['.rsa', '.dsa'])
def getfilenamelistformdir(path, endstringlist):
    retlist = []
    try:
        if os.path.exists(path):
            flist = os.listdir(path)
            for f in flist:
                if os.path.splitext(f)[1].lower() in endstringlist:
                    retlist.append(f)
    except Exception as e:
        print(traceback.format_exc())
        return []
    return retlist

# smaliFileList = Utils.getfilelistfromdir(outDir, '.smali')
def getfilelistfromdir(rootPath, endstring):
    fileList = []
    try:
        for root, dirs, files in os.walk(rootPath):
            for name in files:
                lowerName = name.lower()
                if lowerName.endswith(endstring):
                    fileList.append(os.path.join(root, name))
    except Exception as e:
        print(traceback.format_exc())
        return []
    return fileList