# coding: utf-8

import os
import winreg
import traceback
import itertools


'''
这是一个获取程序安装目录的助手
'''


class InstallPathHelper:
    def __init__(self, app_name):
        self._app_name = app_name.lower()

    def get_path(self):
        file_path = None
        file_path = self.get_path_from_muicache()
        if file_path:
            return file_path
        file_path = self.get_path_from_firewall_rules()
        if file_path:
            return file_path
        file_path = self.get_path_from_Applications()

        return file_path

    def get_path_from_firewall_rules(self):
        '''通过注册表里的防火墙规则来查找'''
        file_path = None
        reg_key = None

        try:
            reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, '''SYSTEM\CurrentControlSet\services\SharedAccess\Parameters\FirewallPolicy\FirewallRules''')
            for i in itertools.count():
                value_name, value_data, value_index = winreg.EnumValue(reg_key, i)
                value_lower = value_name.lower()
                if self._app_name in value_lower:
                    # print(value_name)   # TCP Query User{68AFAC41-33D8-42AF-9C15-8D96D3637598}D:\jetbrains\goland 2019.2.1\bin\goland64.exe
                    pos = value_name.find('}')
                    if pos > 0:
                        file_path = value_name[pos + 1:]
                        if os.path.exists(file_path):
                            print(file_path)
                            break
        except Exception as e:
            # print(traceback.format_stack())
            ...
        finally:
            winreg.CloseKey(reg_key)
        return file_path

    def get_path_from_muicache(self):
        '''通过注册表里的缓存记录查找'''
        file_path = None
        file_path = self._get_path_from_muicache(winreg.HKEY_USERS,'''S-1-5-21-1380817616-3362833225-652976467-13993\Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\MuiCache''')
        if not file_path:
            file_path = self._get_path_from_muicache(winreg.HKEY_USERS,
                                                     '''S-1-5-21-1380817616-3362833225-652976467-13993_Classes\Local Settings\Software\Microsoft\Windows\Shell\MuiCache''')
        return file_path


    def _get_path_from_muicache(self, reg_root_key, reg_sub_path):
        '''通过注册表里的缓存记录查找'''
        file_path = None
        reg_key = None

        try:
            reg_key = winreg.OpenKey(reg_root_key, reg_sub_path)
            for i in itertools.count():
                value_name, value_data, value_index = winreg.EnumValue(reg_key, i)
                value_lower = value_name.lower()
                if self._app_name in value_lower:
                    file_path = value_name
                    if os.path.exists(file_path):
                        print(file_path)
                        break
        except Exception as e:
            # print(traceback.format_stack())
            ...
        finally:
            if reg_key:
                winreg.CloseKey(reg_key)
        return file_path

    def get_path_from_Applications(self):
        '''通过注册表里的shell\open\command查找'''
        file_path = None
        file_path = self._get_path_from_shell_open_command(winreg.HKEY_CLASSES_ROOT, 'Applications')
        if file_path:
            return file_path
        file_path = self._get_path_from_shell_open_command(winreg.HKEY_LOCAL_MACHINE, '''SOFTWARE\Classes\Applications''')
        if file_path:
            return file_path
        file_path = self._get_path_from_shell_open_command(winreg.HKEY_LOCAL_MACHINE, '''SOFTWARE\Classes''')

        return file_path

    def _get_path_from_shell_open_command(self, reg_root_key, reg_sub_path_to_enum):
        '''通过注册表里的shell\open\command查找'''
        file_path = None
        reg_key = None

        try:
            reg_key = winreg.OpenKey(reg_root_key, reg_sub_path_to_enum)
            for i in itertools.count():
                subkeyname = winreg.EnumKey(reg_key, i)
                subkey = None
                value_name = None
                try:
                    subkey = winreg.OpenKey(reg_key, subkeyname + '''\shell\open\command''')
                    value_name = winreg.QueryValue(subkey, None)
                except Exception as e2:
                    ...
                else:
                    value_lower = value_name.lower()
                    if self._app_name in value_lower:
                        pos = value_name.find('"')
                        if pos != -1:
                            pos2 = value_name.find('"', pos + 1)
                            if pos2 != -1:
                                file_path = value_name[pos + 1:pos2]
                                if os.path.exists(file_path):
                                    print(file_path)
                                    break
                finally:
                    if subkey:
                        winreg.CloseKey(subkey)
        except Exception as e:
            # print(traceback.format_stack())
            ...
        finally:
            if reg_key:
                winreg.CloseKey(reg_key)
        return file_path


if __name__ == '__main__':
    helper = InstallPathHelper('idea')
    file_path = helper.get_path()

