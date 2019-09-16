# coding: utf-8

import re

def to_bytes(s):
    '''
    把str转换为bytes
    :param s: 
    :return: 
    '''
    # return s.encode('utf-8', 'ignore')    # Python2
    return bytes(s, encoding='utf-8', errors='ignore')

def to_str(b):
    '''
    把bytes转换为str
    :param b: 
    :return: 
    '''
    # return b.decode('utf-8', 'ignore')    # Python2
    return str(b, encoding='utf-8', errors='ignore')

# win下命令行参数为gbk编码：star.gbk2unicode(sys.argv[1]) + u'你好'
def gbk2unicode(s):
    return s.decode('gbk', 'ignore')

# 脚本文件#coding:utf-8时默认不带u的字符串为utf8字符串：star.utf82unicode('我')
def utf82unicode(s):
    return s.decode('utf-8', 'ignore')

# 带u的字符串为unicode
# star.unicode2gbk(u'\u4e5f\u6709')
# star.unicode2gbk(u'也有')
def unicode2gbk(s):
    return s.encode('gbk')

# 带u的字符串为unicode
# star.unicode2utf8(u'\u4e5f\u6709')
# star.unicode2utf8(u'也有')
def unicode2utf8(s):
    return s.encode('utf-8')

# win下命令行参数为gbk编码：star.gbk2utf8(sys.argv[1]) + '也有'
def gbk2utf8(s):
    return s.decode('gbk', 'ignore').encode('utf-8')

def utf82gbk(s):
    return s.decode('utf-8', 'ignore').encode('gbk')



'''
在content中查找规则为reg的字符串，如果指定捕获的结果列表，则按指定的序号(基数从1开始)返回。
如果未指定结果列表则直接返回命中结果，由调用者自行提取。
若未命中返回None，指定的多返回结果也均为None。

x, y = star.find('"(.*?)"(.*?)"(.*?)"', '"10"20"30"', [2,1])
print x, y  #20 10
x, y = star.find('"(.*?)"(.*?)"(.*?)"1', '"10"20"30"', [2,1])
print x, y  #None None
print star.find('"(.*?)"(.*?)"(.*?)"', '"10"20"30"')    #<_sre.SRE_Match object at 0x03123840>
print star.find('"(.*?)"(.*?)"(.*?)"1', '"10"20"30"')   #None
'''
def find(reg, content, group = None):
    pattern = re.compile(reg, re.U | re.S)
    result = pattern.search(content)
    if result is not None:
        if group is None or len(group) < 2:
            return result.group(1)
        else:
            return (result.group(i) for i in group)
    else:
        if group is None or len(group)==0:
            return None
        else:
            return (None for i in group)

'''
x, y = star.search('"(.*?)"(.*?)"(.*?)"', '"10"20"30"', 2, 1)
print x, y  #20 10
'''
def search(reg, content, *group):
    pattern = re.compile(reg, re.U | re.S)
    result = pattern.search(content)
    if result is not None:
        if group is None or len(group) < 2:
            return result.group(1)
        else:
            return (result.group(i) for i in group)
    else:
        if group is None or len(group) == 0:
            return None
        else:
            return (None for i in group)

'''
s = 'dd10aa20ccdd30aa40ccdd50aa60ccdd70aa80cc'
r = star.findall('dd(.*?)aa(.*?)cc', s)
[('10', '20'), ('30', '40'), ('50', '60'), ('70', '80')]

findall(r"<a.*?href=.*?<\/a>",ss,re.I)
'''
def findall(reg, content):
    r = re.findall(reg, content, re.S)
    return r
