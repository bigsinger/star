# coding: utf-8

import os
import sys
import winreg
import logging
import traceback
import subprocess


'''
ref：Devenv 命令行开关 https://msdn.microsoft.com/zh-cn/library/xee0c8y7.aspx
'''


class VSBuildHelper:
    def __init__(self):
        self._sln = None
        self._current_devenv = None
        self._vs_ver_map = {'2017': '15.0', '2015': '14.0', '2010': '10.0', '2008': '9.0'}

    def get_vs_2017(self):
        return self.get_vs('2017')

    def get_vs_2015(self):
        return self.get_vs('2015')

    def get_vs_2010(self):
        return self.get_vs('2010')

    def get_vs_2008(self):
        return self.get_vs('2008')

    def set_sln(self, sln_path):
        if os.path.exists(sln_path):
            self._sln = sln_path
        else:
            logging.error('设置的sln文件不存在：' + sln_path)

    def switch_vs(self, ver):
        self._current_devenv = self.get_vs(ver)
        if self._current_devenv is None or not os.path.exists(self._current_devenv):
            logging.error('VisualStudio版本切换失败，未能找到指定版本：' + ver)

    def clean(self):
        subprocess.call([self._current_devenv, self._sln, "/Clean"])

    def build(self, args_list):
        new_args_list = [self._current_devenv, self._sln, '/Build'] + args_list
        print(new_args_list)
        subprocess.call(new_args_list)

    def rebuild(self, args_list):
        new_args_list = [self._current_devenv, self._sln, '/Rebuild'] + args_list
        print(new_args_list)
        subprocess.call(new_args_list)

    def get_vs(self, ver):
        ver_inner = self._vs_ver_map.get(ver)
        if ver_inner is None:
            logging.error('未发现指定vs版本的内部版本号，请配置：' + ver)
            return
        try:
            # get visual studio install path
            reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\WOW6432Node\\Microsoft\\VisualStudio\\SxS\\VS7')
            reg_value, reg_type = winreg.QueryValueEx(reg_key, ver_inner)
            winreg.CloseKey(reg_key);
            if reg_type != winreg.REG_SZ:
                logging.error('错误的注册表数值类型：' + str(reg_type))
                return None
            return os.path.join(reg_value, "Common7", "IDE", "devenv.com")
        except Exception as e:
            logging.error(traceback.format_stack())
            return None