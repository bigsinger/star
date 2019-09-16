# coding: utf-8

from random import choice

'''
加解密
'''

#  生成随机密码
def genpasswd(length=8, chars = string.ascii_letters + string.digits):
    return ''.join([choice(chars) for i in range(length)])

# 计算字符串的MD5值，返回32个字符长度小写16进制符号
def md5hex(buf):
    if isinstance(buf, unicode):
        buf = buf.encode("utf-8")
    elif not isinstance(buf, str):
        buf = str(buf)
    m = hashlib.md5()
    m.update(buf)
    return m.hexdigest()

# 计算文件的MD5值
def md5file(fname):
    def read_chunks(fh):
        fh.seek(0)
        chunk = fh.read(8096)
        while chunk:
            yield chunk
            chunk = fh.read(8096)
        else: #最后要将游标放回文件开头
            fh.seek(0)
    m = hashlib.md5()
    if isinstance(fname, basestring) and os.path.exists(fname):
        with open(fname, "rb") as fh:
            for chunk in read_chunks(fh):
                m.update(chunk)
    #上传的文件缓存 或 已打开的文件流
    elif fname.__class__.__name__ in ["StringIO", "StringO"] or isinstance(fname, file):
        for chunk in read_chunks(fname):
            m.update(chunk)
    else:
        return None
    return m.hexdigest()

# 获取文件的sha1值，大写
def sha1file(file_path):
    with open(file_path, "rb") as file:
        s = sha1()
        while True:
            strRead = file.read(1024 * 1024)
            if not strRead:
                break
            s.update(file.read())
    return s.hexdigest().upper()

def getcrc32(s):
    return zlib.crc32(s)

# key = '0123456789abcdef'
def aesencode(s, key):
    mode = AES.MODE_CBC
    encryptor = AES.new(key, mode)
    r = encryptor.encrypt(s)
    return r

def aesdecode(s, key):
    mode = AES.MODE_CBC
    decryptor = AES.new(key, mode)
    r = decryptor.decrypt(s)
    return r

def base64encode(s):
    return base64.b64encode(s)
def base64decode(s):
    return base64.b64decode(s)