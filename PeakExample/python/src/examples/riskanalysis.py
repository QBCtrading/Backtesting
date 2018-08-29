'''
Created on Feb 16, 2018

@author: pzhou
'''

import datetime
import pprint
import peakpy.peak as p
from examples.misc import curvePackName


class RiskAnalyzer(object):
    def __init__(self, anchorDate, curveTenors, curveRates):
        self.anchorDate = anchorDate
        self.curveTenors = curveTenors
        self.curveRates = curveRates
        self.indexId = None
        self.indexName = 'FR007'
        self.curveMethod = 'LinearZero'
        self.cfetsCurveName = 'CFETS_Curve_Test'
        self.swapCurveId = 'Swap_Curve_Test'
        self.discCurveName = 'CFETS_Disc_Curve_Test'
        self.curvePackName = 'CurvePack_Test'
        self.riskTenors = ["1W", "1M", "3M", "6M", "9M", "1Y", "2Y", "3Y", "4Y", "5Y", "6Y", "7Y", "8Y", "9Y", "10y"]

        
        self.contract = self.readSavedContract()
        
        self._addFR007IndexFixings()
    
    @classmethod
    def readPilotScopeIndexFixings(cls, name):
        f = open(name)
        try:
            headings = f.readline().split(',')
            indexCol = headings.index('symbol')
            dateCol = headings.index('business_date')
            rateCol = headings.index('rate')
            data = {}
            for line in (f):
                line = line.split(',')
                fixDate = line[dateCol]
                fixDate = datetime.datetime.strptime(fixDate, "%Y%m%d").date()
                data[fixDate] = float(line[rateCol])
        finally:
            f.close()
        return data
    
    @classmethod
    def readPeakIndexFixings(cls, name):
        f = open(name)
        try:
            headings = f.readline().split(',')
            data = {}
            for t in (f):
                fixDate, rate = t.split(',')
                data[int(fixDate)] = float(rate)/100.0
        finally:
            f.close()
        return data
    
    def _addFR007IndexFixings(self):
        # create a dummy swap, just to get the index object
        att = {'endDateTenor':'1Y', 'notional':50000000.0, 'fixedRate':0.035}
        dummyId = '_dummy'
        startDate = datetime.date(2017, 12, 1)
        p.py_CreateIRSwap(dummyId, {'PredefinedConvention':'CNY_REPO_7D'}, startDate, **att)
        info = p.py_SwapInfo([dummyId], 0, startDate)
        indexId = info['']['IndexObjectID']
#         print '\n\nIndex object Id: %s' % indexId
        self.indexId = indexId
    
        fixings = self.readPeakIndexFixings("../../data/fr007_fixing.csv")
#         print '\n\n%s fixings loaded' % len(fixings)
        
        rc = p.py_IndexAddFixings(indexId, fixings.keys(), fixings.values())
#         print '\nFixings added to %s' % rc

    def readSavedContract(self):
#         res = p.py_ObjectLoad("S:/Private/Ping.Zhou/Compass", "mma_fr007.bin.gz")
        res = p.py_ObjectLoad("S:/Public/TOPS", "20180309_ZQ_TFD002_A1_FR007.bin.gz")
        contractId = res[0]
        return contractId

    def _priceContract(self, contract, curve, ignoreTodayFixing=False, **kwargs):
        npv = p.py_SwapLegNPV([contract], curve, curve, forecastTodaysFixing=ignoreTodayFixing, **kwargs)
        print 'Swap NPV = %s' % npv
        return npv

    def _createCfetsCurve(self):
        curve = p.py_BuildCfetsCurve(self.cfetsCurveName, self.anchorDate, self.indexName, self.curveTenors, self.curveRates, self.curveMethod)
        print '\n\nCurve created: %s' % curve
        return curve

    def _createSwapCurve(self, curveTemplate='RISK', startTenors=[]):
        """
        create a Peak SwapCurve for calculation of risks.
        returns curveEngineName, curveName, discCurveName
        """
        rates = []
        rc = p.py_BuildSwapCurve(self.swapCurveId, self.anchorDate, self.indexName, self.riskTenors, rates, self.cfetsCurveName, self.discCurveName, startTenors=startTenors, template=curveTemplate)
        print '\n\nBuilt swap curve: '
        pprint.pprint(rc, width=500)
        curve, discCurve, curveEngineName = rc[0]
        return curveEngineName, curve, discCurve

    def _calculateRisk(self, curveTemplate='RISK', ignoreFixing=False, startTenors=[]):
        curveEngineName, indexCurveName, discCurveName = self._createSwapCurve(curveTemplate=curveTemplate, startTenors=startTenors)
        rc = p.py_BuildCurvePack(self.curvePackName, curveEngineName)
        print 'Built curve pack %s' % rc
    
        curveMap=[('Index', 'Curve'), ('_'+self.indexName, indexCurveName)]
        rc = p.py_CurvePackRisk(self.curvePackName, instrumentNames=[self.contract], curveMap=curveMap, discountCurveName=discCurveName, forecastTodaysFixing=ignoreFixing, showBasePv=True)
        pprint.pprint('\nCurvePackRisk:')
        pprint.pprint(rc)
        return rc

    def runParRisk(self):
        curve = self._createCfetsCurve()
        ignoreFixing = False
        pv = self._priceContract(self.contract, curve, ignoreTodayFixing=ignoreFixing)
        print 'PV=%s' % pv
        p.py_ObjectCopy(self.cfetsCurveName, self.discCurveName)
        startTenors = ['0D']
        self._calculateRisk(startTenors=startTenors, curveTemplate='RISK', ignoreFixing=ignoreFixing)

    def runIMMRisk(self):
        curve = self._createCfetsCurve()
        bucketDates = p.py_IMMNextDates(self.anchorDate, 40, '3M', datetime.date(2028, 12,23), 'CFFEX')
        print '\n\nIMM dates: '
        pprint.pprint(bucketDates)
        bucketDates = [self.anchorDate] + list(bucketDates)
        rc = p.py_BuildRPCurvePack(self.curvePackName, [curve, curve], bucketDates)
        print '\nBuilt RP curve pack: %s' % rc
        
        curveMap = curveMap=[('Index', 'Curve'), ('_'+self.indexName, curve)]
        rc = p.py_CurvePackRisk(self.curvePackName, instrumentNames=[self.contract], curveMap=curveMap, discountCurveName=curve, showBasePv=True)
        print '\nCurvePackRisk:'
        pprint.pprint(rc)
    
if __name__ == '__main__':
    bizDate = datetime.date(2018, 2, 28)
    tenors = ["1D", "1W", "1M", "3M", "6M", "9M", "1Y", "2Y", "3Y", "4Y", "5Y", "7Y", "10y"]
    rates = [0.0255, 0.030, 0.032177, 0.032263, 0.0331, 0.033724, 0.034273, 0.035496, 0.036543, 0.037503, 0.038259, 0.039168, 0.039613]
    riskRunner = RiskAnalyzer(bizDate, tenors, rates)
    riskRunner.runIMMRisk()
    
    