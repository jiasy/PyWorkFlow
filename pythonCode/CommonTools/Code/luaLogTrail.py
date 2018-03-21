#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
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
from optparse import OptionParser

# 导入 ../../base/ 中的代码
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, os.pardir, "base")))
import FileCopy
import FileReadWrite
import SysInfo
import SysCmd
import CommonUtils

# 修改所需属性
opsDict = {}
opsDict["targetFolderPath"] = 'lua所在的文件夹'
# 过滤 log 可以先跑程序，然后那个输出比较多，比如计时器，循环之类的。
# 按照相对路径带后缀名的一行，知道下一个带后缀名的一行之间，都是这个文件中要忽略的输出。
opsDict["filterLogs"] = '需要过滤掉的Log'


def replace_chars(match):
    char = match.group(0)
    return chars[char]


def getLogOut(path_, funcName_, comment_, pass_, par_):
    _passStr = "True"
    if pass_ == False:
        _passStr = "False"
    return 'LogUtil.fo("' + path_ + '","' + funcName_ + '","' + comment_ + '",' + _passStr + ',' + par_ + ')' + "\n"


def getLogIn(path_, funcName_, comment_, pass_, par_):
    _passStr = "True"
    if pass_ == False:
        _passStr = "False"
    return 'LogUtil.fi("' + path_ + '","' + funcName_ + '","' + comment_ + '",' + _passStr + ',' + par_ + ')' + "\n"


# 在py代码的每一个方法中，进入
# ------------------------------------测试用例---------------------------------------------------------------------------------------
if __name__ == '__main__':
    _ops = SysInfo.getOps(opsDict, OptionParser())
    _currentFolder = SysInfo.fixFolderPath(os.path.dirname(os.path.realpath(__file__)))
    # 获取 工具类 位置
    _luaUtilPath = os.path.join(_currentFolder, "luaLogTrailTemplet/log_trail_util.lua")

    # 后缀
    _codeSuffix = ".lua"
    # 过滤用的字符串链接，类 -> 方法
    _filterClassFuncJoin = " -> "

    # 创建代码备份
    FileCopy.folderBackUp(_ops.targetFolderPath)

    # 获取过滤字典
    _filterLogsList = _ops.filterLogs.split(",")
    _filterLogsDict = CommonUtils.strToListDict(_ops.filterLogs, _codeSuffix)
    _filterPrints = CommonUtils.listDictToList(_filterLogsDict, _filterClassFuncJoin)

    # 过滤文件后缀
    _fileFilter = [_codeSuffix]
    # 过滤出来的文件列表
    _fileList = []
    # 过滤文件 - 先筛选文件，后添加工具，这样工具就不会被解析
    FileReadWrite.gci(_ops.targetFolderPath, _fileFilter, _fileList)
    # 拷贝工具到创建备份后的源文件目录
    shutil.copy(_luaUtilPath, _ops.targetFolderPath)

    for _i in range(len(_fileList)):
        _luaPath = _fileList[_i]
        _shortPath = SysInfo.getRelativePathWithOutSuffix(_ops.targetFolderPath, _luaPath, _codeSuffix)
        print _shortPath
        _luaCodes = FileReadWrite.linesFromFile(_luaPath)
        # 方法的信息，自己的缩进，自己的名称
        _funcDict = {}
        _funcDict["name"] = ""
        _funcDict["spaceStr"] = None
        _isMultipleCommon = False
        # 每一行
        for _j in range(len(_luaCodes)):
            _line = _luaCodes[_j]
            _orginalLine = _line
            # print "--------------------------------------------------------------------------------"
            # print "_orginalLine = " + str(_orginalLine)
            # 是否进行过修改
            _changeBoo =False
            # 注释相关    -------------------------------------------------------------------------------------
            _commenReg = re.search(r'^(\s*)\-\-(.*)', _line)
            _commenMultipleBeginReg = re.search(r'^(\s*)\-\-\[\[(.*)', _line)
            _commenMultipleEndReg = re.search(r'^(.*)\]\](.*)', _line)
            if _isMultipleCommon == False:
                # print "不在多行注释中"
                if _commenReg and not _commenMultipleBeginReg:
                    # print "是注释，不是多行注释起始，直接清除代码，下一行"
                    _luaCodes[_j] = '\r\n'
                    # print "Begin : "+_orginalLine.split("\n")[0]
                    # print "End   : "
                    continue
                else:
                    _commenInLineReg = re.search(r'(.*)\-\-(.*)', _line)
                    if _commenInLineReg and not _commenMultipleBeginReg:
                        # print "是半行注释，不是多行注释起始，留前面的字符串"
                        _line = _commenInLineReg.group(1)
                        _luaCodes[_j] = _line + '\r\n'
                        _changeBoo = True

            # 多行注释
            if _isMultipleCommon == False:
                # print "不在多行注释中"
                # 多行注释 起始
                if _commenMultipleBeginReg and not _commenMultipleEndReg:
                    # print "多行起始，且没在本行结束，下面全都是注释"
                    # 多行注释开始，没有结束
                    _isMultipleCommon = True
                    _line = ""
                    _luaCodes[_j] = _line + '\r\n'
                    _changeBoo = True
                elif _commenMultipleBeginReg and _commenMultipleEndReg:
                    # print "多行起始，在本行结束，留存结束后的字符串"
                    # 多行注释写在同一行
                    _isMultipleCommon = False
                    _line = _commenMultipleEndReg.group(2)
                    _luaCodes[_j] = _line + '\r\n'
                    _changeBoo = True
            else:
                # print "在多行注释"
                if _commenMultipleEndReg:
                    # print "多行注释结束"
                    # 多行注释结束的那一行
                    _isMultipleCommon = False
                    _line = _commenMultipleEndReg.group(2)
                else:
                    # print "没结束，清空当前行"
                    _line = ""
                _luaCodes[_j] = _line + '\r\n'
                _changeBoo = True

            # 把print注释掉     -------------------------------------------------------------------------------------
            _printReg = re.search(r'^(\s+)print\((.*)', _line)
            if _printReg:
                _line = _printReg.group(1) + "--print(" + _printReg.group(2) +"\n"
                _changeBoo = True

            if _changeBoo:
                # print "Begin : "+_orginalLine.split("\n")[0]
                # print "End   : "+_line

            # 空白行跳过     ----------------------------------------------------------------------------------------
            if _line.strip() == "":
                continue






        _luaCodeStr = string.join(_luaCodes, "")
        FileReadWrite.writeFileWithStr(_luaPath, _luaCodeStr)
