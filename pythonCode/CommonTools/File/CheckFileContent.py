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
import JsonMerge

# 修改所需属性
opsDict = {}
opsDict["checkFilePath"] = '要校验的文件路径'
opsDict["content"] = '校验的文件内容'

# json 合并
# 相同层级的同名字段会覆盖，如有覆盖情况，请注意先后顺序
# ------------------------------------测试用例---------------------------------------------------------------------------------------
if __name__ == '__main__':
    _ops = SysInfo.getOps(opsDict, OptionParser())
    _currentFolder = SysInfo.fixFolderPath(os.path.dirname(os.path.realpath(__file__)))
    # 校验文件内容，是否一致
    _content = FileReadWrite.contentFromFile(_ops.checkFilePath)
    if not _content == _ops.content:
        sys.exit(1)
