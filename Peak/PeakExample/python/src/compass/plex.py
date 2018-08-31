'''
Created on Feb 16, 2018

@author: pzhou
'''

import datetime
import pprint
import peakpy.peak as p
from peakpy.peak import py_ObjectCopy
        
def createSwap(swapId, startDate, term, fixRate, notional=100000000.0):
    '''Create a contract so that it has a payment endDate
    '''
    att = {'endDateTenor':term, 'notional':notional, 'fixedRate':fixRate}
    rc = p.py_CreateIRSwap(swapId, {'PredefinedConvention':'CNY_REPO_7D'}, startDate, **att)
    return rc
        
class PnlExplainer(object):
    # for EOD mode where curves are created from market data points
    def __init__(self, indexName, startDate, endDate, startIndexMktData=None, endIndexMktData=None, 
                 discIndex=None, startDiscMktData=None, endDiscMktData=None,
                 startIndexCurve=None, startDiscCurve=None, endIndexCurve=None, endDiscCurve=None, 
                 riskTenors=None, riskStartTenors=None, riskRates=[]):
        self.indexName = indexName
        self.startDate = startDate
        self.endDate = endDate
        self.eodIndexCurve = startIndexCurve
        self.eodDiscCurve = startDiscCurve
        self.liveIndexCurve = endIndexCurve
        self.liveDiscCurve = endDiscCurve
        
        if startIndexMktData:
            # EOD CFETS curves
            curveName = '%s_%s_%s' % (self.indexName, self.startDate.strftime('%Y%m%d'), self.startDate.strftime('%Y%m%d'))
            self.eodIndexCurve = self._createCFETSCurve(curveName, self.indexName, self.startDate, startIndexMktData)
            if discIndex and startDiscMktData:
                discCurveName = '__disc_%s_%s_%s' % (discIndex, self.startDate.strftime('%Y%m%d'), self.startDate.strftime('%Y%m%d'))
                self.eodDiscCurve = self._createCFETSCurve(discCurveName, discIndex, self.startDate, startDiscMktData)
            elif not discIndex or discIndex == self.indexName: # discount curve is the same as index curve
                discCurveName = '__disc_%s_%s_%s' % (self.indexName, self.startDate.strftime('%Y%m%d'), self.startDate.strftime('%Y%m%d'))
                self.eodDiscCurve = py_ObjectCopy(self.eodIndexCurve, discCurveName)
            else:
                raise RuntimeError("Starting discount curve specification error. Don't know how to proceed")
            
            bodCurveName = '%s_%s_%s' % (self.indexName, self.endDate.strftime('%Y%m%d'), self.startDate.strftime('%Y%m%d'))         
            bodDiscCurveName = '__disc_%s_%s_%s' % (discIndex, self.endDate.strftime('%Y%m%d'), self.startDate.strftime('%Y%m%d'))         
            self.bodIndexCurve = self._createCFETSCurve(bodCurveName, self.indexName, self.endDate, startIndexMktData)
            self.bodDiscCurve = self._createCFETSCurve(bodDiscCurveName, discIndex, self.endDate, startDiscMktData or startIndexMktData)

        if not self.liveIndexCurve and endIndexMktData:
            # live CFETS curves
            curveName = '%s_%s_%s' % (self.indexName, self.endDate.strftime('%Y%m%d'), self.endDate.strftime('%Y%m%d'))
            self.liveIndexCurve = self._createCFETSCurve(curveName, self.indexName, self.endDate, endIndexMktData)
            if discIndex and endDiscMktData:
                discCurveName = '__disc_%s_%s_%s' % (discIndex, self.endDate.strftime('%Y%m%d'), self.endDate.strftime('%Y%m%d'))
                self.liveDiscCurve = self._createCFETSCurve(discCurveName, discIndex, self.endDate, endDiscMktData)
            elif not discIndex or discIndex == self.indexName: # discount curve is the same as index curve
                discCurveName = '__disc_%s_%s_%s' % (self.indexName, self.endDate.strftime('%Y%m%d'), self.endDate.strftime('%Y%m%d'))
                self.liveDiscCurve = py_ObjectCopy(self.liveIndexCurve, discCurveName)
            else:
                raise RuntimeError("Live discount curve specification error. Don't know how to proceed")
            
        self.riskTenors = riskTenors 
        self.startTenors = riskStartTenors
        self.riskRates = riskRates

        self.curveMapIndex = self._getCurveMapIndex()

        if 'FR007' in self.indexName:
            indexInfo = self._getIndexInfo("CNY_REPO_7D")
            indexId = indexInfo['IndexObjectID']
            self._addFR007IndexFixings(indexId)
            self.dayCount = indexInfo['IndexDayCounter']
        elif 'SHIBOR' in self.indexName:
            indexInfo = self._getIndexInfo("CNY_SHIBOR_3M")
            indexId = indexInfo['IndexObjectID']
            self._addShiborFixings(indexId)
            self.dayCount = indexInfo['IndexDayCounter']
        
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
    def readComboCurves(cls, name):
        objs = p.py_ObjectLoad("C:/Temp", name)
