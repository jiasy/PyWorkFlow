#! /usr/bin/python   
# -*- coding: UTF-8 -*-  
# 递归将jsonA_内容覆盖到jsonB_中保存到jsonC中
# 如果jsonC没传,则保存到jsonB_中

import sys, os, re
import json


# 读取json文件到一个python对象中
def readJson(filePath_):
    _file = open(filePath_, 'r')
    json_info = json.loads(_file.read())
    _file.close()
    return json_info


# 将一个对象写入json
def writeJson(filePath_, data_):
    _file = open(filePath_, 'w')
    outStr = json.dumps(data_, ensure_ascii=False, sort_keys=True, indent=4)  # 处理完之后重新转为Json格式，并在行尾加上一个逗号
    _file.write(outStr.strip().encode('utf-8') + '\n')
    _file.close()


# 在这里递归替换
def mergeData(jsonA_, jsonB_):
    for _key in jsonA_:
        if type(jsonA_[_key]) == dict and jsonB_.has_key(_key) and type(jsonB_[_key]) == dict:
            mergeData(jsonA_[_key], jsonB_[_key])
        else:
            jsonB_[_key] = jsonA_[_key]


# jsonA_的内容会覆盖jsonB_的内容,然后保存在jsonC中
def jsonMerge(jsonA_, jsonB_, jsonC_):
    _objA = readJson(jsonA_)
    _objB = readJson(jsonB_)
    mergeData(_objA, _objB)
    writeJson(jsonC_, _objB)


if __name__ == '__main__':
    if len(sys.argv) <= 2:
        print 'jsonmerge:需要带jsonA_,jsonB_[,jsonC_] jsonA_的内容会覆盖jsonB_的内容,然后保存在jsonC_中'
    elif len(sys.argv) == 3:
        jsonMerge(sys.argv[1], sys.argv[2], sys.argv[2])
    elif len(sys.argv) >= 3:
        jsonMerge(sys.argv[1], sys.argv[2], sys.argv[3])
