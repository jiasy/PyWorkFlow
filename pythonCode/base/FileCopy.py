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

from SysInfo import os_is_win32
from SysInfo import os_is_32bit_windows
from SysInfo import os_is_mac
from SysInfo import os_is_linux
from SysInfo import add_path_prefix
from SysInfo import getParentPath
from SysInfo import getBaseName
from FileReadWrite import writeFileWithStr

# 单一文件，按照相对文件路径平移
def filTransformWithFolderStructure(sourceFilePath_,sourceMainFolderPath_,targetMainFolderPath_):
    sourceMainFolderPath_ = SysInfo.add_path_prefix(sourceMainFolderPath_)
    targetMainFolderPath_ = SysInfo.add_path_prefix(targetMainFolderPath_)
    # 相对路径
    _relativeFolderPath = getRelativePath(sourceMainFolderPath_,sourceFilePath_)
    _fileName = None
    # 不是一个文件夹，就取得它的上一级文件夹路径
    if not os.path.isdir(_relativeFolderPath):
        _fileName = os.path.basename(_relativeFolderPath)
        _relativeFolderPath = os.path.dirname(_relativeFolderPath)
        
    # 平移结构后的文件夹目录结构
    _targetFolderPath = SysInfo.add_path_prefix((targetMainFolderPath_+_relativeFolderPath).replace('//','/'))
    
    # 路径不存在的话，就创建这个路径
    if not os.path.exists(_targetFolderPath):
        os.makedirs(_targetFolderPath)
    # 如果是一个文件的话，进行实际的拷贝
    if _fileName:
        _sourceFilePath = sourceFilePath_
        _targetFilePath = os.path.join(_targetFolderPath,_fileName)
        shutil.copy(_sourceFilePath,_targetFilePath)
        # 返回拷贝后的路径
        return _targetFilePath
    else:
        # 返回文件夹目录
        return _targetFolderPath


def folderBackUp(folderPath_):
    # 上层路径
    _folderParentPath = getParentPath(folderPath_)

    _backUpPath = os.path.join(_folderParentPath, getBaseName(folderPath_) + "_backUp")
    # 有备份
    if os.path.exists(_backUpPath):
        # 没有源，有可能删了。【代码执行错误的时候，会删除源，因为，源会变】
        if not os.path.exists(folderPath_):
            # 将备份 同步给 源
            shutil.copytree(_backUpPath, folderPath_)
            print "备份文件，拷贝回源路径"
        # 源里没有 创建备份的标示。
        if not os.path.isfile(folderPath_ + '/backup_created'):
            # 删除 原有备份
            shutil.rmtree(_backUpPath)
            # 新备份
            shutil.copytree(folderPath_, _backUpPath)
            # 标记已经备份过了
            writeFileWithStr(folderPath_ + '/backup_created', 'backup end')
        else:
            print "已经创建过备份了"
    else:
        # 没备份文件 - 就备份一份
        shutil.copytree(folderPath_, _backUpPath)
        # 标记已经备份过了
        writeFileWithStr(folderPath_ + '/backup_created', 'backup end')


# 文件夹 同结构拷贝
def copy_files_with_config_base(suffix_, src_root, dst_root, log_):
    _configObject = {}
    _configObject["from"] = ""
    _configObject["to"] = ""
    _configObject["include"] = []
    _suffixList = suffix_.split(",")
    for _i in range(len(_suffixList)):
        _configObject["include"].append("*." + _suffixList[_i] + "$")
    copy_files_with_config([_configObject], src_root, dst_root, log_)


# 根据配置结构拷贝
def copy_files_with_config(config, src_root, dst_root, log_):
    for _i in range(len(config)):
        copy_files_with_config_single(config[_i], src_root, dst_root, log_)


