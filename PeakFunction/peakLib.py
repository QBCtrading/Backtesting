# -*- coding: utf-8 -*-
"""
Created on Fri Aug 31 00:55:03 2018

@author: du
"""

import PeakQL as pk
import peakHelper
import datetime

def py_SwapContract(swapId, convention, anchorDate, settleDate, maturity, notional, fixedRate):
    '''convention is one of CNY_REPO_7D    CNY_SHIBOR_3M    CNY_SHIBOR_ON    CNY_DEPO_1Y
    '''
    errVec = pk.Str_Vec()
    result = pk.Param_VecVec()

    pk.pk_SwapContract(swapId, convention, peakHelper.dateToPkDate(anchorDate), pk.Param_t(settleDate), pk.Param_t(maturity), notional, fixedRate, result, errVec)
    peakHelper.checkPeakErr(errVec)
    created = result[0]
    if created:
        created = created[0]
        if created.isString():
            created = created.asString()
    return created

def py_SwapInfo(objId, legNumber, asOfDate, resultFormat=''):
    resultMap = pk.Matrix_Map()
    errVec = pk.Str_Vec()
    rc = pk.pk_SwapInfo(peakHelper.listToPkVec(objId), legNumber, peakHelper.dateToPkDate(asOfDate), resultFormat, resultMap, errVec)
    peakHelper.checkPeakErr(errVec)
    result = peakHelper.unpackMatrix_Map(resultMap)
    for k, v in result.iteritems():
        if len(v[0]) == 2:
            if v[0][0] == 'Key':
                result[k] = dict(v[1:])
        elif len(v) == 2:
            result[k] = dict(zip(v[0], v[1]))
    return result


def py_BuildSwapCurve(curveName, anchorDate, indexName, tenors, rates, extFwdCurve, extDiscCurve='', startTenors=[], useExtCurveAsBase=True, template=''):
    '''returns forwardCurveId, discountCurveId, curveEngineId
    '''
    result = pk.Param_VecVec()
    errVec = pk.Str_Vec()
    rc = pk.pk_BuildSwapCurve(curveName, peakHelper.dateToPkDate(anchorDate), indexName, peakHelper.listToPkVec(startTenors), peakHelper.listToPkVec(tenors), peakHelper.listToPkVec(rates, pk.Double_Vec), 
                           extFwdCurve, extDiscCurve, result, errVec, useExtCurveAsBase, template)
    peakHelper.checkPeakErr(errVec)
    names = tuple(rc)
    return names, peakHelper.unpackVecVecResult(result)

def py_SwapLegNPV(swapId, forwardCurveId, discountCurveId, cfAfterDate=None, legNumber=PkMissingInt, cfAfterDateInclusive=False, forecastTodaysFixing=False, debugLevel=0):
    errVec = pk.Str_Vec()
    result = pk.Param_VecVec()
    cfAfterDate = peakHelper.dateToPkDate(cfAfterDate) if cfAfterDate else pk.PkMissingDate
    rc = pk.pk_SwapLegNPV(peakHelper.listToPkVec(swapId), legNumber, forwardCurveId, discountCurveId, cfAfterDate, cfAfterDateInclusive, forecastTodaysFixing, debugLevel, result, errVec)
    peakHelper.checkPeakErr(errVec)
    return peakHelper.unpackVecVecResult(result)

def py_SwapLegAnalysis(swapId, legNumber, afterDate, forwardCurveId, discountCurveId, afterDateInclusive=True, forecastTodaysFixing=True, useSqlFriendlyColHeaders=True, selectedColumns='All', toDate=None):
    errVec = pk.Str_Vec()
    result = pk.Param_VecVec()
    if isinstance(selectedColumns, str):
        selectedColumns = [selectedColumns]
    selectedColumns = peakHelper.listToPkVec(selectedColumns)
    rc = pk.pk_SwapLegAnalysis(swapId, legNumber, peakHelper.dateToPkDate(afterDate), forwardCurveId, discountCurveId, afterDateInclusive, forecastTodaysFixing, useSqlFriendlyColHeaders, selectedColumns, peakHelper.dateToPkDate(toDate), result, errVec)
    peakHelper.checkPeakErr(errVec)
    return peakHelper.unpackVecVecResult(result)

def py_IndexAddFixings(indexId, fixingDates, fixingValues):
    errVec = pk.Str_Vec()
    rc = pk.pk_IndexAddFixings(indexId, peakHelper.listToPkVec(fixingDates), peakHelper.listToPkVec(fixingValues), errVec)
    peakHelper.checkPeakErr(errVec)
    return rc