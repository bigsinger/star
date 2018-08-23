# coding: utf-8

import os
import sys
import traceback
import zipfile
import logging
import pyminizip


class ZipFileHelper:
    def __init__(self):
        self._zip_file_name = ''
        self._zip_file_object = None

    @staticmethod
    def zip_file(src_filepath, dst_zip_filename=None, entryname=None, **karg):
        """
        功能：把一个源文件或目录压缩为一个zip文件。该方法为静态方法。
        :param src_filepath: 待压缩的文件或目录，请自行内部判断
        :param dst_zip_filename: 被压缩成的zip文件的路径，可以是相对路径，也可以是全路径。
        如果dst_zip_filename为空或None，则自动取相对路径，名称为src_filepath的文件名（不含后缀，如果是目录直接是目录名），后缀为.zip
        如果是相对路径则在src_filepath的父目录下生成zip文件。
        :param entryname:添加到压缩包里的entry目录名列表，如果不填，则自动计算，计算规则：
        如果filename与src_zip_filename具有相同目录结构如：D:\test\a.zip,D:\test\abc\def\g.txt，则entryname为abc\def\g.txt
        否则entryname为文件名
        filename_list与entryname_list为对应关系，如果某一个entryname为空或None则自动计算。
        :param karg: 关键字参数，压缩文件是否带密码，默认不带，否则请指定密码字符串
        :return: 压缩成功返回True，失败返回False
        """
        password = None
        if 'password' in karg.keys():
            password = karg.get('password')
            if not isinstance(password, str):
                password = None
        base_file_name = ''
        file_name_list = []
        dir_file_path_list = []
        if isinstance(src_filepath, list):
            src_filepath = Utils.normal_list(src_filepath)
            for file in src_filepath:
                file = os.path.normcase(file)
                dst_zip_filename = Utils.get_zip_name(file, dst_zip_filename)  # 压缩包文件名
                if dst_zip_filename is not None:
                    base_file_name = os.path.dirname(dst_zip_filename)
                    break
            for src in src_filepath:
                src_file_list = []
                src_file_path = []
                Utils.dfs_get_file(src, src_file_list, src_file_path)  # 获取所有文件路径
                file_name_list.extend(src_file_list)
                dir_file_path_list.extend(src_file_path)
        elif isinstance(src_filepath, str):
            src_filepath = os.path.normcase(src_filepath)
            dst_zip_filename = Utils.get_zip_name(src_filepath, dst_zip_filename)
            if dst_zip_filename is not None:
                base_file_name = os.path.dirname(dst_zip_filename)
            Utils.dfs_get_file(src_filepath, file_name_list, dir_file_path_list)
        else:
            logging.error('[ZipFileHelper.zip_file] 参数类型错误，src_filepath 应该是str、list类型，不应该是%s',
                          type(src_filepath))
            return False
        if dst_zip_filename is None:
            logging.error('[ZipFileHelper.zip_file] 压缩失败，原因：%s', '找不到源文件，请检查源文件是否存在')
            return False
        dst_zip_filename += '.zip'
        if base_file_name == '':
            base_file_name = os.getcwd()
        if not base_file_name.endswith(os.sep):
            base_file_name = base_file_name + os.sep

        path_for_file = []
        for path in dir_file_path_list:
            path_for_file.append(path.replace(base_file_name, os.sep))  # 压缩后文件路径，pyminizip 压缩所需参数
        if isinstance(entryname, str):
            temp_list = []
            temp_list.append(os.path.normcase(entryname))
            entryname = temp_list
        elif not isinstance(entryname, list):
            entryname = []
        initial_entry = None
        if len(entryname) != 0:
            initial_entry = entryname
        if isinstance(entryname, list):  # 计算entryname
            entryname = Utils.extend_entry_name(file_name_list, entryname, base_file_name)
        try:
            if password is None or password == '':  # 如果没有密码则用zipfile进行压缩
                zip_object = zipfile.ZipFile(dst_zip_filename, 'w')
                for index in range(len(file_name_list)):
                    zip_object.write(file_name_list[index], entryname[index])
                zip_object.close()
            elif initial_entry is None:  # 如果未配置压缩后文件名，则直接压缩
                pyminizip.compress_multiple(file_name_list, path_for_file, dst_zip_filename, password, 0)
            else:  # 对于配置了压缩后文件名的，先将原文件重命名，再压缩，压缩后改回原名
                for index in range(len(initial_entry)):
                    os.rename(file_name_list[index], initial_entry[index])
                pyminizip.compress_multiple(entryname, path_for_file, dst_zip_filename, password, 0)
                for index in range(len(file_name_list)):
                    os.rename(entryname[index], file_name_list[index])
            return True
        except Exception as e:
            logging.error('[ZipFileHelper.zip_file] 压缩失败，原因：%s', e)
            return False

    @staticmethod
    def unzip_file(src_zip_filename, dst_dir_path=None, password=None):
        """
        功能：把压缩包文件解压到指定目录
        :param src_zip_filename:
        :param dst_dir_path: 不填则解压到压缩包的父目录下。否则需要判断dst_dir_path的父目录是否存在，不存在则报错，然后再创建dst_dir_path目录（不存在的话）。
        :param password: 如果解压需要密码，这里输入
        :return: 成功返回True，失败返回False
        """
        src_zip_filename = os.path.normcase(src_zip_filename)
        if not os.path.exists(src_zip_filename):
            logging.error('[ZipFileHelper.unzip_file] 解压失败， 原因：%s文件不存在', src_zip_filename)
            return False
        elif not zipfile.is_zipfile(src_zip_filename):
            logging.error('[ZipFileHelper.unzip_file] 添加失败，原因：%s文件不是ZIP文件',src_zip_filename)
            return False
        zip_file_object = zipfile.ZipFile(src_zip_filename)
        try:
            if password is not None and isinstance(password, str):
                password = bytes(password.encode('utf-8'))
            else:
                password = None
            if isinstance(dst_dir_path, str):
                dst_dir_path = os.path.normcase(dst_dir_path)
                base_file_path = os.path.dirname(dst_dir_path)
                if base_file_path == '':
                    base_file_path = os.getcwd()
                if not os.path.exists(base_file_path):
                    os.makedirs(dst_dir_path)
                    logging.error('[ZipFileHelper.unzip_file] 解压%s到%s失败，原因：%s', src_zip_filename, dst_dir_path,
                                  '不存在目标路径')
                    return False
                if not os.path.exists(dst_dir_path):
                    os.makedirs(dst_dir_path)
                zip_file_object.extractall(dst_dir_path, pwd=password)
            else:
                zip_file_path = os.path.dirname(src_zip_filename)
                zip_file_object.extractall(zip_file_path, pwd=password)
        except Exception as e:
            logging.error('[ZipFileHelper.unzip_file] 解压%s到%s失败，原因：%s', src_zip_filename, dst_dir_path, e)
            return False
        finally:
            zip_file_object.close()
        return True

    @staticmethod
    def zip_add(src_zip_filename, filename_list, entryname_list=None):
        """
        功能：在zip压缩包里添加文件。该方法为静态方法。
        :param src_zip_filename: 待添加文件的zip压缩包
        :param filename_list:待添加到压缩包里的文件列表，自动判断是单个文件路径还是一个列表
        :param entryname_list:添加到压缩包里的entry目录名列表，如果不填，则自动计算，计算规则：
        如果filename与src_zip_filename具有相同目录结构如：D:\test\a.zip,D:\test\abc\def\g.txt，则entryname为abc\def\g.txt
        否则entryname为文件名
        filename_list与entryname_list为对应关系，如果某一个entryname为空或None则自动计算。
        :return:成功返回True，失败返回False
        """
        src_zip_filename = os.path.normcase(src_zip_filename)
        if not os.path.exists(src_zip_filename):
            logging.error('[ZipFileHelper.zip_add] 添加失败，原因：%s文件不存在',src_zip_filename)
            return False
        elif not zipfile.is_zipfile(src_zip_filename):
            logging.error('[ZipFileHelper.zip_add] 添加失败，原因：%s文件不是ZIP文件',src_zip_filename)
            return False
        zip_file_object = zipfile.ZipFile(src_zip_filename, 'a')
        base_file_name = os.path.dirname(src_zip_filename)
        if base_file_name == '':
            base_file_name = os.getcwd()
        if not base_file_name.endswith(os.sep):
            base_file_name = base_file_name + os.sep
        if isinstance(filename_list, str):
            temp_list = []
            temp_list.append(os.path.normcase(filename_list))
            filename_list = temp_list
        elif not isinstance(filename_list, list):
            logging.error('[ZipFileHelper.zip_add] 参数类型错误，filename_list 应该是str、list类型，不应该是%s',
                          type(filename_list))
            return False
        if isinstance(filename_list, list):
            filename_list = Utils.normal_list(filename_list)
            if isinstance(entryname_list, str):
                temp_list = []
                temp_list.append(os.path.normcase(entryname_list))
                entryname_list = temp_list
            elif not isinstance(entryname_list, list):
                entryname_list = []
            if isinstance(entryname_list, list):
                entryname_list = Utils.extend_entry_name(filename_list, entryname_list, base_file_name)
            success = False
            for index in range(len(filename_list)):
                try:
                    if not os.path.exists(filename_list[index]):
                        logging.error('[ZipFileHelper.zip_add] 添加压缩文件%s失败，原因：%s', filename_list[index], '不存在该文件')
                        continue
                    zip_file_object.write(filename_list[index], entryname_list[index])
                    success = True
                except Exception as e:
                    logging.error('[ZipFileHelper.zip_add] 添加压缩文件%s失败，原因：%s', filename_list[index], e)
            zip_file_object.close()
            if success:
                return True
            else:
                return False

    @staticmethod
    def zip_del(src_zip_filename, entryname_list):
        """
        功能：从压缩文件中删除指定文件
        :param src_zip_filename: 待操作的压缩包文件
        :param entryname_list: 待删除的文件列表,自动判断entryname_list的类型是一个字符串还是一个列表。
        :return: 成功返回True，失败返回False
        不能从带密码的压缩包内删除文件
        """
        src_zip_filename = os.path.normcase(src_zip_filename)
        if not os.path.exists(src_zip_filename):
            logging.error('[ZipFileHelper.zip_del] 删除失败，原因：%s文件不存在', src_zip_filename)
            return False
        elif not zipfile.is_zipfile(src_zip_filename):
            logging.error('[ZipFileHelper.zip_del] 删除失败，原因：%s文件不是ZIP文件', src_zip_filename)
            return False
        new_zip_file_name = src_zip_filename + '_'  # zipfile 未提供直接从压缩包中删除文件的方法，这里采用将不删除的文件保存到另外一个压缩包
        src_zip_object = zipfile.ZipFile(src_zip_filename)
        new_zip_object = zipfile.ZipFile(new_zip_file_name, 'w')
        if isinstance(entryname_list, str):
            temp_list = []
            temp_list.append(os.path.normcase(entryname_list))
            entryname_list = temp_list
        elif not isinstance(entryname_list, list):
            logging.error('[ZipFileHelper.zip_del] 参数类型错误，entryname_list 应该是str、list类型，不应该是%s',
                          type(entryname_list))
            return False
        entryname_list = Utils.normal_list(entryname_list)
        for name in src_zip_object.namelist():
            oriname = name
            try:
                if os.sep == '\\':   # zipfile.namelist中存储的文件名以 / 分割
                    name = name.replace('/', os.sep)
                if name not in entryname_list:
                    data = src_zip_object.read(oriname)
                    new_zip_object.writestr(name, data)
            except Exception as e:
                logging.error('[ZipFileHelper.zip_del] 删除文件%s失败，原因：%s', name, e)
                src_zip_object.close()
                new_zip_object.close()
                os.remove(new_zip_file_name)
                return False
        src_zip_object.close()
        new_zip_object.close()
        os.remove(src_zip_filename)
        os.rename(new_zip_file_name, src_zip_filename)

    def create(self, zip_filename):
        """
        功能：新建一个zip压缩包文件
        :param zip_filename:
        :return:
        """
        self._zip_file_name = zip_filename
        self._zip_file_object = zipfile.ZipFile(zip_filename, 'w')
        self._zip_file_object.close()

    def push(self, filename_list, entryname_list=None):
        """
        功能：对zip压缩包文件添加文件
        :param filename_list:可以是单个文件，也可以是列表
        :param entryname_list:
        :return:
        """
        if self._zip_file_object is not None:
            self._zip_file_object.close()
        self._zip_file_object = zipfile.ZipFile(self._zip_file_name, 'a')
        if isinstance(filename_list, str):
            temp_list = []
            temp_list.append(os.path.normcase(filename_list))
            filename_list = temp_list
        elif not isinstance(filename_list, list):
            logging.error('[ZipFileHelper.push] 参数类型错误，push(filename_list) filename_list 应该是str、list类型，不应该是%s',
                          type(filename_list))
            return False
        if isinstance(filename_list, list):
            filename_list = Utils.normal_list(filename_list)
            all_file_path_list = []
            for file_name in filename_list:
                if os.path.exists(file_name):
                    file_path_list = []
                    Utils.dfs_get_file(file_name, file_path_list)  # 遍历文件夹
                    all_file_path_list.extend(file_path_list)
                else:
                    logging.error('[ZipFileHelper.push] 添加%s失败，原因：%s', file_name, '该文件不存在')
            if isinstance(entryname_list, str):
                temp_list = []
                temp_list.append(os.path.normcase(entryname_list))
                entryname_list = temp_list
            elif not isinstance(entryname_list, list):
                entryname_list = []
            base_file_name = os.path.dirname(self._zip_file_name)  # 压缩包路径
            if base_file_name == '':
                base_file_name = os.getcwd()
            if isinstance(entryname_list, list):
                entryname_list = Utils.extend_entry_name(all_file_path_list, entryname_list, base_file_name)
            for file_index in range(len(all_file_path_list)):   # 循环添加文件
                try:
                    self._zip_file_object.write(all_file_path_list[file_index], entryname_list[file_index])
                except Exception as e:
                    logging.error('[ZipFileHelper.push] 添加%s失败，原因：%s', all_file_path_list[file_index], e)
        self._zip_file_object.close()
    def pull(self, entryname_list, filename_list=None):
        """
        功能：从zip压缩包文件拉出文件
        :param entryname_list:可以单个，也可以是列表
        :param filename_list:可以跟entryname_list对应，不填或者是相对路径默认拉出的文件放在zip文件的父目录下
        :return:
        """
        if self._zip_file_object is not None:
            self._zip_file_object.close()
        self._zip_file_object = zipfile.ZipFile(self._zip_file_name, 'r')
        if isinstance(entryname_list, str):
            temp_list = []
            temp_list.append(os.path.normcase(entryname_list))
            entryname_list = temp_list
        elif not isinstance(entryname_list, list):
            logging.error('[ZipFileHelper.push] 参数类型错误，push(filename_list) filename_list 应该是str、list类型，不应该是%s',
                          type(entryname_list))
            return False
        if isinstance(entryname_list, list):
            entryname_list = Utils.normal_list(entryname_list)
            base_file_name = os.path.dirname(self._zip_file_name)
            if base_file_name == '':
                base_file_name = os.getcwd()
            if filename_list is None:
                filename_list = []
                for entry_name in entryname_list:
                    filename_list.append(os.path.join(base_file_name, entry_name))
            elif isinstance(filename_list, str):
                temp_list = []
                if os.path.isabs(filename_list):
                    temp_list.append(os.path.normcase(filename_list))
                else:
                    temp_list.append(os.path.join(base_file_name, filename_list))
                filename_list = temp_list
            elif not isinstance(filename_list, list):
                filename_list = []
            if isinstance(filename_list, list):
                for file_index in range(len(filename_list)):
                    if not os.path.isabs(filename_list[file_index]):
                        file_name = filename_list[file_index]
                        del filename_list[file_index]
                        filename_list.insert(file_index, os.path.join(base_file_name, file_name))
                for file_index in range(len(filename_list), len(entryname_list)):
                    filename_list.append(os.path.join(base_file_name, entryname_list))

            for file_index in range(len(entryname_list)):
                try:
                    file_path = os.path.split(filename_list[file_index])[0]
                    for name in self._zip_file_object.namelist():
                        oriname = name
                        if os.sep == '\\':
                            name = name.replace('/', os.sep)
                        if name == entryname_list[file_index]:
                            if name.endswith(os.sep):
                                os.makedirs(name)
                                pass
                            if file_path is not None and file_path != '':
                                if not os.path.exists(file_path):
                                    os.makedirs(file_path)
                            with open(filename_list[file_index], 'wb') as file:
                                file.write(self._zip_file_object.read(oriname))
                            break
                except Exception as e:
                    logging.error('[ZipFileHelper.pull] 提取%s失败，原因：%s', entryname_list[file_index], e)

    def close(self):
        """
        功能：zip压缩包文件操作完毕，关闭。
        :return:
        """
        if self._zip_file_object is not None:
            self._zip_file_object.close()


