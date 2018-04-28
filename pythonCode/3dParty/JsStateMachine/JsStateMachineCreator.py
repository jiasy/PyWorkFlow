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

# 通过Excel 配置 js-state-machine 状态机
# 拷贝到工程指定位置
# 调用dot命令生成状态流程图。
opsDict = {}
opsDict["stateExcelPath"] = '状态机的excel配置'
opsDict["jsCodeFolder"] = 'js工程代码目录'
opsDict["picFolder"] = '生成的流程图图片目录'


# 依次执行每一行命令
# ---------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    _ops = SysInfo.getOps(opsDict, OptionParser())
    _currentFolder = SysInfo.fixFolderPath(os.path.dirname(os.path.realpath(__file__)))