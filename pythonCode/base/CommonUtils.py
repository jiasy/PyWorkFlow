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


# 参数字符串，转换成字典。
# a:b,c:d -> {{a:b},{c:d}}
def strListToDict(str_):
	# , 分割每一组键值
	_strList = str_.split(",")
	_backDict = {}
	for _i in range(len(_strList)):
		_strItem = _strList[_i]
		# : 分割键值对
		_strKV = _strItem.split(":")
		_backDict[_strKV[0]] = _strKV[1]
	return _backDict

# 参数字符串，整理成键值对字典，字典的值是数组。
# 逐个项判断，是否是一个目标类型的文件
# "/a.js,aCode1,aCode2,aCode3,/b.js,bCode1,bCode2,bCode3"
# 转换成以下格式
# {'/a': ['aCode1', 'aCode2', 'aCode3'], '/b': ['bCode1', 'bCode2']}
def strToListDict(str_,suffix_):
	# /a.js,aCode1,aCode2,aCode3,/b.js,bCode1,bCode2,bCode3
	# /a
	# ,aCode1,aCode2,aCode3,/b
	# ,bCode1,bCode2,bCode3
	_strListTemp = str_.split(suffix_)
	_backDict = {}
	for _i in range(len(_strListTemp)-1):
		_item = _strListTemp[_i]
		# 获取文件名 /a、/b
		_filePathList = _item.split(",")
		_filePath = _filePathList[len(_filePathList)-1]
		# 获取每个文件下的字符串列表
		_itemNext = _strListTemp[_i + 1]
		_contentList = _itemNext.split(",")
		# 建立键值关系
		if _i == (len(_strListTemp)-1):
			_backDict[_filePath] = _contentList[1:len(_contentList)]# 最后一项，不用去掉最后一个字符串
		else:
			_backDict[_filePath] = _contentList[1:len(_contentList)-1]

	return _backDict 

# 将字典转换成列表
# {"/a": ["aCode1", "aCode2", "aCode3"], "/b": ["bCode1", "bCode2"]}
# 转换成以下格式
#  [/b -> bCode1,/b -> bCode2]
def listDictToList(targetDict_,split_):
	backList = []
	for _key in targetDict_:
		_valueList = targetDict_[_key]
		for _i in range(len(_valueList)):
			backList.append(_key + split_ + _valueList[_i])
	return backList





