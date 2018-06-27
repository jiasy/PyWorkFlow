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
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, os.pardir, "base")))
import FileCopy
import FileReadWrite
import SysInfo
import SysCmd

# 简化字符串 转换 成 类型全字符串
def csTypeChange(key_,csTypeName_):
    if csTypeName_ == "none":
        return 'none'
    elif csTypeName_ == "cli":
        return 'cli'
    elif csTypeName_ == "ser":
        return 'ser'
    elif csTypeName_ == "both":
        return 'both'
    else :
        raise TypeError('ERROR ProtoCreator csTypeChange : ' + key_ + " : " + csTypeName_ + ' 必须是 cli / ser / both / none 中的一个')

# 简化字符串 转换 成 类型全字符串
def protoTypeChange(key_,protoTypeName_):
    if protoTypeName_ == "req":
        return 'required'
    elif protoTypeName_ == "opt":
        return 'optional'
    elif protoTypeName_ == "rep":
        return 'repeated'
    else :
        raise TypeError('ERROR ProtoCreator protoTypeChange : '+key_+" : "+protoTypeName_+' 必须是 req / opt / rep 中的一个')

# 简化字符串 转换 成 类型全字符串
def dataTypeChange(key_,dataTypeName_):
    if dataTypeName_ == "i32":
        return 'int32'
    elif dataTypeName_ == "i64":
        return 'int64'
    elif dataTypeName_ == "str":
        return 'string'
    elif dataTypeName_ == "bo":
        return 'bool'
    else :
        raise TypeError('ERROR ProtoCreator dataTypeChange : '+key_+" : "+dataTypeName_+' 必须是 i32 / i64 / str / bo 中的一个')

# dataObject_ 数据对象
# listParameterName_ 数据对象中要替换的列表字段名
# parameterName_ 对象要挂载字符串名
# templateStr_ 模板字符串
def replaceTempletWithListObject(dataObject_,listParameterName_,parameterName_,templateStr_):
    # 循环字符串
    _loopReplaceStr = ""
    # 取得列表
    _dataList =  dataObject_[listParameterName_]
    for _idx in range(len(_dataList)):
        # 每一要替换的数据
        _data = _dataList[_idx]
        # 替换后的字符串
        _replaceStr = replaceTemplet(_data,templateStr_)
        # 合并到循环字符串上
        _loopReplaceStr = _loopReplaceStr + _replaceStr
    # 将合并后的字符串挂载到对象上
    dataObject_[parameterName_] = _loopReplaceStr

# dataObject_ 数据对象
# templateStr_ 模板字符串
def replaceTemplet(dataObject_,templateStr_):
    _replaceStr = templateStr_
    for _key in dataObject_:
        _replaceStr = _replaceStr.replace("${" + _key + "}", str(dataObject_[_key]))
    return _replaceStr

# 修改所需属性
opsDict = {}
opsDict["jsonPath"] = 'json 路径'
opsDict["analyseName"] = '要解析的名'
opsDict["protoTemplatePath"] = '.proto 模板'
opsDict["outputProtoPath"] = '根据.proto 生成 .pb .lua'

