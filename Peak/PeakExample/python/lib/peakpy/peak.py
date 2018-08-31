'''
Created on Jan 12, 2018

@author: pzhou
'''

from PeakQL import *
from peakpy import dateToPkDate, pkDateToDate, _checkAndRaiseErr, _listToPkVec, _unpackVecResult, _unpackVecVecResult, _matrixToStrVecVec,\
    _matrixToDoubleVecVec, dictToKeyValueVec, _unpackMatrix_Map, _pkVecToList
import datetime

def py_ListCalendar():
    errVec = Str_Vec()
    result = Str_VecVec()
    rc = pk_ListCalendar(result, errVec)
    _checkAndRaiseErr(errVec)
    return tuple(tuple(i for i in row) for row in result)

def _py_CalendarHolidayList(calendar, fromDate, toDate, type):
    errVec = Str_Vec()
    result = PkInt_Vec()
    rc = pk_CalendarHolidayList(calendar, dateToPkDate(fromDate), dateToPkDate(toDate), type, result, errVec)
    _checkAndRaiseErr(errVec)
    return tuple(pkDateToDate(d) for d in result)

def py_CalendarHolidayList(calendar, fromDate, toDate):
    return _py_CalendarHolidayList(calendar, fromDate, toDate, 'H')

def py_CalendarWorkingWeekendList(calendar, fromDate, toDate):
    return _py_CalendarHolidayList(calendar, fromDate, toDate, 'W')

def py_CalendarAdvance(calendar, startDates, periods, BusinessDayConvention, endOfMonth):
    errVec = Str_Vec()
    result = PkInt_Vec()
    rc = pk_CalendarAdvance(calendar, _listToPkVec(startDates, vecType=int), _listToPkVec(periods), BusinessDayConvention, endOfMonth, result, errVec)
    _checkAndRaiseErr(errVec)
    return tuple(pkDateToDate(d) for d in result)

def py_FrequencyFromPeriod(periods):
    errVec = Str_Vec()
    result = Str_Vec()
    rc = pk_FrequencyFromPeriod(_listToPkVec(periods), result, errVec)
    _checkAndRaiseErr(errVec)
    return _pkVecToList(result)

def py_CalendarIsBusinessDay(calendar, days):
    errVec = Str_Vec()
    result = PkInt_Vec()
    rc = pk_CalendarIsBusinessDay(calendar, _listToPkVec(days, vecType=int), result, errVec)
    _checkAndRaiseErr(errVec)
    return tuple(bool(d) for d in result)

def py_DaysBetween(days1, days2, calendar):
    errVec = Str_Vec()
    result = PkInt_Vec()
    rc = pk_DaysBetween(_listToPkVec(days1, vecType=int), _listToPkVec(days2, vecType=int), calendar, result, errVec)
    _checkAndRaiseErr(errVec)
    return tuple(result)

def py_CalendarAdjust(calendar, dates, BusinessDayConvention):
    errVec = Str_Vec()
    result = PkInt_Vec()
    rc = pk_CalendarAdjust(calendar, _listToPkVec(dates, vecType=int), BusinessDayConvention, result, errVec)
    _checkAndRaiseErr(errVec)
    return tuple(pkDateToDate(d) for d in result)

def py_YieldTSDiscount(curveId, dates, allowExtrapolation=True):
    """
    Returns the discount factor from the given YieldTermStructure
    """
    result = Double_Vec()
    errVec = Str_Vec()
    rc = pk_YieldTSDiscount(curveId, _listToPkVec(dates, vecType=int), allowExtrapolation, result, errVec)
    _checkAndRaiseErr(errVec)
    return tuple(result)

def py_YieldTSForwardRate(curveId, beginDates, endDates, dayCounter, compounding='Simple', frequency='Annual', allowExtrapolation=True):
    """
    Returns the forward rate from the given YieldTermStructure
    """
    result = Double_Vec()
    errVec = Str_Vec()
    rc = pk_YieldTSForwardRate(curveId, _listToPkVec(beginDates, vecType=int), _listToPkVec(endDates, vecType=int), dayCounter, compounding, frequency, allowExtrapolation, result, errVec)
    _checkAndRaiseErr(errVec)
    return tuple(result)

