#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
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

import ExcelUtils
import SysCmd
import SysInfo
import types

'''
<^> -	 : 0-a		 ,1-b		 ,2-c		 ,3-d		 ,
row - 0   :		   ,		  ,		  ,		  ,
row - 1   : Stage1	,脚本描述   ,工程中过滤出图片文件,		  ,
row - 2   :		   ,脚本路径   ,toolPath  ,/Users/jiasy/Documents/sourceFrame/pythonToolBase/game_tools/file_transform/file_filter_to.py,
row - 3   :		   ,源文件夹   ,s		 ,/Users/jiasy/Documents/develop/doudoule/hall/taianClient/assets/resources/textures/,
row - 4   :		   ,目标文件夹 ,t		 ,/Users/jiasy/Desktop/test_project/plist_to_pngs,
row - 5   :		   ,过滤后缀   ,f		 ,plist,png,jpg,
'''


def getConfigFromSheet(targetSheet_):
	# 校验 sheet
	if targetSheet_.getStrByPos("j2") != "on" or targetSheet_.getStrByPos("j3") != "off":
		print "ERROR workSheet 中 J2,J3 必须是 on/off 用来提供选项"
		sys.exit(1)

	# 创建 WorkFlow 消息对象
	_workFlowInfo = {}
	_workFlowInfo["name"] = targetSheet_.sheetName
	_works = []
	_workFlowInfo["works"] = _works

	# 是否需要输出 子脚本log
	_workFlowInfo["subLogBool"] = targetSheet_.getStrByPos("c2")
	if _workFlowInfo["subLogBool"] != "on" and _workFlowInfo["subLogBool"] != "off":
		print "ERROR workSheet 中 C 2 必须是 on/off 中的一个"
		sys.exit(1)
	print "================脚本执行顺序如下=================="

	for _currentRow in range(targetSheet_.maxRow):
		_val = targetSheet_.getStrByCr(0, _currentRow)
		if _val.find("Stage") == 0:
			_workInfo = {}
			_workInfo["des"] = targetSheet_.getStrByCr(2, _currentRow)
			# work 的信息
			_workInfo["toolPath"] = targetSheet_.getStrByCr(2, _currentRow + 1)
			if not os.path.exists(_workInfo["toolPath"]):
				print "ERROR workSheet 中脚本路径 toolPath 找不到 : " + _workInfo["toolPath"]
				sys.exit(1)

			if _workInfo["toolPath"] == "":
				print "ERROR workSheet 中脚本路径 必须在 C 列，Stage 的下一行"
				sys.exit(1)
			# 是否开启
			_onOff = targetSheet_.getStrByCr(0, _currentRow + 1)
			if _onOff != "on" and _onOff != "off":
				print "ERROR workSheet 中 Stage 下必须是 on/off 标识当前 脚本是否执行。"
				sys.exit(1)

			if _onOff == "off":
				print "<>---------	 > off : " + _workInfo["des"]
			else:
				print "<>---------< on  : " + _workInfo["des"]
				# 获取参数
				_parameters = []
				_workInfo["pars"] = _parameters
				_currentLoopRow = _currentRow + 1
				while (True):
					_currentLoopRow = _currentLoopRow + 1
					# 超界限，或者没有值，就退出
					if _currentLoopRow >= targetSheet_.maxRow or \
							targetSheet_.getStrByCr(1, _currentLoopRow) == "" or \
							targetSheet_.getStrByCr(0, _currentLoopRow).find("Stage") == 0:
						break
					else:
						_parameterObject = {}
						# 当前行
						_currentRowKey = targetSheet_.getStrByCr(2, _currentLoopRow)
						_currentRowValue = targetSheet_.getStrByCr(3, _currentLoopRow)
						_parameterObject["key"] = _currentRowKey
						# 下一行
						_nextLoopRow = _currentLoopRow + 1
						if _nextLoopRow < targetSheet_.maxRow:
							_loopRowKey = targetSheet_.getStrByCr(2, _nextLoopRow)
							_loopRowValue = targetSheet_.getStrByCr(3, _nextLoopRow)
							# 下一行 键为空，值有值。那么就是一个数组
							if _loopRowKey == "" and _loopRowValue != "":
								# 是数组创建数组
								_parameterObject["val"] = [_currentRowValue]
								_parameterObject["val"].append(targetSheet_.getStrByCr(3, _nextLoopRow))
								while (True):
									_nextLoopRow = _nextLoopRow + 1
									if _nextLoopRow >= targetSheet_.maxRow:
										# 当前行，超界，当前循环行变到最后一个元素所在行
										_currentLoopRow = _nextLoopRow - 1
										break
									else:
										_loopRowKey = targetSheet_.getStrByCr(2, _nextLoopRow)
										_loopRowValue = targetSheet_.getStrByCr(3, _nextLoopRow)
										# 当前行，没有键，那么值就是数组的一个元素
										if _loopRowKey == "":
											if _loopRowValue != "":
												_parameterObject["val"].append(_loopRowValue)
											else:
												# 当前行，没有值，那么这个数组就结束，当前循环行变到最后一个元素所在行
												_currentLoopRow = _nextLoopRow - 1
												break
										else:
											# 当前行，有键，那么这个数组就结束，当前循环行变到最后一个元素所在行
											_currentLoopRow = _nextLoopRow - 1
											break
							else:
								# 下一行就超界，当前行肯定不是数组。不是数组的就进行记录
								_parameterObject["val"] = _currentRowValue
						else:
							# 不是数组的就进行记录
							_parameterObject["val"] = _currentRowValue
						# 录制当前键值
						_parameters.append(_parameterObject)
				# 录制当前工作节点
				_works.append(_workInfo)
	print "==================================================\n"
	# print "_workFlowInfo = " + str(json.dumps(_workFlowInfo, indent=4, sort_keys=False, ensure_ascii=False))
	return _workFlowInfo


