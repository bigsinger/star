# coding: utf-8

import os
import sys
import traceback
import logging
import fnmatch
from star.ZipFileHelper import ZipFileHelper


# noinspection PyInterpreter
class PublishHelper:
    def __init__(self, **karg):
        """
        功能：初始化函数，设置想要include的文件和exclude文件
        :param karg: 包含两个关键字参数，exclude 和include
        exclude :要排除的文件夹或 文件，可使用通配符 list类型
        include :要包含的文件夹或文件，可使用通配符 list类型
        两者同时存在时，在include 中去除exclude
        """
        self._exclude = []
        self._include = []
        self._abs_exclude = []
        self._abs_include = []
        if 'include' in karg.keys():
            include_list = karg.get('include')
            if isinstance(include_list, list):
                self._include = include_list
            else:
                logging.error('[PublishHelper.init] 初始化失败，include 参数类型不正确')
        if 'exclude' in karg.keys():
            exclude_list = karg.get('exclude')
            if isinstance(exclude_list, list):
                self._exclude = exclude_list
            else:
                logging.error('[PublishHelper.init] 初始化失败，exclude 参数类型不正确')

    def pack_file(self, dir_path):
        """
        功能：根据exclude 和include 打包指定目录下文件，若exclude 和include均为空则包含所有文件
        :param dir_path: 要打包的目录路径，str类型
        :return:成功返回True，否则返回False
        """
        if not isinstance(dir_path, str):
            logging.error('[PublishHelper.pack_file] 打包失败，dir_path 参数类型不正确')
            return False
        if not os.path.isdir(dir_path):
            logging.error('[PublishHelper.pack_file] 打包失败，dir_path 文件类型不正确')
            return False
        self._abs_include = self.__abs_path(dir_path, self._include)
        self._abs_exclude = self.__abs_path(dir_path, self._exclude)
        all_file_name = []
        if len(self._include) == 0 and len(self._exclude) == 0:
            for dirpath, dirnames, filenames in os.walk(dir_path):
                for file_name in filenames:
                    all_file_name.append(os.path.join(dirpath, file_name))
        else:
            self.__dfs_get_file(dir_path, all_file_name)
        zip_name = dir_path + '.zip'
        result = ZipFileHelper.zip_file(all_file_name, zip_name)
        if result is True:
            return True
        else:
            return False

    def set_include(self, include_list):
        """
        允许用户中途更改include
        :param include_list:
        :return:
        """
        self._include = include_list

    def set_exclude(self, exclude_list):
        """
        允许用户中途更改exclude
        :param exclude_list:
        :return:
        """
        self._exclude = exclude_list

    def __dfs_get_file(self, input_path, all_file_name):
        """
        功能：递归遍历input_path下所有文件
        :param input_path: 文件夹路径
        :param all_file_name: 文件夹内全部文件名列表
        :return:
        """
        files = os.listdir(input_path)
        for file in files:
            file_path = os.path.join(input_path, file)
            if os.path.isdir(file_path):
                if file_path in self._abs_include:
                    # 添加文件夹中非exclude文件 到all_file_name
                    for dirpath, dirnames, filenames in os.walk(file_path):
                        for file_name in filenames:
                            if self.__not_exclude_file(os.path.join(dirpath, file_name)):
                                all_file_name.append(os.path.join(dirpath, file_name))
                elif file_path not in self._abs_exclude:
                    self.__dfs_get_file(file_path, all_file_name)
            else:
                if len(self._include) != 0:
                    # 如果在include 且不在exclude 则添加进all_file_name
                    for case in self._abs_include:
                        if fnmatch.fnmatch(file_path, case):
                            if self.__not_exclude_file(file_path):
                                all_file_name.append(file_path)
                                break
                elif len(self._exclude) != 0:
                    # 如果不在exclude_list则添加
                    if self.__not_exclude_file(file_path):
                        all_file_name.append(file_path)

    def __not_exclude_file(self, file_path):
        if len(self._exclude) != 0:
            is_add = True
            for case in self._abs_exclude:
                if fnmatch.fnmatch(file_path, case):
                    is_add = False
                    break
            if is_add:
                return True
            return False
        return True

    def __abs_path(self, dir_path, rel_path):
        abs_path = []
        for file in rel_path:
            abs_path.append(os.path.join(dir_path, file))
        return abs_path


def getthispath():
    path = sys.path[0]
    #判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.split(path)[0]


'''
如果不能直接执行本py文件，可以建一个bat文件来调用Python执行该脚本：
set dir=%~dp0

cd /d %dir%
python PublishHelper.py
'''
def main():
    include_list = ['*.py']
    exclude_list = ['__init__.py', '*.pyc']
    dir_path = os.path.join(getthispath(), '这里填压缩目录相对路径')
    ph = PublishHelper(include=include_list, exclude=exclude_list)
    ph.pack_file(dir_path)


if __name__ == '__main__':
    try:
        ret = main()
    except:
        print(traceback.format_exc())
        os.system('pause')