def py_BuildSwapCurve(curveName, anchorDate, indexName, tenors, rates, extFwdCurve, extDiscCurve='', startTenors=[], useExtCurveAsBase=True, template=''):
    '''returns forwardCurveId, discountCurveId, curveEngineId
    '''
    result = Param_VecVec()
    errVec = Str_Vec()
    rc = pk_BuildSwapCurve(curveName, dateToPkDate(anchorDate), indexName, _listToPkVec(startTenors), _listToPkVec(tenors), _listToPkVec(rates, Double_Vec), 
                           extFwdCurve, extDiscCurve, result, errVec, useExtCurveAsBase, template)
    _checkAndRaiseErr(errVec)
    names = tuple(rc)
    return names, _unpackVecVecResult(result)
    
def py_BuildCfetsCurve(curveName, anchorDate, indexName, tenors, rates, method, discCurveName=''):
    errVec = Str_Vec()
    result = Param_VecVec() 
    rc = pk_BuildCfetsCurve(curveName, dateToPkDate(anchorDate), indexName, Str_Vec(tenors), Double_Vec(rates), method, discCurveName, result, errVec)
    _checkAndRaiseErr(errVec)
    return rc

def py_SwapContract(swapId, convention, anchorDate, settleDate, maturity, notional, fixedRate):
    '''convention is one of CNY_REPO_7D    CNY_SHIBOR_3M    CNY_SHIBOR_ON    CNY_DEPO_1Y
    '''
    errVec = Str_Vec()
    result = Param_VecVec()

    pk_SwapContract(swapId, convention, dateToPkDate(anchorDate), Param_t(settleDate), Param_t(maturity), notional, fixedRate, result, errVec)
    _checkAndRaiseErr(errVec)
    created = result[0]
    if created:
        created = created[0]
        if created.isString():
            created = created.asString()
    return created

def py_SwapLegNPV(swapId, forwardCurveId, discountCurveId, cfAfterDate=None, legNumber=PkMissingInt, cfAfterDateInclusive=False, forecastTodaysFixing=False, debugLevel=0):
    errVec = Str_Vec()
    result = Param_VecVec()
    cfAfterDate = dateToPkDate(cfAfterDate) if cfAfterDate else PkMissingDate
    rc = pk_SwapLegNPV(_listToPkVec(swapId), legNumber, forwardCurveId, discountCurveId, cfAfterDate, cfAfterDateInclusive, forecastTodaysFixing, debugLevel, result, errVec)
    _checkAndRaiseErr(errVec)
    return _unpackVecVecResult(result)

def py_SwapLegAnalysis(swapId, legNumber, afterDate, forwardCurveId, discountCurveId, afterDateInclusive=True, forecastTodaysFixing=True, useSqlFriendlyColHeaders=True, selectedColumns='All', toDate=None):
    errVec = Str_Vec()
    result = Param_VecVec()
    if isinstance(selectedColumns, str):
        selectedColumns = [selectedColumns]
    selectedColumns = _listToPkVec(selectedColumns)
    rc = pk_SwapLegAnalysis(swapId, legNumber, dateToPkDate(afterDate), forwardCurveId, discountCurveId, afterDateInclusive, forecastTodaysFixing, useSqlFriendlyColHeaders, selectedColumns, dateToPkDate(toDate), result, errVec)
    _checkAndRaiseErr(errVec)
    return _unpackVecVecResult(result)

def py_IMMDateToSymbol(date, twoDigitYear=True):
    errVec = Str_Vec()
    result = Str_Vec()
    rc = pk_IMMDateToSymbol(_listToPkVec(date), twoDigitYear, result, errVec)
    _checkAndRaiseErr(errVec)
    return tuple(result)

def py_IMMSymbolToDate(immCodes, refDate, rule='CFFEX'):
    '''Optional rule is one of 'CFFEX, 'CFFEXLT', 'INTERNATIONAL'
    '''
    errVec = Str_Vec()
    result = Param_Vec()
    if isinstance(immCodes, str):
        immCodes = [immCodes]
    immCodes = _listToPkVec(immCodes)
    if isinstance(refDate, datetime.date):
        refDate = [dateToPkDate(refDate)]
    if len(refDate) < immCodes.size():
        refDate += [refDate[-1]] * (immCodes.size() - len(refDate))
    refDate = _listToPkVec(refDate)
    pk_IMMSymbolToDate(immCodes, refDate, rule, result, errVec)
    _checkAndRaiseErr(errVec)
    result = _unpackVecResult(result)
    return tuple((pkDateToDate(i) for i in result))