#         for o in objs:
#             props = p.py_ObjectProperties(o)
#             print props
        return objs
        
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

    @classmethod
    def _buildSwapCurve(self, curveName, curveDate, indexName, indexCurve, discCurve, riskTenors, riskStartTenors, riskRates=[], **kwargs):
        rc = p.py_BuildSwapCurve(curveName, curveDate, indexName, riskTenors, riskRates, indexCurve, extDiscCurve=discCurve, useExtCurveAsBase=False, template='RISK', startTenors=riskStartTenors)
#         pprint.pprint(rc, width=500)
        return rc
    
    def _getIndexInfo(self, convention='CNY_REPO_7D'):
        # create a dummy contract, just to get the index object
        att = {'endDateTenor':'1Y', 'notional':50000000.0, 'fixedRate':0.035}
        dummyId = '_dummy'
        startDate = datetime.date(2017, 12, 1)
        p.py_CreateIRSwap(dummyId, {'PredefinedConvention':convention}, startDate, **att)
        info = p.py_SwapInfo([dummyId], 0, startDate)
        indexId = info['']['IndexObjectID']
        indexInfo = info[indexId+'_Info']
        print '\n\nIndex Info: %s' % indexInfo
        return indexInfo
    
    def _addFR007IndexFixings(self, indexId, fixingfileName="../../data/fr007_fixing.csv"):
        fixings = self.readPeakIndexFixings(fixingfileName)
#         print '\n\n%s fixings loaded' % len(fixings)
        
        rc = p.py_IndexAddFixings(indexId, fixings.keys(), fixings.values())
#         print '\nFixings added to %s' % rc
    
    def _addShiborFixings(self, indexId, fixingfileName="../../data/shb3m_fixing.csv"):
#         p.py_CreateIRSwap(dummyId, {'PredefinedConvention':'CNY_SHIBOR_3M'}, startDate, **att)
        fixings = self.readPeakIndexFixings(fixingfileName)
#         print '\n\n%s fixings loaded' % len(fixings)
        
        rc = p.py_IndexAddFixings(indexId, fixings.keys(), fixings.values())
#         print '\nFixings added to %s' % rc
    
    @classmethod
    def _createCFETSCurve(cls, curveName, indexName, asofDate, mktdata, method='LinearZero'):
        tenors, rates = mktdata
        curve = p.py_BuildCfetsCurve(curveName, asofDate, indexName, tenors, rates, method)
        print 'Curve created: %s' % curve

