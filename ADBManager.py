#coding:utf-8
import os
import star


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

class ADBManager:
    def __init__(self):
        self._selectedDevice = None
    def select(self, serialno):
        self._selectedDevice = serialno

    def version(self):
        """
        Display the version of adb
        :return: result of star.runcmd() execution
        """
        adb_full_cmd = [ADB_COMMAND_PREFIX, ADB_COMMAND_VERSION]
        return star.runcmd(adb_full_cmd)
    def getserialno(self):
        """
        Get serial number for all available target devices
        :return: result of star.runcmd() execution
        """
        adb_full_cmd = [ADB_COMMAND_PREFIX, ADB_COMMAND_GETSERIALNO]
        return star.runcmd(adb_full_cmd)
    def isDeviceAvailable(self):
        """
        Private Function to check if device is available;
        To be used by only functions inside module
        :return: True or False
        """
        result = self.getserialno()
        if result[1].strip() == "unknown":
            return False
        else:
            return True


    def bugreport(self, dest_file="default.log"):
        """
        Prints dumpsys, dumpstate, and logcat data to the screen, for the purposes of bug reporting
        :return: result of star.runcmd() execution
        """
        adb_full_cmd = [ADB_COMMAND_PREFIX, ADB_COMMAND_BUGREPORT]
        try:
            dest_file_handler = open(dest_file, "w")
        except IOError:
            print "IOError: Failed to create a log file"

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


    def devices(self, opts=[]):
        """
        Get list of all available devices including emulators
        :param opts: list command options (e.g. ["-r", "-a"])
        :return: result of star.runcmd() execution
        """
        adb_full_cmd = [ADB_COMMAND_PREFIX, ADB_COMMAND_DEVICES, self._convert_opts(opts)]
        return star.runcmd(adb_full_cmd)


    def shell(self, cmd):
        """
        Execute shell command on target
        :param cmd: string shell command to execute
        :return: result of star.runcmd() execution
        """
        adb_full_cmd = [ADB_COMMAND_PREFIX, ADB_COMMAND_SHELL, cmd]
        return star.runcmd(adb_full_cmd)


    def install(self, apk, opts=[]):
        """
        Install *.apk on target
        :param apk: string path to apk on host to install
        :param opts: list command options (e.g. ["-r", "-a"])
        :return: result of star.runcmd() execution
        """
        adb_full_cmd = [ADB_COMMAND_PREFIX, ADB_COMMAND_INSTALL, _convert_opts(opts), apk]
        return star.runcmd(adb_full_cmd)


    def uninstall(self, app, opts=[]):
        """
        Uninstall app from target
        :param app: app name to uninstall from target (e.g. "com.example.android.valid")
        :param opts: list command options (e.g. ["-r", "-a"])
        :return: result of star.runcmd() execution
        """
        adb_full_cmd = [ADB_COMMAND_PREFIX, ADB_COMMAND_UNINSTALL, _convert_opts(opts), app]
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

    def runapp(self, package, activity):
        return self.shell('am start -W -n ' + package + '/' + activity)
    def startapp(self, package, activity):
        return self.runapp(package, activity)
    def stopapp(self, package):
        return self.shell('am force-stop ' + package)
    def listpackages(self):
        return self.shell('pm list packages')
if __name__ == '__main__':
    adb = ADBManager()
    adb.version()
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