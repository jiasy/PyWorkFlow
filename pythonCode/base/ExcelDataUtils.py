#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

import json
import string

import FileReadWrite
import ExcelUtils

import os


# 将Excel生成json格式，通过缩进判断归属，通过key来判断类型。
# 将Json文件转换回Excel。
class DataObject(object):
    def __init__(self):
        self.dataJsonStr = None
        self.dataObject = None
        self.dataType = None
        pass

    def initWithJson(self, jsonStr_):
        self.dataType = "json"
        self.dataObject = strToObj(jsonStr_)
        self.dataJsonStr = objToStr(self.dataObject, True)

    def initWithJsonFile(self, jsonFilePath_):
        if not os.path.isfile(jsonFilePath_):
            print 'ExcelJsonUtils.DataObject.initWithJsonFile 文件路径不存在 : : ' + jsonFilePath_
            sys.exit()

        self.dataType = "json"
        self.dataObject = strToObj(FileReadWrite.contentFromFile(jsonFilePath_))
        self.dataJsonStr = objToStr(self.dataObject, True)

    def initWithExcelWorkBook(self, excelWorkBook_):
        # 创建数据对象
        self.dataObject = {}
        self.dataType = "excel"
        # 将每一个Sheet作为一个列表,写入数据对象.
        for _sheetName in excelWorkBook_.sheetDict:
            # 列表式上面是字段名
            if str(_sheetName).find("l") == 0:
                self.dataObject[_sheetName] = self.excelSheetToListData(
                    excelWorkBook_.getSheetByName(_sheetName)
                )
            elif str(_sheetName).find("d") == 0:
                self.dataObject[_sheetName] = self.excelSheetToDictData(
                    excelWorkBook_.getSheetByName(_sheetName)
                )
            else:
                raise TypeError('sheet 命名\n list 列表类 l 起始\n dict 字典类 d 起始\n非以上命名规则无法识别')

        self.dataJsonStr = objToStr(self.dataObject, True)

    def initWithExcelFile(self, excelFilePath_):
        if not os.path.isfile(excelFilePath_):
            print 'ExcelJsonUtils.DataObject.initWithExcelFile 文件路径不存在 : : ' + excelFilePath_
            sys.exit()
        self.dataType = "excel"
        # 读取Excel
        _excelWorkBook = ExcelUtils.WorkBook()
        _excelWorkBook.initWithWorkBook(excelFilePath_)
        self.initWithExcelWorkBook(_excelWorkBook)

    def excelSheetToDictData(self, sheet_):
        # sheet_是一个字典
        # 靠缩进来进行json的属性归属
        # 数据的字段名必须进行类型指定,这样方面识别
        # 从上向下,进行一次路径识别,确保字典和列表的字段名站整个一行
        for _currentRow in range(sheet_.maxRow):
            for _currentCol in range(sheet_.maxCol):
                # 当前的字段名,字典和列表,字段名后面不可以有任何字符串
                if self.getCellStructureData(sheet_, _currentCol, _currentRow):
                    # 得到了,这一行就结束了
                    break
                # 是数据项,那它右面的第一项就是数据,<再往右面就全都是空>
                elif self.getCellParData(sheet_, _currentCol, _currentRow):
                    # 得到了,这一行就结束了
                    break
        # 开始组装
        _dictData = {}

        for _currentRow in range(sheet_.maxRow):
            _cell = sheet_.cells[0][_currentRow]
            if sheet_.cells[0][_currentRow].strValue:
                if hasattr(_cell, 'data'):
                    _cellData = _cell.data
                    # 如果当前是个数据
                    if self.isParNameData(_cellData["parName"]):
                        _dictData[_cellData["parName"]] = _cellData["value"]
                    elif self.isParNameStructure(_cellData["parName"]):
                        # 字典
                        if _cellData["type"] == "d":
                            _dictData[_cellData["parName"]] = dict(self.structDict(_cell))
                        # 列表
                        elif _cellData["type"] == "l":
                            _dictData[_cellData["parName"]] = list(self.structList(_cell))

    def structDict(self, cell_):
        _dictData = {}
        for _cell in cell_.data.cellList:
            _cellData = _cell.data
            if _cellData:
                # 如果当前是个数据
                if self.isParNameData(_cellData["parName"]):
                    _dictData[_cellData["parName"]] = _cellData["value"]
                elif self.isParNameStructure(_cellData["parName"]):
                    # 字典
                    if _cellData["type"] == "d":
                        _dictData[_cellData["parName"]] = dict(self.structDict(_cell))
                    # 列表
                    elif _cellData["type"] == "l":
                        _dictData[_cellData["parName"]] = list(self.structList(_cell))
        return _dictData

    def structList(self, cell_):
        _listData = []
        for _cell in cell_.data.cellList:
            _cellData = _cell.data
            if _cellData:
                # 如果当前是个数据,数组的数据名称没有实际意义,就是个数据类型的标示
                if self.isParNameData(_cellData["parName"]):
                    _listData.append(_cellData["value"])
                elif self.isParNameStructure(_cellData["parName"]):
                    # 字典
                    if _cellData["type"] == "d":
                        _listData.append(dict(self.structDict(_cell)))
                    # 列表
                    elif _cellData["type"] == "l":
                        _listData.append(list(self.structList(_cell)))
        return _listData

    # cell里面是一个数据名,那么取得它的数据信息并且返回
    def getCellParData(self, sheet_, col_, row_):
        _getBoo = False
        _cellStr = sheet_.getStrByCr(col_, row_)
        # 当前的字段名,字典和列表,字段名后面不可以有任何字符串
        if self.isParNameData(_cellStr):
            # 获取格子
            _cell = sheet_.cells[col_][row_]
            # 格子中写入数据
            _dataInfo = {}
            _dataInfo["parName"] = _cellStr
            _dataInfo["type"] = _cellStr[0:1]
            if _dataInfo["type"] == "i":
                _dataInfo["value"] = float(sheet_.getStrByCr(col_ + 1, row_))
            elif _dataInfo["type"] == "f":
                _dataInfo["value"] = float(sheet_.getStrByCr(col_ + 1, row_))
            elif _dataInfo["type"] == "b":
                _cellValue = sheet_.getStrByCr(col_ + 1, row_)
                if _cellValue == 1.0 or _cellValue.lower() == "t" or _cellValue.lower() == "true" or _cellValue == "1":
                    _dataInfo["value"] = True
                elif _cellValue == 0.0 or _cellValue.lower() == "f" or _cellValue.lower() == "false" or _cellValue == "0":
                    _dataInfo["value"] = True
                else:
                    raise TypeError(ExcelUtils.crToPos(col_, row_) + " 所在为一个Boolean值,只能是1/0 true/false t/f 中的一个")

            elif _dataInfo["type"] == "u" or _dataInfo["type"] == "t" or _dataInfo["type"] == "s":
                _dataInfo["value"] = str(sheet_.getStrByCr(col_ + 1, row_))

            _cell.data = _dataInfo
            # <再往后都是空白><但是可能往后超过了列数限制-判断一下>
            if (int(col_ + 2) < sheet_.maxCol):
                # 当前行向后找
                for _currentValueCol in range(col_ + 2, sheet_.maxCol):
                    # 如果出现不为空的格子,报错
                    if not (sheet_.getStrByCr(_currentValueCol, row_) == ""):
                        raise TypeError(ExcelUtils.crToPos(_currentValueCol, row_) + " 不能有值,因为 " \
                                        + ExcelUtils.crToPos(col_, row_) + " 是一个数据")
            _getBoo = True
            print "data : " + str(_dataInfo)
        return _getBoo

    # cell里面是一个结构名,获取它所持有的数据
    def getCellStructureData(self, sheet_, col_, row_):
        _getBoo = False
        _cellStr = sheet_.getStrByCr(col_, row_)
        # 当前的字段名,字典和列表,字段名后面不可以有任何字符串
        if self.isParNameStructure(_cellStr):

            # 获取它的结构
            # 格子中写入数据
            _dataInfo = {}
            _dataInfo["parName"] = _cellStr
            _dataInfo["type"] = _cellStr[0:1]
            # 先存cell,然后按照类型组装成dict/list.遍历过程只负责关联,并不组装
            _dataInfo["cellList"] = []

            # 向下找,找到下一个数据/结构,确定它将持有多少行
            _rangeRow = row_
            # 它的左下方任意一个格子有值都是它的数据的结构截止点
            for _currentValueCol in range(col_ + 1):
                if row_ < sheet_.maxRow:
                    for _currentValueRow in range(row_ + 1, sheet_.maxRow):
                        if sheet_.getStrByCr(_currentValueCol, _currentValueRow) != "":
                            _rangeRow = _currentValueRow
                            break
            # 等同于初始.证明找到底了都没找到.那就是到底为范围
            if _rangeRow == row_:
                _rangeRow = sheet_.maxRow

            if row_ < sheet_.maxRow:
                # 关联的子属性,从下一列开始,因为它自己就是结构了,所以它关联的都是他的属性
                for _currentValueRow in range(row_ + 1, _rangeRow):
                    if sheet_.getStrByCr(col_ + 1, _currentValueRow) != "":
                        _dataInfo["cellList"].append(sheet_.cells[col_ + 1][_currentValueRow])

            # 当前行向后找
            for _currentValueCol in range(col_ + 1, sheet_.maxCol):
                # 如果出现不为空的格子,报错
                if not (sheet_.getStrByCr(_currentValueCol, row_) == ""):
                    raise TypeError(ExcelUtils.crToPos(_currentValueCol, row_) + " 不能有值,因为 " \
                                    + ExcelUtils.crToPos(col_, row_) + " 是一个列表命名/字典命名")
            _getBoo = True
            print "struc : " + str(_dataInfo)
        return _getBoo

    def excelSheetToListData(self, sheet_):
        # sheet 是一个列表.
        # "a1"中文名 中文名称 [0,0],[1,0]~[maxCol,0] 开始就是 中文名
        # "a2"字段名 英文名称 [0,1],[1,1]~[maxCol,1] 开始就是 英文名
        # "a3"序号 数据起始  [0,2] ,[1,2]~[maxCol,2] 开始就是提第一条数据的每一项
        # 依次类推       [1,maxRow]~[maxCol,maxRow] 就是数据的最后一项
        if sheet_.getStrByPos("a1") == "中文名":
            if sheet_.getStrByPos("a2") == "字段名":
                _list = []
                # 先获取字段名称
                _parameterNames = []
                for _col in range(1, sheet_.maxCol):
                    _parameterNames.append(self.isParNameLegal(sheet_.getStrByCr(_col, 1)))

                for _row in range(2, sheet_.maxRow):
                    # 创建数据对象
                    _dataObject = {}
                    for _col in range(1, sheet_.maxCol):
                        # 识别一行数据,按照第二行的字段名进行写入
                        _dataObject[_parameterNames[_col - 1]] = sheet_.getStrByCr(_col, _row)
                    # 将数据添加到列表
                    _list.append(_dataObject)
                return _list
            else:
                print "ERROR 作为 list 结构的Excel数据源，a2 内的字符串必须是 \"字段名\""
        else:
            print "ERROR 作为 list 结构的Excel数据源，a1 内的字符串必须是 \"中文名\""
        raise TypeError("ExcelUtils.Sheet.toListData : 固定格式的Excel才能调用这个方法\na1=中文名\na2==字段名\na3开始为序号")

    def isParNameLegal(self, parameterName_):
        # 判断一个参数的命名是否符合命名规范.
        # 是数据: t 时间 , s 字符串 , u 唯一确定 , i 整形 , f 浮点 , b 布尔
        # 是结构: d 字典 , l 列表
        if (
                (not self.isParNameData(parameterName_))
                and
                (not self.isParNameStructure(parameterName_))
        ):
            raise TypeError('字段名称必须是t,s,u,i,f,b,d,l中的一个,当前字段名为 : ' + parameterName_)
        else:
            return parameterName_

    # 属性名是一个数据
    def isParNameData(self, parameterName_):
        # t 时间 , s 字符串 , u 唯一确定 , i 整形 , f 浮点 , b 布尔
        if (
                str(parameterName_).find("t") == 0
                or
                str(parameterName_).find("s") == 0
                or
                str(parameterName_).find("u") == 0
                or
                str(parameterName_).find("i") == 0
                or
                str(parameterName_).find("f") == 0
                or
                str(parameterName_).find("b") == 0
        ):
            return True
        else:
            return False

    # 属性名是一个结构
    def isParNameStructure(self, parameterName_):
        # d 字典 , l 列表
        if (
                (str(parameterName_).find("d") == 0)
                or
                (str(parameterName_).find("l") == 0)
        ):
            return True
        else:
            return False

    def printSelf(self):
        print(
            "Data : ----------------- {0}\nSource:\n  {1}\nObject:\n  {2}\nSturcture:\n{3}\n".format(
                self.dataType, self.dataJsonStr, self.dataObject, self.getDAtaStructure()
            )
        )

    # 将自己写入路径
    def writeJsonToFile(self, filePath_):
        FileReadWrite.writeFileWithStr(filePath_, self.dataJsonStr)

    def getDAtaStructure(self, withValue_=False):
        _strList = []
        self.structureCreate(self.dataObject, "", _strList, withValue_)
        return string.join(_strList, "\n")

    # 获取当前的数据结构<数组的结构,以数组第一项为准>
    def structureCreate(self, obj_, lv_, strList_, withValue_):
        lv_ += '  '
        if isinstance(obj_, list):
            strList_.append(lv_ + '[')
            self.structureCreate(obj_[0], lv_, strList_, withValue_)
            strList_.append(lv_ + ']')
            return
        if not (lv_ == ""):
            lv_ += "|"
        for _key in obj_:
            if isinstance(obj_[_key], dict):
                strList_.append(lv_ + _key)
                self.structureCreate(obj_[_key], lv_, strList_, withValue_)
            elif isinstance(obj_[_key], list):
                strList_.append(lv_ + _key)
                self.structureCreate(obj_[_key], lv_, strList_, withValue_)
            else:
                if withValue_:
                    strList_.append(
                        lv_ + str(_key).ljust(10) + ":" + str(obj_[_key]).ljust(10) + str(type(obj_[_key])))
                else:
                    strList_.append(lv_ + _key)

    def dataToExcel(self, type_):
        # TODO 按照自己数据的结构输出Excel
        print "todo"


def objToStr(obj_, format_):
    if format_:
        return json.dumps(obj_, ensure_ascii=False, indent=4).encode('utf-8')
    else:
        # TODO 输出没有格式化的json字符串
        return json.dumps(obj_, ensure_ascii=False, indent=4).encode('utf-8')


def strToObj(str_):
    return json.loads(str_)
