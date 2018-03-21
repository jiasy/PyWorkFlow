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
from optparse import OptionParser
from FileReadWrite import dictFromJsonFile

# 获取 subFolderPath_ 相对于 folderPath_ 的路径，去掉后缀
def getRelativePathWithOutSuffix(folderPath_,subFolderPath_,suffix_):
	return str(subFolderPath_).split(folderPath_)[1].split(suffix_)[0]

# 获取 subFolderPath_ 相对于 folderPath_ 的路径
def getRelativePath(folderPath_,subFolderPath_):
	return str(subFolderPath_).split(folderPath_)[1]

# 获取校验参数
def getOps(opsDict_,parse_):
	# 获取临时文件夹路径
	_tempFolder = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, os.pardir,"temp"))
	_jenkinsParameterPath = os.path.join(_tempFolder,"currentJenkinsParameter.json")
	_jenkinsParameterDict = None
	if os.path.exists(_jenkinsParameterPath):
		# 如果有jenkins的参数共享，就取出来
		_jenkinsParameterDict = dictFromJsonFile(_jenkinsParameterPath)

	# 按照参数指定设置参数解析
	for _key in opsDict_:
		_val = opsDict_[_key]
		parse_.add_option('', "--" + _key, dest=_key, help=_val)

	# 取得传入的参数
	_ops = parse_.parse_args()[0]  # 这里参数值对应的参数名存储在这个_ops字典里

	# 解析每一个参数
	for _key in opsDict_:
		if not _ops.__dict__[_key]:
			print "ERROR : 必须有 " + _key + " -> " + opsDict_[_key]
			sys.exit(1)
		else:
			# 当参数是 jenkins.xx 的时候，代表从jenkins的共享参数中取数据
			_ops.__dict__[_key] = getCmdStr(_ops.__dict__[_key])
			if _ops.__dict__[_key].startswith("jenkins."):
				if _jenkinsParameterDict:
					# 取得 jenkins.xx 中的 xx，在共享参数中获取这个 xx 作为 key，取得共享参数中jenkins设置的值。
					_ops.__dict__[_key] = _jenkinsParameterDict[_ops.__dict__[_key].split("jenkins.")[1]]
				else:
					print "ERROR : " + _ops.__dict__[_key] + " 中 jenkins. 代表需要从jenkins的共享参数中取值\n       但是，这个路径不存在 : " + _jenkinsParameterPath
					sys.exit(1)
	return _ops

def getBoolByStr(str_):
	# 字符串 标示的是 boolean 值，那么就转换一下
	if str_ == "True":
		return True
	elif str_ == "False":
		return False
	else:
		print "ERROR str_ 必须是 True/False 中的一个"
		sys.exit(1)

# 设置参数
# <_> 转换回 空格
def getCmdStr(val_):
	return val_.replace('\<', '<').replace('\>', '>').replace("<_>", " ")

# 获取参数
# 空格 转换回 <_>
def setCmdStr(val_):
	return val_.replace('(', '\(').replace(')', '\)').replace(' ', '<_>').replace('<', '\<').replace('>', '\>').replace('\"', '\\"')

# 上层路径
def getParentPath(path_):
	_path = path_
	# 自己是一个文件夹，且 /a/b/c/ 的时候，先变成 /a/b/c 
	if os.path.basename(_path) == "":
		_path = os.path.dirname(_path)
	return os.path.dirname(_path)

def getBaseName(path_):
	_path = path_
	# 自己是一个文件夹，且 /a/b/c/ 的时候，先变成 /a/b/c
	if os.path.basename(_path) == "":
		_path = os.path.dirname(_path)
	return os.path.basename(_path)

def joinPath(parent_,baseName_):
	# parent 添加斜杠，baseName 去掉斜杠，保证拼接处只有一个斜杠
	return fixFolderPath(parent_)+baseName_.replace("\\","").replace("/","")

# 文件夹 路径 修改
def add_path_prefix(path_str):
	if not os_is_win32():
		return path_str
	if path_str.startswith("\\\\?\\"):
		return path_str
	ret = "\\\\?\\" + os.path.abspath(path_str)
	ret = ret.replace("//", "/")
	ret = ret.replace("/", "\\")
	return ret


def fixFolderPath(path_):
	if path_[-1] != add_path_prefix("/"):
		path_ += add_path_prefix("/")
	return path_


# 文件夹下的文件更名
def renameFileInFolder(folderPath_, oldName_, newName_):
	# print "folderPath_ = " + str(folderPath_) 
	# print "oldName_ = " + str(oldName_) 
	# print "newName_ = " + str(newName_) 
	os.rename(os.path.join(folderPath_, oldName_), os.path.join(folderPath_, newName_))