def py_IMMNextDates(startDate, numOfDates, datePref, endDate, rule='CFFEX'):
    '''Optional rule is one of 'CFFEX, 'CFFEXLT', 'INTERNATIONAL'
    '''
    errVec = Str_Vec()
    dateResult = PkInt_Vec()
    symResult = Str_Vec()
    
    rc = pk_IMMNextDates(dateToPkDate(startDate), numOfDates, datePref, dateToPkDate(endDate), rule, dateResult, symResult, errVec)
    _checkAndRaiseErr(errVec)
    return tuple((pkDateToDate(i) for i in dateResult))

def py_RollCurve(curveId, newCurveId, newCurveDate):
    errVec = Str_Vec()
    rc = pk_RollCurve(curveId, newCurveId, dateToPkDate(newCurveDate), errVec)
    _checkAndRaiseErr(errVec)
    return rc

def py_IndexAddFixings(indexId, fixingDates, fixingValues):
    errVec = Str_Vec()
    rc = pk_IndexAddFixings(indexId, _listToPkVec(fixingDates), _listToPkVec(fixingValues), errVec)
    _checkAndRaiseErr(errVec)
    return rc

def py_IndexFixings(indexId, fixingDates, forecastToday=False, fwdCurveId=''):
    errVec = Str_Vec()
    result = Double_Vec()
    rc = pk_IndexFixings(indexId, _listToPkVec(fixingDates), forecastToday, fwdCurveId, result, errVec)
    _checkAndRaiseErr(errVec)
    return tuple(i for i in result)

def py_BuildCurvePack(curvePackName, curveEngineName, baseTargets=[], baseInstrumentNames=[], scenarioInstrumentNames=[], scenarioNames=[], scenarioTargets=[], scenariosAreRelative=False, deltaBumpSize=1.e-4, centralDifference=False, gammaMode='', targetChangeTolerance=0.0, mispriceTolerance=1.e-6, impliedFromTargetTolerance=0.0):
    errVec = Str_Vec()
    result = Param_VecVec() 
    rc = pk_BuildCurvePack(curvePackName, curveEngineName, _listToPkVec(baseTargets, Double_Vec), _listToPkVec(baseInstrumentNames), 
                           _listToPkVec(scenarioInstrumentNames), _listToPkVec(scenarioNames), _matrixToDoubleVecVec(scenarioTargets), scenariosAreRelative, 
                           deltaBumpSize, centralDifference, gammaMode, targetChangeTolerance, mispriceTolerance, impliedFromTargetTolerance, result, errVec)
    _checkAndRaiseErr(errVec)
    return _unpackVecVecResult(result)

def py_CurvePackRisk(curvePackName, instrumentNames, curveMap, discountCurveName, centralDifference=False, gammaMode='', riskMode='All', outputFormat='bt', forecastTodaysFixing=False, showBasePv=False):
    errVec = Str_Vec()
    result = Param_VecVec() 
    rc = pk_CurvePackRisk(curvePackName, _listToPkVec(instrumentNames), _matrixToStrVecVec(curveMap), discountCurveName, centralDifference, gammaMode, riskMode, outputFormat, forecastTodaysFixing, showBasePv, result, errVec)
    _checkAndRaiseErr(errVec)
    return _unpackVecVecResult(result)

def py_BuildRPCurvePack(curvePackName, curveNames, bucketDates, deltaBumpSize=0.0001, centralDifference=False, gammaMode=''):
    errVec = Str_Vec()
    result = Param_VecVec() 
    rc = pk_BuildRPCurvePack(curvePackName, _listToPkVec(curveNames), _listToPkVec(bucketDates), deltaBumpSize, centralDifference, gammaMode, result, errVec)
    _checkAndRaiseErr(errVec)
    return _unpackVecVecResult(result)[0][0]

def py_IndexName(indexId):
    errVec = Str_Vec()
    rc = pk_IndexName(indexId, errVec)
    _checkAndRaiseErr(errVec)
    return rc

def py_IndexGetFwdCurve(indexId, fwdCurveId=''):
    errVec = Str_Vec()
    rc = pk_IndexGetFwdCurve(indexId, fwdCurveId, errVec)
    _checkAndRaiseErr(errVec)
    return rc

def py_IndexSetFwdCurve(indexId, fwdCurveId):
    errVec = Str_Vec()
    rc = pk_IndexSetFwdCurve(indexId, fwdCurveId, errVec)
    _checkAndRaiseErr(errVec)
    return rc

