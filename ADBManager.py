#coding:utf-8
import io
import os
import re
import star
import logging
import subprocess
from PIL import Image
from io import StringIO
from star.APK import APK

'''
负责ADB相关的操作
参考：https://github.com/vmalyi/adb_android
'''

ADB_COMMAND_PREFIX = 'adb'
ADB_COMMAND_SHELL = 'shell'
ADB_COMMAND_PULL = 'pull'
ADB_COMMAND_PUSH = 'push'
ADB_COMMAND_RM = 'rm -r'
ADB_COMMAND_CHMOD = 'chmod -R 777'
ADB_COMMAND_UNINSTALL = 'uninstall'
ADB_COMMAND_INSTALL = 'install'
ADB_COMMAND_UNINSTALL = 'uninstall'
ADB_COMMAND_FORWARD = 'forward'
ADB_COMMAND_DEVICES = 'devices'
ADB_COMMAND_GETSERIALNO = 'get-serialno'
ADB_COMMAND_WAITFORDEVICE = 'wait-for-device'
ADB_COMMAND_KILL_SERVER = 'kill-server'
ADB_COMMAND_START_SERVER = 'start-server'
ADB_COMMAND_GET_STATE = 'get-state'
ADB_COMMAND_SYNC = 'sync'
ADB_COMMAND_VERSION = 'version'
ADB_COMMAND_BUGREPORT = 'bugreport'


SCALE = 0.5

