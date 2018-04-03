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


# ------------------------------------执行脚本---------------------------------------------------------------------------------------
def doShell(_shellScriptStr):
    # print "shell script : "+_shellScriptStr
    # shell是否为shell脚本
    _p = Popen(_shellScriptStr, shell=True, stdout=PIPE, stderr=PIPE)
    # 阻塞等待
    (stdoutdata, stderrdata) = _p.communicate()
    if _p.returncode != 0:
        print "doShell Error."
        return -1
    else:
        # print "doShell Success."
        return 1


def doShellGetOutPut(_shellScriptStr):
    _status, _output = commands.getstatusoutput(_shellScriptStr)
    # 输出
    print _output
    if _status == 0:
        return 1
    else:
        print "doShell Error."
        sys.exit(1)
