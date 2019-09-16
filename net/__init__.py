# coding: utf-8

import os
import re
import http
import requests
import traceback
import urllib, urllib.request
from urllib import parse


# this is a regex to validate a URL. It was taken from Django's URL validation technique
# reference can be found here:
# `https://stackoverflow.com/questions/7160737/python-how-to-validate-a-url-in-python-malformed-or-not/7160778#7160778`
URL_VALIDATION = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE
)


def post(url, data, headers = None):
    '''
    有时不能返回正确的编码导致的乱码文本，可以指定下headers中的：'Accept': 'text/html',
    test code: 
    import star.net
    url = 'http://xxx.com/yyy'
    data = {'param1': data1}
    s = star.net.post(url, data)
    print(s)
    
    :param url: 
    :param data: 
    :param headers: 
    :return: 
    '''
    h = headers
    if h is None:
        h = {
            'Accept': 'text/html',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            }
    r = requests.post(url, data = data, headers = h)
    return r.content.decode()

def post_get_soup(url, data, headers = None):
    '''
    发送post请求并返回BeautifulSoup
    import star.net
    s = star.net.post_get_soup("http://www.ximalaya.com/tracks/19158075/play", {'played_secs': 0, "duration": 0})
    print(s)
    :param url:
    :param data:
    :param headers:
    :return:
    '''
    from bs4 import BeautifulSoup
    h = headers
    if h is None:
        h = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 Safari/537.36'}
    s = requests.session()
    r = s.post(url, data = data, headers = h)
    soup = BeautifulSoup(r.text, "lxml")
    return soup

