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
opsDict["sourceFolder"] = '源目录'
opsDict["targetFolder"] = '目标目录'
opsDict["filters"] = '后缀'
opsDict["withoutReg"] = '过滤用正则表达式'

# 满足后缀条件的文件，进行文件迁移，文件夹结构不变
# ------------------------------------测试用例---------------------------------------------------------------------------------------
if __name__ == '__main__':
    _ops = SysInfo.getOps(opsDict, OptionParser())
    _currentFolder = SysInfo.fixFolderPath(os.path.dirname(os.path.realpath(__file__)))
    # 正则过滤列表
    _withOutRegs = _ops.withoutReg.split(",")
    _filters = _ops.filters
    # 文件列表
    _fileList = []
    FileReadWrite.gci(_ops.sourceFolder, _filters, _fileList)
    for _i in range(len(_fileList)):
        _filePath = _fileList[_i]
        # print "_filePath = " + str(_filePath)
        # 有过滤的正则
        if len(_withOutRegs) > 0:
            # 遍历正则
            _needCopyBoo = True
            for _idx in range(len(_withOutRegs)):
                _filterReg = _withOutRegs[_idx]
                if re.search(_filterReg, _filePath):
                    _needCopyBoo = False
                    break
            if _needCopyBoo:
                # 不在过滤的正则匹配中，就拷贝
                FileCopy.fileTransformWithFolderStructure(_filePath, _ops.sourceFolder, _ops.targetFolder)
                # print "true"
        else:
            # 没有正则列表，直接拷贝。
            FileCopy.fileTransformWithFolderStructure(_filePath, _ops.sourceFolder, _ops.targetFolder)
            # print "true"

