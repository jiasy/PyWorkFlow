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


# 将 targetStr_ 中 满足 regularStr_ 这个正则 的 文字，替换成 replaceToStr_，限制次数 times_ 次
def replaceStrWithReg(targetStr_, regularStr_, replaceToStr_, times_):
    _reRule = re.compile(regularStr_)
    return re.sub(_reRule, replaceToStr_, targetStr_, times_)
