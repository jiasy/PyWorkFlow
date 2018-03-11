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
import Excel

# 修改所需属性
opsDict = {}
opsDict["excelFolderPath"] = 'excel所在文件夹'
opsDict["excelName"] = 'excel名称'

# 通过Excel名，直接执行Excel中配置的WorkFlow，Excel的名字可以直接写成汉子[比如 : 打包.xlsx，热更.xlsx，服务端代码上传.xlsx]
# 	然后在Jenkins 下面 配置一个公共的 excelFolderPath 参数。
# 	再配置一个可选参数 对应执行的 Excel [比如 : 打包、热更、服务端代码上传]。
# 选择参数，构成以下格式，就可以了
# 	python ExcuteWorkFlowByExcel.py --excelFolderPath excel所在文件夹 --excelName 打包/热更/服务端代码上传
# 	python /Users/jiasy/Documents/sourceFrame/excelWorkFlow/pythonCode/CommonTools/Jenkins/ExcuteWorkFlowByExcel.py --excelFolderPath /Users/jiasy/Documents/sourceFrame/excelWorkFlow/excel/dockerContainer --excelName baseDockerContainer
# ------------------------------------测试用例---------------------------------------------------------------------------------------
if __name__ == '__main__':
	_ops = SysInfo.getOps(opsDict,OptionParser())
	_currentFolder = SysInfo.fixFolderPath(os.path.dirname(os.path.realpath(__file__)))
	_excelPath = os.path.join(_ops.excelFolderPath,_ops.excelName+".xlsx")
	_cmd = Excel.getExcuteCmd(_excelPath)
	print "        开始执行 " + str(_ops.excelName) + " 脚本工作流"
	SysCmd.doShellGetOutPut(_cmd)