def py_SwapInfo(objId, legNumber, asOfDate, resultFormat=''):
    resultMap = Matrix_Map()
    errVec = Str_Vec()
    rc = pk_SwapInfo(_listToPkVec(objId), legNumber, dateToPkDate(asOfDate), resultFormat, resultMap, errVec)
    _checkAndRaiseErr(errVec)
    result = _unpackMatrix_Map(resultMap)
    for k, v in result.iteritems():
        if len(v[0]) == 2:
            if v[0][0] == 'Key':
                result[k] = dict(v[1:])
        elif len(v) == 2:
            result[k] = dict(zip(v[0], v[1]))
    return result

def py_CreateIRSwap(swapId, conventions, asofDate, **att):
    errVec = Str_Vec()
    result = Param_VecVec()
#     att = {}
#     for k in ('startDate', 'fwdStartTenor', 'endDate', 'endDateTenor', 'notional', 'fixedRate', 
#               'floatSpread', 'discCurveId', 'fwdCurveId', 'firstStubDate', 'lastStubDate', 'addFixingDelayToStartDate'):
#         att[k] = attributes.get(k, None)
    conventions = dictToKeyValueVec(conventions)

    rc = pk_CreateIRSwap(swapId, conventions, dateToPkDate(asofDate), dateToPkDate(att.get('endDate', None)), 
            att.get('endDateTenor', ''), att.get('notional'), att.get('fixedRate'), att.get('floatSpread', 0.0), 
            att.get('discCurveId', ''), att.get('fwdCurveId', ''), dateToPkDate(att.get('firstStubDate', None)), dateToPkDate(att.get('lastStubDate', None)), 
            att.get('addFixingDelayToStartDate', True), result, errVec, att.get('fwdStartTenor', ''), att.get('resetFrequency', ''))

    _checkAndRaiseErr(errVec)
    return _unpackVecVecResult(result)

def py_ObjectPropertyNames(objId):
    errVec = Str_Vec()
    result = Str_Vec()
    rc = pk_ObjectPropertyNames(objId, result, errVec)
    _checkAndRaiseErr(errVec)
    return rc

def py_ObjectPropertyValues(objId, propertyName):
    errVec = Str_Vec()
    result = Str_Vec()
    rc = pk_ObjectPropertyValues(objId, propertyName, result, errVec)
    _checkAndRaiseErr(errVec)
    r = tuple(result)
    return r

def py_ObjectProperties(objId):
    props = py_ObjectPropertyNames(objId)
    if props:
        res = [(p, py_ObjectPropertyValues(objId, p)) for p in props]
        return dict(zip(res))
    else:
        return None

def py_BondFlowAnalysis(bondId, afterDate):
    errVec = Str_Vec()
    result = Param_VecVec()
    rc = pk_BondFlowAnalysis(bondId, dateToPkDate(afterDate), result, errVec)
    _checkAndRaiseErr(errVec)
    return _unpackVecVecResult(result)

def py_Schedule(scheduleId, startDate, endDate, tenor, calendar, bdc=PkMissingString, endDateBDC=PkMissingString, genRule=PkMissingString, endOfMonth=False, firstDate=PkMissingDate, nextToLastDate=PkMissingDate):
    errVec = Str_Vec()
    rc = pk_Schedule(scheduleId, dateToPkDate(startDate), dateToPkDate(endDate), tenor, calendar, bdc, endDateBDC, genRule, endOfMonth, firstDate, nextToLastDate, errVec)
    _checkAndRaiseErr(errVec)
    return rc

def py_FixedRateBond(objId, description, bondType, faceAmount, coupons, scheduleID, issueDate, paymentCalendar, currency='CNY', settlementDays=1, dayCounter='', paymentBDC='', redemption=PkMissingDouble, compounding=PkMissingString, exerDate=PkMissingDate):
    errVec = Str_Vec()
    type = ['IB', 'SSE', 'Custom'].index(bondType) + 1
    rc = pk_FixedRateBond(objId, description, currency, settlementDays, _listToPkVec(faceAmount, vecType=float), scheduleID, _listToPkVec(coupons, vecType=float), dayCounter, paymentBDC, redemption, dateToPkDate(issueDate), paymentCalendar, compounding, type, errVec, exerDate)
    _checkAndRaiseErr(errVec)
    return rc

