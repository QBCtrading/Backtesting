'''
Created on Feb 16, 2018

@author: pzhou
'''

import datetime
import pprint
import peakpy.peak as p
        
def createSwap(swapId, startDate, term, fixRate, notional=100000000.0):
    '''Create a contract so that it has a payment endDate
    '''
    att = {'endDateTenor':term, 'notional':notional, 'fixedRate':fixRate}
    rc = p.py_CreateIRSwap(swapId, {'PredefinedConvention':'CNY_REPO_7D'}, startDate, **att)
    return rc

class PnlExplainer(object):
    def __init__(self, contract, endDate, startDate, tdayIndexMktData, pdayIndexMktData):
        self.contract = contract
        self.endDate = endDate
        self.startDate = startDate
        self.tdayMktData = tdayIndexMktData
        self.pdayMktData = pdayIndexMktData
        self.indexId = None
        self.indexName = 'FR007'
    
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
                data[int(fixDate)] = float(rate)
        finally:
            f.close()
        return data
    
    def _addFR007IndexFixings(self):
        # create a dummy contract, just to get the index object
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

    def getCurve(self, asofDate):
        return None
    
    def getSwapPV(self, asofDate):
        return None
    
    def _createCFETSCurve(self, curveName, asofDate, mktdata):
        tenors, rates = mktdata
        curve = p.py_BuildCfetsCurve(curveName, asofDate, self.indexName, tenors, rates, 'LinearZero')
#         print 'Curve created: %s' % curve

#        double check index fixings
#         rc = p.py_IndexFixings(self.indexId, [asofDate], fwdCurveId=curveName)
#         print 'Fixing on %s is %f' % (asofDate, rc[0])
        return curve

    def _priceContract(self, curve, forecastTodaysFixing=False, **kwargs):
        npv = p.py_SwapLegNPV([self.contract], curve, curve, forecastTodaysFixing=forecastTodaysFixing, **kwargs)
        print 'Swap NPV = %s' % npv
        return npv

    def _calculateRisk(self, curve, curveDate):
        tenors, rates = self.pdayMktData
        riskCurveId = '_risk_%s' % self.indexName
#         rc = p.py_BuildSwapCurve(riskCurveId, self.endDate, self.indexName, tenors, rates, curve, useExtCurveAsBase=False, template='RISK')
        rc = p.py_BuildSwapCurve(riskCurveId, curveDate, self.indexName, tenors, rates, curve)
        fwdCurveName, discCurveName, curveEngineName = rc[0]
        curvePackName = '_riskCurvePack_%s' % curveDate.strftime('%Y%m%d')
        rc = p.py_BuildCurvePack(curvePackName, curveEngineName)
        print 'Built curve pack %s' % rc
    
        curveMap=[('Index', 'Curve'), ('_'+self.indexName, fwdCurveName)]
        rc = p.py_CurvePackRisk(curvePackName, instrumentNames=[self.contract], curveMap=curveMap, discountCurveName=discCurveName, showBasePv=True)
#         print('\nCurvePackRisk:')
#         pprint.pprint(rc)
        return rc
    
    def getTotalPnl(self):
        '''calculate the pnl from previous day to endDate
        '''
        return None
    
    def getAmendmentPnl(self):
        return None
    
    def _calculateFixingPnl(self):
        '''price difference between with implied fixing for endDate and with actual fixing endDate
        '''
        return None
    
    def explainPnl(self):
        '''
        Steps: (calculate theta first, mktdata change second.
        1. Calculate beginning PV (pvEOD), with previous day date, curve, and with fixing
        2. Calculate endDate's PV (pvLast), with endDate's date, curve, and with fixing applied
        3. calculate total payments between previous and endDate by including past cash flows using endDate's curve
        4. calculate total pnl by subtracting the two PVs + payments
        5. Calculate pnl due to date change alone, theta. This is split into two parts
            5.1 on previous day's curve, calculate the pnl change due to one day's discount
            5.2 Build curve with endDate's date but with previous day's curve points, BOD curve
            5.3 Price contract with BOD curve (without fixing), but include payment
            5.4 The difference with EOD PV is theta
            5.5 Drift is theta subtracting the one day discount
        5. Price the contract again with the BOD curve, with fixing applied (if available), the PV difference is the fixing pnl
        6. Calculate pnl due to market data change
            6.1 Price the contract without payment using the BOD curve
            6.2 The difference between endDate's regular PV with this PV is the pnl due to mktdata change
        7. Calculate pnl estimate
            7.1 Calculate delta on BOD curve
            7.2 Multiply the delta by market data change from previous day to endDate
        8. Unexplained pnl = total pnl - mkt pnl - theta - fixing pnl
        
        The path from EOD PV to Last PV is:
        EOD PV --(date change)-> BOD PV --(apply fixing)-> --(apply mktdata change)-> Last PV 
        '''
        
        print '\n\nExplaining contract pnl from %s to %s' % (self.startDate, self.endDate)
        
        self._addFR007IndexFixings()

        # Calculate beginning PV, with previous day date, curve, and with fixing
        curveName = '%s_%s_%s' % (self.indexName, self.startDate.strftime('%Y%m%d'), self.startDate.strftime('%Y%m%d'))         
        curveEOD = self._createCFETSCurve(curveName, self.startDate, self.pdayMktData)
        rc = self._priceContract(curveEOD)
        pvEOD, fwdCurve, discCurve = rc[0]

        df = p.py_YieldTSDiscount(curveEOD, [self.endDate])
        df = df[0]
        print 'df is', df
        discount = pvEOD * (1.0/df - 1.0)
        print 'One day discount: %f' % discount

        #Calculate endDate's PV, with endDate's date, curve, and with fixing applied
        curveName = '%s_%s_%s' % (self.indexName, self.endDate.strftime('%Y%m%d'), self.endDate.strftime('%Y%m%d'))
        curveLast = self._createCFETSCurve(curveName, self.endDate, self.tdayMktData)
        rc = self._priceContract(curveLast) #without cash, with fixing
        pvLast, fwdCurve, discCurve = rc[0]
        
        #calculate total payments between previous and endDate by including past cash flows using endDate's curve
        rc = self._priceContract(curveLast, cfAfterDate=self.startDate, cfAfterDateInclusive=False)
        pvCash, _, _ = rc[0]
        payments = pvCash - pvLast
        print 'Payments between previous day (exc) and endDate (inc) is %s' % payments

        # total pnl
        pnlTotal = pvLast-pvEOD+payments

        #Calculate pnl due to date change alone
        #This is done by calculating the pv difference between previous day's curve points but on previous and endDate's date and regular pv         curveName = '%s_%s_%s' % (self.indexName, self.startDate.strftime('%Y%m%d'), self.endDate.strftime('%Y%m%d'))
        curveName = '%s_%s_%s' % (self.indexName, self.endDate.strftime('%Y%m%d'), self.startDate.strftime('%Y%m%d'))
        curveBOD = self._createCFETSCurve(curveName, self.endDate, self.pdayMktData)

        rc = self._priceContract(curveBOD, cfAfterDate=self.endDate, cfAfterDateInclusive=True, forecastTodaysFixing=True) # with payment
        pvBOD = rc[0][0]
        pnlTheta = pvBOD - pvEOD
        drift = pnlTheta - discount

        rc = self._priceContract(curveBOD, cfAfterDate=self.endDate, cfAfterDateInclusive=True, forecastTodaysFixing=False) # with fixing and payment
        pvBODwFixing = rc[0][0]
        pnlFixing = pvBODwFixing - pvBOD

        #Calculate pnl due to market data change
        #By calculating pv difference between using endDate's curve points and previous day's curve points, both on endDate
        rc = self._priceContract(curveBOD, cfAfterDate=self.endDate, cfAfterDateInclusive=False, forecastTodaysFixing=False)
        pvBODClean = rc[0][0] # without payment, with fixing applied
        pnlMktdata = pvLast - pvBODClean
