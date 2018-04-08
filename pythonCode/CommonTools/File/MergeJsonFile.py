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
import JsonMerge

# 修改所需属性
opsDict = {}
opsDict["inputJsonPaths"] = '要合并的json文件路径列表'
opsDict["outputJsonPath"] = '合并后的json文件路径'

# json 合并
# 相同层级的同名字段会覆盖，如有覆盖情况，请注意先后顺序
# ------------------------------------测试用例---------------------------------------------------------------------------------------
if __name__ == '__main__':
    _ops = SysInfo.getOps(opsDict, OptionParser())
    _currentFolder = SysInfo.fixFolderPath(os.path.dirname(os.path.realpath(__file__)))

    # 合并的目标
    _targetJsonDict = {}
    # 要合并的json文件
    _jsonPaths = _ops.inputJsonPaths.split(",")
    # 合并json对象
    for _i in range(len(_jsonPaths)):
        _currentJsonDict = FileReadWrite.dictFromJsonFile(_jsonPaths[_i])
        _targetJsonDict = JsonMerge.mergeData(_currentJsonDict, _targetJsonDict)

    # 写入文件
    FileReadWrite.writeFileWithStr(_ops.outputJsonPath, str(json.dumps(_targetJsonDict, indent=4, sort_keys=False, ensure_ascii=False)))
