#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import re
import os
import json
import time
import string
import shutil
import urllib2
from subprocess import PIPE, Popen
from PIL import Image
import xlrd
import datetime
import commands
import getopt
import errno
import getpass
from biplist import *

# 移除掉一些麻烦的字符串
chars = {
    '\xc2\x82': ',',  # High code comma
    '\xc2\x84': ',,',  # High code double comma
    '\xc2\x85': '...',  # Tripple dot
    '\xc2\x88': '^',  # High carat
    '\xc2\x91': '\x27',  # Forward single quote
    '\xc2\x92': '\x27',  # Reverse single quote
    '\xc2\x93': '\x22',  # Forward double quote
    '\xc2\x94': '\x22',  # Reverse double quote
    '\xc2\x95': ' ',
    '\xc2\x96': '-',  # High hyphen
    '\xc2\x97': '--',  # Double hyphen
    '\xc2\x99': ' ',
    '\xc2\xa0': ' ',
    '\xc2\xa6': '|',  # Split vertical bar
    '\xc2\xab': '<<',  # Double less than
    '\xc2\xbb': '>>',  # Double greater than
    '\xc2\xbc': '1/4',  # one quarter
    '\xc2\xbd': '1/2',  # one half
    '\xc2\xbe': '3/4',  # three quarters
    '\xca\xbf': '\x27',  # c-single quote
    '\xcc\xa8': '',  # modifier - under curve
    '\xcc\xb1': ''  # modifier - under line
}


def replace_chars(match):
    char = match.group(0)
    return chars[char]


def removeAnnoyingChars(targetStr_):
    return re.sub('(' + '|'.join(chars.keys()) + ')', replace_chars, targetStr_)


# 参数字符串，转换成字典。
# a:b,c:d -> {{a:b},{c:d}}
def strListToDict(str_):
    # , 分割每一组键值
    _strList = str_.split(",")
    _backDict = {}
    for _i in range(len(_strList)):
        _strItem = _strList[_i]
        # : 分割键值对
        _strKV = _strItem.split(":")
        _backDict[_strKV[0]] = _strKV[1]
    return _backDict


# 参数字符串，整理成键值对字典，字典的值是数组。
# 逐个项判断，是否是一个目标类型的文件
# "a.lua,aCode1,aCode2,aCode3,b.lua,bCode1,bCode2,bCode3"
# 转换成以下格式
# {'a': ['aCode1', 'aCode2', 'aCode3'], 'b': ['bCode1', 'bCode2']}
def strToListDict(str_, suffix_):
    # a.js,aCode1,aCode2,aCode3,b.js,bCode1,bCode2,bCode3
    # a
    # ,aCode1,aCode2,aCode3,b
    # ,bCode1,bCode2,bCode3
    _strListTemp = str_.split(suffix_)
    _backDict = {}
    for _i in range(len(_strListTemp) - 1):
        _item = _strListTemp[_i]
        # 获取文件名 a、b
        _filePathList = _item.split(",")
        _filePath = _filePathList[len(_filePathList) - 1]
        # 获取每个文件下的字符串列表
        _itemNext = _strListTemp[_i + 1]
        _contentList = _itemNext.split(",")
        # 建立键值关系
        if _i == (len(_strListTemp) - 2):
            _backDict[_filePath + suffix_] = _contentList[1:len(_contentList)]  # 最后一项，不用去掉最后一个字符串
        else:
            _backDict[_filePath + suffix_] = _contentList[1:len(_contentList) - 1]
    return _backDict


# 将字典转换成列表
# {"/a": ["aCode1", "aCode2", "aCode3"], "/b": ["bCode1", "bCode2"]}
# 转换成以下格式
#  [/b -> bCode1,/b -> bCode2]
def listDictToList(targetDict_, split_):
    backList = []
    for _key in targetDict_:
        _valueList = targetDict_[_key]
        for _i in range(len(_valueList)):
            backList.append(_key + split_ + _valueList[_i])
    return backList
