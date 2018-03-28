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
import codecs


def removeBom(filePath_):
    '''移除UTF-8文件的BOM字节'''
    BOM = b'\xef\xbb\xbf'
    existBom = lambda s: True if s == BOM else False

    f = open(filePath_, 'rb')
    if existBom(f.read(3)):
        print "utf-8"
        _fbody = f.read()
        with open(filePath_, 'wb') as f:
            f.write(_fbody)


# ------------------------------------文件读写--------------------------------------------------------------------------------
# 文件是否含有字符串
def fileHasString(filePath_, string_):
    return_value = False

    try:
        _file = open(filePath_, 'r')
        try:
            _fileLines = _file.readlines()
            for _line in _fileLines:
                if string_ in _line:
                    return_value = True
        finally:
            _file.close()
    except Exception as e:
        print(filePath_, e)
    return return_value


# 重新创建一个空文件夹
def reCreateFolder(folderPath_):
    if os.path.exists(folderPath_):
        shutil.rmtree(folderPath_)
    os.makedirs(folderPath_)


def contentFromFile(filePath_):
    _file = open(filePath_, 'r')
    _backStr = _file.read()
    return _backStr


# json文件直接读取成字典
def dictFromJsonFile(jsonPath_):
    return json.loads(contentFromFile(jsonPath_))


# 读取文件的每一行
def linesFromFile(filePath_):
    return open(filePath_, 'r').readlines()


# 文件夹里有没有这个类型的文件
def hasFileTypeInFolder(folderPath_, fileType_):
    _haveBoo = False
    for _parent, _dir_names, _file_names in os.walk(folderPath_):
        for _file_name in _file_names:
            if _file_name.split(".")[1] == fileType_:
                _haveBoo = True
                break
    return _haveBoo


# 文件夹里有没有这个类型的文件
def getFilePathsByType(folderPath_, fileType_):
    _filePathList = []
    for _parent, _dir_names, _file_names in os.walk(folderPath_):
        for _file_name in _file_names:
            if _file_name.split(".")[1] == fileType_:
                _file_path = os.path.join(_parent, _file_name)
                _filePathList.append(_file_path)
    return _filePathList


# 获取这个类型的文件的路径集合
def getFileContentByType(folderPath_, fileType_):
    _fileContentDict = {}
    for _parent, _dir_names, _file_names in os.walk(folderPath_):
        for _file_name in _file_names:
            if _file_name.split(".")[1] == fileType_:
                _file_path = os.path.join(_parent, _file_name)
                _fileContentDict[_file_path] = contentFromFile(_file_path)
    return _fileContentDict


# 删除文件夹中，对应类型的文件
def deleteFileTypeInFolder(folderPath_, fileType_):
    for _parent, _dir_names, _file_names in os.walk(folderPath_):
        for _file_name in _file_names:
            if _file_name.split(".")[1] == fileType_:
                os.remove(os.path.join(_parent, _file_name))


# 写文件
def writeFileWithStr(filePath_, codeStr_):
    try:
        _file = open(filePath_, 'w')
        try:
            _file.write(codeStr_)
        finally:
            _file.close()
    except Exception as e:
        print(filePath_, e)


# filepath_  中，满足 fileFilter_ 后缀条件的文件，放置到 fileList_ 中
# gci(文件目录,[".jpg",".jpeg",".bmp",".png"],存留列表)
def gci(filepath_, fileFilter_, fileList_):
    # 遍历filepath下所有文件，包括子目录
    files = os.listdir(filepath_)
    for fi in files:
        fi_d = os.path.join(filepath_, fi)
        if os.path.isdir(fi_d):
            gci(fi_d, fileFilter_, fileList_)
        else:
            jsPath = os.path.join(filepath_, fi_d)
            if jsPath and (os.path.splitext(jsPath)[1] in fileFilter_):
                fileList_.append(jsPath)


# filepath_  中，所有文件路径
def getAllFilePath(filepath_, fileList_):
    files = os.listdir(filepath_)
    for fi in files:
        fi_d = os.path.join(filepath_, fi)
        if os.path.isdir(fi_d):
            getAllFilePath(fi_d, fileList_)
        else:
            fileList_.append(os.path.join(filepath_, fi_d))


def makeDirPlus(path_):
    try:
        os.mkdir(path_)
    except OSError as exc:
        print "ERROR : 重置文件夹错误"
        print path_
        if exc.errno == errno.EEXIST:
            print "文件 已经 存在"
        elif exc.errno == errno.EACCES:
            print "文件 许可 拒绝"
        elif exc.errno == errno.ENOSPC:
            print "没有 硬盘 空间"
        elif exc.errno == errno.EROFS:
            print "文件 只读 存在"
        else:
            print "exc.errno : " + os.strerror(exc.errno)
        sys.exit(1)


# 文件夹中查找字符串------------------------------------------------------------------------------------------------------------------------
# strList_ 要找的字符串的列表
# fileFilters_ 在什么类型的文件中找
# folder_ 目标文件夹
# resultList_ 找到包含字符串的文件
# needAll_ 结果集中的文件,是否必须包含全部 strList_ 的字符串.
def findStrInFolder(strList_, fileFilters_, folder_, resultList_, needAll_):
    _fileList = []
    gci(folder_, fileFilters_, _fileList)
    for _filePath in _fileList:
        # 每一个File都重置成空
        _lineInfo = None
        _resultList = []
        for _str in strList_:
            _lineStr = fileHasString(_filePath, _str)
            if not (_lineStr == ""):
                if _lineInfo:
                    _lineInfo = _lineInfo
                else:
                    # 这个File里有才会成
                    _lineInfo = {}
                    _lineInfo["lineList"] = []
                    _lineInfo["filePath"] = _filePath
                _lineInfo["lineList"].append(_lineStr)
        if _lineInfo:
            # strList_ 中所有都满足才添加
            if needAll_:
                _findCount = 0
                # 传进来的每一个字符串,都满足
                for _str in strList_:
                    for _line in _lineInfo["lineList"]:
                        if _line.find(_str) >= 0:
                            _findCount += 1
                            break
                if _findCount == len(strList_):
                    resultList_.append(_lineInfo)
            else:
                resultList_.append(_lineInfo)


# 文件是否含有字符串-------------------------------
# filePath_ 文件路径
# string_ 是否包含的那个字符串
def fileHasString(filePath_, string_):
    _returnValue = ""
    try:
        _file = open(filePath_, 'r')
        try:
            _fileLines = _file.readlines()
            _countLine = 0
            for _line in _fileLines:
                _countLine += 1
                if string_ in _line:
                    _returnValue = "<" + str(_countLine) + "> " + _line
        finally:
            _file.close()
    except Exception as e:
        print(filePath_, e)
    return _returnValue
