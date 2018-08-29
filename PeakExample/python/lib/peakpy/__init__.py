import PeakQL as pk
import datetime

_holidays = '../../data/ChinaHolidays.csv'
_workingWeekend = '../../data/ChinaIBWorkingWeekends.csv'

def _checkAndRaiseErr(errVec):
    if errVec.size() > 0:
        raise Exception(errVec[0])

def _initPeak():
    errVec = pk.Str_Vec()
    pk.pk_InitializeAddin(errVec)
    _checkAndRaiseErr(errVec)

    import os
    dir = os.path.dirname(__file__) + os.path.sep

    fname = dir+_holidays
    print '...Loading holidays from file %s...' % fname
    try:
        f = open(fname)
        data = f.read()
    finally:
        if f:
            f.close()
    pk.pk_LoadChinaHolidays(len(data), data, errVec)
    _checkAndRaiseErr(errVec)

    fname = dir+_workingWeekend
    print '...Loading working weekends from file %s...' % fname
    try:
        f = open(fname)
        data = f.read()
    finally:
        if f:
            f.close()
    pk.pk_LoadChinaWorkingWkends(len(data), data, errVec)
    _checkAndRaiseErr(errVec)

def _cleanupPeak():
    errVec = pk.Str_Vec()
    pk.pk_Cleanup(errVec)
    _checkAndRaiseErr(errVec)

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
    
def _listToPkVec(alist, vecType=pk.Str_Vec):
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

def _pkVecToList(pkVec):
    return list(pkVec)

def _pkVecVecToMatrix(vecvec):
    return [(vec) for vec in vecvec]

def _matrixToParamVecVec(matrix):
    return pk.Param_VecVec([[pk.Param_t(i) for i in o] for o in matrix])

def _matrixToIntVecVec(matrix):
    return pk.Int_VecVec([[i for i in o] for o in matrix])

def _matrixToStrVecVec(matrix):
    return pk.Str_VecVec([[i for i in o] for o in matrix])

def _matrixToDoubleVecVec(matrix):
    return pk.Double_VecVec([[i for i in o] for o in matrix])

def _paramToPyNative(param):
    pkTypes = ['Double', 'Long', 'String', 'Bool']
    methods = [('isDate', 'asInt')] + [('is'+t, 'as'+t) for t in pkTypes]
    for m in methods:
        if hasattr(param, m[0]) and getattr(param, m[0])():
            return getattr(param, m[1])()
    
def _unpackVecVecResult(resultVecVec):
    result = []
    for row in resultVecVec:
        result.append(tuple(_paramToPyNative(i) for i in row))
    return result
    
def _unpackVecResult(resultVec):
    return tuple(_paramToPyNative(i) for i in resultVec)

def _unpackMatrix(matrix):
    '''unpacking tuple of tuple of Param_t
    '''
    return tuple(tuple(_paramToPyNative(i) for i in row) for row in matrix)

def _unpackMatrix_Map(result):
    output = {}
    for k, v in result.iteritems():
        output[k] = _unpackMatrix(v)
    return output

_initPeak()
print '...Peak initiated...'
