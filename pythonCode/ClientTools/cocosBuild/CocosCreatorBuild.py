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
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, os.pardir,"base")))
import FileCopy
import FileReadWrite
import SysInfo
import SysCmd

# 修改所需属性
opsDict = {}
opsDict["projectFolder"] = '工程文件夹'
opsDict["targetFolder"] = '导出目标文件夹'
opsDict["platform"] = '目标平台'
opsDict["debug"] = '是否是debug'
opsDict["title"] = '项目名称'
opsDict["webOrientation"] = 'WebMobile 平台下的旋转选项'

# 端口全部映射到主机，利用pm2进行性能监听
if __name__ == '__main__':
	_ops = SysInfo.getOps(opsDict,OptionParser())
	_currentFolder = SysInfo.fixFolderPath(os.path.dirname(os.path.realpath(__file__)))

	_cmd = '\
/Applications/CocosCreator.app/Contents/MacOS/CocosCreator \
--path '+_ops.projectFolder+'  \
--build "\
platform='+_ops.platform+';\
debug='+_ops.debug+';\
buildPath='+_ops.targetFolder+';\
title='+_ops.title+';\
webOrientation='+_ops.webOrientation+';\
"'

	print "执行构建命令 : " + str(_cmd)
	# SysCmd.doShellGetOutPut(_cmd)
	