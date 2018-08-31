# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import PeakQL as pk
import datetime

_holidays = 'D:\git_root\Backtesting\PeakData\ChinaHolidays.csv'
_workingWeekend = 'D:\git_root\Backtesting\PeakData\ChinaIBWorkingWeekends.csv'

def checkPeakErr(errVec):
    if errVec.size() > 0:
        raise Exception(errVec[0])

 
def loadHolidayCalendars(holidayFile=None, workingWeekendFile=None):
    import os
    errVec = pk.Str_Vec()
    dir = os.path.dirname(os.__file__) + os.path.sep
    if not holidayFile:
        holidayFile = dir + _holidays
    print '...Loading holidays from file %s...' % holidayFile
    try:
        f = open(holidayFile)
        data = f.read()
    finally:
        if f:
            f.close()

    pk.pk_LoadChinaHolidays(len(data), data, errVec)
    checkPeakErr(errVec)

    if not workingWeekendFile:
        workingWeekendFile = dir + _workingWeekend
    print '...Loading working weekends from file %s...' % workingWeekendFile
    try:
        f = open(workingWeekendFile)
        data = f.read()
    finally:
        if f:
            f.close()

    pk.pk_LoadChinaWorkingWkends(len(data), data, errVec)
    checkPeakErr(errVec)    
        

def initPeak():
    errVec = pk.Str_Vec(0)
    pk.pk_InitializeAddin(errVec)
    checkPeakErr(errVec)
    loadHolidayCalendars(_holidays, _workingWeekend)
    
def cleanupPeak():
    errVec = pk.Str_Vec(0)
    pk.pk_Cleanup(errVec)
    checkPeakErr(errVec)

    

def dateToPkDate(adate):
    if not adate:
        return pk.PkMissingDate
    temp = datetime.date(1899, 12, 30)    # Note, not 31st Dec but 30th!
    delta = adate - temp
    return delta.days

def pkDateToDate(pkdate):
    temp = datetime.date(1899, 12, 30)    # Note, not 31st Dec but 30th!
    return temp + datetime.timedelta(days=pkdate)

def dictToKeyValueVec(input):
    output = pk.KeyValue_Vec()
    for k,v in input.iteritems():
        output.append(pk.KeyValue_t(k, pk.Param_t(v)))
    return output

def pkKeyValueVecToDict(vec):
    output = dict()
    a = pk.KeyValue_Vec()
    return dict([(t.key, _paramToPyNative(t.value)) for t in vec])
    
def listToPkVec(alist, vecType=pk.Str_Vec):
    '''Take a list and convert into the few known Peak vectors based on the first element of the list
    '''
    if not alist:
        return vecType()
    a = type(alist[0])
    l = len(alist)
    if a is datetime.date:
        dateVec = pk.PkInt_Vec([dateToPkDate(t) for t in alist])
        return dateVec
    elif a in (int, long):
        vec = pk.PkInt_Vec(alist)
    elif a is str:
        vec = pk.Str_Vec(alist)
    elif a is bool:
        vec = pk.Bool_Vec(alist)
    elif a is float:
        vec = pk.Double_Vec(alist)
    else: #Assuming it's a Param_Vec
        vec = pk.Param_Vec(alist)
    return vec

def pkVecToList(pkVec):
    return list(pkVec)

def pkVecVecToMatrix(vecvec):
    return [(vec) for vec in vecvec]

def matrixToParamVecVec(matrix):
    return pk.Param_VecVec([[pk.Param_t(i) for i in o] for o in matrix])

def matrixToIntVecVec(matrix):
    return pk.Int_VecVec([[i for i in o] for o in matrix])

def matrixToStrVecVec(matrix):
    return pk.Str_VecVec([[i for i in o] for o in matrix])

def matrixToDoubleVecVec(matrix):
    return pk.Double_VecVec([[i for i in o] for o in matrix])

def paramToPyNative(param):
    pkTypes = ['Double', 'Long', 'String', 'Bool']
    methods = [('isDate', 'asInt')] + [('is'+t, 'as'+t) for t in pkTypes]
    for m in methods:
        if hasattr(param, m[0]) and getattr(param, m[0])():
            return getattr(param, m[1])()
    
def unpackVecVecResult(resultVecVec):
    result = []
    for row in resultVecVec:
        result.append(tuple(paramToPyNative(i) for i in row))
    return result
    
def unpackVecResult(resultVec):
    return tuple(paramToPyNative(i) for i in resultVec)

def unpackMatrix(matrix):
    '''unpacking tuple of tuple of Param_t
    '''
    return tuple(tuple(_paramToPyNative(i) for i in row) for row in matrix)

def unpackMatrix_Map(result):
    output = {}
    for k, v in result.iteritems():
        output[k] = _unpackMatrix(v)
    return output

initPeak()
print '...Peak initiated...'        