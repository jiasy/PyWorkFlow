# -*- coding=utf-8 -*-
'''
Created on 2016年6月29日

@author: jiasy
'''


def convertToStr(object_):
    if isinstance(object_, float) or isinstance(object_, int) or isinstance(object_, bool):
        return str(object_)
    elif isinstance(object_, unicode):
        return object_.decode('utf-8')
    elif isinstance(object_, str):
        return object_
    elif isinstance(object_, NoneType):
        return "< NoneType >"


def dump(obj_):
    repr(obj_)