#        double check index fixings
#         rc = p.py_IndexFixings(self.indexId, [asofDate], fwdCurveId=curveName)
#         print 'Fixing on %s is %f' % (asofDate, rc[0])
        return curve
    
    def _getCurveMapIndex(self):
        if "FR007" in self.indexName:
            return '_'+self.indexName
        elif "SHIBOR" in self.indexName:
            return '_SHIBOR_3M'

    def _priceContract(self, contract, curve, discCurve=None, forecastTodaysFixing=False, **kwargs):
        discCurve = discCurve or curve
        npv = p.py_SwapLegNPV([contract], curve, discCurve, forecastTodaysFixing=forecastTodaysFixing, **kwargs)
        print 'Swap NPV = %s' % npv
        return npv

    def _calculateBODRisk(self, contract, riskTenors=[], startTenors=[], rates=[]):
        riskCurveId = '_risk_%s' % 'BOD'
        rc = self._buildSwapCurve(riskCurveId, self.endDate, self.indexName, self.bodIndexCurve, self.bodDiscCurve, riskTenors, startTenors, riskRates=rates)
        fwdCurveName, discCurveName, curveEngineName = rc[0]
        numCurvePoints = len(riskTenors)
        fairRates = self._extractFairRate(rc)
#         print 'FairRates: ', fairRates

        print '\nBuilding curve pack for BOD risk'
        curveDate = self.endDate
        curvePackName = '_riskCurvePack_%s' % curveDate.strftime('%Y%m%d')
        rc = p.py_BuildCurvePack(curvePackName, curveEngineName)
        print 'Built curve pack %s' % rc
    
        curveMap=[('Index', 'Curve'), (self.curveMapIndex, fwdCurveName)]
        print '\nCalculating BOD risk...'
        rcIndex = p.py_CurvePackRisk(curvePackName, instrumentNames=[contract], curveMap=curveMap, discountCurveName=discCurveName, showBasePv=True, riskMode="index")
        rcDisc = p.py_CurvePackRisk(curvePackName, instrumentNames=[contract], curveMap=curveMap, discountCurveName=discCurveName, showBasePv=True, riskMode="discount")
#         print('\nCurvePackRisk:')
#         pprint.pprint(rc)
        return (rcIndex, rcDisc, fairRates)

    def calculateSmoothPV(self, contract, curve, discCurve=None, forecastTodaysFixing=False, **kwargs):
        """
        calculate the PV using the smooth curve used by risk calculation.
        this should be the same as the base pv output from the risk calculation
        """
        riskCurveId = '__smoothPV_'
        discCurve = discCurve or curve
        rc = self._buildSwapCurve(riskCurveId, self.endDate, self.indexName, curve, discCurve, self.riskTenors, self.startTenors)
        fwdCurveName, discCurveName, curveEngineName = rc[0]
        rc = p.py_SwapLegNPV([contract], fwdCurveName, discCurveName, forecastTodaysFixing=forecastTodaysFixing, **kwargs)
        p.py_DeleteObjects([riskCurveId])
        return rc[0][0]

        
    def _calculateIMMEstimate(self, contract):
        print '\nBuilding IMM curve pack'
        curveDate = self.endDate
        curvePackName = '_immriskCurvePack_%s' % curveDate.strftime('%Y%m%d')

        immDates = p.py_IMMNextDates(self.endDate, 40, '3M', datetime.date(2028, 12,23), 'CFFEX')
