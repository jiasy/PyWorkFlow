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
import ExcelUtils
import ExcelDataUtils
import CommonUtils
import Excel

# 通过Excel 配置 js-state-machine 状态机
# 拷贝到工程指定位置
# 调用dot命令生成状态流程图。
opsDict = {}
opsDict["stateExcelPath"] = '状态机的excel配置'
opsDict["jsonFolder"] = 'json描述文件的路径'
opsDict["picFolder"] = '生成的流程图图片目录'

# 依次执行每一行命令
# ---------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    _ops = SysInfo.getOps(opsDict, OptionParser())
    _currentFolder = SysInfo.fixFolderPath(os.path.dirname(os.path.realpath(__file__)))
    # State的配置
    _excelPath = _ops.stateExcelPath
    # js、pic 生成的路径，重新生成
    FileReadWrite.reCreateFolder(_ops.jsonFolder)
    FileReadWrite.reCreateFolder(_ops.picFolder)
    # Excel 解析
    _currentWorkBook = ExcelUtils.WorkBook()
    _currentWorkBook.initWithWorkBook(_excelPath)

    # 每一个状态解析，状态之间是相互关联的。APP 为最起始
    for _sheetName in _currentWorkBook.sheetDict:
        _sheet = _currentWorkBook.getSheetByName(_sheetName)
        _stateList = []
        _stateToDict = {}
        # 左上角第一个格子忽略
        for _col in range(_sheet.maxCol - 1):
            if not _sheet.cells[_col + 1][0].strValue == _sheet.cells[0][1 + _col].strValue:
                print "ERROR " + _excelPath + " : " + _sheetName + " : 行列对应值应当相同 "
                sys.exit(1)
            else:
                _currentStateName = _sheet.cells[_col + 1][0].strValue
                _stateList.append(_currentStateName)
        # # 默认第一个必须是start
        # if _stateList[0] != "start":
        #     print "ERROR " + _excelPath + " : " + _sheetName + " : 第一个状态必须是 start"
        #
        _stateToDict["init"] = _stateList[0]
        _transitionsList = []
        _stateToDict["transitions"] = _transitionsList

        for _col in range(1, _sheet.maxCol):
            _currentStateName = _sheet.cells[_col][0].strValue
            for _row in range(1, _sheet.maxRow):
                _targetStateName = _sheet.cells[0][_row].strValue
                _transName = _sheet.cells[_col][_row].strValue
                # 转换名称 不是空，去往一个状态
                if _transName != "" and _currentStateName != _targetStateName:
                    _stateTransDict = {}
                    _stateTransDict["name"] = _transName
                    _stateTransDict["to"] = _currentStateName
                    _stateTransDict["from"] = _targetStateName
                    _transitionsList.append(_stateTransDict)
        # 生成 js 给 代码用。
        _targetJsonPath = os.path.join(_ops.jsonFolder, _sheetName + ".json")
        FileReadWrite.writeFileWithStr(_targetJsonPath, str(json.dumps(_stateToDict, indent=4, sort_keys=False)))

        # 构成 dot 文件
        _dot_state_str = "digraph " + _sheetName + " { "+_stateList[0]+" [shape = Msquare]\n"
        for _i in range(len(_stateList)):
            _dot_state_str = _dot_state_str + _stateList[_i] + " \n"
        for _i in range(len(_transitionsList)):
            _dot_trans_dict = _transitionsList[_i]
            _dot_state_str = _dot_state_str + _dot_trans_dict["from"] + " -> " + _dot_trans_dict["to"] + " [ label= " + _dot_trans_dict["name"] + " ]" + " \n"
        _dot_state_str = _dot_state_str + "}"
        # 生成dot 给 可视化 用
        _targetDotPath = os.path.join(_ops.picFolder, _sheetName + ".dot")
        _targetPngPath = os.path.join(_ops.picFolder, _sheetName + ".png")
        FileReadWrite.writeFileWithStr(_targetDotPath, _dot_state_str)
        _graphCmd = "dot " + _targetDotPath + " -T png -o " + _targetPngPath

        print "_graphCmd = " + str(_graphCmd)
        SysCmd.doShellGetOutPut(_graphCmd)
