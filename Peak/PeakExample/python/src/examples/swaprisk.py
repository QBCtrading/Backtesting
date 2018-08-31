'''
Created on Jan 15, 2018

@author: pzhou
'''
import datetime
import pprint

import peakpy.peak as p

'''
    This example creates a swap, get its info, and run risks
'''

curveName = "cfets_FR007"
anchorDate = datetime.date(2017, 11, 14)
startDate = datetime.date(2017, 11, 15)
indexName = "FR007"
tenors = ["1d", "7d", "1M", "3M", "6M", "1Y", "5Y", "10y"]
rates = [0.030, 0.030, 0.032, 0.033, 0.034, 0.037, 0.040, 0.045]
method = "LinearZero" #"LinearSwap"
discCurveName = curveName
swapId = 'TestSwap'
swapCurveId = 'cfets_FR007_wap'
curvePackName = 'FR007_curve_pack'

def calendarCheck():
    print "\n\nChecking holiday calendar..."
    print 'China.IB holiday list'
    cal = p.py_CalendarHolidayList('China.IB', datetime.date(2018,1,1), datetime.date(2020,1,1))
    pprint.pprint(cal)
    
    print 'China.IB working weekend days list'
    cal = p.py_CalendarWorkingWeekendList('China.IB', datetime.date(2018,1,1), datetime.date(2020,1,1))
    pprint.pprint(cal)

def runSwapInfo():

    # create a dummy swap, just to get the index object
    att = {'endDateTenor':'5Y', 'notional':50000000.0, 'fixedRate':0.035}
    dummyId = '_dummy'
    p.py_CreateIRSwap(dummyId, {'PredefinedConvention':'CNY_REPO_7D'}, startDate, **att)
    rc = p.py_SwapInfo([dummyId], 0, startDate)
    print '\n\nSwap Info:'
    pprint.pprint(rc, width=1000)
    indexId = rc['']['IndexObjectID']
    print '\n\nIndex object Id: %s' % indexId

    fixings = readPeakIndexFixings("../../data/fr007_fixing.csv")
    print '\n\n%s fixings loaded' % len(fixings)
    
    rc = p.py_IndexAddFixings(indexId, fixings.keys(), fixings.values())
    print '\nFixings added to %s' % rc
    
    d = datetime.date(2017,12,18)
    rc = p.py_IndexFixings(indexId, [d])
    print '\nFixings without curve for %s is %s' % (d, rc)

    rc = p.py_CreateIRSwap(swapId, {'PredefinedConvention':'CNY_REPO_7D'}, startDate, **att)
    rc = p.py_SwapInfo([swapId], 0, anchorDate)
    print '\n\nSwapInfo:'
    pprint.pprint(rc, width=1000)
    
    curve = p.py_BuildCfetsCurve(curveName, anchorDate, indexName, tenors, rates, method, discCurveName=discCurveName)
    print '\n\nCurve created: %s' % curve

    d1 = startDate + datetime.timedelta(days=7)
    df = p.py_YieldTSDiscount(curveName, [startDate, d1], allowExtrapolation=True)
    print 'Discount factor for %s is %s' % ([startDate, d1], df)
    
    rc = p.py_IndexFixings(indexId, [d], fwdCurveId=curveName)
    print '\nFixings with curve for %s is %s' % (d, rc)
    
    npv = p.py_SwapLegNPV([swapId], curveName, discCurveName, anchorDate, True, debugLevel=2)
    print '\nSwap NPV = %s' % npv
    
    rc = p.py_SwapLegAnalysis(swapId, 0, afterDate=datetime.date(2018,1,25), forwardCurveId=curveName, discountCurveId='', afterDateInclusive=False, forecastTodaysFixing=True, 
                              useSqlFriendlyColHeaders=True, selectedColumns='All', toDate=datetime.date(2100,12,31))
    print '\nSwapLegAnalysis:'
    pprint.pprint(rc, width=1000)

    rc = p.py_IndexName(indexId)
    print '\nIndex Name "%s"' % rc

def runCFETSCurveRisk():
    rc = p.py_BuildSwapCurve(swapCurveId, anchorDate, indexName, tenors, rates, curveName, discCurveName)
    print '\n\nBuilt swap curve: '
    pprint.pprint(rc, width=500)

    curve, discCurve, curveEngineName = rc[0]
    rc = p.py_BuildCurvePack(curvePackName, curveEngineName)
    print '\nBuilt curve pack %s' % rc

    rc = p.py_CurvePackRisk(curvePackName, instrumentNames=[swapId], curveMap=[('Index', 'Curve'), ('_'+indexName, curve)], discountCurveName=discCurve, showBasePv=True)
    pprint.pprint('\nCurvePackRisk:')
    pprint.pprint(rc)

def runIMMRIsk():
    bucketDates = p.py_IMMNextDates(anchorDate, 30, '3M', datetime.date(2025, 2,25), 'CFFEX')
    print '\n\nIMM dates: '
    pprint.pprint(bucketDates)
    bucketDates = [anchorDate] + list(bucketDates)
    rc = p.py_BuildRPCurvePack(curvePackName, [curveName, discCurveName], bucketDates)
    print '\nBuilt RP curve pack: %s' % rc
    
    rc = p.py_CurvePackRisk(curvePackName, instrumentNames=[swapId], curveMap=[('Index', 'Curve'), ('_'+indexName, curveName)], discountCurveName=discCurveName, showBasePv=True)
    print '\nCurvePackRisk:'
    pprint.pprint(rc)

def readPeakIndexFixings(name):
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
    
def readPilotScopeIndexFixings(name):
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

def runExample():
    calendarCheck()
    runSwapInfo()
    runCFETSCurveRisk()
    runIMMRIsk()
    
if __name__ == '__main__':
    runExample()