#         print '\n\nIMM dates: '
#         pprint.pprint(immDates)
        startDates = [self.endDate] + list(immDates)[:-1]
        rc = p.py_BuildRPCurvePack(curvePackName, [self.bodIndexCurve, self.bodDiscCurve], startDates)
        print '\nBuilt RP curve pack: %s' % rc
        
        curveMap=[('Index', 'Curve'), (self.curveMapIndex, self.bodIndexCurve)]
        rcDisc = p.py_CurvePackRisk(curvePackName, instrumentNames=[contract], curveMap=curveMap, discountCurveName=self.bodDiscCurve, showBasePv=True, riskMode='discount')
        discDelta = [r[1] for r in rcDisc[2:]]
        rcIndex = p.py_CurvePackRisk(curvePackName, instrumentNames=[contract], curveMap=curveMap, discountCurveName=self.bodDiscCurve, showBasePv=True, riskMode='index')
        indexDelta = [r[1] for r in rcIndex[2:]]
        """
        print '\nCurvePackRisk:'
        print 'Index risk:'
        pprint.pprint(rcIndex)
        print 'Discount risk:'
        pprint .pprint(rcDisc)
        """
        
        bodIndexRates = p.py_YieldTSForwardRate(self.bodIndexCurve, startDates, immDates, self.dayCount)
        bodDiscRates = p.py_YieldTSForwardRate(self.bodDiscCurve, startDates, immDates, self.dayCount)
        """
        print "Index forward rates:"
        print bodIndexRates
        print "Discount forward rates:"
        print bodDiscRates
        """
        
        liveIndexRates = p.py_YieldTSForwardRate(self.liveIndexCurve, startDates, immDates, self.dayCount)
        liveDiscRates = p.py_YieldTSForwardRate(self.liveDiscCurve, startDates, immDates, self.dayCount)
        """
        print "Index forward rates:"
        print liveIndexRates
        print "Discount forward rates:"
        print liveDiscRates
        """
        indexEstimate = [risk*(live-bod)*10000.0 for risk, live, bod in zip(indexDelta, liveIndexRates, bodIndexRates)]
        discEstimate = [risk*(live-bod)*10000.0 for risk, live, bod in zip(discDelta, liveDiscRates, bodDiscRates)]
        
        print 'IMM dates:'
        symDates = p.py_IMMDateToSymbol(immDates)
        print symDates
        print ', '.join(['{:,.0f}']*len(indexEstimate)).format(*indexEstimate)
        print ', '.join(['{:,.0f}']*len(discEstimate)).format(*discEstimate)
        immEstimate = sum(indexEstimate) + sum(discEstimate)
        return immEstimate
    
    def _extractFairRate(self, swapCurveBuildResult):
        resultList = swapCurveBuildResult[1]
        for i, r in enumerate(resultList):
            if r and r[0]=='Instrument':
                break
        fairRates = [(row[0], row[1]) for row in resultList[i+1:]]
        return fairRates
                
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
    
    def _calculatePnlEstimate(self, contract, curveBOD, discBOD, curveBODDate, liveCurve, discCurve, liveCurveDate):
        """Calculate pnl estimate using delta and market data change
        First calculate the risk and fair rates using the BOD curve.
        Then calculate the fair rates only using the current curve
        The estimated pnl is the vector product of the BOD risk and the fair rates shift
        """

        indexRisk, discRisk, fairRatesBOD = self._calculateBODRisk(contract, riskTenors=self.riskTenors, startTenors=self.startTenors)
        basePV = indexRisk[1][-1]
        print 'BOD smooth PV is: %.2d' % basePV
        indexRiskVec = indexRisk[2:]
        indexRiskVec = [r[2] for r in indexRiskVec] #for bp shift
        discRiskVec = discRisk[2:]
        discRiskVec = [r[2] for r in discRiskVec] #for bp shift
        riskVec = indexRiskVec + discRiskVec

        ratesBOD = [r for i, r in fairRatesBOD]

#         curveDates, curveRatesP = self.pdayMktData
#         print 'curveDates is ', curveDates, 'curveRatesP is ', curveRatesP

        tempCurveId = "__Dummy_RiskCurveId_"
        rates = []
        rc = self._buildSwapCurve(tempCurveId, self.endDate, self.indexName, self.liveIndexCurve, self.liveDiscCurve, self.riskTenors, self.startTenors, riskRates=rates)
        
        fairRatesLive = self._extractFairRate(rc)
#         print 'fairRatesLive from risk run: ' ,fairRatesLive
        ratesLive = [r for i, r in fairRatesLive]

