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


# #从Excel中获取字典对象
# def dictFromExcelFile(excelPath_):
# 	_workBook = xlrd.open_workbook(excelPath_)
# 	_configDict = {}
# 	for _sheetName in _workBook.sheet_names():
# 		if isinstance(_sheetName, unicode):
# 			_sheetName = _sheetName.encode('utf-8')
# 		_configDict[_sheetName] = dictFromExcelSheet(_workBook.sheet_by_name(_sheetName))
# 	return _configDict

# #从每一个sheet页取数据 数据都是k - v 摆放的。
# def dictFromExcelSheet(sheet_):
# 	_sheetDict = {}
# 	for _rowNum in range(sheet_.nrows):
# 		for _colNum in range(sheet_.ncols):
# 			if _colNum + 2 >= sheet_.ncols:
# 				break
# 			else:
# 				_key = str(sheet_.cell(_rowNum, _colNum + 1).value)
# 				_value = str(sheet_.cell(_rowNum, _colNum + 2).value)
# 				if str(sheet_.cell(_rowNum, _colNum).value) and _key and _value:
# 					_sheetDict[_key] = _value
# 				else:
# 					continue
# 				break
# 	return _sheetDict


# KeyValue ------------------------------------------------------------------------------------
def dictFromExcelSheet(sheet_):
    _sheetDict = {}
    _haveStartBool = False
    for _rowNum in range(sheet_.nrows):
        # 规定 第一个 三个都有值的行为起始行
        if str(sheet_.cell(_rowNum, 2).value) != "" and str(sheet_.cell(_rowNum, 3).value) != "" and str(sheet_.cell(_rowNum, 4).value) != "":
            _haveStartBool = True
            # 取得 每一列的名称
            for _colNum in range(4, sheet_.ncols):
                _currentLocationName = str(sheet_.cell(_rowNum, _colNum).value)
                if _currentLocationName and _currentLocationName != "":
                    _currentLocationDict = {}
                    _sheetDict[_currentLocationName] = _currentLocationDict
                    # 取得键值 
                    for _rowNumInside in range(_rowNum + 1, sheet_.nrows):
                        if str(sheet_.cell(_rowNumInside, 2).value) != "" and str(sheet_.cell(_rowNumInside, 3).value) != "" and str(sheet_.cell(_rowNumInside, 4).value) != "":
                            _currentLocationDict[str(sheet_.cell(_rowNumInside, 3).value)] = str(sheet_.cell(_rowNumInside, _colNum).value)
                else:
                    break
            break
    return _sheetDict


def dictFromExcelFile(excelPath_):
    _workBook = xlrd.open_workbook(excelPath_)
    _configDict = {}
    for _sheetName in _workBook.sheet_names():
        if isinstance(_sheetName, unicode):
            _sheetName = _sheetName.encode('utf-8')
        _configDict[_sheetName] = dictFromExcelSheet(_workBook.sheet_by_name(_sheetName))
    return _configDict


# 获取 执行命令那一个格子
def getExcuteCmd(excelPath_):
    _workBook = xlrd.open_workbook(excelPath_)
    _configDict = {}
    for _sheetName in _workBook.sheet_names():
        if isinstance(_sheetName, unicode):
            _sheetName = _sheetName.encode('utf-8')
        _sheet = _workBook.sheet_by_name(_sheetName)
        # 逐行判断
        for _rowNum in range(0, _sheet.nrows):
            if str(_sheet.cell(_rowNum, 1).value) == "复制命令行":
                return str(_sheet.cell(_rowNum, 2).value)
        print "ERROR 用来配置 pyWorkFlow 的 Excel 必须有 复制命令行。"
        sys.exit(1)
