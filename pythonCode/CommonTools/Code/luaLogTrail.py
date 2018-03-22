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
# 过滤 file 文件
opsDict["filterFiles"] = '需要过滤掉的File'
# 过滤 reg 文件
opsDict["regFilters"] = '满足正则表达式的行，过滤掉'

def replace_chars(match):
    char = match.group(0)
    return chars[char]


def getLogOut(path_, funcName_, comment_, pass_, par_):
    _passStr = "True"
    if pass_ == False:
        _passStr = "false"
    return '    LogUtil:getInstance():fo("' + path_ + '","' + funcName_ + '","' + comment_ + '",' + _passStr + ',' + par_ + ')' + "\n"


def getLogIn(path_, funcName_, comment_, pass_, par_):
    _passStr = "True"
    if pass_ == False:
        _passStr = "true"
    return '    LogUtil:getInstance():fi("' + path_ + '","' + funcName_ + '","' + comment_ + '",' + _passStr + ',' + par_ + ')' + "\n"


def getCodeBlockInfo(regBegin_,regEndInCurrentLine_,line_):
    _funcReg = re.search(regBegin_, line_)
    if _funcReg:
        _funcReg_end = re.search(regEndInCurrentLine_, line_)
        if _funcReg_end:# 当前行开始当前行结束
            return _funcReg,True
        else:
            return _funcReg,False
    else:
        return None,False


