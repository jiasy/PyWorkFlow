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
opsDict["targetFolderPath"] = 'py所在的文件夹'
# 过滤 log 可以先跑程序，然后那个输出比较多，比如计时器，循环之类的。
# 按照相对路径带后缀名的一行，知道下一个带后缀名的一行之间，都是这个文件中要忽略的输出。
opsDict["filterLogs"] = '需要过滤掉的Log'


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
    _pyUtilPath = os.path.join(_currentFolder, "pyLogTrailTemplet/log_util.py")

    # 后缀
    _codeSuffix = ".py"
    # 过滤用的字符串链接，类 -> 方法
    _filterClassFuncJoin = " -> "
    # 是否需要参数输出
    _needParStr = True
    # 是否哦屏蔽原有输出
    _blockPrint = True
    # 是否不进行log添加
    _addLog = True

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
    shutil.copy(_pyUtilPath, _ops.targetFolderPath)
    # 每一个类需要引用logUtil，然后进行调用
    _importLogStr = "from log_util import LogUtil"

    for _i in range(len(_fileList)):
        _pyPath = _fileList[_i]
        _shortPath = SysInfo.getRelativePathWithOutSuffix(_ops.targetFolderPath, _pyPath, _codeSuffix)
        print _shortPath
        _pyCodes = FileReadWrite.linesFromFile(_pyPath)

        # 每一个文件初始的时候，import都是重置的
        _importAdded = False

        # 方法的信息，自己的缩进，自己的名称
        _funcDict = {}
        # 方法名
        _funcDict["name"] = ""
        # 代码缩进相关
        _funcDict["spaceStr"] = None
        # 每一行
        for _j in range(len(_pyCodes)):
            _line = _pyCodes[_j]
            # 去除代码内的 ";"
            _line = _line.replace(";", "")

            # 注释的话直接跳过     -------------------------------------------------------------------------------------
            _commenReg = re.search(r'^(\s+)#(.*)', _line)
            if _commenReg:
                continue
            else:
                _commenInLineReg = re.search(r'(.*)#(.*)', _line)
                if _commenInLineReg:
                    # '#'作为一个字符串在代码中,这个就比较麻烦了...
                    if _line.find("\'#\'") < 0:
                        _line = _commenInLineReg.group(1)
                        _pyCodes[_j] = _line + '\r\n'
                    else:
                        print _line

            # 匹配第一个import,将自己的import加入     ------------------------------------------------------------------
            if _importAdded == False:
                # 匹配第一个import
                _reg = re.search(r'(.*)import\s*(.*)', _line)
                if _reg:
                    _pyCodes[_j] = _line + _importLogStr + "\n"
                    _importAdded = True
                else:
                    _classReg = re.search(r'^class\s+.*\s*\(.*\)\s*:', _line)
                    # 到了class声明还没有import的话，就引用吧
                    if _classReg:
                        _pyCodes[_j] = _importLogStr + "\n" + _pyCodes[_j]
                        _importAdded = True

            # 把print注释掉     -------------------------------------------------------------------------------------
            if _blockPrint:
                _printReg = re.search(r'^(\s+)print\s+(.*)', _line)
                if _printReg:
                    _line = _printReg.group(1) + "pass" + "\n"
                    _pyCodes[_j] = _line

            # 空白行跳过     ----------------------------------------------------------------------------------------
            if _line.strip() == "":
                continue

            # 不进行log添加的话,直接进行下一行
            if _addLog == False:
                continue
            # def func(xx):
            _reg = re.search(r'^(\s+)def\s*(.*)\s*\((.*)\)\s*:', _line)
            if _reg:
                # 这个方法开始了上个方法就结束吧
                if _funcDict["spaceStr"] != None:
                    # 在上一行的最后添加输出字符串
                    _pyCodes[_j - 1] += _funcDict["spaceStr"] + _spaceAdd + getLogOut(_shortPath, _funcDict["name"], " V", _funcDict["pass"], '""')
                    _funcDict["spaceStr"] = None

                # 是否不输出当前LOG
                _funcDict["pass"] = False

                # 设定当前的函数
                _funcDict["spaceStr"] = _reg.group(1)
                _spaceAdd = "    "
                _funcDict["name"] = _reg.group(2)
                _parArr = _reg.group(3).split(",")

                for _classFunctionStr in _filterPrints:
                    # 如果是过滤项就直接过滤
                    _currentFunctionStr = _shortPath + " -> " + _funcDict["name"]
                    if _currentFunctionStr == _classFunctionStr:
                        # 直接越过配置的忽略项
                        _funcDict["pass"] = True

                # 是 静态方法 还是 实例方法
                _singleOrStatic = ""
                if _parArr[0] == "cls":
                    _singleOrStatic = "[ - ]"
                elif _parArr[0] == "self":
                    _singleOrStatic = "<>"

                # 参数的输出,默认的时候是空字符串
                _parStr = '""'
                if _needParStr:
                    # 遍历参数
                    for _k in range(1, len(_parArr)):
                        _parReg = re.search(r'(.*)=.*', _parArr[_k])
                        if _parReg:
                            _parArr[_k] = _parReg.group(1)
                        _addStr = "+ "
                        # 最后一个不能加 '+'
                        if _k == (len(_parArr) - 1):
                            _addStr = ""
                            # 有参数的时候，先把原来的空字符串删掉
                        if _k == 1:
                            _parStr = ''
                        # 没有参数的时候是 "" 这样的形式
                        # 有参数的话
                        # 		整理成 "(1)uid : "+str(uid)+ "(2)seatId : "+str(seatId） 这样的形式
                        _parStr += '"(' + str(_k) + ')' + _parArr[_k].strip() + ' : "+str(' + _parArr[_k].strip() + ') ' + _addStr

                        # 方法名的输出
                _funcStr = _funcDict["spaceStr"] + _spaceAdd + getLogIn(_shortPath, _funcDict["name"], " Λ " + _singleOrStatic, _funcDict["pass"], _parStr)
                _pyCodes[_j] += _funcStr + "\n"
            # 输出变更后的log输出。
            # print _pyCodes[_j]
            else:
                # 方法结束，一种是return
                #    这个结束，只是添加log，并不添加任何东西。
                # 一种是自然结束。
                #    自然，结束是方法结束标示改变的唯一位置。
                # 已经在一个方法里面了，没出来
                if _funcDict["spaceStr"] != None:
                    # 在一个方法内
                    _reg = re.search(r'^(\s+)(.*)', _line)
                    # 前面带空格的
                    if _reg:
                        # 取得前面的空格
                        _currentSpaceStr = _reg.group(1)
                        # 空格小于等于方法的缩进，就证明方法结束了
                        if len(_currentSpaceStr) <= len(_funcDict["spaceStr"]):
                            # 在当前行的前面加输出
                            _pyCodes[_j] = _funcDict["spaceStr"] + _spaceAdd + getLogOut(_shortPath, _funcDict["name"], " V", _funcDict["pass"], '""') + _pyCodes[_j]
                            _funcDict["spaceStr"] = None
                        else:
                            # return / pass 出现，那么结束的输出是按照这个缩进进行的
                            _tempSpaceStr = ""
                            _returnReg = re.search(r'^(\s+)return(\s+)(.*)', _line)
                            if _returnReg:
                                _tempSpaceStr = _returnReg.group(1)
                                _returnStr = _returnReg.group(3)
                                # 如果返回的是对象
                                # return {'result': True, 'command': command, 'length': length}
                                _returnObj = re.search(r'(.*){(.*)}(.*)', _returnStr)
                                if _returnObj:
                                    # 存在对象的就不输出参数了
                                    _returnStr = '""'
                                else:
                                    ''' 返回值 是代码拼接的多行的情况,不输出参数
                                        return self.a.getState() \
                                        + self.b.getState()
                                    '''
                                    if _returnStr.find("\\") != -1:
                                        _returnStr = '""'
                                    else:
                                        # 有方法存在的话,就直接输出字符串了,不要拆分了.免得方法执行两次
                                        # return func(...)
                                        if _returnStr.find("(") != -1 and _returnStr.find(")") != -1:
                                            _returnStrLastChar = _returnStr[len(_returnStr) - 1]
                                            if _returnStrLastChar == "\n" or _returnStrLastChar == "\r" or _returnStrLastChar == "\r\n":
                                                _returnStr = _returnStr[0:len(_returnStr) - 1]
                                            _returnStr = '"' + _returnStr + '"'
                                        else:
                                            _returnArr = _returnStr.split(",")
                                            _returnStr = '""'
                                            # 遍历参数
                                            for _k in range(0, len(_returnArr)):
                                                _addStr = "+ "
                                                # 最后一个不能加 '+'
                                                if _k == (len(_returnArr) - 1):
                                                    _addStr = ""
                                                    # 有参数的时候，先把原来的空字符串删掉
                                                if _k == 0:
                                                    _returnStr = ''
                                                # 没有参数的时候是 "" 这样的形式
                                                # 有参数的话
                                                # 		整理成 "(1)uid : "+str(uid)+ "(2)seatId : "+str(seatId） 这样的形式
                                                _currentReturnPar = _returnArr[_k].strip()
                                                # (1)self.__processors[seatId]['state'] -> (1)self.__processors[seatId][\'state\']
                                                _currentReturnParReplace = _currentReturnPar.replace("\'", "\\\'")
                                                if _currentReturnPar == "True" or _currentReturnPar == "False":
                                                    _returnStr += '\'(' + str(_k) + ')' + _currentReturnParReplace + '\'' + _addStr
                                                elif re.search(r'^\[(.*)\]$', _currentReturnPar):
                                                    _returnStr += '\'(' + str(_k) + ')' + _currentReturnParReplace + '\'' + _addStr
                                                else:
                                                    _returnStr += '\'(' + str(_k) + ')' + _currentReturnParReplace + ' : \'+str(' + _currentReturnPar + ') ' + _addStr

                                                    # _passReg=re.search(r'^(\s+)pass(.*)',_line)
                                                    # if _passReg:
                                                    # 	_tempSpaceStr=_passReg.group(1)
                                                    # 前面带空格的
                            if _tempSpaceStr != "":
                                # 在当前行的前面加输出
                                _pyCodes[_j] = _tempSpaceStr + getLogOut(_shortPath, _funcDict["name"], " V", _funcDict["pass"], _returnStr) + _pyCodes[_j]
                                # 这里不能结束方法，return可能在方法中出现很多个
                    else:
                        # 前面不带空格就是终结
                        _pyCodes[_j] = _funcDict["spaceStr"] + _spaceAdd + getLogOut(_shortPath, _funcDict["name"], " V", _funcDict["pass"], '""') + _pyCodes[_j]
                        _funcDict["spaceStr"] = None
        if _funcDict["spaceStr"] != None:
            # 如果到结束了,还没有停止当前方法,那么就在最后一行补一个结束
            _pyCodes.append("\n" + _funcDict["spaceStr"] + _spaceAdd + getLogOut(_shortPath, _funcDict["name"], " V", _funcDict["pass"], '""'))

        # 去除特殊字符...不知道如何产生的...其他机器,可能还需要去掉
        if len(_pyCodes) > 0:
            _firstLine = _pyCodes[0]
            _pyCodes[0] = _firstLine[3:]

        # 添加两行 必要 注释
        _pyCodes.insert(0, "# -*- coding: UTF-8 -*-\n")
        _pyCodes.insert(0, "#!/usr/bin/python\n")
        _pyCodeStr = string.join(_pyCodes, "")

        _pyCodeStr = CommonUtils.removeAnnoyingChars(_pyCodeStr)

        FileReadWrite.writeFileWithStr(_pyPath, _pyCodeStr)
