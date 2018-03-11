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
opsDict["excelPaths"] = 'Excel文件路径集合'
opsDict["outputJsonFolderPath"] = '文件路径，每一个Sheet一个文件夹，每数列生成一个Json文件'

# 解析 Excel 文件，生成 json 文件。键值对类型的Excel文件。
# Excel 解析后，将生成的文件都放置到 outputJsonFolderPath 中。
# 每一个Sheet对应一组键值对儿，每一个Sheet也会变成一个文件夹。
# 每一个数列value形成一个单一的文件，放置到 outputJsonFolderPath/[Sheet名称]/[数列名称].xlsx
# ------------------------------------测试用例---------------------------------------------------------------------------------------
if __name__ == '__main__':
	_ops = SysInfo.getOps(opsDict,OptionParser())
	_currentFolder = SysInfo.fixFolderPath(os.path.dirname(os.path.realpath(__file__)))
	# 重新创建输出文件夹
	if os.path.exists(_ops.outputJsonFolderPath):
		shutil.rmtree(_ops.outputJsonFolderPath)
	FileReadWrite.makeDirPlus(_ops.outputJsonFolderPath)
	# 解析每一个Excel文件
	_excelPaths = _ops.excelPaths.split(",")
	for _i in range(len(_excelPaths)):
		_excelName = SysInfo.justName(_excelPaths[_i])
		_excelFolderPath = os.path.join(_ops.outputJsonFolderPath,_excelName)
		FileReadWrite.makeDirPlus(_excelFolderPath)
		_excelDict = Excel.dictFromExcelFile(_excelPaths[_i])
		for _sheetName in _excelDict:
			# 创建每一个Sheet 的文件夹
			_sheetFolderPath = os.path.join(_excelFolderPath,_sheetName)
			FileReadWrite.makeDirPlus(_sheetFolderPath)
			_sheetDict = _excelDict[_sheetName]
			for _colName in _sheetDict:
				# 创建每一个数列的文件
				_colDict = _sheetDict[_colName]
				FileReadWrite.writeFileWithStr(os.path.join(_sheetFolderPath,_colName+".json") , str(json.dumps( _colDict, indent=4, sort_keys=False, ensure_ascii=False)))





