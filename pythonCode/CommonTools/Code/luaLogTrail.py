#!/usr/bin/python
# -*- coding: UTF-8 -*-
# from __future__ import print_function
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
opsDict["logToolPath"] = 'lua工具的路径'
opsDict["logImportCode"] = 'lua工具的引用的代码'


def getLogOut(path_, funcName_, comment_, pass_, par_):
    _passStr = "true"
    if pass_ == False:
        _passStr = "false"
    return '    LogUtil:getInstance():fo("' + path_ + '","' + funcName_ + '","' + comment_ + '",' + _passStr + ',' + par_ + ')'


def getLogIn(path_, funcName_, comment_, pass_, par_):
    _passStr = "true"
    if pass_ == False:
        _passStr = "false"
    return '    LogUtil:getInstance():fi("' + path_ + '","' + funcName_ + '","' + comment_ + '",' + _passStr + ',' + par_ + ')'


def getParameterPrint(parStr_):
    return


def check_filterPrints(filePath_, filterPrints_):
    return (filePath_ in filterPrints_)


def getCodeBlockInfo(regBegin_, regEndInCurrentLine_, line_):
    _funcReg = re.search(regBegin_, line_)
    if _funcReg:
        _funcReg_end = re.search(regEndInCurrentLine_, line_)
        if _funcReg_end:  # 当前行开始当前行结束
            return _funcReg, True
        else:
            return _funcReg, False
    else:
        return None, False


