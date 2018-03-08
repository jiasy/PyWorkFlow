#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import re
import os
import json
import string
from subprocess import PIPE, Popen
reload(sys)
sys.setdefaultencoding('utf-8')

import xlrd
import xlsxwriter

import SysInfo


class WorkBook(object):
	def __init__(self):
		self.currentWorkBook = None
		self.readPath = None
		self.savePath = None
		self.sheetDict = {}

	def printSelf(self):
		print "WorkBook".ljust(20) + " : " + os.path.basename(self.readPath)
		print "  readForm".ljust(20) + " : " + self.readPath
		print "  writeTo".ljust(20) + " : " + self.savePath
		print "  sheets".ljust(20) + " -----------------------------------------"
		for _sheetName in self.sheetDict:
			self.getSheetByName(_sheetName).printSelf()

	def initBlankWorkBook(self):
		self.currentWorkBook = None

	def initWithWorkBook(self, filePath_):
		print("> WorkBook > initWithWorkBook : " + filePath_)
		if not os.path.isfile(filePath_):
			print 'ExcelUtils.WorkBook.initWithWorkBook 文件路径不存在 : ' + filePath_
			sys.exit()

		# 只读的那个
		self.currentWorkBook = xlrd.open_workbook(filePath_)

		# # Notice 
		# _typeDict = {}
		# _typeDict["currentWorkBook"] = self.currentWorkBook
		# self.currentWorkBook = _typeDict.get("currentWorkBook", xlrd.Workbook())

		_baseFileName = os.path.basename(filePath_)
		self.readPath = filePath_
		self.savePath = SysInfo.getPathWithOutPostfix(filePath_) + "_save.xlsx"

		for _sheetName in self.currentWorkBook.sheet_names():
			if isinstance(_sheetName, unicode):
				_sheetName = _sheetName.encode('utf-8')
			_currentSheet = Sheet()
			_currentSheet.initWithSheet(
				self.currentWorkBook.sheet_by_name(_sheetName),
				_sheetName
			)
			self.addSheet(_currentSheet)

	# search --------------------------------------------------------------------------------------------------------
	def getSheetByName(self, sheetName_):
		# # Notice 字典里取得对象,指定他的类型.
		# return self.sheetDict.get(sheetName_, SheetType)
		return self.sheetDict[sheetName_]

	# save ----------------------------------------------------------------------------------------------------------
	def save(self):
		self.saveToPath(self.savePath)

	def saveToPath(self, filePath_):
		self.getWriteWorkBook(filePath_).close()

	def getWriteWorkBook(self, savePath_):
		# 创建一个可写文件
		_writeWorkbook = xlsxwriter.Workbook(savePath_)
		# 循环 只读 的 workBook
		for _sheetName in self.sheetDict:
			# 在 写入 workBook 中 创建 写入Sheet
			_currentWriteSheet = _writeWorkbook.add_worksheet(_sheetName)
			# 读取一个 sheet
			_currentReadSheet = self.getSheetByName(_sheetName)
			# 将 只读文件的内容 拷贝 到 写入文件
			_currentReadSheet.copyToWriteSheet(_currentWriteSheet)
		return _writeWorkbook

	# change --------------------------------------------------------------------------------------------------------
	def addSheet(self, sheet_):
		if sheet_.sheetName in self.sheetDict:
			raise TypeError("WorkBook 中 已经存在 名称为 : " + sheet_.sheetName + " 的Sheet")
		else:
			self.sheetDict[sheet_.sheetName] = sheet_
		return sheet_


