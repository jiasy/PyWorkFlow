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

# 列表结构的excel数据输出，json结构的数据输出
opsDict = {}
opsDict["enginePath"] = 'cocos2dx本地路径'
opsDict["directory"] = '创建工程的目标路径'
opsDict["language"] = '语言'
opsDict["package"] = '包名'
opsDict["portrait"] = '是否竖屏'
opsDict["projectName"] = '工程名'

# 依次执行每一行命令
# ---------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    _ops = SysInfo.getOps(opsDict, OptionParser())
    _currentFolder = SysInfo.fixFolderPath(os.path.dirname(os.path.realpath(__file__)))
    # 命令基础
    _cmd = SysInfo.fixFolderPath(_ops.enginePath) + "tools/cocos2d-console/bin/cocos new "
    # 参数变换
    _enginePath = CommonUtils.getParameterStr("engine-path", _ops.enginePath, False)
    _directory = CommonUtils.getParameterStr("directory", _ops.directory, False)
    _language = CommonUtils.getParameterStr("language", _ops.language, False)
    _package = CommonUtils.getParameterStr("package", _ops.package, False)
    # 拼接命令
    _cmd = _cmd + _enginePath
    _cmd = _cmd + _directory
    _cmd = _cmd + _language
    _cmd = _cmd + _package
    if _ops.portrait == "True":
        _cmd = _cmd + "--portrait"
    _cmd = _cmd + " " + _ops.projectName

    # 命令输出
    print "_cmd = " + str(_cmd)

    # 执行命令
    SysCmd.doShellGetOutPut(_cmd)

# /Users/jiasy/Documents/sourceFrame/cocos2d-x-3.16/tools/cocos2d-console/bin/cocos new
# --engine-path=/Users/jiasy/Documents/sourceFrame/cocos2d-x-3.16/
# --directory=/Users/jiasy/Documents/develop/selfDevelop/cocosLuaTest/LuaClient/
# --language=lua
# --package=com.jiasy.cocosLuaTest