class Utils:
    def __init__(self):
        pass

    @staticmethod
    def dfs_get_file(input_path, result, path=None):
        """
        功能：递归遍历input_path下所有文件
        :param input_path: 文件夹路径
        :param result: 文件夹内全部文件名列表
        :param path: 可选项，文件 父目录列表
        :return:
        """
        if os.path.isdir(input_path):
            files = os.listdir(input_path)
            for file in files:
                file_path = os.path.join(input_path, file)
                Utils.dfs_get_file(file_path, result, path)
        else:
            s = os.path.split(input_path)[0]
            if path is not None:
                if not s.endswith(os.sep):
                    path.append(s + os.sep)
            result.append(input_path)

    @staticmethod
    def entry_name(file_name, base_file_path):
        """
        功能：根据file_name 和base_file_path 计算entry_name 相对路径
        :param file_name: 文件名
        :param base_file_path: 压缩包path
        :return: 返回值为entry_name相对路径
        """
        if os.path.splitdrive(file_name)[0] == '':   # 如果是相对路径 则转为绝对路径
            file_name = os.path.join(os.getcwd(), file_name)
        file_name = file_name.upper()
        base_file_path = base_file_path.upper()
        index = file_name.find(base_file_path)
        if index == 0:
            if base_file_path == os.sep:
                return file_name[1:]
            else:
                entry_name = file_name.replace(base_file_path, '')
                return entry_name
        else:
            entry_name = os.path.split(file_name)[1]
            return entry_name

    @staticmethod
    def normal_list(file_list):
        """
        功能：将用户输入的路径转换为与系统相同路径
        :param file_list: 用户输入路径
        :return: 与系统相同的路径
        """
        if isinstance(file_list, list):
            normal = []
            for file in file_list:
                normal.append(os.path.normcase(file))
            file_list = normal
            return file_list
        return None

    @staticmethod
    def get_zip_name(input_file, output_file):
        """
        功能：获取压缩包名
        :param input_file: 要压缩的文件
        :param output_file: 压缩包名
        :return: 压缩包名
        """
        try:
            if output_file is None or output_file == '':
                dirname = os.path.dirname(input_file)
                file_name = os.path.split(input_file)[1]
                output_file = os.path.join(dirname, file_name)
            else:
                if os.path.isabs(output_file):
                    output_file = os.path.splitext(output_file)[0]
                else:
                    dirname = os.path.dirname(input_file)
                    file_name = os.path.splitext(output_file)[0]
                    output_file = os.path.join(dirname, file_name)
            return output_file
        except:
            return None

    @staticmethod
    def extend_entry_name(file_name_list, entryname, base_file_name):
        """
        功能：根据file_name_list 扩展entryname
        :param file_name_list: 文件列表
        :param entryname: emtryname列表，与file_name_list相对应
        :param base_file_name: 压缩包path
        :return: entryname 列表
        """
        entryname = Utils.normal_list(entryname)
        for index in range(len(entryname)):
            if entryname[index] is None or entryname[index] == '':
                entry_name = Utils.entry_name(file_name_list[index], base_file_name)
                del entryname[index]
                entryname.insert(index, entry_name)
        if len(entryname) < len(file_name_list):
            for index in range(len(entryname), len(file_name_list)):
                entryname.append(Utils.entry_name(file_name_list[index], base_file_name))
        return entryname

