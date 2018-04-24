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
import Excel
import CommonUtils

# 修改所需属性
opsDict = {}
opsDict["excelFolderPath"] = 'excel所在文件夹'
opsDict["excelName"] = 'excel名称'
opsDict["jenkinsParameters"] = '当前Jenkins的全局参数，供各个work阶段使用'
opsDict["__option__"] = ["jenkinsParameters"]



# 通过Excel名，直接执行Excel中配置的WorkFlow，Excel的名字可以直接写成汉子[比如 : 打包.xlsx，热更.xlsx，服务端代码上传.xlsx]
# 	然后在Jenkins 下面 配置一个公共的 excelFolderPath 参数。
# 	再配置一个可选参数 对应执行的 Excel [比如 : 打包、热更、服务端代码上传]。
# 选择参数，构成以下格式，就可以了
# 	python ExcuteWorkFlowByExcel.py --excelFolderPath excel所在文件夹 --excelName 打包/热更/服务端代码上传 --jenkinsParameters aKey:aValue,bKey:bValue
# eg: 执行
# 	python /Users/jiasy/Documents/sourceFrame/pyWorkFlow/pythonCode/CommonTools/Jenkins/ExcuteWorkFlowByExcel.py --excelFolderPath /Users/jiasy/Documents/sourceFrame/pyWorkFlow/excel/build --excelName CocosCreatorBuild_Jenkins --jenkinsParameters debug:false,platform:web-mobile
#     Jenkins <WORKSPACE 自带的环境参数，标示工程迁出的路径，DEBUG 自定义参数，PLATFORM 自定义参数>
#   python $WORKSPACE/pythonCode/CommonTools/Jenkins/ExcuteWorkFlowByExcel.py --excelFolderPath $WORKSPACE/excel/build --excelName CocosCreatorBuild_Jenkins --jenkinsParameters debug:$DEBUG,platform:$PLATFORM
# ------------------------------------测试用例---------------------------------------------------------------------------------------
if __name__ == '__main__':
    _ops = SysInfo.getOps(opsDict, OptionParser())
    _currentFolder = SysInfo.fixFolderPath(os.path.dirname(os.path.realpath(__file__)))
    _excelPath = os.path.join(_ops.excelFolderPath, _ops.excelName + ".xlsx")
    _cmd = Excel.getExcuteCmd(_excelPath)

    _jenkinsParametersDict = {}
    if _ops.jenkinsParameters :
        # 当前 Jenkins 全局参数的留存文件。独立脚本执行的时候内存不共享，所以，参数存到临时目录。
        _jenkinsParametersDict = CommonUtils.strListToDict(_ops.jenkinsParameters)
        # 将其中的value参数话一下。
        for _key in _jenkinsParametersDict:
            print  _key + " : " + _jenkinsParametersDict[_key]
            _jenkinsParametersDict[_key] = SysInfo.setCmdStr(_jenkinsParametersDict[_key])

    # 重新创建临时路径
    _tempFolder = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, os.pardir, os.pardir, "temp"))
    FileReadWrite.reCreateFolder(_tempFolder)

    # 转换后的键值对，作为当前jenkins执行的共享参数保存到Temp文件夹。
    _jenkinsParameterPath = os.path.join(_tempFolder, "currentJenkinsParameter.json")
    FileReadWrite.writeFileWithStr(_jenkinsParameterPath, str(json.dumps(_jenkinsParametersDict, indent=4, sort_keys=False, ensure_ascii=False)))

    print "		开始执行 " + str(_ops.excelName) + " 脚本工作流"
    print "		jenkins参数 : " + str(json.dumps(_jenkinsParametersDict, indent=4, sort_keys=False, ensure_ascii=False))

    SysCmd.doShellGetOutPut(_cmd)
