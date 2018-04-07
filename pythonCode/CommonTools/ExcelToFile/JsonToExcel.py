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

# 多个json合并到一个Excel中
opsDict = {}
opsDict["inputJsonPath"] = '输入的json集合'
opsDict["outputExcelPath"] = '写入Excel的路径'

# ------------------------------------测试用例---------------------------------------------------------------------------------------
if __name__ == '__main__':
    _ops = SysInfo.getOps(opsDict, OptionParser())
    _currentFolder = SysInfo.fixFolderPath(os.path.dirname(os.path.realpath(__file__)))

    _ops.jsonPath
    _opes.excelPath
