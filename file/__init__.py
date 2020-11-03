# coding: utf-8

import io
import os
import sys
import json
import traceback


def read(filename, binary=True):
    '''
    一次性读取文本文件中的内容并返回。
    file：文本文件的路径。
    '''
    try:
        with open(filename, 'rb' if binary else 'r') as f:
            return f.read()
    except Exception as e:
        print(e)
        return None

def process_file(filename, chunk=1024):
    """
    process a file in chunks, this should save some time when processing large files
    testing with 37 million lines the file processed in just under 40 seconds
    """
    retval = set()
    with open(filename) as data:
        while True:
            piece = data.read(chunk)
            if piece:
                for item in piece.splitlines():
                    item = item.strip()
                    if not str(item).startswith("/"):
                        item = "/{}".format(item)
                    retval.add(item)
            else:
                break
    return retval

def write(filename, buf, binary=True):
    try:
        with open(filename, 'wb' if binary else 'w') as f:
            return f.write(buf)
    except Exception as e:
        print(e)
        return None

def load_json_file(file_path):
    '''
    功能：以utf-8编码的方式加载json文件，兼容Windows下以b'\xef\xbb\xbf'开头的utf-8文件.
    j = load_json_file('sample.json')
    print(j.get('keyname'))

    from codecs import BOM_UTF8
    BOM_UTF8 = b'\xef\xbb\xbf'
    :param file_path:json文件路径
    :return:返回解析好的json字典，失败返回None
    '''
    j = None
    s = None
    try:
        with io.open(file_path, 'rb') as f:
            s = f.read()
    except Exception as e:
        print(e)
        s = None

    if s is not None:
        try:
            if s.startswith(b'\xef\xbb\xbf'):
                j = json.loads(s[3:])
            else:
                j = json.loads(s)
        except:
            j = None

    return j