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
from optparse import OptionParser

# 导入 ../../base/ 中的代码
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, os.pardir, "base")))
import FileCopy
import FileReadWrite
import SysInfo
import SysCmd
import RegExp

# 修改所需属性
opsDict = {}
opsDict["targetFolder"] = '目标目录'
opsDict["regular"] = '正则表达式，注意括号要加\\'

# /Users/jiasy/Desktop/testJs/pics/ 下，
# /Users/jiasy/Desktop/testJs/pics/PIC/ 内的图片 名称变更 x_n.png -> PIC_n.png

# ------------------------------------测试用例---------------------------------------------------------------------------------------
if __name__ == '__main__':
    _ops = SysInfo.getOps(opsDict, OptionParser())
    _currentFolder = SysInfo.fixFolderPath(os.path.dirname(os.path.realpath(__file__)))
    # 递归遍历文件夹 -------------------------------------------
    _filePathList = []
    FileReadWrite.getAllFilePath(_ops.targetFolder, _filePathList)
    # 获取所有的子文件路径
    for _i in range(len(_filePathList)):
        _filePath = _filePathList[_i]
        # 文件所在目录
        _folderPath = os.path.dirname(_filePath)
        # 文件夹名称
        _folderName = _folderPath.split("/").pop()
        # 原名称
        _fileName = os.path.basename(_filePath)
        # 新名称
        _replacedName = RegExp.replaceStrWithReg(_fileName, _ops.regular, _folderName, 100000000)
        # 重新命名文件
        SysInfo.renameFileInFolder(_folderPath, _fileName, _replacedName)
