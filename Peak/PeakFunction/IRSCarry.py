# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 15:59:26 2018

@author: DUYONGLIANG366

"""


import peakHelper
import peakLib
import datetime as dt
import pprint

    
def getSwapFairRate(SwapIndex, swapMaturityTenor, forwardCurveId, discountCurveId, forecastTodaysFixing=False):
    swapContractId = SwapIndex + "_" + swapMaturityTenor
    existed = peakLib.py_ObjectExists(swapContractId)
    if existed == False:
        anchorDate = dt.date.today()
        settleDate='0D'
        rc = peakLib.py_SwapContract(swapContractId, SwapIndex, anchorDate, settleDate, swapMaturityTenor, notional=10000.0, fixedRate=0.03)
        
    fairRate = peakLib.py_VanillaSwapFairRate([swapContractId], [forwardCurve], [discCurve], forecastTodaysFixing)
    print '\nSwap FairRate = %s' % fairRate

peakHelper.initPeak()
indexName = "FR007"
anchorDate = dt.date(2017, 11, 14)
startDate = dt.date(2017, 11, 30)
swapId = "test"
rc = peakLib.py_SwapContract(swapId, indexName, startDate, settleDate='0D', maturity='5Y', notional=10000.0, fixedRate=0.03)
print 'swap contract: ', rc

existed = peakLib.py_ObjectExists(rc)
existed == False

curveName = "cfets_FR007"
indexName = "FR007"
tenors = ["1d", "7d", "1M", "3M", "6M", "1Y", "5Y", "10y"]
rates = [0.030, 0.030, 0.032, 0.033, 0.034, 0.037, 0.040, 0.045]
curveResult = peakLib.py_BuildSwapCurve(curveName, anchorDate, indexName, tenors, rates, "")
print '\n\nBuilt swap curve: '
pprint.pprint(curveResult, width=500)

forwardCurve, discCurve, curveEngineName = curveResult[0]

npv = peakLib.py_SwapLegNPV([swapId], forwardCurve, discCurve)
print '\nSwap NPV = %s' % npv

fairRate = peakLib.py_VanillaSwapFairRate([swapId], [forwardCurve], [discCurve], forecastTodaysFixing=False)
print '\nSwap FairRate = %s' % fairRate

getSwapFairRate("FR007", "5y", forwardCurve, discCurve, False)

peakHelper.cleanupPeak()
    