#         curveRatesT = self.tdayMktData[1]
#         print 'curveRatesT is ', curveRatesT
#         ratesDiff = [(rt - rp) * 10000.0 for rp, rt in zip(curveRatesP, curveRatesT)] #in bp
#         print 'ratesDiff is ', ratesDiff

        print "\nBOD risk Vec: ", ', '.join(['{:,.2f}']*len(riskVec)).format(*riskVec)
        print "Start fair rates: ", ', '.join(['{:,.4f}']*len(ratesBOD)).format(*ratesBOD)
        print "End fair rates: ", ', '.join(['{:,.4f}']*len(ratesLive)).format(*ratesLive)
        
        ratesDiff = [(rt - rp) for rt, rp in zip(ratesLive, ratesBOD)] #in bp
        pnlBuckets = [r*dr*10000.0 for (r, dr) in zip(ratesDiff, riskVec)]
        
        print 'PNL buckets:'
        print 'Index', self.riskTenors, '\nDisc:', self.riskTenors
        print ', '.join(['{:,.0f}']*len(pnlBuckets)).format(*pnlBuckets)
        pnlEstimate = sum(pnlBuckets)
        
        return pnlEstimate

    def explainPnl(self, contract):
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

        # Calculate beginning PV, with previous day date, curve, and with fixing
        rc = self._priceContract(contract, self.eodIndexCurve, self.eodDiscCurve)
        pvEOD, fwdCurve, discCurve = rc[0]

        discCurve = self.eodDiscCurve or self.eodIndexCurve
        df = p.py_YieldTSDiscount(discCurve, [self.endDate])
        df = df[0]
        print 'df is', df
        discount = pvEOD * (1.0/df - 1.0)
        print 'One day discount: %f' % discount

        #Calculate endDate's PV, with endDate's date, curve, and with fixing applied
        rc = self._priceContract(contract, self.liveIndexCurve, self.liveDiscCurve) #without cash, with fixing
        pvLast, fwdCurve, discCurve = rc[0]
        smoothPV = self.calculateSmoothPV(contract, self.liveIndexCurve, self.liveDiscCurve)
        
        #calculate total payments between previous and endDate by including past cash flows using endDate's curve
        rc = self._priceContract(contract, self.liveIndexCurve, self.liveDiscCurve, cfAfterDate=self.startDate, cfAfterDateInclusive=False)
        pvCash, _, _ = rc[0]
        payments = pvCash - pvLast
        print '\nPayments between previous day (exc) and endDate (inc) is %s' % payments

        # total pnl
        pnlTotal = pvLast-pvEOD+payments

        #Calculate pnl due to date change alone
        #This is done by calculating the pv difference between previous day's curve points but on previous and endDate's date and regular pv         curveName = '%s_%s_%s' % (self.indexName, self.startDate.strftime('%Y%m%d'), self.endDate.strftime('%Y%m%d'))

        # price without fixing
        rc = self._priceContract(contract, self.bodIndexCurve, self.bodDiscCurve, cfAfterDate=self.endDate, cfAfterDateInclusive=True, forecastTodaysFixing=True) # with payment
        pvBOD = rc[0][0]
        pnlTheta = pvBOD - pvEOD
        drift = pnlTheta - discount
        smoothBOD = self.calculateSmoothPV(contract, self.bodIndexCurve, self.bodDiscCurve, cfAfterDate=self.endDate, cfAfterDateInclusive=True, forecastTodaysFixing=True)

        # price with fixing
        rc = self._priceContract(contract, self.bodIndexCurve, self.bodDiscCurve, cfAfterDate=self.endDate, cfAfterDateInclusive=True, forecastTodaysFixing=False) # with fixing and payment
        pvBODwFixing = rc[0][0]
        pnlFixing = pvBODwFixing - pvBOD

        #Calculate pnl due to market data change
        #By calculating pv difference between using endDate's curve points and previous day's curve points, both on endDate
        rc = self._priceContract(contract, self.bodIndexCurve, self.bodDiscCurve, cfAfterDate=self.endDate, cfAfterDateInclusive=False, forecastTodaysFixing=False)
        pvBODClean = rc[0][0] # without payment, with fixing applied
        pnlMktdata = pvLast - pvBODClean
