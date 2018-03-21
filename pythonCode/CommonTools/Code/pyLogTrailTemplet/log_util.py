#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import re
import os
import json
import string
import shutil
from subprocess import PIPE, Popen

import logging
import logging.handlers

reload(sys)
sys.setdefaultencoding('utf-8')

functionStack = []
interStr = "|   "
countMax = 2000
count = 0
# 当前的Log是否处于可输出状态
passCount = 0


LOG_FILE = 'tst.log'

handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes= 1024 * 1024 * 1024, backupCount=5)
fmt = '%(message)s'

formatter = logging.Formatter(fmt)  # 实例化formatter
handler.setFormatter(formatter)  # 为handler添加formatter

logger = logging.getLogger('tst')  # 获取名为tst的logger
logger.addHandler(handler)  # 为logger添加handler
logger.setLevel(logging.DEBUG)


class LogUtil(object):
    @classmethod
    def fi(cls, path_, functionName_, comment_, pass_, par_):

        global countMax
        global count
        global functionStack
        global interStr
        global passCount
        global logger

        if pass_ == True:
            passCount = passCount + 1

        if passCount > 0:
            # 当前已经被锁
            return
        elif passCount == 0:
            count += 1
            if count > countMax:
                return
            # 记录这个方法执行时的相关信息
            _tempTable = {}
            # 组合成唯一函数路径
            _tempTable["uniquePath"] = path_ + " -> " + functionName_

            functionStack.append(_tempTable)

            # 层级字符串
            _tempStr = ""

            for _i in range(len(functionStack)):
                _tempStr = _tempStr + interStr

            # 层级叠加得到当前的方法执行字符串
            _tempStr = _tempStr + path_ + " -> " + functionName_

            # 显示LOG
            if comment_ and comment_ != "":
                # print "->"+_tempStr+"  :  "+comment_+" "+par_
                logger.info("->" + _tempStr + "  :  " + comment_ + " " + par_)
            else:
                # print "->"+_tempStr
                logger.info("->" + _tempStr + "  :  " + comment_ + " " + par_)
        else:
            logger.info("ERROR -------------------------------passCount - fi ")

    @classmethod
    def fo(cls, path_, functionName_, comment_, pass_, par_):
        global countMax
        global count
        global functionStack
        global interStr
        global passCount
        global logger

        # 当前的路径
        nowFunStr = path_ + " -> " + functionName_

        if len(functionStack) == 0:
            return

        if passCount > 0:
            pass
        elif passCount == 0:
            # 可以输出LOG的情况下
            # pass_ 本身需要跳过
            if pass_:
                return
            if count > countMax:
                return
            _tempStr = ""
            for _i in range(len(functionStack)):
                _tempStr = _tempStr + interStr

            # 获取堆栈的最后一个
            _tempTable = functionStack[len(functionStack) - 1]
            # 不论后面对不对,都推出最后一个
            functionStack.remove(_tempTable)

            # 最后一个Function组合名
            _lastFunStr = _tempTable["uniquePath"]

            # 组合成唯一函数路径
            if nowFunStr == _lastFunStr:
                _tempStr = _tempStr + _lastFunStr  # 显示LOG
                if comment_ and comment_ != "":
                    if par_:
                        # print "<-"+_tempStr+"  :  "+comment_+" "+par_
                        logger.info("<-" + _tempStr + "  :  " + comment_ + " " + par_)
                    else:
                        # print "<-"+_tempStr+"  :  "+comment_
                        logger.info("<-" + _tempStr + "  :  " + comment_)
                else:
                    # print "<-"+_tempStr
                    logger.info("<-" + _tempStr)
            else:
                # print("ERROR -------------------------------")
                logger.info("ERROR -------------------------------")
                logger.info("now  : " + nowFunStr)
                logger.info("last : " + _lastFunStr)
        else:
            logger.info("ERROR -------------------------------passCount - fi ")

        # 已经锁的情况下解锁
        if pass_ == True:
            # 解锁
            passCount = passCount - 1
