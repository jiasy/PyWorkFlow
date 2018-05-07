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

# 修改所需属性
opsDict = {}
opsDict["targetPicFolder"] = '图片路径'
opsDict["blankPicPath"] = '用来放缩的空白图'
opsDict["createPicFolder"] = '生成的图片放置到哪里'

# 将一个 ICON 变成不同大小，适合不同工程的一堆图标
# ------------------------------------测试用例---------------------------------------------------------------------------------------
if __name__ == '__main__':
    _ops = SysInfo.getOps(opsDict, OptionParser())
    _currentFolder = SysInfo.fixFolderPath(os.path.dirname(os.path.realpath(__file__)))
    # 重新创建输出文件夹
    FileReadWrite.reCreateFolder(_ops.createPicFolder)

    # png 路径集
    _pngList = FileReadWrite.getFilePathsByType(_ops.targetPicFolder, "png")

    for _i in range(len(_pngList)):
        _pngPath = _pngList[_i]
        if _pngPath.find(".meta") >= 0:
            continue
        # 有同名的文件就是大图用的plist
        _plistPath = SysInfo.getPathWithOutPostfix(_pngPath) + ".plist"
        # plist对应的大图，不要做替换
        if os.path.exists(_plistPath):
            continue
        # 拷贝到生成路径。
        _createPicPath = FileCopy.fileTransformWithFolderStructure(_pngPath, _ops.targetPicFolder, _ops.createPicFolder)
        # 用来替换的图片
        _im = Image.open(_ops.blankPicPath)
        # 获取要生成的图片的大小
        _createPic = Image.open(_pngPath)
        _w = _createPic.size[0]
        _h = _createPic.size[1]
        # 变成要替换图片的大小
        _out = _im.resize((_w, _h))

        # 写到要替换的路径
        _out.save(str(_createPicPath), "PNG")

# 以下是 网络截取的例子， https://blog.csdn.net/ln152315/article/details/42777149
# # coding=utf-8
# import Image
# import shutil
# import os
#
#
# class Graphics:
#     infile = 'D:\\myimg.jpg'
#     outfile = 'D:\\adjust_img.jpg'
#
#     @classmethod
#     def fixed_size(cls, width, height):
#         """按照固定尺寸处理图片"""
#         im = Image.open(cls.infile)
#         out = im.resize((width, height), Image.ANTIALIAS)
#         out.save(cls.outfile)
#
#     @classmethod
#     def resize_by_width(cls, w_divide_h):
#         """按照宽度进行所需比例缩放"""
#         im = Image.open(cls.infile)
#         (x, y) = im.size
#         x_s = x
#         y_s = x / w_divide_h
#         out = im.resize((x_s, y_s), Image.ANTIALIAS)
#         out.save(cls.outfile)
#
#     @classmethod
#     def resize_by_height(cls, w_divide_h):
#         """按照高度进行所需比例缩放"""
#         im = Image.open(cls.infile)
#         (x, y) = im.size
#         x_s = y * w_divide_h
#         y_s = y
#         out = im.resize((x_s, y_s), Image.ANTIALIAS)
#         out.save(cls.outfile)
#
#     @classmethod
#     def resize_by_size(cls, size):
#         """按照生成图片文件大小进行处理(单位KB)"""
#         size *= 1024
#         im = Image.open(cls.infile)
#         size_tmp = os.path.getsize(cls.infile)
#         q = 100
#         while size_tmp > size and q > 0:
#             print q
#             out = im.resize(im.size, Image.ANTIALIAS)
#             out.save(cls.outfile, quality=q)
#             size_tmp = os.path.getsize(cls.outfile)
#             q -= 5
#         if q == 100:
#             shutil.copy(cls.infile, cls.outfile)
#
#     @classmethod
#     def cut_by_ratio(cls, width, height):
#         """按照图片长宽比进行分割"""
#         im = Image.open(cls.infile)
#         width = float(width)
#         height = float(height)
#         (x, y) = im.size
#         if width > height:
#             region = (0, int((y - (y * (height / width))) / 2), x, int((y + (y * (height / width))) / 2))
#         elif width < height:
#             region = (int((x - (x * (width / height))) / 2), 0, int((x + (x * (width / height))) / 2), y)
#         else:
#             region = (0, 0, x, y)
#
#             # 裁切图片
#         crop_img = im.crop(region)
#         # 保存裁切后的图片
#         crop_img.save(cls.outfile)