#         print 'Pnl due to mktdata move alone: %f' % pnlMktdata

        #pnl due to urve adjustments
        front, end = (smoothBOD-pvBOD), (smoothPV-pvLast)
        pnlCurveAdj = front - end 
        
        pnlEstimate = self._calculatePnlEstimate(contract, self.bodIndexCurve, self.bodDiscCurve, self.endDate, self.liveIndexCurve, self.liveDiscCurve, self.endDate)
        immEstimate = self._calculateIMMEstimate(contract)
        print '\nMktPnl, EstimatedPnl, IMMEsimate, CurveAdj: ', '{:,.2f}, {:,.2f}, {:,.2f}, {:,.2f}, {:,.2f}'.format(pnlMktdata, pnlEstimate, immEstimate, front, end)
        
        # calculate unexplained pnl
        unexplained = pnlTotal - pnlTheta - pnlFixing - pnlEstimate - pnlCurveAdj

        #tabulate results
        buckets = (pvEOD, pvBOD, pvLast, payments, pnlTotal, pnlMktdata, pnlEstimate, discount, drift, pnlFixing, pnlCurveAdj, unexplained)
        print ['SwapId', 'BegPV', 'BodPV', 'EndPV', 'Payment', 'TotalPnl', 'MktPnl', 'EstPnl', 'Discount', 'Drift', 'FixingPnl', 'CurveCorrection', 'Unexplained']
        spec = ', '.join(['{%d:,.2f}' % i for i in range(len(buckets))])
        print contract, ', ', spec.format(*buckets)
    
def readSavedContract(filename):
    path, name = filename.rsplit('/', 1)
    res = p.py_ObjectLoad(path, name)
    
    contractId = res[0]
    print "contract Id: %s" % contractId
    return contractId
        
def runFR007PnlExplain():
    print '\n\nRunning Pnl Explain...'
    calendar = 'China.IB'
    
    fr007CurveTenors = ['1W', '1M', '3M', '6M', '9M', '1Y', '2Y', '3Y', '4Y', '5Y', '7Y', '10Y']
    pdayCurveRates  = [3.2, 3.239, 3.2088, 3.2613, 3.3077, 3.3534, 3.4735, 3.5652, 3.6478, 3.7109, 3.7938, 3.8592]
    pdayMktdata = [fr007CurveTenors, [t/100.0 for t in pdayCurveRates]]
    
    tdayCurveRates = [3.5, 3.3, 3.2079, 3.2725, 3.3506, 3.3622, 3.4785, 3.5676, 3.6448, 3.7113, 3.7875, 3.8463]
    tdayMktdata = [fr007CurveTenors, [t/100.0 for t in tdayCurveRates]]

    today = datetime.date(2018, 3, 30)
    pday = today - datetime.timedelta(days=1)
    pday = p.py_CalendarAdjust(calendar, [pday], BusinessDayConvention='P')[0]

    indexName = "FR007"
    discIndex = "FR007"
    riskTenors = ["1W", "1M", "3M", "6M", "9M", "1Y", "2Y", "3Y", "4Y", "5Y", "6Y", "7Y", "8Y", "9Y", "10y"]
    riskStartTenors = ["0D"]

    plex = PnlExplainer(indexName, pday, today, 
                 startIndexMktData=pdayMktdata, discIndex=discIndex, endIndexMktData=tdayMktdata,
                 riskTenors=riskTenors, riskStartTenors=riskStartTenors)
    
#     contract = p.py_ObjectLoad("S:/Public/TOPS", '20180309_ZQ_TFD002_A1_FR007.bin.gz')[0]
#     contract = readSavedContract("S:/Public/TOPS/20180309_ZQ_TFD004_Z8_FR007.bin.gz")
#     contract = readSavedContract("S:/Private/shanshan.Lin/PnLExplain/SwapContract/20180330_43988PS.bin")
    contract = readSavedContract("S:/Private/shanshan.Lin/PnLExplain/SwapContract/20180330_45048PS1.bin")
    plex.explainPnl(contract)
        
