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
opsDict["sourceFolder"] = '碎图的文件夹'
opsDict["targetFolder"] = '生成的plist放置的文件夹'

# 合并大图
#   在sourceFolde 中 png / jpg
#   放置到 targetFolder。如果targetFolder已经存在，校验它是不是生成的文件夹，是的话，就删除。
#   把文件夹内的图片都合成大图，然后删除原来的文件夹，和不能合成大图的png图片。
# ------------------------------------测试用例---------------------------------------------------------------------------------------
if __name__ == '__main__':
	_ops = SysInfo.getOps(opsDict,OptionParser())
	_currentFolder = SysInfo.fixFolderPath(os.path.dirname(os.path.realpath(__file__)))

	# 判断之前是否已经有一个目标文件夹存在。
	if os.path.exists(_ops.targetFolder):
		# 合并的图只能是png,plist。所以只能有这两类
		if SysInfo.isFolderContainesExcludePostfix(_ops.targetFolder,[".png",".plist"]):
			print "ERROR : 目标文件夹 : "+_ops.targetFolder+" 不能存在 .png,.plist 之外的文件"
		# 满足特征就删除掉这个，之后的代码再创建这个文件夹
		shutil.rmtree(_ops.targetFolder)

	# 当前执行脚本所在的路径
	_currentFolder = SysInfo.fixFolderPath(os.path.dirname(os.path.realpath(__file__)))
	# 拷贝图片
	FileCopy.copy_files_with_config_base("png,jpg",_ops.sourceFolder,_ops.targetFolder,False)

	if not os.path.exists(_ops.targetFolder):
		# 拷贝成功的时候，_ops.targetFolder 会创建，没有创建，就是没有拷贝成功。可能是源目录没图？
		print "ERROR {0} 没有任何图片？".format(_ops.sourceFolder)
		sys.exit(1)


	# 文件列表
	_filePathList = []
	_filters=[".jpg",".png"]
	FileReadWrite.gci(_ops.targetFolder,_filters,_filePathList)
	# 已经合并过的文件夹 集合
	_alreadPackList = []
	# 合并图片
	for _i in range(len(_filePathList)):
		_filePath = _filePathList[_i]
		_folderPath = os.path.dirname(_filePath) 
		_folderName = os.path.basename(_folderPath)
		# 已经 合并 完的列表
		if SysInfo.fixFolderPath(_folderPath) not in _alreadPackList:
			# 判断一下 合并过的图 是否有不合理的文件夹放置
			for _j in range(len(_alreadPackList)):
				_packFolderPath = _alreadPackList[_j]
				if _folderPath.find(SysInfo.fixFolderPath(_packFolderPath)) == 0 or _packFolderPath.find(SysInfo.fixFolderPath(_folderPath)) == 0:
					print "ERROR PngToPList 文件夹内有图，就不能有子文件夹 -------- "
					print		"_packFolderPath : "+_packFolderPath
					print		"_folderPath	 : "+_folderPath
					sys.exit(1)
			# 文件夹的上层路径
			_folderParentPath = os.path.dirname(_folderPath)
			# 调用 TexturePacker 命令行
			_cmd = ""
			_cmd += "TexturePacker "
			_cmd += "--format cocos2d "
			_cmd += "--texture-format png "
			_cmd += "--data "+_folderPath+".plist "
			_cmd += "--sheet "+_folderPath+".png "
			_cmd += "--opt RGBA8888 "
			_cmd += "--max-width 2048 "
			_cmd += "--max-height 2048 "
			_cmd += "--padding 2 "
			_cmd += _folderPath
			# 执行脚本
			print "_cmd = " + str(_cmd)
			SysCmd.doShell(_cmd)
			# _cmd = TexturePacker --format cocos2d --texture-format png --data <plist文件路径> --sheet <png大图路径> --opt RGBA8888 --max-width 2048 --max-height 2048 --padding 2 <文件夹>
			# 记录 合并完 的路径
			_alreadPackList.append(SysInfo.fixFolderPath(_folderPath))

	# 删除合并完的文件夹
	for _i in range(len(_alreadPackList)):
		shutil.rmtree( _alreadPackList[_i])

