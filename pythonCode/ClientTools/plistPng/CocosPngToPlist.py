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
opsDict["targetFolder"] = '要合并的目标文件夹，结构满足 plist + png + png文件夹'
opsDict["backIntoFolder"] = "合并结束后，放回工程中"

# 合并大图
#   文件夹里有 xx.plist + xx.png 找到对应的 xx 文件夹 
#   删除xx.plist,删除xx.png
#   xx 文件夹 合并 成 xx.plist,xx.png
#   删除 xx 文件夹
# ------------------------------------测试用例---------------------------------------------------------------------------------------
if __name__ == '__main__':
    _ops = SysInfo.getOps(opsDict, OptionParser())
    _currentFolder = SysInfo.fixFolderPath(os.path.dirname(os.path.realpath(__file__)))
    # plist 路径集
    _plistPathList = FileReadWrite.getFilePathsByType(_ops.targetFolder, "plist")
    for _i in range(len(_plistPathList)):
        _plisPath = _plistPathList[_i]
        # 有同名的文件就是大图用的plist
        _pngPath = SysInfo.getPathWithOutPostfix(_plisPath) + ".png"
        if os.path.exists(_pngPath):
            # 移除原有
            os.remove(_pngPath)
            os.remove(_plisPath)
            # 获取文件夹路径
            _foldPath = SysInfo.fixFolderPath(os.path.dirname(_pngPath)) + SysInfo.justName(_pngPath)
            # 调用 TexturePacker 命令行
            _cmd = ""
            _cmd += "TexturePacker "
            _cmd += "--format cocos2d "
            _cmd += "--texture-format png "
            _cmd += "--data " + _foldPath + ".plist "
            _cmd += "--sheet " + _foldPath + ".png "
            _cmd += "--opt RGBA8888 "
            _cmd += "--max-width 2048 "
            _cmd += "--max-height 2048 "
            _cmd += "--padding 2 "
            _cmd += _foldPath
            print "_cmd = " + str(_cmd)
            SysCmd.doShell(_cmd)
            # 移除碎图文件夹
            shutil.rmtree(SysInfo.fixFolderPath(_foldPath))
    # 拷贝合并后的资源拷贝回工程
    FileCopy.copy_files_with_config_base(["png", "plist"], _ops.targetFolder, _ops.backIntoFolder, False)
    print "PngToPlst ---------- 合并结束 ---------- "
