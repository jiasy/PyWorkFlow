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


#从Excel中获取字典对象
def dictFromExcelFile(excelPath_):
	_workBook = xlrd.open_workbook(excelPath_)
	_configDict = {}
	for _sheetName in _workBook.sheet_names():
		if isinstance(_sheetName, unicode):
			_sheetName = _sheetName.encode('utf-8')
		_configDict[_sheetName] = dictFromExcelSheet(_workBook.sheet_by_name(_sheetName))
	return _configDict

#从每一个sheet页取数据 数据都是k - v 摆放的。
def dictFromExcelSheet(sheet_):
	_sheetDict = {}
	for _rowNum in range(sheet_.nrows):
		for _colNum in range(sheet_.ncols):
			if _colNum + 2 >= sheet_.ncols:
				break
			else:
				_key = str(sheet_.cell(_rowNum, _colNum + 1).value)
				_value = str(sheet_.cell(_rowNum, _colNum + 2).value)
				if str(sheet_.cell(_rowNum, _colNum).value) and _key and _value:
					_sheetDict[_key] = _value
				else:
					continue
				break
	return _sheetDict