# jsonPath 中的 一级 目录 为 模块，二级 目录 为 模块内的一个协议，三级 目录 为 每一个游戏的初始值
#     Login
#         Login_Ins            模块 内存数据
#             GameA.json           每个数列会生成一个数据源
#             GameB.json           要解析那个数据源，把目标名称传递进来
#         Login_User           用户 存储数据
#         Login_Auth_Req       用户 验证 请求
#         Login_Auth_Res       用户 验证 返回
# ------------------------------------测试用例---------------------------------------------------------------------------------------
if __name__ == '__main__':
    _ops = SysInfo.getOps(opsDict, OptionParser())
    _currentFolder = SysInfo.fixFolderPath(os.path.dirname(os.path.realpath(__file__)))
    # 重新 创建 生成目录
    FileReadWrite.reCreateFolder(_ops.outputProtoPath)
    # 文件循环，取得
    _jsonPathList = []
    _filters = [".json"]
    FileReadWrite.gci(_ops.jsonPath, _filters, _jsonPathList)
    # 模块数据收集
    _moudleInfos = {}
    for _i in range(len(_jsonPathList)):
        _jsonPath = _jsonPathList[_i]
        if _jsonPath.find(_ops.analyseName + ".json") > 0:
            _subJsonPath = _jsonPath.split(_ops.jsonPath)[1]
            _jsonDict = FileReadWrite.dictFromJsonFile(_jsonPath)
            # 取得模块名
            _moudleNameArr = _subJsonPath.split("/")
            _moudleProtoName = _moudleNameArr[0]
            _moudleProtoBlockName = _moudleNameArr[1]
            # 创建 模块数据
            if _moudleInfos.has_key(_moudleProtoName) == False:
                _moudleInfos[_moudleProtoName] = {}
                _moudleInfos[_moudleProtoName]['blockList'] = []
                _moudleInfos[_moudleProtoName]['protoBlock_Loop'] = ""
            # 模块中的协议块
            _moudleProtoBlock = {}
            _moudleProtoBlock['lineList'] = []
            _moudleProtoBlock['protoLine_Loop'] = ""
            _moudleProtoBlock['protoBlockName'] = _moudleProtoBlockName
            _moudleInfos[_moudleProtoName]['blockList'].append(_moudleProtoBlock)
            _moudleInfos[_moudleProtoName]["moudleName"] = _moudleProtoName

            _count = 0
            # 协议快中的行块
            for _key in _jsonDict:
                _count = _count + 1
                # 字段名称
                #     cli_req_str_downUrl
                #     req_str_clientVersion
                #     both_opt_i32_sex
                #     ser_req_i32_userMax
                _keyArr = str(_key).split("_")
                # 三个的话，需要自己补充一个
                if len(_keyArr) == 3:
                    _keyArr.insert(0, "none")
                elif len(_keyArr) == 4:
                    _keyArr = _keyArr
                else:
                    raise TypeError('ERROR ProtoCreator 参数字段名称，必须是 三段 或者 四段')
                # 参数字典，需要转换一下
                _moudleProtoLine = {}
                _moudleProtoLine["csType"] = csTypeChange(_key,_keyArr[0])
                _moudleProtoLine["protoType"] = protoTypeChange(_key,_keyArr[1])
                _moudleProtoLine["dataType"] = dataTypeChange(_key,_keyArr[2])
                _moudleProtoLine["key"] = _keyArr[3]
                _moudleProtoLine["value"] = _jsonDict[_key]
                _moudleProtoLine["count"] = _count
                _moudleProtoBlock['lineList'].append(_moudleProtoLine)

    # print "_moudleInfo = " + str(json.dumps( _moudleInfos, indent=4, sort_keys=False, ensure_ascii=False))

    # 模板字符串获取
    _protoTemplateStr      = FileReadWrite.contentFromFile(os.path.join(_ops.protoTemplatePath, "proto.templete"))
    _protoBlockTemplateStr = FileReadWrite.contentFromFile(os.path.join(_ops.protoTemplatePath, "protoBlock.templete"))
    _protoLineTemplateStr  = FileReadWrite.contentFromFile(os.path.join(_ops.protoTemplatePath, "protoLine.templete"))

    # 模块名列表
    moudleNameList = []
    # 对每一个模块进行proto生成
    for _moudleProtoName in _moudleInfos:
        # print "_moudleProtoName = " + str(_moudleProtoName) +" ----------------------------------------------------------"
        _moudleInfo =  _moudleInfos[_moudleProtoName]
        _blockList = _moudleInfo['blockList']
        for _i in range(len(_blockList)):
            _block = _blockList[_i]
            # 循环 lineList 字段，用 _protoLineTemplateStr 模板 进行替换，放置到 protoLine_Loop 字段中
            replaceTempletWithListObject(_block, 'lineList', 'protoLine_Loop', _protoLineTemplateStr)
        # 循环 blockList 字段，用 _protoBlockTemplateStr 模板 进行替换，放置到 protoBlock_Loop 字段中
        replaceTempletWithListObject(_moudleInfo, 'blockList', 'protoBlock_Loop', _protoBlockTemplateStr)
        _moudleStr = replaceTemplet(_moudleInfo,_protoTemplateStr)
        # 记录模块名
        moudleNameList.append(_moudleInfo['moudleName'])
        FileReadWrite.writeFileWithStr(_ops.outputProtoPath+"/"+ moudleNameList[len(moudleNameList)-1] +".proto",_moudleStr)

    # proto -> pb -> lua  -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    # proto -> pb
    for _i in range(len(moudleNameList)):
        _moudleName = moudleNameList[_i]
        _protoToPbCommond = 'protoc --descriptor_set_out ' + _moudleName + '.pb ' + _moudleName + '.proto'
        _cmd = 'cd ' + _ops.outputProtoPath + " && " + _protoToPbCommond + " && cd "+_currentFolder
        print "_cmd = " + str(_cmd)
        SysCmd.doShellGetOutPut(_cmd)

    # # proto -> lua
    # for _i in range(len(moudleNameList)):
    #     _moudleName = moudleNameList[_i]
    #     _protoToPbCommond = 'protoc --lua_out=./ ./' + _moudleName + '.proto'
    #     _cmd = 'cd ' + _ops.outputProtoPath + " && " + _protoToPbCommond
    #     print "_cmd = " + str(_cmd)
    #     SysCmd.doShellGetOutPut(_cmd)