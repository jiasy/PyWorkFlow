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


# 参数字符串，转换成字典。 kvSplit_ 传递 < : >
# a : b,c : d -> {{a:b},{c:d}}
def strListToDict(str_, kvSplit_):
	_strList = str_.split(",")
	_backDict = {}
	for _i in range(len(_strList)):
		_strItem = _strList[_i]
		_strKV = _strItem.split(kvSplit_)
		_backDict[_strKV[0]] = _strKV[1]
	return _backDict
