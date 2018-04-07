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
import ExcelUtils
import ExcelDataUtils

# 列表结构的excel数据输出，json结构的数据输出
opsDict = {}
opsDict["inputExcelPaths"] = '输入Excel数据的路径集合'
opsDict["outputJsonFolder"] = '承载输出json文件的文件夹'

# 将 列表、Json格式的Excel文件，一对一转换成Json文件
# Json第一层级的键值对，为Sheet表明。
# 表明有特殊要求，必须是 l[列表格式]/d[json格式]
# ---------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    _ops = SysInfo.getOps(opsDict, OptionParser())
    _currentFolder = SysInfo.fixFolderPath(os.path.dirname(os.path.realpath(__file__)))
    _excelPaths = _ops.inputExcelPaths.split(",")
    for _i in range(len(_excelPaths)):
        _excelPath = _excelPaths[_i]
        # Excel 解析
        _currentWorkBook = ExcelUtils.WorkBook()
        _currentWorkBook.initWithWorkBook(_excelPath)
        # 数据转换
        _excelDataObject = ExcelDataUtils.DataObject()
        _excelDataObject.initWithExcelWorkBook(_currentWorkBook)
        # _excelDataObject.printSelf()
        # 写入输出文件
        _excelDataObject.writeJsonToFile(os.path.join(_ops.outputJsonFolder, SysInfo.justName(_excelPath) + ".json"))
