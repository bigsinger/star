# coding: utf-8

import win32gui
import win32con
import win32api


def press_enter_on_window(hwnd):
    '''
    在某个窗口上发送enter按键
    :param hwnd: 需要发送enter按键的窗口句柄
    :return: 无返回值
    '''
    if hwnd:
        win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, 0)
        win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, 0)
        win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
        win32gui.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
    else:
        win32api.keybd_event(13, 0, 0, 0)
        win32api.keybd_event(13, 0, win32con.KEYEVENTF_KEYUP, 0)


def get_window_text(hwnd):
    '''
    获取某窗口的窗口文本
    :param hwnd: 待获取文本的窗口句柄
    :return: 窗口文本，未获取到返回None
    '''
    text = None
    if hwnd:
        # 文本框内容长度
        length = win32gui.SendMessage(hwnd, win32con.WM_GETTEXTLENGTH)
        if length:
            length += 1
            buf = win32gui.PyMakeBuffer(length)
            result_length = win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, length, buf)
            # print(result_length)
            address, length = win32gui.PyGetBufferAddressAndLen(buf)
            text = win32gui.PyGetString(address, length)
            # print('text: ', text)
    return text


def get_box_text(hwnd_box):
    '''
    获取对话框的弹框内容
    :param hwnd_box: 弹的对话框的句柄
    :return: 弹框内容的static的句柄, 文本；未获取到返回None, None
    '''
    hwnd_result = None
    hwnd_after = None
    text = None
    for i in range(3):
        hwnd_after = win32gui.FindWindowEx(hwnd_box, hwnd_after, 'Static', None)
        if hwnd_after:
            text = get_window_text(hwnd_after)
            if text:
                text = text.strip()
                if text:
                    hwnd_result = hwnd_after
                    break
        else:
            hwnd_after = None
    return hwnd_result, text


def find_box_from_browser():
    '''
    查找浏览器网页的弹框
    :return: 弹框句柄，未找到返回0
    '''
    hwnd_box = win32gui.FindWindow('#32770', '来自网页的消息')
    return hwnd_box


