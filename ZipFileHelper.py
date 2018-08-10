# coding: utf-8

import os
import sys
import traceback


class ZipFileHelper:
    def __init__(self):
        pass

    @staticmethod
    def zip_file(src_filepath, dst_zip_filename=None, password=None):
        '''
        功能：把一个源文件或目录压缩为一个zip文件。该方法为静态方法。
        :param src_filepath: 待压缩的文件或目录，请自行内部判断
        :param dst_zip_filename: 被压缩成的zip文件的路径，可以是相对路径，也可以是全路径。
        如果dst_zip_filename为空或None，则自动取相对路径，名称为src_filepath的文件名（不含后缀，如果是目录直接是目录名），后缀为.zip
        如果是相对路径则在src_filepath的父目录下生成zip文件。
        :param password: 压缩文件是否带密码，默认不带，否则请指定密码字符串
        :return: 压缩成功返回True，失败返回False
        '''
        pass

    @staticmethod
    def unzip_file(src_zip_filename, dst_dir_path=None, password=None):
        '''
        功能：把压缩包文件解压到指定目录
        :param src_zip_filename:
        :param dst_dir_path: 不填则解压到压缩包的父目录下。否则需要判断dst_dir_path的父目录是否存在，不存在则报错，然后再创建dst_dir_path目录（不存在的话）。
        :param password: 如果解压需要密码，这里输入
        :return: 成功返回True，失败返回False
        '''
        pass

    @staticmethod
    def zip_file(src_filepath, entryname=None, dst_zip_filename=None, password=None):
        '''
        功能：压缩单个文件。该方法为静态方法。
        :param src_filepath: 单个文件路径
        :param entryname: 显示在压缩包里的文件名
        :param dst_zip_filename:
        :param password: 压缩文件是否带密码，默认不带，否则请指定密码字符串
        :return: 压缩成功返回True，失败返回False
        '''
        pass

    @staticmethod
    def zip_add(src_zip_filename, filename_list, entryname_list=None):
        '''
        功能：在zip压缩包里添加一个文件。该方法为静态方法。
        :param self:
        :param src_zip_filename: 待添加文件的zip压缩包
        :param filename_list:待添加到压缩包里的文件列表，自动判断是单个文件路径还是一个列表
        :param entryname_list:添加到压缩包里的entry目录名列表，如果不填，则自动计算，计算规则：
        如果filename与src_zip_filename具有相同目录结构如：D:\test\a.zip,D:\test\abc\def\g.txt，则entryname为abc\def\g.txt
        否则entryname为文件名
        filename_list与entryname_list为对应关系，如果某一个entryname为空或None则自动计算。
        :return:成功返回True，失败返回False
        '''
        pass

    @staticmethod
    def zip_del(src_zip_filename, entryname_list):
        '''
        功能：从压缩文件中删除指定文件
        :param src_zip_filename: 待操作的压缩包文件
        :param entryname_list: 待删除的文件列表,自动判断entryname_list的类型是一个字符串还是一个列表。
        :return: 成功返回True，失败返回False
        '''
        pass


    def ceate(self, zip_filename):
        '''
        功能：新建一个zip压缩包文件
        :param zip_filename:
        :return:
        '''
        pass

    def push(self, filename_list, entryname_list=None):
        '''
        功能：对zip压缩包文件添加文件
        :param filename:可以是单个文件，也可以是列表
        :param entryname:
        :return:
        '''
        pass

    def pull(self, entryname_list, filename_list=None):
        '''
        功能：从zip压缩包文件拉出文件
        :param entryname_list:可以单个，也可以是列表
        :param filename_list:可以跟entryname_list对应，不填默认拉出的文件放在zip文件的父目录下。
        :return:
        '''

    def close(self):
        '''
        功能：zip压缩包文件操作完毕，关闭。
        :return:
        '''

def main():
    # 这里写测试代码
    z = ZipFileHelper()

    z.zip_file('d:\\test')
    z.zip_file('d:\\test', None, '123')
    z.unzip_file('d:\\test.zip')
    z.unzip_file('d:\\test.zip', None, '123')
    z.unzip_file('d:\\test.zip', 'e:\\test\\abc\\def')

    z.zip_add('test.zip', ['1.txt', 'abc\\2.txt'])
    z.zip_add('test.zip', ['1.txt', 'abc\\2.txt'], ['1.txt', '2.txt'])
    z.zip_add('test.zip', '1.txt')

    z.zip_del('test.zip', ['1.txt', 'abc\\2.txt'])
    z.zip_del('test.zip', '3.txt')

    z.create('c.zip')
    z.push('1.txt')
    z.push('2.png', 'res\\2.png')
    z.push(['1.txt', 'res\\2.png'])

    z.pull('1.txt')
    z.pull('res\\2.png')
    z.pull(['1.txt', 'res\\2.png'])

    z.close()

    return True


if __name__ == '__main__':
    try:
        main()
    except:
        print(traceback.format_exc())