# 在py代码的每一个方法中，进入
# ------------------------------------测试用例---------------------------------------------------------------------------------------
if __name__ == '__main__':
    _ops = SysInfo.getOps(opsDict, OptionParser())
    _currentFolder = SysInfo.fixFolderPath(os.path.dirname(os.path.realpath(__file__)))

    # 获取 工具类 位置
    _luaUtilPath = _ops.logToolPath
    _requireStr = _ops.logImportCode


    _regFilters = _ops.regFilters.split(",")

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
        _shortPath = SysInfo.getRelativePath(_ops.targetFolderPath, _luaPath)
        print(_shortPath + "----------------------------------------------------------------------------------------------------------------")
        if _shortPath in _filterFilesList:
            print(" 忽略")
            continue
        # 去掉utf-8 的头
        FileReadWrite.removeBom(_luaPath)
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
        _funcStack = []
        _currentFuncDict = None

        # 每一行
        for _j in range(len(_luaCodes)):
            _line = _luaCodes[_j]
            _orginalLine = _line

            while _line.find("---") >= 0:
                _line = _line.replace("---", "--")
            # print "_line = " + str(_line)

            # # Debug 到达这一行就断点 ---------------------------------------------------------------------------------
            # if (_j + 1) < len(_luaCodes) and _luaCodes[_j + 1].find('取消链接计时器') >= 0:
            #     pass
            # if _j == 106:
            #     pass

            # 是否进行过修改
            _changeBoo = False
            _commenReg = re.search(r'^(.*)\-\-(.*)', _line)
            _commenInQuoationReq = re.search(r'^(.*)[\"\'](.*)\-\-(.*)[\"\'](.*)', _line)
            _commenMultipleBeginReg = re.search(r'^(.*)\-\-\[\[(.*)', _line)
            _commenMultipleEndReg = re.search(r'^(.*)\]\](.*)', _line)
            _commenMultipleInOneLineReg = re.search(r'(.*)(\-\-\[\[.*\]\])(.*)', _line)
            if _isMultipleCommon == False:
                # 是注释
                if _commenReg and not _commenInQuoationReq:
                    # 是不是多行注释起始
                    if _commenMultipleBeginReg:
                        # 是不是当前行就结束
                        if _commenMultipleInOneLineReg:
                            _line = _commenMultipleInOneLineReg.group(1) + _commenMultipleInOneLineReg.group(3)
                            _luaCodes[_j] = _line + '\r\n'
                            _changeBoo = True
                        else:
                            _isMultipleCommon = True
                            _line = ""
                            _luaCodes[_j] = _line + '\r\n'
                            _changeBoo = True
                    else:
                        # 不是多行注释的起始，清除注释部分
                        _line = _commenReg.group(1)
                        _luaCodes[_j] = _line + '\r\n'
                        _changeBoo = True
            else:
                # 多行注释结束
                if _commenMultipleEndReg:
                    _line = _commenMultipleEndReg.group(2)
                    _isMultipleCommon = False
                else:
                    _line = ""
                _luaCodes[_j] = _line + '\r\n'
                _changeBoo = True

            # 把print注释掉     ------------------------------------------------------------------------------------
            _printReg = re.search(r'^(\s+)print\((.*)', _line)
            if _printReg:
                _line = _printReg.group(1) + "--print(" + _printReg.group(2) + "\n"
                _changeBoo = True

            # 判断是不是要过滤的     ---------------------------------------------------------------------------------
            for _k in range(len(_regFilters)):
                # 满足条件当前行，过滤掉
                regFilterReg = re.search(_regFilters[_k], _line)
                if regFilterReg:
                    _regStr = regFilterReg.group(1)
                    if _regStr:
                        _line = _line.replace(_regStr, "--" + _regStr)
                        _luaCodes[_j] = _line + '\r\n'
                    else:
                        print("ERROR 过滤的正则表达式，需要把要注释的那段文字，括号匹配出来")
                        sys.exit(1)
                    _changeBoo = True
                    break

            if _changeBoo:
                # print "Begin : "+_orginalLine.split("\n")[0]
                # print "End   : "+_line
                pass

            # 空白行跳过     ----------------------------------------------------------------------------------------
            if _line.strip() == "":
                continue

            # 一行内有两个function。。。
            _twoFunRegInLine = re.search(r'^.*function\s*.*\s*\(.*\)\s*.*\s+function', _line)
            if _twoFunRegInLine:
                print("ERROR 一行 两个function")
                sys.exit(1)

            # 一行内是否有两个end
            _twoEndRegInLine = re.search(r'^.*\s*(\)?)\s*end\s*.*\s+(\)?)\s*end', _line)
            if _twoFunRegInLine:
                print("ERROR 一行 两个end")
                sys.exit(1)

            # 当前行可能是一个function -------------------------------------------------------------------
            _funcReg = re.search(r'^.*function\s*.*\s*\(.*', _line)
            # 简单过滤掉两边有 冒号的。不包括 "x" function "x" 这样的，有这样的就改一改吧。。。
            _commentFuncReg1 = re.search(r'^.*\".*function\s+.*\".*', _line)
            _commentFuncReg2 = re.search(r'^.*\'.*function\s+.*\'.*', _line)
            if _commentFuncReg1 or _commentFuncReg2:
                # print "function 在引号中的 : " + _line
                pass

            _isFunction = True
            if _funcReg and (not _commentFuncReg1) and (not _commentFuncReg2):
                # 满足正则之后，判断这个方法是不是在当前行就结束
                _funcRegStrToEnd = r'(.*)\s+end\s*'
                # 当前行 满足一个方法的正则，这里是有方法名的方法，匿名函数在后面
                _regList = [
                    # a.b = function(c)
                    r'^\s*([A-Za-z0-9_\.]+)\s*=\s*function\s*\((.*)\)\s*',
                    # function a:b(c) / function a.b(c) / function a(c)
                    r'^\s*function\s+([A-Za-z0-9_\:\.]+)\s*\((.*)\)\s*',
                    # local a function(c)
                    r'^\s*local\s+([0-9a-zA-Z_]+)\s+function\s*\((.*)\)\s*',
                    # local a = function(c)
                    r'^\s*local\s+([A-Za-z0-9_]+)\s*=\s*function\s*\((.*)\)\s*',
                    # local function a(c)
                    r'^\s*local\s+function\s+([0-9a-zA-Z_]+)\s*\((.*)\)\s*',
                    # # 可能是闭包
                    # r'^.*return\s+function\s*(.*)\s*\((.*)\)\s*'
                    # 匿名 方法
                    r'^.*()function\s*()\s*\((.*)\)\s*'
                ]

                # 退出当前行判断的标示
                _endCurrentLineCheck = False
                for _idx in range(len(_regList)):
                    _regItem = _regList[_idx]
                    # 判断满不满足，是不是满足了且当前行就结束了
                    _isCodeBlockInfo, _endInOneLine = getCodeBlockInfo(_regItem, _regItem + _funcRegStrToEnd, _line)
                    # 当前行自己结束
                    if _isCodeBlockInfo and _endInOneLine:
                        _endCurrentLineCheck = True
                    # 没结束，且没符合条件，才能再判断是否满足下一个
                    if not (not _endCurrentLineCheck and not _isCodeBlockInfo):
                        break

                # 当前行开始，当前行结束，不用再判断了
                if _endCurrentLineCheck:
                    continue

                # 闭包的话，return function(),需要结束上一个Function.
                if re.search(r'^.*return\s+.*function\s*(.*)\s*\((.*)\)\s*', _line):
                    # 还没开始记录当前的闭包方法，所以，当前的 _currentFuncDict 还是上一个的。
                    _line = getLogOut(_shortPath, _currentFuncDict["name"], " V ", _currentFuncDict["fiterPrintBoo"], '""') + '\n' + _line
                    _luaCodes[_j] = _line
                    _currentBlockDict = _codeBlockStack[-1]
                    # 所在的代码块是一个方法的话，那么，当前方法结束，return之后的end，是不需要输出log的。
                    if _currentBlockDict["type"] == "func":
                        # print "函数 return : "+_line
                        _currentFuncDict["isReturnBoo"] = True

                # 是一个函数代码块，且没在本行结束，压栈
                if _isCodeBlockInfo and not _endInOneLine:
                    _tempFuncDict = {}
                    _tempFuncDict["name"] = _isCodeBlockInfo.group(1).replace(' ', '')
                    _tempFuncDict["parameters"] = _isCodeBlockInfo.group(2).replace(' ', '')

                    # 参数解析
                    _parStrList = _tempFuncDict["parameters"].split(",")
                    _parList = []
                    for _k in range(len(_parStrList)):
                        _par = str(_parStrList[_k]).replace(" ", "")
                        if _par:
                            # 是多参数的，直接略过
                            if _par == "...":
                                break
                            else:
                                _parList.append(_par)
                    _parStr = ""
                    if str(_tempFuncDict["name"]).strip() != "" and len(_parList) > 0:
                        # print "_tempFuncDict[\"name\"] = " + str(_tempFuncDict["name"])
                        # print "_tempFuncDict[\"parameters\"] = " + str(_parList)
                        for _k in range(len(_parList)):
                            _parStr = _parStr + '"' + _parList[_k] + '="..LogUtil:getInstance():parCut(' + _parList[_k] + ')'
                            if not (_k == (len(_parList) - 1)):
                                _parStr = _parStr + '.." ,"..'
                        # print _parStr
                    else:
                        _parStr = '""'

                    _currentFuncDict = _tempFuncDict
                    _allPath = (_shortPath + _filterClassFuncJoin + _currentFuncDict["name"])
                    _currentFuncDict["allPath"] = _allPath
                    _currentFuncDict["fiterPrintBoo"] = (_allPath in _filterPrints)
                    if _currentFuncDict["name"] == "":  # 匿名函数直接过滤
                        _currentFuncDict["fiterPrintBoo"] = True
                    # 当前的方法还没有return过
                    _currentFuncDict["isReturnBoo"] = False
                    # print "_tempFuncDict[\"fiterPrintBoo\"] = " + str(_tempFuncDict["fiterPrintBoo"])
                    #   lineNum:行数,
                    #   funcDict:自己所属的函数的信息。自己是函数块
                    #   type:类型,if/repeat/while/for/func/anonymousFunc 中的一种
                    _blockDict = {}
                    _blockDict["lineNum"] = _j
                    _blockDict["type"] = "func"
                    _codeBlockStack.append(_blockDict)
                    _funcStack.append(_currentFuncDict)
                    _line = _line + "-- --> " + str(_currentFuncDict["name"]) + '\n' + getLogIn(_shortPath, _currentFuncDict["name"], " Λ ", _currentFuncDict["fiterPrintBoo"], _parStr) + '\n'
                    _luaCodes[_j] = _line
                else:
                    # 走到这里可能就是一个 匿名方法 anonymousFunc
                    _betweenFuncReg = re.search(r'^.*function\s*(.*?)\s*\(.*', _line)
                    if _betweenFuncReg:
                        # function 和 （ 中间夹的部分有以下字符，那么这个就不是个方法了
                        if re.search(r'^[A-Za-z0-9_]*$', _betweenFuncReg.group(1)):
                            print("意料之外，改写法吧，要不就改这个py脚本 : " + _line)
                        else:
                            # 当前行的function后面的参数是分多行写的
                            _funcReg = re.search(r'^.*function\s*[A-Za-z0-9\._\:]*\s*\(.*(?!\))', _line)
                            if _funcReg:
                                _tempJ = _j + 1  # 下一行，当前行清空，将自己合并到下一行
                                if _tempJ <= len(_luaCodes):
                                    _luaCodes[_j] = ""
                                    _luaCodes[_tempJ] = _line.replace('\n', '').replace('\t', '').replace('\r', '').strip() + _luaCodes[_tempJ]
                                    # print "合并到下一行 : " + _luaCodes[_tempJ]
                                else:
                                    print("ERROR 当前方法参数没有括号收尾，代码已经结束了")
                                    sys.exit(1)
                            else:
                                # print "不是方法 : " + _line
                                _isFunction = False
            else:
                _isFunction = False

            # 不是方法的话，进行下面的判断
            if not _isFunction:
                # 当前行可能是一个 逻辑/流程 控制 -------------------------------------------------------------------
                # 可以忽略 repeat until 因为它跟 end 不冲突
                # if end
                # while end
                # for end
                _haveControlBoo = False

                _controlKeyWordInfo = [['if', "(\s+)"], ["while", "(\s+)"], ["for", "(\s+)"], ['if\(', "(.*)"], ['while\(', "(.*)"], ['for\(', "(.*)"]]
                for _k in range(len(_controlKeyWordInfo)):
                    _keyWord = re.search("^(\s*)" + _controlKeyWordInfo[_k][0] + _controlKeyWordInfo[_k][1], _line)
                    _keyWordEnd1 = re.search("^(\s*)" + _controlKeyWordInfo[_k][0] + "(.*)\s+end\s*$", _line)
                    _keyWordEnd2 = re.search("^(\s*)" + _controlKeyWordInfo[_k][0] + "(.*)\s+end\s*\)\s*", _line)
                    _keyWordEnd3 = re.search("^(\s*)" + _controlKeyWordInfo[_k][0] + "(.*)\s+end\s*\,.*\)\s*", _line)
                    _keyWordEnd4 = re.search("^(\s*)" + _controlKeyWordInfo[_k][0] + "(.*)\s+end\s*\,\s*", _line)
                    if _keyWord and (not _keyWordEnd1) and (not _keyWordEnd2) and (not _keyWordEnd3) and (not _keyWordEnd4):
                        if _haveControlBoo:
                            print("ERROR 同一行 有两个 流程控制 关键字，请修改代码。不符合规范")
                            sys.exit(1)
                        _blockDict = {}
                        _blockDict["lineNum"] = _j
                        _blockDict["type"] = _controlKeyWordInfo[_k][0]
                        _codeBlockStack.append(_blockDict)
                        _haveControlBoo = True
                        # print " --> " + str(_blockDict["type"])
                        _luaCodes[_j] = _line + "-- --> " + str(_blockDict["type"]) + '\n'

                    if _keyWordEnd1 or _keyWordEnd2 or _keyWordEnd3 or _keyWordEnd4:
                        _replaceList = [
                            r'(.*)(if[ ]+.*[ ]+then)[ ]+(.*)[ ]*(end)',
                            r'(.*)(for[ ]+.*[ ]+do)[ ]+(.*)[ ]*(end)',
                            r'(.*)(while[ ]+.*[ ]+do)[ ]+(.*)[ ]*(end)'
                        ]
                        for _l in range(len(_replaceList)):
                            _controlOneLineReplaceReg = re.search(_replaceList[_l], _line)
                            if _controlOneLineReplaceReg:
                                _g1 = _controlOneLineReplaceReg.group(1)
                                _g2 = _controlOneLineReplaceReg.group(2)
                                _g3 = _controlOneLineReplaceReg.group(3)
                                _g4 = _controlOneLineReplaceReg.group(4)
                                _g5 = "".ljust(len(_g1))
                                _line = _g1 + _g2 + '\n' + _g5 + '    ' + _g3 + '\n' + _g5 + _g4
                                # print _orginalLine
                                # print _line

                if not _haveControlBoo:
                    _endReg = re.search("^\s*end\s*$", _line)
                    _endReg1 = re.search("^\s*end\s*\)\s*", _line)
                    _endReg2 = re.search("^\s*end\s*\,.*\)\s*", _line)
                    _endReg3 = re.search("^\s*end\s*\,\s*", _line)
                    _endReg4 = re.search("^\s*end\s*;", _line)
                    if _endReg or _endReg1 or _endReg2 or _endReg3 or _endReg4:
                        _currentBlockDict = _codeBlockStack.pop(-1)
                        # 方法的end
                        if _currentBlockDict["type"] == "func":
                            # 没有return过的方法，才能在end前面加函数退出的log
                            if _currentFuncDict["isReturnBoo"] == False:
                                # 退出LOG生成
                                _allPath = (_shortPath + _filterClassFuncJoin + _currentFuncDict["name"])
                                _line = getLogOut(_shortPath, _currentFuncDict["name"], " V ", _currentFuncDict["fiterPrintBoo"], '""') + '\n' + _line
                                _luaCodes[_j] = _line
                            # funcStack中推出
                            if len(_funcStack) > 0:
                                _funcStack.pop(-1)
                            # print " <-- " + str(_currentFuncDict["name"])
                            if _currentFuncDict:
                                _luaCodes[_j] = _line + "-- <-- " + str(_currentFuncDict["name"]) + '\n'
                            # _curr entFuncDict 变成funcStack中最后一个，如果长度为零，那么_currentFuncDict为None
                            if len(_funcStack) > 0:
                                _currentFuncDict = _funcStack[-1]
                            else:
                                _currentFuncDict = None
                        else:
                            # print " <-- " + str(_currentBlockDict["type"])
                            _luaCodes[_j] = _line + "-- <-- " + str(_currentBlockDict["type"]) + '\n'
                            pass
                    else:
                        _returnReg = re.search("\s*return(\s*)(.*)", _line)
                        _returnInCommonReg = re.search(".*\".*\s+return\s+.*\".*", _line)

                        # '    local returnOptions = {}'
                        if _returnReg and _returnReg.group(1) == "" and re.search(r'[a-zA-Z0-9_]', _returnReg.group(2)):
                            _returnReg = None

                        # 是返回，且当前还在一个函数中，且当前行不是一个流程控制语句
                        if _returnReg and _currentFuncDict and (not _haveControlBoo) and (not _returnInCommonReg):
                            _allPath = (_shortPath + _filterClassFuncJoin + _currentFuncDict["name"])
                            _backStr = _returnReg.group(2)
                            if _backStr:
                                # print "_backStr = " + str(_backStr)
                                # 返回，可能是执行方法的结果，可能是执行方法的话，变成字符串，免得二次执行生成多余的LOG
                                _maybeFuncReg = re.search("\(.*\)", _backStr)
                                if _maybeFuncReg:
                                    _backStr = '"maybeExecFunc"'
                                _maybeObject = re.search("{.*", _backStr)
                                if _maybeObject:
                                    _backStr = '"maybeOject"'
                                # 参数解析
                                _parStrList = _backStr.split(",")
                                # 如果返回两个或者两个以上,一个也输出，免得{a,b}这样的返回值出问题
                                if len(_parStrList) > 1:
                                    _parStrList = []
                                _parList = []
                                for _k in range(len(_parStrList)):
                                    _par = str(_parStrList[_k])
                                    _par = _par.strip()
                                    _par = _par.replace('\r', "")
                                    _par = _par.replace(';', "")
                                    if _par:
                                        _parList.append(_par)

                                _parStr = ""
                                if str(_tempFuncDict["name"]).strip() != "" and len(_parList) > 0:
                                    # print ("_tempFuncDict[\"name\"] = " + str(_tempFuncDict["name"]))
                                    # print ("_tempFuncDict[\"parameters\"] = " + str(_parList))
                                    for _k in range(len(_parList)):
                                        _parStr = _parStr + 'LogUtil:getInstance():parCut(' + _parList[_k] + ')'
                                        if not (_k == (len(_parList) - 1)):
                                            _parStr = _parStr + '.." ,"..'
                                    # print "_parStr : " + _parStr
                                else:
                                    _parStr = '""'

                            _line = getLogOut(_shortPath, _currentFuncDict["name"], " V ", _currentFuncDict["fiterPrintBoo"], _parStr) + '\n' + _line
                            _luaCodes[_j] = _line
                            _currentBlockDict = _codeBlockStack[-1]
                            # 所在的代码块是一个方法的话，那么，当前方法结束，return之后的end，是不需要输出log的。
                            if _currentBlockDict["type"] == "func":
                                # print "函数 return : "+_line
                                _currentFuncDict["isReturnBoo"] = True

        _luaCodes.insert(0, _requireStr + "\r\n")
        _luaCodeStr = string.join(_luaCodes, "")
        _luaCodeStr = CommonUtils.removeAnnoyingChars(_luaCodeStr)
        FileReadWrite.writeFileWithStr(_luaPath, _luaCodeStr)