# 在py代码的每一个方法中，进入
# ------------------------------------测试用例---------------------------------------------------------------------------------------
if __name__ == '__main__':
    _ops = SysInfo.getOps(opsDict, OptionParser())
    _currentFolder = SysInfo.fixFolderPath(os.path.dirname(os.path.realpath(__file__)))
    # 获取 工具类 位置
    _luaUtilPath = os.path.join(_currentFolder, "luaLogTrailTemplet/LogTrailUtil.lua")
    _luaUtilRelativePath = 'LogTrailUtil.lua'
    _requireStr = 'local LogUtil = require("app.LogTrailUtil")'


    _regFilters = _ops.regFilters.split(",")
    # for _i in range(len(_regFilters)):
    #     _item = _regFilters[_i]
    #     print "_item = " + str(_item)  


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

    # 获取过滤的文件
    _filterFilesList = list(_ops.filterFiles.split(","))

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
        if _shortPath in _filterFilesList:
            print " 忽略"
            continue
        # 每一行代码
        _luaCodes = FileReadWrite.linesFromFile(_luaPath)

        _isMultipleCommon = False
        # 代码块堆栈
        # 堆栈内的最后一项，为当前_line 所在的代码块。
        # 代码块，为流程控制、方法【if/repeat/while/for/func/anonymousFunc】中的一个
        # 代码块都属于一个函数:
        #   最外层的不属于任何函数，但是它属于他自己。
        #   函数的代码块，所携带的函数信息(funcDict)，就是它自己的信息。
        #   当发现一个函数，当前的代码所在函数信息重置(_currentFuncDict)。
        # {
        #   lineNum:行数,
        #   funcDict:自己所属的函数的信息。自己是函数块
        #   type:类型，if/repeat/while/for/function 中的一种
        # }
        _codeBlockStack = []
        _currentFuncDict = None

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

            # 把print注释掉     ------------------------------------------------------------------------------------
            _printReg = re.search(r'^(\s+)print\((.*)', _line)
            if _printReg:
                _line = _printReg.group(1) + "--print(" + _printReg.group(2) +"\n"
                _changeBoo = True

            # 判断是不是要过滤的     ---------------------------------------------------------------------------------
            for _k in range(len(_regFilters)):
                # 满足条件当前行，过滤掉
                if re.search(_regFilters[_k],_line):
                    _line = ""
                    _luaCodes[_j] = _line + '\r\n'
                    _changeBoo = True;
                    break

            if _changeBoo:
                # print "Begin : "+_orginalLine.split("\n")[0]
                # print "End   : "+_line
                pass

            # 空白行跳过     ----------------------------------------------------------------------------------------
            if _line.strip() == "":
                continue

            # Debug 到达这一行就断点 ---------------------------------------------------------------------------------
            if _line.find('AMapService:_createLocationOption_android(') >= 0:
                pass

            # 一行内有两个function。。。
            _twoFunRegInLine = re.search(r'^.*function\s*.*\s*\(.*\)\s*.*\s+function', _line)
            if _twoFunRegInLine:
                print "ERROR 一行 两个function"
                sys.exit(1)

            # 一行内是否有两个end
            _twoEndRegInLine = re.search(r'^.*\s*(\)?)\s*end\s*.*\s+(\)?)\s*end', _line)
            if _twoFunRegInLine:
                print "ERROR 一行 两个end"
                sys.exit(1)

            # 当前行可能是一个function
            _funcReg = re.search(r'^.*function\s*.*\s*\(.*', _line)
            # 简单过滤掉两边有 冒号的。不包括 "x" function "x" 这样的，有这样的就改一改吧。。。
            _commentFuncReg1 = re.search(r'^.*\".*function\s+.*\".*', _line)
            _commentFuncReg2 = re.search(r'^.*\'.*function\s+.*\'.*', _line)
            if _commentFuncReg1 or _commentFuncReg2:
                print "function 在引号中的 : "+_line
            if _funcReg and (not _commentFuncReg1) and (not _commentFuncReg2):
                # 满足正则之后，判断这个方法是不是在当前行就结束
                _funcRegStrToEnd = r'(.*)\s+end\s*'
                # 当前行 满足一个方法的正则，这里是有方法名的方法，匿名函数在后面
                _regList = [
                    #a.b = function(c
                    r'^\s*([A-Za-z0-9_\.]+)\s*=\s*function\s*\((.*)\)\s*',
                    # function a:b(c / function a.b(c / function a(c
                    r'^\s*function\s+([A-Za-z0-9_\:\.]+)\s*\((.*)\)\s*',
                    # local a function(c
                    r'^\s*local\s+([0-9a-zA-Z_]+)\s+function\s*\((.*)\)\s*',
                    # local a = function(c
                    r'^\s*local\s+([A-Za-z0-9_]+)\s*=\s*function\s*\((.*)\)\s*',
                    # local function a(c
                    r'^\s*local\s+function\s+([0-9a-zA-Z_]+)\s*\((.*)\)\s*',
                    # 匿名 方法
                    r'^.*function\s*()\s*\((.*)\)\s*'
                ]

                # 退出当前行判断的标示
                _endCurrentLineCheck = False
                for _idx in range(len(_regList)):
                    _regItem = _regList[_idx]
                    # 判断满不满足，是不是满足了且当前行就结束了
                    _isCodeBlockInfo,_endInOneLine = getCodeBlockInfo(_regItem,_regItem + _funcRegStrToEnd,_line)
                    # 当前行自己结束
                    if _isCodeBlockInfo and _endInOneLine == True:
                        _endCurrentLineCheck = True
                    # 没结束，且没符合条件，才能再判断是否满足下一个
                    if not(_endCurrentLineCheck == False and _isCodeBlockInfo == None):
                        break

                # 当前行不用再判断了
                if _endCurrentLineCheck:
                    continue

                # 是一个函数代码块，且没在本行结束，压栈
                if _isCodeBlockInfo and _endInOneLine == False:
                    _tempFuncDict = {}
                    _tempFuncDict["name"]       = _isCodeBlockInfo.group(1)
                    _tempFuncDict["parameters"] = _isCodeBlockInfo.group(2)
                    _currentFuncDict = _tempFuncDict
                    #   lineNum:行数,
                    #   funcDict:自己所属的函数的信息。自己是函数块
                    #   type:类型，if/repeat/while/for/func/anonymousFunc 中的一种
                    _blockDict = {}
                    _blockDict["lineNum"] = _j
                    _blockDict["funcDict"] = _currentFuncDict
                    _blockDict["type"] = "func"
                    _codeBlockStack.append(_blockDict)
                else:
                    # 走到这里可能就是一个 匿名方法 anonymousFunc
                    _betweenFuncReg = re.search(r'^.*function\s*(.*?)\s*\(.*', _line)
                    if _betweenFuncReg:
                        # function 和 （ 中间夹的部分有以下字符，那么这个就不是个方法了
                        if re.search(r'^[A-Za-z0-9_]*$',_betweenFuncReg.group(1)):
                            print "意料之外，改写法吧，要不就改这个py脚本 : " + _line
                        else:
                            # 当前行的function后面的参数是分多行写的
                            _funcReg = re.search(r'^.*function\s*[A-Za-z0-9\._\:]*\s*\(.*(?!\))', _line)
                            if _funcReg:
                                _tempJ = _j + 1#下一行，当前行清空，将自己合并到下一行
                                if _tempJ <= len(_luaCodes):
                                    _luaCodes[_j] = ""
                                    _luaCodes[_tempJ] = _line.replace('\n', '').replace('\t', '').replace('\r', '').strip() + _luaCodes[_tempJ]
                                    print "合并到下一行 : " + _luaCodes[_tempJ]
                                else:
                                    print "ERROR 当前方法参数没有括号收尾，代码已经结束了"
                                    sys.exit(1)
                            else:
                                print "不是方法 : " + _line
        _luaCodeStr = string.join(_luaCodes, "")
        # FileReadWrite.writeFileWithStr(_luaPath, _luaCodeStr)
