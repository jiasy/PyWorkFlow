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

sys.path.append('/Users/jiasy/Documents/sourceFrame/pythonToolBase/self/')
import FileCopy
import FileReadWrite
import SysInfo
import SysCmd
import CommonUtils


# ________________________________________________________________________________________________________________________________________________________
def addLogFun(startLogCount_, endLogCount_):
    logCode = '\n'
    logCode += 'var _global = global || window;' + '\n'
    logCode += 'if(_global["getPropertys"]){' + '\n'
    logCode += '}else{' + '\n'
    logCode += '	_global.getPropertys = function (obj){					' + '\n'
    logCode += '		var argumertsStr="";				' + '\n'
    logCode += '		argumertsStr="  | ";				' + '\n'
    logCode += '		for (var key in obj) {				' + '\n'
    logCode += '			if (obj.hasOwnProperty(key)) {			' + '\n'
    logCode += '				var element = obj[key];		' + '\n'
    logCode += '				if (typeof element =="string"){		' + '\n'
    logCode += '					argumertsStr+= key +" : "+element;	' + '\n'
    logCode += '				}else if(typeof element =="number"){		' + '\n'
    logCode += '					argumertsStr+= key +" : "+element.toFixed(2);	' + '\n'
    logCode += '				}else if(typeof element =="boolean"){		' + '\n'
    logCode += '					if (element){	' + '\n'
    logCode += '						argumertsStr+= key +" : true";	' + '\n'
    logCode += '					}else{' + '\n'
    logCode += '					    argumertsStr+= key +" : false";	' + '\n'
    logCode += '					}' + '\n'
    logCode += '				}else {		' + '\n'
    logCode += '					argumertsStr+= key +" : <"+typeof element+">";	' + '\n'
    logCode += '				}		' + '\n'
    logCode += '				argumertsStr+=" | ";		' + '\n'
    logCode += '			}			' + '\n'
    logCode += '		}				' + '\n'
    logCode += '		return argumertsStr;				' + '\n'
    logCode += '	}					' + '\n'
    logCode += '						' + '\n'
    logCode += '	_global.log=(function(pass_,fileName_,className_,functionName_,argumentObj_,contentObject_){					' + '\n'
    logCode += '		var _lastFileName="";				' + '\n'
    logCode += '		var _logCount=0;				' + '\n'
    logCode += '		var _startLogCount=' + ("%d" % startLogCount_) + ';				' + '\n'
    logCode += '		var _endLogCount=' + ("%d" % endLogCount_) + ';				' + '\n'
    logCode += '		var _lastContentObject=null;				' + '\n'
    logCode += '		return function(pass_,fileName_,className_,functionName_,argumentObj_,contentObject_){				' + '\n'
    logCode += '			_logCount+=1;			' + '\n'
    logCode += '			if(pass_){return};			' + '\n'
    logCode += '			var logStr="";			' + '\n'
    logCode += '			var _strLength=0;			' + '\n'
    logCode += '			argumentsStr=_global.getPropertys(argumentObj_)			' + '\n'
    logCode += '			if (fileName_ == _lastFileName){' + '\n'
    logCode += '			//if (fileName_ == _lastFileName && this === _lastContentObject){' + '\n'
    logCode += '				if (className_==""){		' + '\n'
    logCode += '					_strLength = String(fileName_+"  ").length;	' + '\n'
    logCode += '				}else{		' + '\n'
    logCode += '					_strLength = String(fileName_+" __ "+className_ +"  ").length;	' + '\n'
    logCode += '				}		' + '\n'
    logCode += '				var spaceStr="";' + '\n'
    logCode += '				for (var i = 0; i<_strLength; i++) {' + '\n'
    logCode += '					spaceStr+=" ";' + '\n'
    logCode += '				}' + '\n'
    logCode += '				logStr=spaceStr + "| "+functionName_+argumentsStr+"    <"+_logCount+">";' + '\n'
    logCode += '			}else{' + '\n'
    logCode += '				lastStrLength_=0;' + '\n'
    logCode += '				if (className_==""){' + '\n'
    logCode += '					logStr = String(fileName_+" __ "+ functionName_+argumentsStr+"    <"+_logCount+">");' + '\n'
    logCode += '				}else{' + '\n'
    logCode += '					logStr = String(fileName_+" __ "+className_ +" __ "+ functionName_+argumentsStr+"    <"+_logCount+">");' + '\n'
    logCode += '				}' + '\n'
    logCode += '			}' + '\n'
    logCode += '			if(_logCount>=_startLogCount&&_logCount<=_endLogCount){' + '\n'
    logCode += '				console.log(" -- "+logStr);' + '\n'
    logCode += '			}' + '\n'
    logCode += '			if(_logCount>=_startLogCount){' + '\n'
    logCode += '				_lastFileName=fileName_;' + '\n'
    logCode += '			}' + '\n'
    logCode += '			_lastContentObject=contentObject_;' + '\n'
    logCode += '		}' + '\n'
    logCode += '	}());' + '\n'
    logCode += '};' + '\n'
    return logCode


