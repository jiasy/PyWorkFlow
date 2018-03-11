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

# 修改所需属性
opsDict = {}
opsDict["baseIconPath"] = '图标文件路径'
opsDict["iosIconsPath"] = 'ios 工程 Icon 路径'
opsDict["androidIconsPath"] = 'android 工程 Icon 路径'
# opsDict["h5IconsPath"] = 'h5 工程 Icon 路径'

# 将一个 ICON 变成不同大小，适合不同工程的一堆图标
# ------------------------------------测试用例---------------------------------------------------------------------------------------
if __name__ == '__main__':
    _ops = SysInfo.getOps(opsDict, OptionParser())
    _currentFolder = SysInfo.fixFolderPath(os.path.dirname(os.path.realpath(__file__)))

    _iosSizes = {
        '29': (29, 29),
        '40': (40, 40),
        '50': (50, 50),
        '57': (57, 57),
        '58': (58, 58),
        '72': (72, 72),
        '76': (76, 76),
        '80': (80, 80),
        '87': (87, 87),
        '100': (100, 100),
        '114': (114, 114),
        '120': (120, 120),
        '144': (144, 144),
        '152': (152, 152),
        '180': (180, 180)
    }

    _androidSizes = {
        'mipmap-mdpi': (48, 48),
        'mipmap-hdpi': (72, 72),
        'mipmap-xhdpi': (96, 96),
        'mipmap-xxhdpi': (144, 144)
    }

    # 重新创建输出文件夹
    if os.path.exists(_ops.iosIconsPath):
        shutil.rmtree(_ops.iosIconsPath)
    os.makedirs(_ops.iosIconsPath)

    if os.path.exists(_ops.androidIconsPath):
        shutil.rmtree(_ops.androidIconsPath)
    os.makedirs(_ops.androidIconsPath)

    for _key, _value in _iosSizes.items():
        _IOSFileName = os.path.join(_ops.iosIconsPath, 'Icon-' + _key + '.png')
        try:
            im = Image.open(_ops.baseIconPath)
            im.thumbnail(_value)
            im.save(str(_IOSFileName), "PNG")
        except IOError:
            print "IOS 没能创建 " + _key + " 图标 : " + _ops.baseIconPath

    for _key, _value in _androidSizes.items():
        os.makedirs(os.path.join(_ops.androidIconsPath, _key))
        _AndIconName = os.path.join(_ops.androidIconsPath, _key + '/ic_launcher.png')
        try:
            im = Image.open(_ops.baseIconPath)
            im.thumbnail(_value)
            im.save(str(_AndIconName), "PNG")
        except IOError:
            print "AND 没能创建 " + _key + " 图标 : " + _ops.baseIconPath