def doWorkFlow(workFlowInfo_):
	_name = workFlowInfo_["name"]
	_subLogBool = workFlowInfo_["subLogBool"]
	print "WorkFlow " + _name + " start ----------------------------------------------------------"
	_works = workFlowInfo_["works"]
	for _i in range(len(_works)):
		_workInfo = _works[_i]
		doWork(_workInfo, _subLogBool)


def doWork(workInfo_, subLogBool_):
	_cmd = "python "
	_des = workInfo_["des"]
	_toolPath = workInfo_["toolPath"]
	_cmd += _toolPath + " "
	_pars = workInfo_["pars"]
	for _i in range(len(_pars)):
		_parInfo = _pars[_i]
		_key = _parInfo["key"]
		_val = _parInfo["val"]
		if type(_val) is types.ListType:
			_val = ",".join(_val)
		_val = SysInfo.setCmdStr(_val)
		# 区分简写的还是全称
		if len(_key) == 1:
			_cmd += "-" + _key + " " + _val + " "
		else:
			_cmd += "--" + _key + " " + _val + " "
	print "\n^----------" + _des + " start : " + _cmd
	if subLogBool_ == "on":
		SysCmd.doShellGetOutPut(_cmd);
	else:
		SysCmd.doShell(_cmd)
	print "V----------" + _des + " end\n"


# ------------------------------------测试用例---------------------------------------------------------------------------------------
if __name__ == '__main__':
	# e _excelFile
	opts, args = getopt.getopt(sys.argv[1:], "he:")
	_excelFile = None
	for _op, _value in opts:
		if _op == "-e":
			_excelFile = _value

	_excelWorkBook = ExcelUtils.WorkBook()
	_excelWorkBook.initWithWorkBook(_excelFile)
	for _key in _excelWorkBook.sheetDict:
		_currentSheet = _excelWorkBook.sheetDict[_key]
		_currentSheet.printSelf()
		_workFlowInfo = getConfigFromSheet(_currentSheet)
		doWorkFlow(_workFlowInfo)