def runShiborPnlExplain():
    print '\n\nRunning Pnl Explain...'
    calendar = 'China.IB'

    today = datetime.date(2018, 3, 30)
    pday = today - datetime.timedelta(days=1)
    pday = p.py_CalendarAdjust(calendar, [pday], BusinessDayConvention='P')[0]
    
    indexName = "SHIBOR3M"
    discIndex = "FR007"

    fr007CurveTenors = ['1W', '1M', '3M', '6M', '9M', '1Y', '2Y', '3Y', '4Y', '5Y', '7Y', '10Y', '11Y', '15Y', '20Y', '25Y', '30Y', '40Y', '50Y']
    pDiscCurveRates  = [3.2, 3.239, 3.2088, 3.2013, 3.3077, 3.3534, 3.4735, 3.5652, 3.6478, 3.7109, 3.7938] + [4.8692]*8

    pdayDiscMktdata = [fr007CurveTenors, [t/100.0 for t in pDiscCurveRates]]
    
    shiborCurveTenors = ['3M', '6M', '9M', '1Y', '2Y', '3Y', '4Y', '5Y', '7Y', '10Y', '11Y', '15Y', '20Y', '25Y', '30Y', '40Y', '50Y']
    shiborCurveRates  = [4.5247, 4.4488, 4.42, 4.41, 4.4119, 4.4209, 4.4309, 4.4288, 4.4713] + [4.4863]*8
    pdayMktdata = [shiborCurveTenors, [t/100.0 for t in shiborCurveRates]]

    # CFETS live curve
    tdayCurveRates = [4.4615, 4.4677, 4.4022, 4.3892, 4.392, 4.4047, 4.4135, 4.4264, 4.4443, 4.46, 4.46, 4.46, 4.46, 4.46, 4.46, 4.46, 4.46]
    tdayMktdata = [shiborCurveTenors, [t/100.0 for t in tdayCurveRates]]
    
    tDiscCurveRates = [3.5, 3.3, 3.2079, 3.2725, 3.3506, 3.3622, 3.4785, 3.5676, 3.6448, 3.7113, 3.7875] + [3.8463]*8
    tDiscMktdata = [fr007CurveTenors, [t/100.0 for t in tDiscCurveRates]]

    shiborRiskTenors = ["3M", "6M", "9M", "1Y", "2Y", "3Y", "4Y", "5Y", "6Y", "7Y", "8Y", "9Y", "10y", "12Y", "15Y", "20Y", "30Y", "40Y", "50Y"]
    shiborStartTenors = ["0D"]

    # Chirs curve plex
    liveCurves = PnlExplainer.readComboCurves("Ncurve_20180330.bin")
    r1dCurve, fr7Curve, shbCurve, discCurve, s1dCurve = liveCurves
    plex = PnlExplainer(indexName, pday, today, 
                 startIndexMktData=pdayMktdata, discIndex=discIndex, startDiscMktData=pdayDiscMktdata, endIndexCurve=shbCurve, endDiscCurve=discCurve,
                 riskTenors=shiborRiskTenors, riskStartTenors=shiborStartTenors)
    """
    # CFETS curve plex
    plex = PnlExplainer(indexName, pday, today, 
                startIndexMktData=pdayMktdata, discIndex=discIndex, startDiscMktData=pdayDiscMktdata, endIndexMktData=tdayMktdata, endDiscMktData=tDiscMktdata,
                 riskTenors=shiborRiskTenors, riskStartTenors=shiborStartTenors)
    """

#     contract = readSavedContract("S:/Private/shanshan.Lin/PnLExplain/SwapContract/20180330_ZQ_TFD004_Z6_SHB3M_fixed_aggregate.bin")
    contract = readSavedContract("S:/Private/shanshan.Lin/PnLExplain/SwapContract/20180330_ZQ_TFD004_Z6_SHB3M_SHIBOR3M Actual_360_aggregate.bin")
    plex.explainPnl(contract)
    
if __name__ == '__main__':
#     runFR007PnlExplain()
    runShiborPnlExplain()
    