# 拷贝文件---------------------------------------------------------------------------------------
def copy_files_in_dir(src, dst, log_):
    for item in os.listdir(src):
        path = os.path.join(src, item)
        if os.path.isfile(path):
            path = add_path_prefix(path)
            copy_dst = add_path_prefix(dst)
            shutil.copy(path, copy_dst)
            if log_:
                print "---File Copy---"
                print "		src : " + path
                print "		tar : " + copy_dst
        if os.path.isdir(path):
            new_dst = os.path.join(dst, item)
            if not os.path.isdir(new_dst):
                os.makedirs(add_path_prefix(new_dst))
            copy_files_in_dir(path, new_dst, log_)


def copy_files_with_config_single(config, src_root, dst_root, log_):
    src_dir = config["from"]
    dst_dir = config["to"]
    src_dir = os.path.join(src_root, src_dir)
    dst_dir = os.path.join(dst_root, dst_dir)
    include_rules = None
    if "include" in config:
        include_rules = config["include"]
        include_rules = convert_rules(include_rules)

    exclude_rules = None
    if "exclude" in config:
        exclude_rules = config["exclude"]
        exclude_rules = convert_rules(exclude_rules)

    copy_files_with_rules(
        src_dir, src_dir, dst_dir, log_, include_rules, exclude_rules)


def copy_files_with_rules(src_rootDir, src, dst, log_, include=None, exclude=None):
    if os.path.isfile(src):
        if not os.path.exists(dst):
            os.makedirs(add_path_prefix(dst))
        copy_src = add_path_prefix(src)
        copy_dst = add_path_prefix(dst)
        shutil.copy(copy_src, copy_dst)
        return

    if (include is None) and (exclude is None):
        if not os.path.exists(dst):
            os.makedirs(add_path_prefix(dst))
        copy_files_in_dir(src, dst, log_)
    elif (include is not None):
        # have include
        for name in os.listdir(src):
            abs_path = os.path.join(src, name)
            rel_path = os.path.relpath(abs_path, src_rootDir)
            if os.path.isdir(abs_path):
                sub_dst = os.path.join(dst, name)
                copy_files_with_rules(
                    src_rootDir, abs_path, sub_dst, log_, include=include)
            elif os.path.isfile(abs_path):
                if _in_rules(rel_path, include):
                    if not os.path.exists(dst):
                        os.makedirs(add_path_prefix(dst))

                    abs_path = add_path_prefix(abs_path)
                    copy_dst = add_path_prefix(dst)
                    shutil.copy(abs_path, copy_dst)
    elif (exclude is not None):
        # have exclude
        for name in os.listdir(src):
            abs_path = os.path.join(src, name)
            rel_path = os.path.relpath(abs_path, src_rootDir)
            if os.path.isdir(abs_path):
                sub_dst = os.path.join(dst, name)
                copy_files_with_rules(
                    src_rootDir, abs_path, sub_dst, exclude=exclude)
            elif os.path.isfile(abs_path):
                if not _in_rules(rel_path, exclude):
                    if not os.path.exists(dst):
                        os.makedirs(add_path_prefix(dst))

                    abs_path = add_path_prefix(abs_path)
                    copy_dst = add_path_prefix(dst)
                    shutil.copy(abs_path, copy_dst)


def _in_rules(rel_path, rules):
    import re
    ret = False
    path_str = rel_path.replace("\\", "/")
    for rule in rules:
        if re.match(rule, path_str):
            ret = True
    return ret


def convert_rules(rules):
    ret_rules = []
    for rule in rules:
        ret = rule.replace('.', '\\.')
        ret = ret.replace('*', '.*')
        ret = "%s" % ret
        ret_rules.append(ret)
    return ret_rules


# ------------------------------------测试用例---------------------------------------------------------------------------------------
if __name__ == '__main__':
    # s source
    # t target
    opts, args = getopt.getopt(sys.argv[1:], "hs:t:c:")
    _sourceFolder = None
    _targetFolder = None
    _configPath = None
    for _op, _value in opts:
        if _op == "-s":
            _sourceFolder = _value
        elif _op == "-t":
            _targetFolder = _value
        elif _op == "-c":
            _configPath = _value
