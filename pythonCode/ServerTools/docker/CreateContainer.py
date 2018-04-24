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
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, os.pardir, "base")))
import FileCopy
import FileReadWrite
import SysInfo
import SysCmd
import CommonUtils

# 修改所需属性
opsDict = {}
opsDict["imageNameAndVersion"] = '镜像名:版本号'
opsDict["name"] = '容器名'
opsDict["hostname"] = '主机名'
opsDict["privileged"] = '是否赋予宿主机权限'
opsDict["restart"] = '重启模式'
opsDict["publish"] = '端口映射列表'
opsDict["volume"] = '共享磁盘路径列表'
opsDict["link"] = '链接容器列表'
opsDict["env"] = '环境变量'
opsDict["net"] = '网络链接模式'
# 可选项包括,可选项可以不填写
opsDict["__option__"] = ["net","env","link","volume","publish","restart","privileged","hostname"]

# 只映射部分端口
if __name__ == '__main__':
    _ops = SysInfo.getOps(opsDict, OptionParser())
    _currentFolder = SysInfo.fixFolderPath(os.path.dirname(os.path.realpath(__file__)))
    # 拼接端口号
    _publishListStr = CommonUtils.getParameterListStr("publish", _ops.publish, False)
    # 拼接外挂磁盘
    _volumeListStr = CommonUtils.getParameterListStr("volume", _ops.volume, False)
    # 拼接容器链接
    _linkListStr = CommonUtils.getParameterListStr("link", _ops.link, False)
    # 拼接环境变量
    _envListStr = CommonUtils.getParameterListStr("env", _ops.env, True)
    # 是否最大 权限
    _privileged = CommonUtils.getParameterStr("privileged", _ops.privileged, False)
    # 主机容器映射关系
    _hostname = CommonUtils.getParameterStr("hostname", _ops.hostname, True)
    # 重启模式
    _restart = CommonUtils.getParameterStr("restart", _ops.restart, False)
    # 容器名
    _name = CommonUtils.getParameterStr("name", _ops.name, False)
    # 网络链接方式
    _net = CommonUtils.getParameterStr("net", _ops.net, True)

    _cmd = '\
docker run -d ' + '\
' + _name + ' \
' + _privileged + ' \
' + _hostname + ' \
' + _restart + ' \
' + _publishListStr + ' \
' + _volumeListStr + ' \
' + _linkListStr + ' \
' + _envListStr + ' \
' + _net + ' \
' + _ops.imageNameAndVersion + ' \
'

    print str(_cmd)
    # SysCmd.doShellGetOutPut(_cmd)
