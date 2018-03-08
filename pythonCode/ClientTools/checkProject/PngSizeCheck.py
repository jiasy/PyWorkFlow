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

def calculateArea(picPath_,maxWidth_,maxHeight_):
	_sizeMax = int(float(maxWidth_))*int(float(maxHeight_))
	_pic = Image.open(picPath_)
	_w, _h = _pic.size
	_width = getNextLevel(int(_w))
	_height = getNextLevel(int(_h))
	if (_width * _height) > _sizeMax:
		_infoObj = {}
		_infoObj["picPath"] = picPath_
		_infoObj["width"] = _width
		_infoObj["height"] = _height
		_infoObj["w"] = _w
		_infoObj["h"] = _h
		return _infoObj
	else:
		return None

def checkWidthAndHeight(picPath_,maxWidth_,maxHeight_):
	_pic = Image.open(picPath_)
	_w, _h = _pic.size
	_width = getNextLevel(int(_w))
	_height = getNextLevel(int(_h))
	if _width>int(float(maxWidth_)) or _height>int(float(maxHeight_)):
		_infoObj = {}
		_infoObj["picPath"] = picPath_
		_infoObj["width"] = _width
		_infoObj["height"] = _height
		_infoObj["w"] = _w
		_infoObj["h"] = _h
		return _infoObj
	else:
		return None

def getNextLevel(int_):
	_sizeLevelList = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]
	_currentLevel = 0
	while int_ > _sizeLevelList[_currentLevel]:
		_currentLevel += 1
	return int(_sizeLevelList[_currentLevel])

# 修改所需属性
opsDict = {}
opsDict["targetFolder"] = '检验的资源文件夹'
opsDict["maxWidth"] = '最大宽'
opsDict["maxHeight"] = '最大高'
opsDict["onlyCalculateArea"] = '只计算面积'

# python PngSizeCheck1024.py -targetFolder 要校验的文件夹
if __name__ == '__main__':
	_ops = SysInfo.getOps(opsDict,OptionParser())
	# boolean 值转换。
	_ops.onlyCalculateArea = SysInfo.getBoolByStr(_ops.onlyCalculateArea)
	_currentFolder = SysInfo.fixFolderPath(os.path.dirname(os.path.realpath(__file__)))
	# 图片路径集合
	_pngList = FileReadWrite.getFilePathsByType(_ops.targetFolder,"png")
	_jpgList = FileReadWrite.getFilePathsByType(_ops.targetFolder,"jpg")
	_picList = _pngList + _jpgList
	# 不合条件的集合
	_overList = []
	for _i in range(len(_picList)):
		if _ops.onlyCalculateArea:
			_overPicInfo = calculateArea( _picList[_i],_ops.maxWidth,_ops.maxHeight)
			if _overPicInfo: _overList.append(_overPicInfo)
		else:
			_overPicInfo = checkWidthAndHeight( _picList[_i],_ops.maxWidth,_ops.maxHeight)
			if _overPicInfo: _overList.append(_overPicInfo)

	print "  共有 {0} 张图片，不合格图片有 {1} 张。".format(len(_picList),len(_overList))

	if len(_overList)>0:
		if _ops.onlyCalculateArea:
			print "	WARN PicSizeCheck 以下图片大小超过 {0}x{1} ----------".format(_ops.maxWidth,_ops.maxHeight)
		else:
			print "	WARN PicSizeCheck 以下图片大小超过 宽高超限制 < {0} {1} >----------".format(_ops.maxWidth,_ops.maxHeight)
		for _i in range(len(_overList)):
			_item = _overList[_i]
			print "	  {0}\n		{1} x {2} - <内存加载时尺寸 : {3} x {4}>".format(_item["picPath"], _item["w"], _item["h"], _item["width"],_item["height"])
		sys.exit(1)