def post2(url, data, headers = None):
    '''
    import star.net
    s = star.net.post2('http://xxx.com/yyy', {'param1': data1})
    print(s)
    如果把调用urllib.request.Request的参数method设为GET，即是GET请求
    :param url: 
    :param data: 
    :param headers: 
    :return: 
    '''
    h = headers
    if not h:
        h = {
            'Accept': 'text/html',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
    data = urllib.parse.urlencode(data)
    data = data.encode('utf-8')
    try:
        req = urllib.request.Request(url=url, data=data, headers=h, method='POST')
        response = urllib.request.urlopen(req)
        # print(response.info())              # 返回的http头
        return response.read().decode()
    except urllib.error.HTTPError as e:
        print(traceback.format_exc())
        return None
    else:
        return None


def postdata(url, data, headers = None, isdecode = False):
    '''
    import star.net
    s = star.net.postdata("http://xxx.com/yyy", {'param1': data1})

    :param url:
    :param data:
    :param headers:
    :param isdecode:
    :return:
    '''
    post_data = urllib.parse.urlencode(data)
    post_data = post_data.encode('utf-8')

    h = headers
    if h is None:
        h = {
            'Accept': 'text/html',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 Safari/537.36',
        }
    cj = http.cookiejar.CookieJar() # cookielib.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    req = urllib.request.Request(url=url, data=post_data, headers=h, method='POST')
    response = opener.open(req)
    # print(response.info())              # 返回的http头
    content = response.read()
    if isdecode is True:
        content = gzipdecode(content)
    return content.decode()

###################################################

def build_opener_with_chrome_cookies(domain=None):
    import sqlite3
    import http.cookiejar
    import urllib
    import os, sys
    import win32crypt
    import browsercookie

    cookie_file_path = os.path.join(os.environ['LOCALAPPDATA'], 'Google/Chrome/User Data/Default/Cookies')
    if not os.path.exists(cookie_file_path):
        raise Exception('Cookies file not exist!')
    conn = sqlite3.connect(cookie_file_path)
    # sql = 'select host_key, name, value, path from cookies'
    sql="select host_key,name,encrypted_value,path from cookies";
    if domain:
        sql += ' where host_key like "%{}%";'.format(domain)

    cookie_jar = http.cookiejar.CookieJar()  # No cookies stored yet

    for row in conn.execute(sql):
        pwd_hash = str(row[2])
        try:
            ret = win32crypt.CryptUnprotectData(pwd_hash, None, None, None, 0)
        except:
            print('Fail to decrypt chrome cookies')
            sys.exit(-1)

        cookie_item = http.cookiejar.Cookie(
            version=0, name=row[1], value=ret[1],
            port=None, port_specified=None,
            domain=row[0], domain_specified=None, domain_initial_dot=None,
            path=row[3], path_specified=None,
            secure=None,
            expires=None,
            discard=None,
            comment=None,
            comment_url=None,
            rest=None,
            rfc2109=False,
        )
        cookie_jar.set_cookie(cookie_item)  # Apply each cookie_item to cookie_jar
    conn.close()
    proxy = {'http':'27.24.163.155:10'}
    # Return opener
    return urllib.request.build_opener(urllib.request.ProxyHandler(proxy),urllib.request.HTTPCookieProcessor(cookie_jar))

def get_page_content_1(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6',
    }
    opener = build_opener_with_chrome_cookies(domain='baidu.com')
    req = urllib.request.Request(url, headers=headers, method='GET')
    page_content = opener.open(req).read()
    return page_content


def get_page_content_2(url):
    '''
    pip install browsercookie2
    s = star.net.get_page_content_2('www.baidu.com')

    :param url:
    :return:
    '''
    import browsercookie
    cj = browsercookie.chrome()
    page = requests.get(url, cookies=cj)
    return page.content

'''
网络相关
'''
###################################################

# 获取网页源码，内部已设置浏览器引擎防止反爬虫。
def get_data(url):
    req = urllib.request.Request(url)
    useragent =  "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0"
    try:
        req.add_header('User-Agent', useragent)
        req.add_header('Referer',url)
        #req.add_header('Cookie',cookie)
        response = urllib.request.urlopen(req, timeout=5)
        data = response.read().decode()
        return data
    except :
        return None

#使用requests库封装一个简单的通过get方式获取网页源码的函数
def get_data2(url, decode = True):
    html = requests.get(url)
    # print(html.encoding)

    if decode is True:
        s = html.text.encode(html.encoding)
    else:
        s = html.text
    # s = BeautifulSoup(s, "lxml")

    s = s.decode() # Python3添加，转换为Unicode
    return s

#简单的爬虫脚本，用来爬取网页gethtmlex('xxxxx', {'ip': '8.8.8.8'})
def get_data_ex(url, params = None):
    headers = {
           'Accept-Language': 'en-US,en;q=0.5',
           'Accept-Encoding': 'gzip, deflate',
           'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Connection' : 'keep-alive',
           }
    headers['User-Agent'] = "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0" #USER_AGENTS[random.randint(0, len(USER_AGENTS)-1)]
    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        r.raise_for_status()
    except requests.RequestException as e:
        logging.error(e)
        return None
    else:
        # print(r.encoding)
        return r.content.decode()

# 下载网页源码到本地文件
def download_file(url, f):
    filename = None
    try:
        filename = urllib.urlretrieve(url, filename = f)
        # print filename[0], filename[1]
    except Exception as e:
        print('except: ' + e.message)
        filename = None
    return filename

# 下载文件
def download_file2(url, file):
    if url.find('http') < 0:
        url = 'http:' + url
    else:
        url = url.replace('https:', 'http:')
    print(url)
    urllib.request.urlretrieve(url, file)

# 下载图片到本地
def download_images(photos=[]):
    save_dir = os.path.join(os.getcwd(), 'images')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # downloads
    for url in photos:
        download_file(url, os.path.join(save_dir,os.path.basename(url)))


# star.net.quote("你好") 输出 %E4%BD%A0%E5%A5%BD
def quote(s):
    return urllib.request.quote(s)
# star.unquote("%E4%BD%A0%E5%A5%BD") 输出 你好
def unquote(s):
    return urllib.request.unquote(s)


# 解密网络数据中的gzip加密数据
def gzipdecode(data):
    import gzip
    from io import StringIO
    s = StringIO.StringIO(data)
    gziper = gzip.GzipFile(fileobj = s)
    data = gziper.read()
    return data

def grab_random_user_agent():
    """
    grab a random user agent out of a file
    """
    import random

    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'user_agents.txt')
    with open(path) as agents:
        return random.choice(agents.readlines()).strip()

def create_request_headers(proxy=None, headers=None, user_agent=False):
    """
    configure the request headers and proxy information
    """
    if proxy is not None:
        proxy_retval = {"http": proxy, "https": proxy}
    else:
        proxy_retval = {}
    if headers is not None:
        header_retval = {}
        for k in headers.keys():
            header_retval[k] = headers[k]
    else:
        header_retval = {"Connection": "close"}
    if user_agent:
        header_retval["User-Agent"] = grab_random_user_agent()
    return proxy_retval, header_retval

def is_valid_url(url):
    """
    basic heuristic check to see if the URL is validated or not
    a valid URL should have 'http(s)://' in it
    
    test, usable_url = star.net.heuristics('http://www.baidu.com/adfljl?a;lsdfk')
    print(test)         # True
    print(usable_url)   # http://www.baidu.com/adfljl
    """
    if not URL_VALIDATION.match(url):
        return False, None
    parsed_url = parse.urlparse(url)
    try:
        usable_url = "{}://{}{}".format(parsed_url.scheme, parsed_url.netloc, parsed_url.path)
    except:
        usable_url = "{}://{}".format(parsed_url.scheme, parsed_url.netloc)
    return True, usable_url