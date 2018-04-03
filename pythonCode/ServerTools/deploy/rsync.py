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
import CommonUtils

# 修改所需属性
opsDict = {}
opsDict["username"] = '远程服务器登陆账户'
opsDict["exclude"] = '排除设定'
opsDict["localFolderPath"] = '本地目录'
opsDict["hostList"] = '要推送的服务器地址列表'
opsDict["hostFolderPath"] = '服务器接收路径'

# 满足后缀条件的文件，进行文件迁移，文件夹结构不变
# ------------------------------------测试用例---------------------------------------------------------------------------------------
if __name__ == '__main__':
    _ops = SysInfo.getOps(opsDict, OptionParser())
    _currentFolder = SysInfo.fixFolderPath(os.path.dirname(os.path.realpath(__file__)))

    # 拼接排除
    _excludeListStr = CommonUtils.getParameterListStr("exclude", _ops.exclude, False)
    _hostList = _ops.hostList.split(",")

    for _i in range(len(_hostList)):
        _cmd = 'rsync -vrltczOu --chmod=a+rx,u+rwx,g+rx ' + _excludeListStr + ' ' + _ops.localFolderPath + ' ' + _ops.username + '@' + _hostList[_i] + ':' + _ops.hostFolderPath
        print str(_cmd)
        # SysCmd.doShellGetOutPut(_cmd)
