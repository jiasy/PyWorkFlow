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
opsDict["templet"] = '文件模板'
# 模板可能从不同的数据来源获取数据
opsDict["jsonPaths"] = 'Json文件路径集合'
opsDict["outputPath"] = '替换完之后放置的位置，包含文件名及后缀'

# 读取json文件，或者将Excel文件转换成json。将列表中的文件合并成一个json。
# json 最后是一个键值对对象[key:value]，然后模板中的 ${key}，替换成 value。
# 将替换完的文件，放置到 outputPath 路径下。
# ------------------------------------测试用例---------------------------------------------------------------------------------------
if __name__ == '__main__':
    _ops = SysInfo.getOps(opsDict,OptionParser())
    _currentFolder = SysInfo.fixFolderPath(os.path.dirname(os.path.realpath(__file__)))


