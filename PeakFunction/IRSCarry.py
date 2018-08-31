# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 15:59:26 2018

@author: DUYONGLIANG366

"""


import peakHelper
import peakLib
import datetime
import pprint


peakHelper.initPeak()
indexName = "FR007"
anchorDate = datetime.date(2017, 11, 14)
startDate = datetime.date(2017, 11, 30)
swapId = "test"
rc = peakLib.py_SwapContract(swapId, indexName, startDate, settleDate='0D', maturity='5Y', notional=50000000.0, fixedRate=0.03)
print 'swap contract: ', rc


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

peakHelper.cleanupPeak()
    