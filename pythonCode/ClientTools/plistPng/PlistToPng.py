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
opsDict["sourceFolder"] = 'plist大图的文件夹'
opsDict["targetFolder"] = '拆分小图后，放置到哪个文件夹'

# 合并大图
#   在sourceFolde 中 png,plist 
#   复制到 targetFolder 中，如果 targetFolder 中只有plist + png 那么就可以把这个文件夹删除。
#   将 png + plist 一一对应的，进行拆分图片。
#   删除原来的plist + png，删除掉 不能拆分小图的png。
#   python /Users/jiasy/Documents/sourceFrame/pythonToolBase/game_tools/plist_to_pngs/PngToPlist.py -s /Users/jiasy/Desktop/testJs/pics/ -t /Users/jiasy/Desktop/testJs/packPics
# ------------------------------------测试用例---------------------------------------------------------------------------------------
if __name__ == '__main__':
	_ops = SysInfo.getOps(opsDict,OptionParser())
	_currentFolder = SysInfo.fixFolderPath(os.path.dirname(os.path.realpath(__file__)))

	# 判断之前是否已经有一个目标文件夹存在。
	if os.path.exists(_ops.targetFolder):
		# 拆分出来的图只能是png,jpg。所以只能有这两类
		if SysInfo.isFolderContainesExcludePostfix(_ops.targetFolder,[".jpg",".png"]):
			print "ERROR : 目标文件夹 : "+_ops.targetFolder+" 不能存在 .jpg .png 之外的文件"
		# 满足特征就删除掉这个，之后的代码再创建这个文件夹
		shutil.rmtree(_ops.targetFolder)

	# 当前执行脚本所在的路径
	_currentFolder = SysInfo.fixFolderPath(os.path.dirname(os.path.realpath(__file__)))
	# 切分脚本位置
	_slicePyFilePath = _currentFolder + "unpack/unpacker.py"
	 # 拷贝
	_configObject = {}
	_configObject["from"] = ""
	_configObject["to"] = ""
	_configObject["include"] = []
	_configObject["include"].append("*.png$")
	_configObject["include"].append("*.plist$")
	FileCopy.copy_files_with_config_base("png,plist",_ops.sourceFolder,_ops.targetFolder,False)
	
	# plist 路径集
	_pngPathList = FileReadWrite.getFilePathsByType(_ops.targetFolder,"png")
	for _i in range(len(_pngPathList)):
		_pngPath = _pngPathList[_i]
		#有同名的文件就是大图用的plist
		_plistPath = SysInfo.getPathWithOutPostfix(_pngPath)+ ".plist"
		if os.path.exists(_plistPath):
			# 执行脚本路径，大图所在的路径
			_cmdPath = os.path.dirname(_pngPath)
			# 纯名
			_bigPicNameWithOutPostfix =  SysInfo.justName(_pngPath)
			_cmd = "cd "+_cmdPath+";" + "python "+_slicePyFilePath +" "+_bigPicNameWithOutPostfix
			print "_cmd = " + str(_cmd)
			SysCmd.doShell(_cmd);
			os.remove(_plistPath)
		# 移除原有的图-不论是不是大图，都删掉他
	   	os.remove(_pngPath)

