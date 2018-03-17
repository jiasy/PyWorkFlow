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
opsDict["codeType"] = '代码类型'
opsDict["jsonPath"] = 'json文件路径'
opsDict["outputFolderPath"] = '生成代码放置的路径'

# 解析 Excel 文件，生成 json 文件。
# ------------------------------------测试用例---------------------------------------------------------------------------------------
if __name__ == '__main__':
	_ops = SysInfo.getOps(opsDict,OptionParser())
	_currentFolder = SysInfo.fixFolderPath(os.path.dirname(os.path.realpath(__file__)))
	_keyValueDict = FileReadWrite.dictFromJsonFile(_ops.jsonPath)
	_templetFolder = os.path.join(_currentFolder,"KeyValueToCodeTemplet")
	_oc_h_templet_path = os.path.join(_templetFolder,"KeyValueFromJson.h")
	_oc_mm_templet_path = os.path.join(_templetFolder,"KeyValueFromJson.mm")
	_java_templet_path = os.path.join(_templetFolder,"KeyValueFromJson.java")
	_splitStr = "//KeyValue==============================================="
	# 重新创建输出文件夹
	FileReadWrite.reCreateFolder(_ops.outputFolderPath)
	
	if _ops.codeType == "java":
		_classArr = FileReadWrite.contentFromFile(_java_templet_path).split(_splitStr)
		_codeTemp = ""
		for _key in _keyValueDict:
			_codeTemp = _codeTemp + 'public static final String ' + _key + ' = "' + _keyValueDict[_key] + '";' + "\n"
		FileReadWrite.writeFileWithStr(os.path.join(_ops.outputFolderPath,"KeyValueFromJson.java"), "".join([_classArr[0], _splitStr+"\n", _codeTemp, _splitStr, _classArr[2]]))
	elif _ops.codeType == "oc":
		_classArr = FileReadWrite.contentFromFile(_oc_h_templet_path).split(_splitStr)
		_codeTemp = ""
		for _key in _keyValueDict:
			_codeTemp = _codeTemp + '+(NSString*) ' + _key + ';' + "\n"
		FileReadWrite.writeFileWithStr(os.path.join(_ops.outputFolderPath,"KeyValueFromJson.h"), "".join([_classArr[0], _splitStr+"\n", _codeTemp, _splitStr, _classArr[2]]))
		_classArr = FileReadWrite.contentFromFile(_oc_mm_templet_path).split(_splitStr)
		_codeTemp = ""
		for _key in _keyValueDict:
			_codeTemp = _codeTemp + '+(NSString*)' + _key + '{ return @"' + _keyValueDict[_key] + '"; }' + "\n"
		FileReadWrite.writeFileWithStr(os.path.join(_ops.outputFolderPath,"KeyValueFromJson.mm"), "".join([_classArr[0], _splitStr+"\n", _codeTemp, _splitStr, _classArr[2]]))
	else:
		print "ERROR 不支持当前的代码类型"+_ops.codeType+"，请自行完善"
		sys.exit(1)
