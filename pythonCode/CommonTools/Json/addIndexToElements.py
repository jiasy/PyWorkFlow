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

sys.path.append('/Users/jiasy/Documents/sourceFrame/pythonToolBase/self/')

import FileCopy
import FileReadWrite
import SysInfo
import SysCmd
import RegExp


# ------------------------------------测试用例---------------------------------------------------------------------------------------
if __name__ == '__main__':
	parse = OptionParser()
	parse.add_option('-f','--filePath',dest='filePath',help='json地址')
	#(options,argvs) = parse.parse_args()
	options = parse.parse_args()[0]	#这里参数值对应的参数名存储在这个options字典里
	_filePath = options.filePath
	if not _filePath:
		print "ERROR : 必须有 filePath 指定目标文件夹 "
		sys.exit(1)

	_list = FileReadWrite.dictFromJsonFile(_filePath)
	_count = 0
	for _i in range(len(_list)):
		_item = _list[_i]
		_count = _count + 1
		_item["index"] = _count

	_listStr = str(json.dumps(_list, indent=4, sort_keys=False, ensure_ascii=False))
	FileReadWrite.writeFileWithStr(_filePath,_listStr.replace("\n", "").replace(' ', ''))

