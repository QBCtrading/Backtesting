# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 15:59:26 2018

@author: DUYONGLIANG366
"""

import PeakQL as pk
import Helper
import datetime as dt

def py_SwapContract(swapId, convention, anchorDate, settleDate, maturity, notional, fixedRate):
    '''convention is one of CNY_REPO_7D    CNY_SHIBOR_3M    CNY_SHIBOR_ON    CNY_DEPO_1Y
    '''
    errVec = pk.Str_Vec()
    result = pk.Param_VecVec()

    pk.pk_SwapContract(swapId, convention, Helper.dateToPkDate(anchorDate), pk.Param_t(settleDate), pk.Param_t(maturity), notional, fixedRate, result, errVec)
    Helper.checkPeakErr(errVec)
    created = result[0]
    if created:
        created = created[0]
        if created.isString():
            created = created.asString()
    return created

def main():
    Helper.initPeak()
    indexName = "FR007"
    startDate = datetime.date(2018, 8, 30)
    swapId = "test"
    rc = py_SwapContract(swapId, indexName, startDate, settleDate='0D', maturity='5Y', notional=50000000.0, fixedRate=0.03)
    print 'swap contract: ', rc

    Helper.cleanupPeak()
    