class ADBManager:
    def __init__(self):
        self._deviceSelected = None
        self._devices = None #{[0].name = "", [0].info = "", }
        self.get_devices()
        if len(self._devices)==1:
            self.select(0)
        elif len(self._devices)==0:
            print("no devices")
        self._sdk_version = None
        self._adb_path = None

    # 获取ADB文件的路径，默认使用环境变量中的路径
    def get_adb_path(self):
        if self._adb_path is None:
            found = False
            for root in os.environ.get('path').split(';'):
                adb_path = os.path.join(root, 'adb.exe')
                if os.path.exists(adb_path):  # 优先使用环境变量中指定的 adb
                    self._adb_path = adb_path
                    found = True
                    break
            if found is False:
                cur_path = os.path.dirname(os.path.abspath(__file__))
                self._adb_path = os.path.join(cur_path, 'tools', 'adb.exe')
        return self._adb_path

    # 获取ADB工具的版本
    def get_adb_version(self):
        adb_full_cmd = [ADB_COMMAND_PREFIX, ADB_COMMAND_VERSION]
        code, ret = star.runcmd(adb_full_cmd)
        try:
            pattern = re.compile(r"version\s(.*?)\s")
            version = pattern.search(ret).group(1)
        except Exception as e:
            print(e)
            version = None
        return version

    # 获取SDK版本（int类型数值），如：16
    def get_sdk_version(self):
        if not self._sdk_version:
            code, self._sdk_version = self.runshellcmd('getprop ro.build.version.sdk')
            if code == 0:
                self._sdk_version = int(self._sdk_version)
        return self._sdk_version

    def is_rooted(self):
        result = self.runshellcmd('id')
        logger.debug('is_rooted: %s' % result)
        return result.find('uid=0(root)') >= 0

    def is_no_device(self):
        return len(self.get_devices()) == 0

    def is_connected(self, serial_no):
        return serial_no in self.get_devices()

    def get_devices(self):
        """
        Return a list containing all connected ADB-devices.
        """
        devices = {}
        out = subprocess.check_output([ADB_COMMAND_PREFIX, "devices", "-l"],
                                      universal_newlines=True)
        self.check_output(out)
        ADB_DEV_PATTERN = re.compile(r"(\S*?)\s*?device\s")
        for line in out.split('\n'):
            matched = ADB_DEV_PATTERN.search(line)
            if matched:
                name = matched.group(1)
                devices[name] = line
        self._devices = devices
        return devices

    def select(self, name_or_id):
        """
        Specify the device name to target
        example: set_target_device('emulator-5554')
        """
        if not self._devices:
            self.get_devices()

        # 是否有设备链接
        if not self._devices:
            logging.error('no devices connected!')
            return False

        if name_or_id is None:
            self.__error = 'Must get device list first'
            logging.error("[!] Device not found in device list")
            return False

        if isinstance(name_or_id, int):
            index = 0
            for name, info in self._devices.items():
                if index==name_or_id:
                    self._deviceSelected = name
                    break
                index = index + 1
        else:
            for name, info in self._devices.items():
                if info.find(name_or_id)>=0:
                    self._deviceSelected = name
                    break
        # print("Target device select: %s" % self.get_device_selected())
        return self._deviceSelected is not None

    # 为ADB命令添加一个设备选择，也即-s参数
    def gen_adb_args(self, cmd):
        args = [adb_path, cmd]
        if self._device_name:
            args = [self._adb_path, '-s', self._deviceSelected, cmd]
        return  args

    def get_device_selected(self):
        """
        Returns the selected device to work with
        """
        if self._deviceSelected == None:
            print("[*] No device target set")

        return self._deviceSelected

    def get_model(self):
        """
        Get Model name from taget device
        """
        model = None
        if self._deviceSelected is None:
            print("No device target set")
        else:
            pattern = re.compile(r"model:(.+)\sdevice")
            matched = pattern.search(self._devices[self._deviceSelected])
            if matched:
                model = matched.group(1)
        return model

    def get_serialno(self):
        """
        Get serial number for all available target devices
        :return: result of star.runcmd() execution
        """
        cmds = [ADB_COMMAND_PREFIX]
        if len(self._devices)>1 or not self._deviceSelected:
            cmds.append("-s")
            cmds.append(self._deviceSelected)
        cmds.append(ADB_COMMAND_GETSERIALNO)
        code,ret = star.runcmd(cmds)
        if code==0:
            return ret
        else:
            return None

    def get_build_props(self):
        """
        Get contents of /system/build.prop as dict.
        Return dictionary like: Property => Value
        """
        build_props = {}
        cmds = [ADB_COMMAND_PREFIX]
        if len(self._devices) > 1 or not self._deviceSelected:
            cmds.append("-s")
            cmds.append(self._deviceSelected)
        cmds.append("shell")
        cmds.append("cat /system/build.prop")
        out = subprocess.check_output(cmds, universal_newlines=True)
        for line in out.split('\n'):
            if line == '':
                continue
            prop = line.split('=')
            if not prop[0].startswith('#'):
                build_props[prop[0]] = prop[1]
        return build_props

    def bugreport(self, dest_file="default.log"):
        """
        Prints dumpsys, dumpstate, and logcat data to the screen, for the purposes of bug reporting
        :return: result of star.runcmd() execution
        """
        adb_full_cmd = [ADB_COMMAND_PREFIX, ADB_COMMAND_BUGREPORT]
        try:
            dest_file_handler = open(dest_file, "w")
        except IOError:
            print("IOError: Failed to create a log file")

        # We have to check if device is available or not before executing this command
        # as adb bugreport will wait-for-device infinitely and does not come out of
        # loop
        # Execute only if device is available only
        if _isDeviceAvailable():
            result = star.runcmd_to_file(adb_full_cmd, dest_file_handler)
            return (result, "Success: Bug report saved to: " + dest_file)
        else:
            return (0, "Device Not Found")


    def push(self, src, dest):
        """
        Push object from host to target
        :param src: string path to source object on host
        :param dest: string destination path on target
        :return: result of star.runcmd() execution
        """
        adb_full_cmd = [ADB_COMMAND_PREFIX, ADB_COMMAND_PUSH, src, dest]
        return star.runcmd(adb_full_cmd)


    def pull(self, src, dest):
        """
        Pull object from target to host
        :param src: string path of object on target
        :param dest: string destination path on host
        :return: result of star.runcmd() execution
        """
        adb_full_cmd = [ADB_COMMAND_PREFIX, ADB_COMMAND_PULL, src, dest]
        return star.runcmd(adb_full_cmd)



    def shell(self, cmd):
        """
        Execute shell command on target
        :param cmd: string shell command to execute
        :return: result of star.runcmd() execution
        """
        cmds = [ADB_COMMAND_PREFIX]
        if len(self._devices) > 1 or not self._deviceSelected:
            cmds.append("-s")
            cmds.append(self._deviceSelected)
        cmds.append(ADB_COMMAND_SHELL)
        cmds.append(cmd)
        return star.runcmd(cmds)


    def install(self, apk, opts = None):
        """
        Install *.apk on target
        :param apk: string path to apk on host to install
        :param opts: list command options (e.g. "-r", "-a")
        :return: result of star.runcmd() execution
        """
        cmds = [ADB_COMMAND_PREFIX]
        if len(self._devices) > 1 or not self._deviceSelected:
            cmds.append("-s")
            cmds.append(self._deviceSelected)
        cmds.append(ADB_COMMAND_INSTALL)
        if opts is not None:
            cmds.append(opts)
        cmds.append(apk)
        code, ret = star.runcmd(cmds)
        if ret.find('Failure') != -1:
            pattern = re.compile('Failure(.*?)\r\n', re.U | re.S)
            result = pattern.search(ret)
            reason = ''
            if result is not None:
                reason = result.group(1).strip()
            logging.error('[x] Failure ' + reason)
            return False
        return True


    def uninstall(self, app, opts=[]):
        """
        Uninstall app from target
        :param app: app name to uninstall from target (e.g. "com.example.android.valid")
        :param opts: list command options (e.g. ["-r", "-a"])
        :return: result of star.runcmd() execution
        """
        adb_full_cmd = [ADB_COMMAND_PREFIX, ADB_COMMAND_UNINSTALL, self._convert_opts(opts), app]
        return star.runcmd(adb_full_cmd)

    def wait_for_device(self):
        """
        Block execution until the device is online
        :return: result of star.runcmd() execution
        """
        adb_full_cmd = [ADB_COMMAND_PREFIX, ADB_COMMAND_WAITFORDEVICE]
        return star.runcmd(adb_full_cmd)


    def sync(self):
        """
        Copy host->device only if changed
        :return: result of star.runcmd() execution
        """
        adb_full_cmd = [ADB_COMMAND_PREFIX, ADB_COMMAND_SHELL ,ADB_COMMAND_SYNC]
        return star.runcmd(adb_full_cmd)


    def start_server(self):
        """
        Startd adb server daemon on host
        :return: result of star.runcmd() execution
        """
        adb_full_cmd = [ADB_COMMAND_PREFIX, ADB_COMMAND_START_SERVER]
        return star.runcmd(adb_full_cmd)


    def kill_server(self):
        """
        Kill adb server daemon on host
        :return: result of star.runcmd() execution
        """
        adb_full_cmd = [ADB_COMMAND_PREFIX, ADB_COMMAND_KILL_SERVER]
        return star.runcmd(adb_full_cmd)


    def get_state(self):
        """
        Get state of device connected per adb
        :return: result of star.runcmd() execution
        """
        adb_full_cmd = [ADB_COMMAND_PREFIX, ADB_COMMAND_GET_STATE]
        return star.runcmd(adb_full_cmd)


    def _convert_opts(self, opts):
        """
        Convert list with command options to single string value
        with 'space' delimeter
        :param opts: list with space-delimeted values
        :return: string with space-delimeted values
        """
        return ' '.join(opts)

    def start(self, apkfile, force = True):
        '''
        运行一个APK，首先解析包名和activity，force为真时，如果未安装则强制安装，如果已经打开了则重新打开。
        :param apkfile: APK全路径
        :param force: 是否强制运行
        :return:
        '''
        apk = APK(apkfile)
        main_activity = apk.get_main_activity()
        package = apk.get_package()
        code, ret = self.runapp(package, main_activity)
        if force and ret:
            if ret.find("does not exist")>=0:
                code, ret = self.install(apkfile)
                if code==0:
                    code, ret = self.runapp(package, main_activity)
            elif ret.find("brought to the front")>=0:
                self.stopapp(package)
                code, ret = self.runapp(package, main_activity)
        return (code, ret)

    def runapp(self, package, activity):
        return self.shell('am start -W -n ' + package + '/' + activity)
    def startapp(self, package, activity):
        return self.runapp(package, activity)
    def stopapp(self, package):
        return self.shell('am force-stop ' + package)
    def listpackages(self):
        return self.shell('pm list packages')



    def check_output(self, out):
        """
        Check if the response of a command is valid.
        """
        if out == "error: device not found":
            sys.exit("Error connecting to device!")

    def reboot(self, option):
        if option == "system":
            subprocess.call([ADB_COMMAND_PREFIX, "reboot"])
        elif option in ("recovery", "bootloader"):
            subprocess.call([ADB_COMMAND_PREFIX, "reboot", option])
        else:
            print("Invalid reboot-option!")

    def reboot_wait_completed(self, _timeout=180):
        '''等待手机启动完成'''
        # 手机重启完后 adbd Insecure 启动时会导致adb断开重连，qt4a框架己经实现了adb root权限功能，测试手机请不要安装 adbd Insecure
        import time
        cmds = self.gen_adb_args('wait-for-_adb')
        star.runcmd(cmds, timeout=_timeout)
        boot_complete = False
        attempts = 0
        wait_period = 5
        while not boot_complete and (attempts * wait_period) < _timeout:
            code, output = self.runshellcmd("getprop sys.boot_completed", retry_count=1)
            output = output.strip()
            if output == "1":
                boot_complete = True
            else:
                time.sleep(wait_period)
                attempts += 1
        if not boot_complete:
            raise RuntimeError("dev.bootcomplete 标志在  %s 秒后仍未设置，手机重启失败" % _timeout)

    def get_screenshot(self, filename, scale = 0.5):
        retcode, data = self.shell("screencap -p")
        if retcode==0:
            data = data.replace(b'\r\n', b'\n')
            data = data.replace(b'\r\n', b'\n')
            # star.write(filename, data)
            im = Image.open(io.BytesIO(data))
            w, h = im.size
            im_ss = im.resize((int(w*scale), int(h*scale)), Image.ANTIALIAS).convert('RGBA')
            im_ss.save(filename)

    def is_app_installed(self, package):
        '''
        判断app是否安装
        '''
        if package in self.list_installed_app():
            return True
        else:
            return False

    def runshellcmd(self, cmd):
        cmds = [ADB_COMMAND_PREFIX, 'shell', cmd]
        return star.runcmd(cmds)

    def list_installed_app(self):
        '''
        获取已安装app列表
        :return: 返回app列表
        :rtype: list
        '''
        retcode, result = self.runshellcmd('pm list packages')
        result = result.replace('\r', '').splitlines()
        logging.info(result)
        installed_app_list = []
        for app in result:
            if not 'package' in app: continue
            if app.split(':')[0] == 'package':
                # 只获取连接正常的
                installed_app_list.append(app.split(':')[1])
        logging.info(installed_app_list)
        return installed_app_list

    # 获取app的userid
    def get_app_userid(self, package_name):
        uid = None
        retcode, out = self.runshellcmd('dumpsys package %s' % package_name)
        if retcode == 0:
            if package_name in out and "Unable to find package:" not in out:
                db_result = re.findall('userId=(\d+)', out)
                if len(db_result) > 0:
                    uid = db_result[0]
        return uid

    # 获取app的pid
    def get_app_pid(self, package_name):
        pid = None
        code, result = self.runshellcmd('ps "| grep ' + package + '"')
        if code==0:
            m = re.search(r'\S+\s+(\d+)\s+.+', result)
            if m:
                pid = m.group(1)
        return pid

    # 检测app是否在顶层
    def is_app_on_the_top(self, package):
        code, result = self.runshellcmd('shell dumpsys activity activities "| grep mFocusedActivity"')
        if code==0:
            appActivity = result.split("{")[1].strip('}')
            return package in appActivity
        return False

    def get_current_activity(self):
        # 获取当前activity名
        if self.get_sdk_version() < 26:  # android8.0以下优先选择dumpsys activity top获取当前的activity
            current_activity = self.get_top_activity_with_activity_top()
            if current_activity:
                return current_activity
            current_activity = self.get_top_activity_with_usagestats()
            if current_activity:
                return current_activity
            return None
        else:  # android 8.0以上优先根据dumsys usagestats来获取当前的activity
            current_activity = self.get_top_activity_with_usagestats()
            if current_activity:
                return current_activity
            current_activity = self.get_top_activity_with_activity_top()
            if current_activity:
                return current_activity

    def get_top_activity_with_activity_top(self):
        '''通过dumpsys activity top 获取当前activity名
        '''
        code, ret = self.runshellcmd("dumpsys activity top")
        if not ret:
            return None
        lines = ret.split("\n")
        top_activity = ""
        for line in lines:
            if "ACTIVITY" in line:
                line = line.strip()
                logging.debug("dumpsys activity top info line :" + line)
                activity_info = line.split()[1]
                if "." in line:
                    top_activity = activity_info.replace("/", "")
                else:
                    top_activity = activity_info.split("/")[1]
                logging.debug("dump activity top activity:" + top_activity)
                return top_activity
        return top_activity

    def get_top_activity_with_usagestats(self):
        '''通过dumpsys usagestats获取当前activity名
        '''
        top_activity = ""
        code, ret = self.runshellcmd("dumpsys usagestats")
        if not ret:
            return None
        last_activity_line = ""
        lines = ret.split("\n")
        for line in lines:
            if "MOVE_TO_FOREGROUND" in line:
                last_activity_line = line.strip()
        logging.debug("dumpsys usagestats MOVE_TO_FOREGROUND lastline :" + last_activity_line)
        if len(last_activity_line.split("class=")) > 1:
            top_activity = last_activity_line.split("class=")[1]
            if " " in top_activity:
                top_activity = top_activity.split()[0]
        logging.debug("dumpsys usagestats top activity:" + top_activity)
        return top_activity

    # 清空日志
    def clear_log(self):
        code, result = self.runshellcmd('logcat -c')
        return code==0

    #tag ActivityManager 的 Info 以上级别日志
    #后面可以考虑做成通用的函数
    def get_log(self, timeout=40):
        cmds = [ADB_COMMAND_PREFIX]
        if len(self._devices) > 1 or not self._deviceSelected:
            cmds.append("-s")
            cmds.append(self._deviceSelected)
        cmds.append('logcat -v time ActivityManager:I *:S')
        code, result = star.runcmd(cmds)
        return result

    def run_monkey(self, package_name, num):
        code, result = self.runshellcmd('monkey -p ' + package_name + ' -v ' + str(num))
        return code==0

    # 清除手机缓存
    def clear_ram_caches(self):
        self.runshellcmd('sync')
        self.runshellcmd('echo 3 > /proc/sys/vm/drop_caches')


    def forward(self, port1, port2, type='tcp'):
        '''端口转发
        :param port1: PC上的TCP端口
        :type port1:  int
        :param port2: 手机上的端口或LocalSocket地址
        :type port2:  int或String
        :param type:  手机上的端口类型
        :type type:   String，LocalSocket地址使用“localabstract”
        '''
        while 1:
            ret = self.run_adb_cmd('forward', 'tcp:%d' % (port1), '%s:%s' % (type, port2))
            if not 'cannot bind socket' in ret and not 'cannot bind to socket' in ret: return port1
            port1 += 1

    def _push_file(self, src_path, dst_path, uid=None):
        '''以指定身份拷贝文件到手机中
        '''
        result = self.run_adb_cmd('push', src_path, dst_path, timeout=None)
        if 'No space left on _adb' in result or 'No such file or directory' in result:
            # 如果源文件不存在不会执行到这里
            raise RuntimeError('设备存储空间不足')
        if uid and uid != 'shell' and uid != 'root':
            self.runshellcmd('mv %s %s0' % (dst_path, dst_path), True)
            dst_dir = dst_path[:dst_path.rfind('/')]
            self.runshellcmd('rm %s' % dst_path, True)
            self.runshellcmd('rmdir %s' % dst_dir, True)
            self.runshellcmd('su %s mkdir %s' % (uid, dst_dir))
            self.runshellcmd('chmod 777 %s' % dst_dir, True)
            self.runshellcmd('su %s cp %s0 %s' % (uid, dst_path, dst_path))
            self.runshellcmd('rm %s0' % dst_path)  # 只能复制再删除
        return result

    # 从电脑中上传文件到手机设备中
    def push_file(self, src_path, dst_path, uid=None):
        for _ in range(3):
            file_size = os.path.getsize(src_path)  # 防止取到的文件大小不正确
            result = self._push_file(src_path, dst_path, uid)
            if file_size == 0:
                logger.warn('文件大小为0')
                return result
            if ('%d' % file_size) in result:
                try:
                    _, file_list = self.list_dir(dst_path)
                    if len(file_list) == 0:
                        logger.warn('push file failed: file not exist')
                    elif file_list[0]['size'] != file_size:
                        logger.warn('push file failed: file size error, expect %d, actual is %d' % (file_size, file_list[0]['size']))
                    else:
                        return result
                except RuntimeError as e:
                    err_msg = e.args[0]
                    if not isinstance(err_msg, unicode):
                        err_msg = err_msg.decode('utf8')
                    logger.warn(err_msg)
            else:
                logger.warn('push file failed: %s' % result)
        raise RuntimeError('拷贝文件到手机：%r 失败：%s' % (self._device_name, result))

    # 从手机设备中下载文件到电脑中
    def pull_file(self, src_path, dst_path):
        result = self.run_adb_cmd('pull', src_path, dst_path, timeout=600)
        if 'failed to copy' in result:
            raise RuntimeError(result)
        if not 'bytes in' in result:
            logger.warn(repr(result))
            code, ret = self.runshellcmd('ls -l %s' % src_path, True)
            logger.debug(ret)
        return result

    def get_package_path(self, pkg_name):
        '''获取应用安装包路径
        '''
        for _ in range(3):
            # 为避免某些情况下获取不到应用安装包路径，重试多次
            code, result = self.runshellcmd('pm path %s' % pkg_name)
            logger.debug('get_package_path: %r' % result)
            pos = result.find('package:')
            if pos >= 0: return result[pos + 8:]
            time.sleep(1)
        return ''

    def start_activity(self, activity_name, action='', type='', data_uri='', extra={}, wait=True):
        '''打开一个Activity
        '''
        if action != '':  # 指定Action
            action = '-a %s ' % action
        if type != '':
            type = '-t %s ' % type
        if data_uri != '':
            data_uri = '-d %s ' % data_uri
        extra_str = ''
        for key in extra.keys():  # 指定额外参数
            p_type = ''
            if extra[key] in ['true', 'false']:
                p_type = 'z'  # EXTRA_BOOLEAN_VALUE
            elif isinstance(extra[key], int):
                p_type = 'i'  # EXTRA_INT_VALUE
            elif isinstance(extra[key], long):
                p_type = 'l'  # EXTRA_LONG_VALUE
            elif isinstance(extra[key], float):
                p_type = 'f'  # EXTRA_FLOAT_VALUE
            elif extra[key].startswith('file://'):  # EXTRA_URI_VALUE
                p_type = 'u'
            if not p_type and '&' in extra[key]:
                extra[key] = extra[key].replace('&', r'\&')
            param = '-e%s %s %s ' % (p_type, key, extra[key])
            if p_type: param = '-' + param
            extra_str += param
        if len(extra_str) > 0: extra_str = extra_str[:-1]
        W = ''
        if wait: W = '-W'  # 等待启动完成才返回
        # 如果/sbin/sh指向busybox，就会返回“/sbin/sh: am: not found”错误
        # 返回am找不到是因为am缺少“#!/system/bin/sh”
        command = 'am start %s -n %s %s%s%s%s' % (W, activity_name, action, type, data_uri, extra_str)
        if command[-1] == ' ': command = command[:-1]
        code, result = self.runshellcmd(command, timeout=15, retry_count=3)
        if 'Permission Denial' in result or not 'Activity' in result or not 'Complete' in result:
            # 使用root权限运行
            code, result = self.runshellcmd(command, True, timeout=15, retry_count=3)
            # raise RuntimeError('打开Activity失败：\n%s' % result)
        ret_dict = {}

        for line in result.split('\r\n'):
            if ': ' in line:
                key, value = line.split(': ')
                ret_dict[key] = value
        if ret_dict.has_key('Error'):
            raise RuntimeError(ret_dict['Error'])
        return ret_dict

    def get_cpu_abi(self):
        '''获取系统的CPU架构信息
        '''
        code, ret = self.runshellcmd('getprop ro.product.cpu.abi')
        if not ret: ret = 'armeabi'  # 有些手机可能没有这个系统属性
        return ret

    def get_device_module(self):
        '''获取设备型号
        '''
        code, module = self.runshellcmd('getprop ro.product.model')
        code, brand = self.runshellcmd('getprop ro.product.brand')
        if module.find(brand) >= 0:
            return module
        return '%s %s' % (brand, module)

    def get_model(self):
        code, module = self.runshellcmd('getprop ro.product.model')
        return module

    def get_brand(self):
        code, brand = self.runshellcmd('getprop ro.product.brand')
        return brand

    def get_system_version(self):
        '''获取系统版本
        '''
        code, ret = self.runshellcmd('getprop ro.build.version.release')
        return ret

    def get_uid(self, app_name):
        '''获取APP的uid
        '''
        code, result = self.runshellcmd('ls -l /data/data', True)
        result = result.replace('\r\r\n', '\n')
        for line in result.split('\n'):
            items = line.split(' ')
            for item in items:
                if not item: continue
                if item == app_name: return items[1]
        return None

    def is_selinux_opened(self):
        '''selinux是否是enforcing状态
        '''
        if self.get_sdk_version() < 18: return False
        code, ret = self.runshellcmd('getenforce', True)
        return 'Enforcing' in ret

    def close_selinux(self):
        '''关闭selinux
        '''
        code, result = self.runshellcmd('setenforce 0', True)
        if 'Permission denied' in result: return False
        return True

    def chmod(self, file_path, attr):
        '''修改文件/目录属性

        :param file_path: 文件/目录路径
        :type file_path:  string
        :param attr:      设置的属性值，如：777
        :type attr:       int
        '''

        def _parse(num):
            num = str(num)
            attr = ''
            su_flag = ''
            if len(num) == 4:
                su_flag = int(num[0])
                num = num[1:]
            for c in num:
                c = int(c)
                if c & 4:
                    attr += 'r'
                else:
                    attr += '-'
                if c & 2:
                    attr += 'w'
                else:
                    attr += '-'
                if c & 1:
                    attr += 'x'
                else:
                    attr += '-'

            if su_flag and su_flag == 4:
                attr = attr[:2] + 's' + attr[3:]
            return attr

            code, ret = self.runshellcmd('chmod %s %s' % (attr, file_path), True)
        dir_list, file_list = self.list_dir(file_path)

        if len(dir_list) == 0 and len(file_list) == 1 and file_path.endswith('/' + file_list[0]['name']):
            # 这是一个文件
            new_attr = file_list[0]['attr']
        else:
            # 目录
            dir_name = file_path.split('/')[-1]
            parent_path = '/'.join(file_path.split('/')[:-1])
            dir_list, _ = self.list_dir(parent_path)
            for dir in dir_list:
                if dir['name'] == dir_name:
                    new_attr = dir['attr']
                    break

        if new_attr != _parse(attr):
            logger.warn('chmod failed: %r(%s)' % (ret, new_attr))
            return self.chmod(file_path, attr)
        return new_attr

    def mkdir(self, dir_path, mod=None):
        '''创建目录
        '''
        cmd = 'mkdir %s' % (dir_path)
        code, ret = self.runshellcmd(cmd, True)
        #        if not 'File exists' in ret:
        #            #加了-p参数貌似不会返回这个提示信息
        try:
            self.list_dir(dir_path)
        except RuntimeError as e:
            logging.error('mkdir %s failed: %s(%s)' % (dir_path, ret, e))
            return self.mkdir(dir_path, mod)
        # 修改权限
        if mod != None:
            self.chmod(dir_path, mod)

    def list_dir(self, dir_path):
        '''列取目录
        '''
        if ' ' in dir_path: dir_path = '"%s"' % dir_path
        code, result = self.runshellcmd('ls -l %s' % dir_path, True)
        result = result.replace('\r\r\n', '\n')

        if 'No such file or directory' in result:
            raise RuntimeError(u'文件(夹) %s 不存在' % dir_path)
        if 'Not a directory' in result:
            raise RuntimeError(u'%s %s' % (dir_path, result))

        dir_list = []
        file_list = []

        def _handle_name(name):
            return name.split('/')[-1]

        is_busybox = None
        # busybox格式 -rwxrwxrwx    1 shell    shell        13652 Jun  3 10:56 /data/local/tmp/qt4a/inject

        for line in result.split('\n'):
            items = line.split()
            if len(items) < 6: continue  # (6, 7, 9)
            if line[0] != '-' and line[0] != 'd': continue

            is_dir = items[0][0] == 'd'  # 是否是目录
            if is_busybox == None:
                item = items[4]  # 日期字段
                if is_dir: item = items[3]  # 目录没有size字段
                pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
                if pattern.match(item):
                    is_busybox = False
                else:
                    is_busybox = True

            if not is_busybox:
                # 防止文件名称中有空格
                if not is_dir and len(items) > 7:
                    items[6] = line[line.find(items[6]):].strip()
                elif is_dir and len(items) > 6:
                    items[5] = line[line.find(items[5]):].strip()

            attrs = items[0]
            if attrs[0] == 'd':
                if is_busybox:
                    name = _handle_name(items[8])
                else:
                    name = items[5]
                dir_list.append({'name': name, 'attr': attrs[1:]})
            elif attrs[0] == '-':  # 不支持其它类型
                if is_busybox:
                    name = _handle_name(items[8])
                    size = int(items[4])
                    last_modify_time = items[7]
                else:
                    name = items[6]
                    size = int(items[3])
                    last_modify_time = time.strptime('%s %s:00' % (items[4], items[5]), "%Y-%m-%d %X")
                file_list.append({'name': name, 'attr': attrs[1:], 'size': size, 'last_modify_time': last_modify_time})
        return dir_list, file_list

    def get_file_info(self, file_path):
        '''获取文件信息
        '''
        return self.list_dir(file_path)[1][0]

    def copy_file(self, src_path, dst_path):
        '''在手机上拷贝文件
        '''
        if not hasattr(self, '_has_cp'):
            code, ret = self.runshellcmd('cp')
            self._has_cp = 'not found' not in ret
        if self._has_cp:  # 不是所有的ROM都有cp命令
            self.runshellcmd('cp %s %s' % (src_path, dst_path), True)
        else:
            self.runshellcmd('cat %s > %s' % (src_path, dst_path), True, timeout=30)  # 部分手机上发现此方法耗时较多

    def delete_file(self, file_path):
        '''删除手机上文件
        '''
        if '*' in file_path:
            # 使用通配符时不能使用引号
            self.runshellcmd('rm %s' % file_path, True)
        else:
            file_path = file_path.replace('"', r'\"')
            self.runshellcmd('rm "%s"' % file_path, True)

    def delete_folder(self, folder_path):
        '''删除手机上的目录
        '''
        folder_path = folder_path.replace('"', r'\"')
        self.runshellcmd('rm -R "%s"' % folder_path, True)

    def get_process_uid(self, pid):
        '''获取进程uid'''
        if not pid:
            return None
        if len(self._device_name) > 0:
            res = os.popen("adb -s %s shell cat /proc/%s/status" % (self._device_name, pid)).readlines()
        else:
            res = os.popen("adb shell cat /proc/%s/status" % pid).readlines()
        if (not res) or len(res[0]) == 0:
            return None
        for res_item in res:
            if len(res_item.split()) == 0:
                continue
            if res_item.split()[0] == "Uid:":
                return res_item.split()[1]
        return None

    def _list_process(self):
        '''获取进程列表
        '''
        import re
        code, result = self.runshellcmd('ps')  # 不能使用grep
        result = result.replace('\r', '')
        lines = result.split('\n')
        busybox = False
        if lines[0].startswith('PID'): busybox = True

        result_list = []
        for i in range(1, len(lines)):
            items = lines[i].split()
            if not busybox:
                if len(items) < 9:
                    raise RuntimeError("ps命令返回格式错误：\n%s" % result)
                result_list.append({'pid': int(items[1]), 'ppid': int(items[2]), 'proc_name': items[8]})
            else:
                idx = 4
                cmd = items[idx]
                if len(cmd) == 1:
                    # 有时候发现此处会有“N”
                    idx += 1
                    cmd = items[idx]
                idx += 1
                if cmd[0] == '{' and cmd[-1] == '}': cmd = items[idx]
                ppid = 0
                if items[1].isdigit(): ppid = int(items[1])  # 有些版本中没有ppid
                result_list.append({'pid': int(items[0]), 'ppid': ppid, 'proc_name': cmd})
        return result_list

    def list_process(self):
        '''获取进程列表
        '''
        for _ in range(3):
            try:
                return self._list_process()
            except RuntimeError as e:
                logging.error('list_process error: %s' % e)
        else:
            raise RuntimeError('获取进程列表失败')

    def get_pid(self, proc_name):
        '''获取进程ID
        '''
        process_list = self.list_process()
        for process in process_list:
            if process['proc_name'] == proc_name:
                return process['pid']
        return 0

    def get_process_status(self, pid):
        '''获取进程状态信息
        '''
        code, ret = self.runshellcmd('cat /proc/%d/status' % pid, True)
        result = {}
        for line in ret.split('\n'):
            if not line: continue
            if not ':' in line:
                logger.warn('get_process_status line error: %r' % line)
                continue
            key, value = line.split(':')
            result[key] = value.strip()
        return result

    def kill_process(self, proc_name_or_pid):
        '''杀死进程
        '''
        kill_list = []
        cmd = ''

        if isinstance(proc_name_or_pid, (str, unicode)):
            process_list = self.list_process()
            for process in process_list:
                if process['proc_name'].find(proc_name_or_pid) >= 0:
                    if process['proc_name'] == proc_name_or_pid:
                        # 保证主进程首先被杀
                        kill_list.insert(0, process['pid'])
                    else:
                        kill_list.append(process['pid'])
        else:
            kill_list.append(proc_name_or_pid)

        for pid in kill_list:
            cmd += 'kill -9 %d && ' % pid
        if cmd:
            cmd = cmd[:-4]
            self.runshellcmd(cmd, True)
            return True
        else:
            return False

    def get_device_imei(self):
        '''获取手机串号
        '''
        code, result = self.runshellcmd('dumpsys iphonesubinfo', True)
        for line in result.split('\n'):
            if line.find('Device ID') >= 0:
                return line.split('=')[1].strip()
        raise RuntimeError('获取imei号失败：%r' % result)

    def get_cpu_total_time(self):
        cpu_time = 0
        code, result = self.runshellcmd('cat /proc/stat')
        result = result.split('\r\n')[0]
        for item in result.split(' '):
            item = item.strip()
            if not item: continue
            if item == 'cpu': continue
            cpu_time += int(item)
        return cpu_time

    def get_process_cpu_time(self, pid):
        code, result = self.runshellcmd('cat /proc/%d/stat' % pid)
        result = result.split(' ')
        utime = int(result[13])
        stime = int(result[14])
        cutime = int(result[15])
        cstime = int(result[16])
        return utime + stime + cutime + cstime

    def get_thread_cpu_time(self, pid, tid):
        code, result = self.runshellcmd('cat /proc/%d/task/%d/stat' % (pid, tid))
        result = result.split(' ')
        utime = int(result[13])
        stime = int(result[14])
        cutime = int(result[15])
        cstime = int(result[16])
        return utime + stime + cutime + cstime

    def get_process_cpu(self, proc_name, interval=0.1):
        '''获取进程中每个线程的CPU占用率
        '''
        import time
        pid = self.get_pid(proc_name)
        # print pid'
        if not pid: return None
        total_cpu1 = self.get_cpu_total_time()
        process_cpu1 = self.get_process_cpu_time(pid)
        thread_cpu1 = self.get_thread_cpu_time(pid, pid)
        time.sleep(interval)
        total_cpu2 = self.get_cpu_total_time()
        process_cpu2 = self.get_process_cpu_time(pid)
        thread_cpu2 = self.get_thread_cpu_time(pid, pid)
        total_cpu = total_cpu2 - total_cpu1
        process_cpu = process_cpu2 - process_cpu1
        thread_cpu = thread_cpu2 - thread_cpu1
        return process_cpu * 100 / total_cpu, thread_cpu * 100 / total_cpu

    def read_event(self):
        '''读取事件
        '''
        import re, time
        pattern = re.compile(r'/dev/input/event\d: (\w+) (\w+) (\w+)')
        proc = self.runshellcmd('getevent', sync=False)
        while True:
            line = proc.stdout.readline().strip()
            # print line
            ret = pattern.search(line)
            if ret:
                # print ret.group(1)
                event_type = int(ret.group(1), 16)
                # print ret.group(2), ret.group(3)
                parm1 = int(ret.group(2), 16)
                parm2 = int(ret.group(3), 16)
                print
                time.time(),
                if event_type == 0:
                    print('EV_SYN', parm1, parm2)
                elif event_type == 1:
                    print('EV_KEY')
                    if parm1 == 0x14a:
                        print('BTN_TOUCH')
                    else:
                        print(parm1)
                    print(parm2)
                elif event_type == 3:
                    print('EV_ABS')
                    if parm1 == 0:
                        print('x')
                    elif parm1 == 1:
                        print('y')
                    elif parm1 == 0x30:
                        print('ABS_MT_TOUCH_MAJOR')
                    elif parm1 == 0x31:
                        print('ABS_MT_TOUCH_MINOR')
                    elif parm1 == 0x32:
                        print('ABS_MT_WIDTH_MAJOR')
                    elif parm1 == 0x33:
                        print('ABS_MT_WIDTH_MINOR')
                    elif parm1 == 0x34:
                        print('ABS_MT_ORIENTATION')
                    elif parm1 == 0x35:
                        print('ABS_MT_POSITION_X')
                    elif parm1 == 0x36:
                        print('ABS_MT_POSITION_Y')
                    elif parm1 == 0x39:
                        print('ABS_MT_TRACKING_ID')
                    elif parm1 == 0x3a:
                        print('ABS_MT_PRESSURE')
                    else:
                        print('%x' % parm1)
                    print(parm2)
                else:
                    print(line)

    def get_cpu_time(self):
        '''获取手机全局总时间片和空闲时间片
        '''
        import re
        cpu_time = 0
        code, result = self.runshellcmd('cat /proc/stat')
        result = result.split('\r\n')[0]
        result, num = re.subn(r'\s+', ' ', result)  # 将字符串中多个相连的空白字符合并成一个空白字符
        results = result.split(' ')
        if len(results) < 5:
            logger.warn('无法取得CPU时间片统计，请确保手机正常链接，并已启动！')
            return 0, 0
        idle_time = int(results[4])
        for item in results:
            item = item.strip()
            if not item: continue
            if item == 'cpu': continue
            cpu_time += int(item)
        return cpu_time, idle_time

    def get_cpu_usage(self, interval=0.5):
        '''获取手机全局CPU使用率
        '''
        total_time1, idle_time1 = self.get_cpu_time()
        time.sleep(interval)
        total_time2, idle_time2 = self.get_cpu_time()
        total_time = total_time2 - total_time1
        idle_time = idle_time2 - idle_time1
        if total_time == 0:
            return -1
        return (total_time - idle_time) * 100 / total_time

    def dump_stack(self, pid_or_procname):
        '''获取进程调用堆栈
        '''
        if isinstance(pid_or_procname, (str, unicode)):
            pid = self.get_pid(pid_or_procname)
        else:
            pid = pid_or_procname
        anr_dir = '/data/anr'
        try:
            self.list_dir(anr_dir)
        except RuntimeError:
            self.mkdir(anr_dir)
        self.chmod(anr_dir, 777)
        cmd = 'kill -3 %d' % pid
        self.runshellcmd(cmd, True)
        code, out =self.runshellcmd('cat %s/traces.txt' % anr_dir, True)
        return out


if __name__ == '__main__':
    adb = ADBManager()
    adb.get_version()
    adb.getserialno()
    adb.isDeviceAvailable()
    adb.devices()
    adb.push('/tmp/file.txt', '/data/media/0')
    adb.pull('/data/media/0/file.txt', '/tmp/')
    adb.shell('ls')
    adb.install('/usr/local/app.apk')
    adb.uninstall('com.example.android.valid')
    apk = APK('demo.apk')
    main_activity = apk.get_main_activity()
    package = apk.get_package()
    adb.startapp(package, main_activity)