# 文件目录是否有子文件夹
def isFolderHasSubFolder(folderPath_):
	if os.path.isdir(folderPath_):
		_filePathsInDir = os.listdir(folderPath_)
		for _fileName in _filePathsInDir:
			_filePath = os.path.join(folderPath_, _fileName)
			if os.path.isdir(_filePath):
				return True
	else:
		print "ERROR SysInfo -> isFolderHasSubFolder : 不是一个文件夹 : " + folderPath_ + " "
		sys.exit(1)
	return False


# 文件夹 是否 含有除了给定类型之外的文件类型。
def isFolderContainesExcludePostfix(folderPath_, filters_):
	for _parent, _dir_names, _file_names in os.walk(folderPath_):
		for _file_name in _file_names:
			_postfix = getPostfix(_file_name)
			if _postfix not in filters_:
				return True
	return False


# ------------------------------------系统判断---------------------------------------------------------------------------------------
def os_is_win32():
	return sys.platform == 'win32'


def os_is_32bit_windows():
	if not os_is_win32():
		return False
	arch = os.environ['PROCESSOR_ARCHITECTURE'].lower()
	archw = "PROCESSOR_ARCHITEW6432" in os.environ
	return (arch == "x86" and not archw)


def os_is_mac():
	return sys.platform == 'darwin'


def os_is_linux():
	return 'linux' in sys.platform


# ------------------------------------时间戳---------------------------------------------------------------------------------------
def time_stamp():
	_reg = re.search(r'(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)\.(\d+)', str(datetime.datetime.now()))
	if _reg:
		return str(_reg.group(2)) + "_" + str(_reg.group(3)) + "_" + str(_reg.group(4)) + "_" + str(_reg.group(5))
	else:
		print "ERROR : 时间戳格式错误 "


# 获取没有后缀的路径
def getPathWithOutPostfix(filePath_):
	return os.path.splitext(filePath_)[0]


# 只要后缀
def getPostfix(filePath_):
	return os.path.splitext(filePath_)[1]


# 只去名，去掉路径，去掉后缀
def justName(filePath_):
	_basePath = os.path.basename(filePath_)
	_basePathArr = os.path.splitext(_basePath)
	return _basePathArr[0]


# 对象转换字符串
def convertToStr(object_):
	if isinstance(object_, float) or isinstance(object_, int) or isinstance(object_, bool):
		return str(object_)
	elif isinstance(object_, unicode):
		return object_.decode('utf-8')
	elif isinstance(object_, str):
		return object_
	elif isinstance(object_, NoneType):
		return "< NoneType >"


'''
os.path.abspath(path) #返回绝对路径
os.path.basename(path) #返回文件名
os.path.commonprefix(list) #返回list(多个路径)中，所有path共有的最长的路径。
os.path.dirname(path) #返回文件路径
os.path.exists(path)  #路径存在则返回True,路径损坏返回False
os.path.lexists  #路径存在则返回True,路径损坏也返回True
os.path.expanduser(path)  #把path中包含的"~"和"~user"转换成用户目录
os.path.expandvars(path)  #根据环境变量的值替换path中包含的”$name”和”${name}”
os.path.getatime(path)  #返回最后一次进入此path的时间。
os.path.getmtime(path)  #返回在此path下最后一次修改的时间。
os.path.getctime(path)  #返回path的大小
os.path.getsize(path)  #返回文件大小，如果文件不存在就返回错误
os.path.isabs(path)  #判断是否为绝对路径
os.path.isfile(path)  #判断路径是否为文件
os.path.isdir(path)  #判断路径是否为目录
os.path.islink(path)  #判断路径是否为链接
os.path.ismount(path)  #判断路径是否为挂载点（）
os.path.join(path1[, path2[, ...]])  #把目录和文件名合成一个路径
os.path.normcase(path)  #转换path的大小写和斜杠
os.path.normpath(path)  #规范path字符串形式
os.path.realpath(path)  #返回path的真实路径
os.path.relpath(path[, start])  #从start开始计算相对路径
os.path.samefile(path1, path2)  #判断目录或文件是否相同
os.path.sameopenfile(fp1, fp2)  #判断fp1和fp2是否指向同一文件
os.path.samestat(stat1, stat2)  #判断stat tuple stat1和stat2是否指向同一个文件
os.path.split(path)  #把路径分割成dirname和basename，返回一个元组
os.path.splitdrive(path)   #一般用在windows下，返回驱动器名和路径组成的元组
os.path.splitext(path)  #分割路径，返回路径名和文件扩展名的元组
os.path.splitunc(path)  #把路径分割为加载点与文件
os.path.walk(path, visit, arg)  #遍历path，进入每个目录都调用visit函数，visit函数必须有
'''