def main():

    # 这里写测试代码
    z = ZipFileHelper()

    # z.zip_file('abc\\test\\2.jpg', 'd:\\remote.zip')
    # z.zip_file('test')
    # z.zip_file(['2.txt', '12.txt'], '2.zip', None, password='')
    # z.zip_file(['test'], 'good.zip', ['test/1/test.txt'], password='123')
    # z.unzip_file('d:\\test.zip')
    # z.unzip_file('good.zip', None, '123')
    # z.unzip_file('test.zip', 'abc', password='123')
    #
    # z.zip_add('d:\\test.zip', 'd:\\1.txt', 'b.txt')
    # z.zip_add('c.zip', ['1.txt', 'res\\3.jpg'])
    # z.zip_add('d:\\test.zip', ['d:\\1.txt', 'd:\\abc\\2.txt'], ['1.txt', 'abc\\3.txt'])
    # z.zip_add('d:\\test.zip', '1.txt')
    # z.zip_add('e:\\star\\c.zip', ['2.txt', '1.txt'])
    #
    # z.zip_del('d:\\test.zip', ['test\\2.txt', 'abc\\2.txt'])
    # z.zip_del('d:\\test.zip', 'test\\1\\good.txt')
    #
    z.create('e:\\star\\c.zip')
    # z.push(['test'])
    # z.push(['1.txt', 'd:\\test\\2.txt'])
    # z.push('test\\3.txt')
    z.push('res\\2.jpg', 'test\\2.jpg')
    #
    z.pull('test\\2.jpg')
    # z.pull('1.txt', 'test\\2.jpg')
    # z.pull(['1.txt'], ['2.txt'])
    #
    z.close()
    return True


if __name__ == '__main__':
    try:
        main()
    except:
        print(traceback.format_exc())