#         print 'Pnl due to mktdata move alone: %f' % pnlMktdata
        
        #Calculate pnl estimate using delta and market data change    
        risk = self._calculateRisk(curveBOD, self.endDate)
        basePV = risk[1][-1]
        print 'PV from risk run: %.2d' % basePV
        riskVec = risk[2:]
        riskVec = [r[2] for r in riskVec] #for bp shift
        curveDates, curveRatesP = self.pdayMktData
        print 'curveDates is ', curveDates, 'curveRatesP is ', curveRatesP
        curveRatesT = self.tdayMktData[1]
        print 'curveRatesT is ', curveRatesT
        ratesDiff = [(rt-rp)*10000.0 for (rp, rt) in zip(curveRatesP, curveRatesT)] #in bp
        print 'ratesDiff is ', ratesDiff
        pnlEstimate = sum([r * dr for (r, dr) in zip(ratesDiff, riskVec)])
        print 'MktPnl and EstimatedPnl: ', ['{:,.2f}'.format(f) for f in (pnlMktdata, pnlEstimate)]

        # calculate unexplained pnl        
        unexplained = pnlTotal - pnlMktdata - pnlTheta - pnlFixing

        #tabulate results
        buckets = (pvEOD, pvLast, payments, pnlTotal, pnlMktdata, pnlEstimate, discount, drift, pnlFixing, unexplained)
        print ['SwapId', 'BegPV', 'EndPV', 'Payment', 'TotalPnl', 'MktPnl', 'EstPnl', 'Discount', 'Drift', 'FixingPnl', 'Unexplained']
        spec = ', '.join(['{%d:,.2f}' % i for i in range(len(buckets))])
        print self.contract, ', ', spec.format(*buckets)

def readSavedContract():
    res = p.py_ObjectLoad("S:/Private/Ping.Zhou/Compass", "mma_fr007.bin.gz")
    contractId = res[0]
    return contractId
        
def runPnlExplain():
    print '\n\nRunning Pnl Explain...'
    calendar = 'China.IB'

    contract = readSavedContract()
    
    pdayCurveTenors = ['1W', '1M', '3M', '6M', '9M', '1Y', '2Y', '3Y', '4Y', '5Y', '7Y', '10Y']
    pdayCurveRates  = [2.9, 3.2461, 3.295, 3.38, 3.4331, 3.4892, 3.6225, 3.7328, 3.8375, 3.9115, 3.985, 4.0375]
    pdayMktdata = [pdayCurveTenors, [t/100.0 for t in pdayCurveRates]]
    
    tdayCurveTenors = ['1W', '1M', '3M', '6M', '9M', '1Y', '2Y', '3Y', '4Y', '5Y', '7Y', '10Y']
    tdayCurveRates = [2.9, 3.2119, 3.275, 3.3746, 3.4325, 3.49, 3.6338, 3.743, 3.8476, 3.9236, 3.995, 4.0475]
    tdayMktdata = [tdayCurveTenors, [t/100.0 for t in tdayCurveRates]]

    today = datetime.date(2018, 3, 9)
    pday = today - datetime.timedelta(days=1)
    pday = p.py_CalendarAdjust(calendar, [pday], BusinessDayConvention='P')[0]
    pex = PnlExplainer(contract, today, pday, tdayMktdata, pdayMktdata)
    pex.explainPnl()
    
if __name__ == '__main__':
    runPnlExplain()
    
