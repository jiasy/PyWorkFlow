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

# 列表结构的excel数据输出，json结构的数据输出
opsDict = {}
opsDict["commands"] = '要执行的命令序列'

# 依次执行每一行命令
# ---------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    _ops = SysInfo.getOps(opsDict, OptionParser())
    _currentFolder = SysInfo.fixFolderPath(os.path.dirname(os.path.realpath(__file__)))
    _commands = _ops.commands.split(",")
    for _i in range(len(_commands)):
        _command = _commands[_i]
        print "执行构建命令 : " + str(_command)
        # SysCmd.doShellGetOutPut(_command)
