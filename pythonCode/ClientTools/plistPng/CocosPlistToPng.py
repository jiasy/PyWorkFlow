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
opsDict["sourceFolder"] = '图片资源文件路径'
opsDict["putInToFolder"] = 'plist图片拷贝出来之后放置的路径'

# 拆分小图
#   sourceFolder 里找出 plist 的大图。
#   同路径结构 拷贝 到 putInToFolder 文件夹中。
#   putInToFolder 中 xx.plist 大图 拆分成 xx 这样的文件夹，将图片拆分到这个文件夹里。
# ------------------------------------测试用例---------------------------------------------------------------------------------------
if __name__ == '__main__':
    _ops = SysInfo.getOps(opsDict, OptionParser())
    _currentFolder = SysInfo.fixFolderPath(os.path.dirname(os.path.realpath(__file__)))
    # 切分脚本位置
    _slicePyFilePath = os.path.join(_currentFolder, "unpack/unpacker.py")
    # plist 路径集
    _plistPathList = FileReadWrite.getFilePathsByType(_ops.sourceFolder, "plist")
    for _i in range(len(_plistPathList)):
        _plistPath = _plistPathList[_i]
        # 有同名的文件就是大图用的plist
        _pngPath = SysInfo.getPathWithOutPostfix(_plistPath) + ".png"
        if os.path.exists(_pngPath):
            # 拷贝到新路径下
            SysInfo.filTransformWithFolderStructure(_plistPath, _ops.sourceFolder, _ops.putInToFolder)
            SysInfo.filTransformWithFolderStructure(_pngPath, _ops.sourceFolder, _ops.putInToFolder)
            # 执行脚本路径，大图所在的路径
            _cmdPath = os.path.dirname(_pngPath)
            _bigPicNameWithOutPostfix = SysInfo.justName(_pngPath)  # 纯名
            _cmd = "cd " + _cmdPath + ";" + "python " + _slicePyFilePath + " " + _bigPicNameWithOutPostfix
            print "_cmd = " + str(_cmd)
            SysCmd.doShell(_cmd)
    print "PngToPlst ---------- 拆分结束 ---------- "
