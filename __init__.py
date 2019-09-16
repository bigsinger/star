# coding: utf-8

'''
A Common Python Lib By Sing

path
路径操作模块

file
文件操作模块

net
网络操作模块

zip
压缩包操作模块

加解密操作模块

pycrypto https://www.dlitz.net/software/pycrypto/

import star.net
import star.path
import star.debug
import star.strings
from star.debug.formatter import info, error
'''
import os
import sys
import base64
import ctypes
import datetime
import hashlib
import logging
import platform
import requests
import shutil
import socket
import struct
import urllib
import uuid
import zlib
import tempfile
from io import StringIO

# from Crypto.Cipher import AES

__all__ = ['path', 'file', 'net', 'zip', 'crypt']



# 先抓大后抓小
# html = star.gethtml("https://github.com/pythonstar/star/wiki/%E8%AF%B4%E6%98%8E%E6%96%87%E6%A1%A3")
# result = star.find('"wiki-pages"(.*?)"wiki-more-pages-link"', html)
# print result
# if result is not None:
#     r = re.findall(r'href="(.*?)" class="wiki-page-link">(.*?)<', result.group(1))
#     for i in r:
#         s = '[' + i[1] + '](https://github.com' + i[0] + ')'
#         print s


# def getImg(html):
#     reg = r'src="(.+?\.jpg)" pic_ext'
#     imgre = re.compile(reg)
#     imglist = re.findall(imgre,html)
#     x = 0
#     for imgurl in imglist:
#         urllib.urlretrieve(imgurl,'%s.jpg' % x)
#         x+=1

""" 或者参考：http://www.phpxs.com/code/1009240

from django.core import mail
connection = mail.get_connection()

# 手动打开链接(connection)
connection.open()

# 使用该链接构造一个邮件报文
email1 = mail.EmailMessage('Hello', 'Body goes here', 'from@example.com',
                          ['to1@example.com'], connection=connection)
email1.send() # 发送邮件

# 构造其他两个报文
email2 = mail.EmailMessage('Hello', 'Body goes here', 'from@example.com',
                          ['to2@example.com'])
email3 = mail.EmailMessage('Hello', 'Body goes here', 'from@example.com',
                          ['to3@example.com'])

# 在一个调用中发送两封邮件
connection.send_messages([email2, email3])
# 链接已打开，因此 send_messages() 不会关闭链接
# 要手动关闭链接
connection.close()
"""