def py_BondNextCashflowDate(bondId, settlementDate=None):
    errVec = Str_Vec()
    settlementDate = settlementDate or PkMissingDate
    rc = pk_BondNextCashflowDate(bondId, settlementDate, errVec)
    _checkAndRaiseErr(errVec)
    return pkDateToDate(rc)

def py_BondNextCashflowAmount(bondId, settlementDate=None):
    errVec = Str_Vec()
    settlementDate = settlementDate or PkMissingDate
    rc = pk_BondNextCashflowAmount(bondId, settlementDate, errVec)
    _checkAndRaiseErr(errVec)
    return rc

def py_BondAccruedAmount(bondId, settlementDate=None):
    errVec = Str_Vec()
    settlementDate = settlementDate or PkMissingDate
    rc = pk_BondAccruedAmount(bondId, settlementDate, errVec)
    _checkAndRaiseErr(errVec)
    return rc

def py_BondPV(bondIds, discontCurveId, spreadBps=[], indexCurveId='', toCleanPrice=False, settlementDate=None, scaleTo100=False):
    errVec = Str_Vec()
    settlementDate = settlementDate or PkMissingDate
    rc = pk_BondPV(bondIds, discontCurveId, _listToPkVec(spreadBps, vecType=float), indexCurveId, toCleanPrice, settlementDate, scaleTo100, errVec)
    _checkAndRaiseErr(errVec)
    return rc

def py_BondPVBP(bondId, bondYield, compounding, settlementDateIn, errVec, tradeDate, scaleByDirtyPrice):
    errVec = Str_Vec()
    rc = pk_BondPVBP(bondId, bondYield, compounding, settlementDateIn, errVec, tradeDate, scaleByDirtyPrice)
    _checkAndRaiseErr(errVec)
    return rc


def py_ObjectSave(objectList, filename, user='', compress=True, overwrite=True, includeGroups=True, recurisve=False):
    resultVec = Str_Vec()
    errVec = Str_Vec()
    rc = pk_ObjectSave(_listToPkVec(objectList), filename, user, compress, overwrite, includeGroups, recurisve, resultVec, errVec)
    _checkAndRaiseErr(errVec)
    result = _unpackVecResult(resultVec)
    return result
    
def py_ObjectLoad(directory, pattern='.*\.bin', recursive=False, overwrite=True, times=[], users=[], files=[]):
    resultVec = Str_Vec()
    errVec = Str_Vec()
    rc = pk_ObjectLoad(directory, pattern, recursive, overwrite, _listToPkVec(times), _listToPkVec(users), _listToPkVec(files), resultVec, errVec)
    _checkAndRaiseErr(errVec)
    result = tuple(resultVec)
    return result

def py_ObjectLoadFromBinary(length, data, times=[], users=[], files=[], prefix='', mode=0, suffix=''):
    resultVec = Str_Vec()
    errVec = Str_Vec()
    rc = pk_ObjectLoadFromBinary(length, data, _listToPkVec(times), _listToPkVec(users), _listToPkVec(files), resultVec, errVec, prefix, mode, suffix)
    _checkAndRaiseErr(errVec)
    result = tuple(resultVec)
    return result

def py_ObjectLoadFromFile(fileName):
    resultVec = Str_Vec()
    errVec = Str_Vec()
    try:
        file = open(fileName, 'rb')
        data = file.read()
    finally:
        if file:
            file.close()
    size = len(data)
    rc = py_ObjectLoadFromBinary(size, data)
    _checkAndRaiseErr(errVec)
    result = tuple(resultVec)
    return result

def py_ObjectCopy(oldId, newId):
    errVec = Str_Vec()
    rc = pk_ObjectCopy(oldId, newId, errVec)
    _checkAndRaiseErr(errVec)
    return rc

def py_DeleteAllObjects(deletePermanent=True):
    errVec = Str_Vec()
    rc = pk_DeleteAllObjects(deletePermanent, errVec)
    _checkAndRaiseErr(errVec)
    return rc

def py_DeleteObjects(objectIds):
    errVec = Str_Vec()
    rc = pk_DeleteObjects(_listToPkVec(objectIds), errVec)
    _checkAndRaiseErr(errVec)
    return rc

def py_CurveDates(curveId):
    result = PkInt_Vec()
    errVec = Str_Vec()
    rc = pk_CurveDates(curveId, result, errVec)
    _checkAndRaiseErr(errVec)
    return tuple(pkDateToDate(d) for d in result)