class Sheet(object):
	def __init__(self):
		# print "> > > >Sheet_init"
		self.sheetName = None
		self.cells = []
		self.maxCol = None
		self.maxRow = None
		# 一些附加数据
		self.data = None
		pass

	def printSelf(self):
		print "Sheet Name".ljust(20) + " : " + self.sheetName
		print "col : ".ljust(20) + str(self.maxCol)
		print "row : ".ljust(20) + str(self.maxRow)
		self.printSheet()

	# 初始化一个Sheet,利用一个读取到的Sheet来创建
	def initWithSheet(self, targetSheet_, sheetName_):
		# print("> > Sheet > initWithSheet")
		self.sheetName = sheetName_
		self.maxCol = targetSheet_.ncols
		self.maxRow = targetSheet_.nrows

		for _colNum in range(targetSheet_.ncols):
			self.cells.append([])
			for _rowNum in range(targetSheet_.nrows):
				_currentCell = Cell(targetSheet_.cell(_rowNum, _colNum).value, _colNum, _rowNum,
									crToPos(_colNum, _rowNum))
				self.cells[_colNum].append(_currentCell)

	# 利用名称,初始化一个空sheet
	def initWithName(self, sheetName_):
		# print("> > Sheet > initBlankSheet")
		self.sheetName = sheetName_
		self.maxCol = 0
		self.maxRow = 0

	# print------------------------------------------------------------------------------------------------------------
	def printSheet(self):
		print("> > Sheet > printSheet---------------" + self.sheetName + "---------------")
		_printStr = "<^> - " + str("").ljust(3) + " : "
		for _colNum in range(self.maxCol):
			_printStr+=str(_colNum)+"-"+cToPos(_colNum).ljust(10)+","
		print(_printStr)
		for _rownum in range(self.maxRow):
			self.printRow(_rownum)
		# for _colNum in range(self.maxCol):
		#	 self.printCol(_colNum)

	def printCol(self, col_):
		_printStr = "col - " + str(col_).ljust(3) + " : "
		_splitStr = ","
		for _row in range(self.maxRow):
			_printStr += self.cells[col_][_row].strValue.ljust(10) + _splitStr
		print _printStr

	def printRow(self, row_):
		_printStr = "row - " + str(row_).ljust(3) + " : "
		_splitStr = ","
		for _col in range(self.maxCol):
			_printStr += self.cells[_col][row_].strValue.ljust(10) + _splitStr
		print _printStr

	# search-----------------------------------------------------------------------------------------------------------
	def getCellsByStr(self, str_):
		# print("> > Sheet > getCrByStr : " + str_)
		_cellList = []
		# Notice string 和 unicode 相互转化
		# string -> unicode : s.decode
		# unicode -> string : u.encode
		_uniStr = str_.decode('utf-8')
		for _row in range(self.maxRow):
			for _col in range(self.maxCol):
				if self.cells[_col][_row].value == _uniStr:
					_cellList.append(self.cells[_col][_row])

		if len(_cellList) == 0:
			print "Sheet.getCrByStr " + str_ + " 不存在"

		return _cellList

	# get--------------------------------------------------------------------------------------------------------------
	def getStrByPos(self, posStr_):
		# print("> > Sheet > getStrByPos : " + posStr_)
		_col, _row = posToCr(posStr_)
		return self.getStrByCr(_col, _row)

	def getStrByCr(self, col_, row_):
		# print("> > Sheet > getStrByCr :  _c: " + str(col_) + " _r: " + str(row_))
		if row_ >= self.maxRow:
			raise TypeError("ExcelUtils.Sheet.getStrByPos posStr_ : " + str(row_) + " 行数越界 " + str(self.maxRow))
		if col_ >= self.maxCol:
			raise TypeError("ExcelUtils.Sheet.getStrByPos posStr_ : " + str(col_) + " 列数越界 " + str(self.maxCol))

		_backValue = self.cells[col_][row_].strValue
		# print "Sheet.getStrByCr  : " + _backValue

		return _backValue

	# set--------------------------------------------------------------------------------------------------------------
	def setStrToPos(self, str_, posStr_):
		_col, _row = posToCr(posStr_)
		self.setStrToCr(str_, _col, _row)

	def setStrToCr(self, str_, col_, row_):
		# print("> > Sheet > setStrToCr : " + str_ + " _c: " + str(col_) + " _r: " + str(row_))
		# 这里注意-有先后,先列拓展,后行拓展
		if col_ >= self.maxCol:
			self.extendCol(col_)
		if row_ >= self.maxRow:
			self.extendRow(row_)
		self.cells[col_][row_].write(str_)

	# copy-------------------------------------------------------------------------------------------------------------
	def copyToWriteSheet(self, writeSheet_):
		for _row in range(self.maxRow):
			for _col in range(self.maxCol):
				writeSheet_.write(_row, _col, self.cells[_col][_row].value)

	# extends----------------------------------------------------------------------------------------------------------
	def extendCol(self, col_):
		# 这里注意-有先后,先列拓展,后行拓展
		# print("> > Sheet > extendCol : " + str(col_))
		for _col in range(int(self.maxCol), int(col_ + 1)):
			print "_col : " + str(_col)
			self.cells.append([])
			for _row in range(self.maxRow):
				self.cells[_col].append(Cell("", _col, _row, crToPos(_col, _row)))
		self.maxCol = len(self.cells)
		# print("self.maxCol : " + str(self.maxCol))

	def extendRow(self, row_):
		# print("> > Sheet > extendRow")
		# 这里注意-有先后,先列拓展,后行拓展
		for _col in range(self.maxCol):
			for _row in range(int(self.maxRow), int(row_ + 1)):
				self.cells[_col].append(Cell("", _col, _row, crToPos(_col, _row)))

		self.maxRow = len(self.cells[self.maxCol - 1])
		# print("self.maxRow : " + str(self.maxRow))


class Cell(object):
	def __init__(self, value_, col_, row_, pos_):
		self.value = None
		self.strValue = None
		# 赋值
		self.write(value_)
		self.col = col_
		self.row = row_
		self.pos = pos_
		pass

	def __str__(self):
		return 'cell %s:%s p:%s v:%s' % (
			str(self.col).rjust(3), str(self.row).ljust(3), self.pos.ljust(5), self.strValue
		)

	def write(self, value_):
		self.value = value_
		self.strValue = SysInfo.convertToStr(self.value)


# 列名 数字 对应 关系
colNameList = [
	"a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
	"n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
	"aa", "ab", "ac", "ad", "ae", "af", "ag", "ah", "ai", "aj", "ak", "al", "am",
	"an", "ao", "ap", "aq", "ar", "as", "at", "au", "av", "aw", "ax", "ay", "az",
	"ba", "bb", "bc", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bk", "bl", "bm",
	"bn", "bo", "bp", "bq", "br", "bs", "bt", "bu", "bv", "bw", "bx", "by", "bz",
	"ca", "cb", "cc", "cd", "ce", "cf", "cg", "ch", "ci", "cj", "ck", "cl", "cm",
	"cn", "co", "cp", "cq", "cr", "cs", "ct", "cu", "cv", "cw", "cx", "cy", "cz",
]


# 列行 转换 格子 字符串
def crToPos(col_, row_):
	return str(colNameList[col_] + str(int(row_ + 1)))

# 列行 转换 格子 字符串
def cToPos(col_):
	return str(colNameList[col_])

# 格子 字符串 转换 列行
def posToCr(posStr_):
	_posStrMatch = re.search(r'([a-z]*)(\d+)', posStr_)
	if _posStrMatch:
		_colName = str(_posStrMatch.group(1))
		_rowNum = int(_posStrMatch.group(2))
		_colNum = colNameList.index(str(_colName).lower())
		_rowNum -= 1
		return _colNum, _rowNum
	else:
		raise TypeError("ExcelUtils.Sheet.getStrByPos posStr_ : " + posStr_ + " 参数不正确")


SheetType = Sheet()
