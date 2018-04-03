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

# 修改所需属性
opsDict = {}
opsDict["templetPath"] = '文件模板'
opsDict["jsonPath"] = 'Json文件路径'
opsDict["outputPath"] = '替换完之后放置的位置，包含文件名及后缀'

# json 是一个键值对对象[key:value]，然后模板中的 ${key}，替换成 value。
# 将替换完的文件，放置到 outputPath 路径下。
# ------------------------------------测试用例---------------------------------------------------------------------------------------
if __name__ == '__main__':
    _ops = SysInfo.getOps(opsDict, OptionParser())
    _currentFolder = SysInfo.fixFolderPath(os.path.dirname(os.path.realpath(__file__)))
    _templetContent = FileReadWrite.contentFromFile(_ops.templetPath)
    _keyValueDict = FileReadWrite.dictFromJsonFile(_ops.jsonPath)
    _outputFolder = os.path.dirname(_ops.outputPath)
    print "_outputFolder = " + str(_outputFolder)
    # 重新创建输出文件夹
    FileReadWrite.reCreateFolder(_outputFolder)

    for _key in _keyValueDict:
        _templetContent = _templetContent.replace("${" + _key + "}", _keyValueDict[_key])
    FileReadWrite.writeFileWithStr(_ops.outputPath, _templetContent)
