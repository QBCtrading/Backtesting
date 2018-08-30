# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 15:59:26 2018

@author: DUYONGLIANG366
"""

import PeakQL as pk
import peakHelper
import peakLib
import datetime

def main():
    peakHelper.initPeak()
    indexName = "FR007"
    startDate = datetime.date(2018, 8, 30)
    swapId = "test"
    rc = peakLib.py_SwapContract(swapId, indexName, startDate, settleDate='0D', maturity='5Y', notional=50000000.0, fixedRate=0.03)
    print 'swap contract: ', rc

    peakHelper.cleanupPeak()
    