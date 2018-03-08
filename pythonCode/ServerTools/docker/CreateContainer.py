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
opsDict["imageNameAndVersion"] = '镜像名:版本号'
opsDict["containerName"] = '容器名'
opsDict["mappingPorts"] = '端口映射'
opsDict["mappingFolder"] = '共享文件夹设置'

# 只映射部分端口
if __name__ == '__main__':
	_ops = SysInfo.getOps(opsDict,OptionParser())
	_currentFolder = SysInfo.fixFolderPath(os.path.dirname(os.path.realpath(__file__)))
	_ports = _ops.mappingPorts.split(",")
	# 拼接端口号
	_portListStr = ""
	for _i in range(len(_ports)):
		_portListStr += '-p '+_ports[_i]+' '

	_cmd = '\
docker run -tid '+_portListStr+'\
--name '+_ops.containerName+' \
--privileged=true \
--hostname="'+_ops.containerName+'" \
--restart=always \
-v '+_ops.mappingFolder+' \
'+_ops.imageNameAndVersion+' \
/bin/bash \
'

	'''
	docker run -tid -p 80:80 -p 3000:3000 -p 7101:7101 -p 6379:6379 --name ubtnode --privileged=true --restart=always -v 本机路径:Docker容器路径 ubtnodejs:v1 /bin/bash
	'''

	print "_cmd = " + str(_cmd)
	# SysCmd.doShellGetOutPut(_cmd)
	