# 修改所需属性
opsDict = {}
opsDict["targetJSPath"] = 'JS所在的文件夹'
opsDict["startLogCount"] = '从多少开始输出'
opsDict["endLogCount"] = '到多少结束输出'
opsDict["justFilterLogsBoo"] = '只跟踪过滤LOG'
opsDict["filterLogs"] = '需要过滤掉的Log'
opsDict["specialFuncLogs"] = '特殊键值显示'
opsDict["fileNameToObjNameBoo"] = '是否开启文件名类名的映射'
opsDict["filNameToObjName"] = '文件名对应的工具类名'

# 
if __name__ == '__main__':
    _ops = SysInfo.getOps(opsDict,OptionParser())
    # log用来过滤，还是用来输出---------------------------------
    _justFilterLogsBoo = False
    if _ops.justFilterLogsBoo == 'false':
        # 用来过滤
        _justFilterLogsBoo = False
    elif _ops.justFilterLogsBoo == 'true':
        # 用来输出
        _justFilterLogsBoo = True
    else:
        print "ERROR : justFilterLogsBoo 值必须是 false/true 中的一个"
        sys.exit(1)

    # 是否将文件名 映射到 对应的全局对象
    _fileNameToObjNameBoo = True
    if _ops.fileNameToObjNameBoo == 'false':
        # 用来过滤
        _fileNameToObjNameBoo = False
    elif _ops.fileNameToObjNameBoo == 'true':
        # 用来输出
        _fileNameToObjNameBoo = True
    else:
        print "ERROR : fileNameToObjNameBoo 值必须是 false/true 中的一个"
        sys.exit(1)

    # 获取过滤字典
    _filterLogsList = _ops.filterLogs.split(",")
    _filterLogsDict = {}
    # "/login_server.js,LoginServer.prototype.tick,server.timer = setInterval,checkNeedLog"
    # 转换成一下格式
    # ("/login_server.js",["LoginServer.prototype.tick","server.timer = setInterval","checkNeedLog"])
    for _i in range(len(_filterLogsList)):
        _strItem = _filterLogsList[_i]
        _opsList = _strItem.split("<>")
        # 第一项 是 Key,第二项 是 Value
        _opsName = _opsList[0]
        del _opsList[0]
        # 对应到字典上
        _filterLogsDict[_opsName] = _opsList
    # 后两个字典正常
    _specialFuncLogs = CommonUtils.strListToDict(_ops.specialFuncLogs, "<>")
    _fileNameToObjName = CommonUtils.strListToDict(_ops.filNameToObjName, "<>")
    # 起止序号
    _startLogCount = int(_ops.startLogCount)
    _endLogCount = int(_ops.endLogCount)

    # 目标文件
    _targetJSPath = _ops.targetJSPath
    # 上层路径
    _targetParentPath = SysInfo.getParentPath(_targetJSPath);
    # 备份路径
    _backUpPath = os.path.join(_targetParentPath, SysInfo.getBaseName(_targetJSPath) + "_backUp")

    # 有备份
    if os.path.exists(_backUpPath):
        # 没有源，有可能删了。【代码执行错误的时候，会删除源，因为，源会变】
        if not os.path.exists(_targetJSPath):
            # 将备份 同步给 源
            shutil.copytree(_backUpPath, _targetJSPath)
            print "备份文件，拷贝回源路径"
        # 源里没有 创建备份的标示。
        if not os.path.isfile(_targetJSPath + '/backup_created'):
            # 删除 原有备份
            shutil.rmtree(_backUpPath)
            # 新备份
            shutil.copytree(_targetJSPath, _backUpPath)
            # 标记已经备份过了
            FileReadWrite.writeFileWithStr(_targetJSPath + '/backup_created', 'backup end')
        else:
            print "已经创建过备份了"
    else:
        # 没备份文件 - 就备份一份
        shutil.copytree(_targetJSPath, _backUpPath)
        # 标记已经备份过了
        FileReadWrite.writeFileWithStr(_targetJSPath + '/backup_created', 'backup end')

    # 取得的文件列表
    _jsFileList = []
    # 从备份 向现有文件夹 转换输出
    FileReadWrite.gci(_backUpPath, [".js"], _jsFileList)

    # 代码中使用function的次数
    _funcLineCount = 0

    # 正则表达式队列
    for _jsPath in _jsFileList:
        # 文件路径,相对于_backUpPath
        fileName = _jsPath.split(_backUpPath)[1]
        tarPath = SysInfo.joinPath(_targetJSPath, fileName)
        # 做判断的,用来显示的路径
        fileShowName = _jsPath.split(_backUpPath)[1]
        # 实质内容的行数
        currentLine = 0
        # 行数
        lineCount = 0
        # 多行注释堆栈
        multiCommon = False
        # 记录判断修改后的行
        jsLines = []
        # 读每一行
        jsCodes = FileReadWrite.linesFromFile(_jsPath)

        # 逐行循环
        for jsLine in jsCodes:
            # 记录行号
            lineCount = lineCount + 1
            # 临时的行副本
            tempJsLine = jsLine

            # 多行注释/*...
            if multiCommon == False:
                commonMatchBegin = re.search(r'/\*.*', tempJsLine)
                if commonMatchBegin:
                    # /* ... */
                    commonMatchOneLine = re.search(r'/\*.*\*/(.*)', tempJsLine)
                    if commonMatchOneLine:
                        multiCommon = False
                        tempJsLine = commonMatchOneLine.group(1)
                    else:
                        multiCommon = True
                        tempJsLine = ''
            else:
                # ...*/
                commonMatchEnd = re.search(r'.*\*/(.*)', tempJsLine)
                if commonMatchEnd:
                    multiCommon = False
                    tempJsLine = commonMatchEnd.group(1)
            if multiCommon:
                # 处于多行注释,相当于代码是空行
                jsLine = "\n"
                jsLines.append(jsLine)
                continue

            # 单行注释
            commonMatch = re.search(r'(.*)//.*', tempJsLine)

            if commonMatch:
                # 排除网址,最后一个字符为\这样的字符串拼接.字符串拼接里面的//不是代码的注释,是字符串的一部分.
                if tempJsLine.find("http://") < 0 and tempJsLine.find("https://") < 0 and tempJsLine.strip()[
                    len(tempJsLine.strip()) - 1] != "\\":
                    tempJsLine = commonMatch.group(1)
                    # 分割注释,提取非注释部分
                    jsLine = tempJsLine + "\n"
                    # 去空格及特殊符号
                    tempJsLine = tempJsLine.strip()

            # 去掉空白行
            if tempJsLine.strip() == '':
                jsLines.append("\n")
                continue

                # 不考虑 '...function...' 以及 "...function..." 的情况。。。

            # 有实质内容，行数叠加
            currentLine = currentLine + 1

            # log取得
            logMatch = re.search(r'(.*)cc\.log\(.*\);?(.*)', tempJsLine)
            # 含log
            if logMatch:
                # 去掉原有log
                jsLine = logMatch.group(1) + logMatch.group(2)
            # log取得
            logMatch = re.search(r'(.*)console\.log\(.*\);?(.*)', tempJsLine)
            # 含log
            if logMatch:
                # 去掉原有log
                jsLine = logMatch.group(1) + logMatch.group(2)

            # 用于 new Function 的方式。工程内没有
            # functionBigMatch=re.search(r'(.*)Function(.*)',tempJsLine)
            # if functionBigMatch:
            #     print tempJsLine

            functionMatch = re.search(r'.*function.*\(.*\).*', tempJsLine)
            if functionMatch:
                # 工程里有/function\s*([^(]*)\(/ 这个正则表达式 规避掉这个情况
                if tempJsLine.find('match(/function\s*([^(]*)\(/)') < 0:
                    # 记录Function数量
                    _funcLineCount = _funcLineCount + 1
                    functionName = ''
                    arguments = ''
                    functionOneLine_1 = re.search(r'.*function\s*(.*)\s*\(\s*.*\s*\)\s*\{.*', tempJsLine)
                    if functionOneLine_1:
                        # xx:function(xx){
                        functionOneLine_2 = re.search(r'\s*(.*)\s*:\s*function\s*\(\s*(.*)\s*\)\s*\{.*', tempJsLine)
                        if functionOneLine_2:
                            functionName = functionOneLine_2.group(1)
                            arguments = functionOneLine_2.group(2)
                        else:
                            # * (function(){
                            functionOneLine_3 = re.search(r'.*\(\s*function\s*\(\s*(.*)\s*\)\s*\{.*', tempJsLine)
                            if functionOneLine_3:
                                if tempJsLine.strip() == '(function(){':
                                    # 就是初始化用的
                                    functionName = "__init__"
                                    arguments = functionOneLine_3.group(1)
                                else:
                                    # ty.PublishersManager = (function(){
                                    functionOneLine_4 = re.search(r'\s*(.*)\s*=\s*\(\s*function\s*\(\s*(.*)\s*\)\s*\{.*',
                                                                  tempJsLine)
                                    if functionOneLine_4:
                                        functionName = functionOneLine_4.group(1)
                                        arguments = functionOneLine_4.group(2)
                                    else:
                                        #       this.view.ccbRootNode.setOnExitCallback(function(){
                                        functionOneLine_5 = re.search(r'\s*(.*)\(\s*function\s*\(\s*(.*)\s*\)\s*\{.*',
                                                                      tempJsLine)
                                        if functionOneLine_5:
                                            functionName = functionOneLine_5.group(1)
                                            arguments = functionOneLine_5.group(2)
                            else:
                                # ty.PublishersManager = function(){
                                functionOneLine_6 = re.search(r'\s*(.*)\s*=\s*function\s*\(\s*(.*)\s*\)\s*\{.*', tempJsLine)
                                if functionOneLine_6:
                                    # var sss = function(){
                                    functionOneLine_7 = re.search(r'\s*var\s*(.*)\s*=\s*function\s*\(\s*(.*)\s*\)\s*\{.*',
                                                                  tempJsLine)
                                    if functionOneLine_7:
                                        functionName = "var_" + functionOneLine_7.group(1)
                                        arguments = functionOneLine_7.group(2)
                                    else:
                                        functionName = functionOneLine_6.group(1)
                                        arguments = functionOneLine_6.group(2)
                    else:
                        functionOneLine_11 = re.search(r'\s*function\s*(.*)\s*\(\s*(.*)\s*\)\s*\{.*', tempJsLine)
                        if functionOneLine_11:
                            functionName = functionOneLine_11.group(1)
                            arguments = functionOneLine_11.group(2)
                    if functionName.strip() == '':
                        # function xx(){ 这样的全局函数。
                        jsLines.append(jsLine)
                        print "{0} _ {1} _ 类似全局函数，或者特殊写法，未添加log".format(fileShowName, jsLine.split('\n'[0]))
                    else:
                        # 去掉没过滤好的空格
                        functionName = functionName.strip()
                        # 拆分模式
                        replace = re.search(r'(.*function.*\(.*\).*\{)(.*)', jsLine)

                        # 整理参数-让参数 得以在运行时输出成对应值
                        argumentsStr = '{'
                        argumentsList = arguments.split(",")
                        for arg_i in range(len(argumentsList)):
                            argument = argumentsList[arg_i].strip()
                            if argument == '':
                                continue
                            else:
                                argumentsStr += '"' + argument + '":' + argument + ','
                        argumentsStr += '}'

                        # 折射全局对象名-全局函数的文件不输出js路径，而是输出自己的全局类名
                        className = ''
                        if _fileNameToObjNameBoo:
                            # 存在对应关系就转换
                            if fileShowName in _fileNameToObjName:
                                className = _fileNameToObjName[fileShowName]
                        # 函数名有 ' 的话,把 ' 转意了.
                        if functionName.find("\'") > 0:
                            functionName = string.join(functionName.split("'"), "\\\'")

                        # 是否需要过滤-运行时，取得这个作为参数，决定是否显示log
                        passBooStr = 'false'
                        if _justFilterLogsBoo:
                            # 只过滤
                            passBooStr = 'true'
                            if fileShowName in _filterLogsDict:
                                passBooStr = 'false'
                                print "{0} _ {1} _会输出".format(fileShowName, functionName)
                        else:
                            # 只显示
                            if passBooStr == 'false':
                                changeBoo = True
                                if fileShowName in _filterLogsDict:
                                    if functionName in _filterLogsDict[fileShowName]:
                                        changeBoo = False
                                if changeBoo == False:
                                    passBooStr = 'true'
                                    print "{0} _ {1} _输出被过滤".format(fileShowName, functionName)
                            if (fileShowName + ' -> ' + functionName) in _specialFuncLogs:
                                functionName = _specialFuncLogs[fileShowName + ' -> ' + functionName]
                        newJsLine = replace.group(1) + '\n' + '_global.log(' + passBooStr + ',\'' + fileShowName.ljust(
                            45) + '\',\'' + className.rjust(
                            25) + '\',\'' + functionName + '\',' + argumentsStr + ');\n' + replace.group(2)
                        # 修改后的
                        jsLines.append(newJsLine)
                else:
                    # 使用Function做正则表达式的行
                    jsLines.append(jsLine)
            else:
                # 非function行
                jsLines.append(jsLine)

        if (len(jsLines) != lineCount):
            print '识别行数与给定行数不一致 : {0} {1} - {2}'.format(fileShowName, len(jsLines), lineCount)
        else:
            # 如果存在任意一行的话
            if len(jsLines) > 0:
                jsLines[0] = jsLines[0].split('\n')[0] + '\n'
                jsLines.insert(0, addLogFun(_startLogCount, _endLogCount))
                jsCodeStr = string.join(jsLines, "")
                # 写一个新的
                FileReadWrite.writeFileWithStr(tarPath, jsCodeStr)

    print '共有 {0} 处function使用'.format(_funcLineCount)
