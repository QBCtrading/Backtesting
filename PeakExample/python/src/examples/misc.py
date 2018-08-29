'''
Created on Jan 15, 2018

@author: pzhou
'''
import datetime
import peakpy.peak as p
import pprint
from calendar import calendar

curveName = "cfets_FR007"
swapCurveId = 'cfets_FR007_wap'
curvePackName = 'FR007_curve_pack'
anchorDate = datetime.date(2017, 11, 14)
startDate = datetime.date(2017, 11, 15)
indexName = "FR007"
indexId = '_' + indexName
tenors = ["7d", "1M", "3M", "6M", "1Y", "5Y", "10y"]
rates = [0.030, 0.032, 0.033, 0.034, 0.037, 0.040, 0.045]
method = "LinearZero" #"LinearSwap"
discCurveName = curveName
swapId = 'TestSwap'

def createSwap():
    rc = p.py_SwapContract(swapId, indexName, startDate, settleDate='1D', maturity='5Y', notional=50000000.0, fixedRate=0.03)
#     rc = p.py_CreateIRSwap()
    print 'swap contract: ', rc
    return rc

def addFixings():
    print '\n\n'
    
    curve = p.py_BuildCfetsCurve(curveName, anchorDate, indexName, tenors, rates, method, discCurveName=discCurveName)
    print 'Curve created: %s' % curve
    
#   Create a swap to get the index object
    att = {'endDateTenor':'5Y', 'notional':50000000.0, 'fixedRate':0.035, 'discCurveId':curveName, 'fwdCurveId':curveName}
    p.py_CreateIRSwap(swapId, {'PredefinedConvention':'CNY_REPO_7D'}, anchorDate, **att)
    
    fixings = readPilotScopeIndexFixings("../../data/fr007_fixing.csv")
    print '%s fixings loaded' % len(fixings)
    
    rc = p.py_IndexAddFixings(indexId, fixings.keys(), fixings.values())
    print 'Fixings added to %s' % rc
    
    rc = p.py_IndexFixings(indexId, [datetime.date(2017,12,18)], fwdCurveId=curveName)
    print rc
    
def runIMMDates():
    rc = p.py_IMMSymbolToDate(['F18', 'Z23'], datetime.date(2017,1,25), rule='CFFEXLT')
    print 'F18, Z23 IMM date: ', rc
    
    rc = p.py_IMMNextDates(startDate=datetime.date(2018,1,5), numOfDates=20, datePref='1m', endDate=None) #numOfDates has no effect
    print '\n1M IMM dates: ', rc
    
    p.py_IndexAddFixings('_FR007', [datetime.date(2018,1,22), datetime.date(2018,1,23)], [0.033, 0.034])
    print '\nIndex fixings added'

    dates = (datetime.date(2017,12,22), datetime.date(2018,1,23), datetime.date(2018,12,24))
    fixings = p.py_IndexFixings('_CNY_REPO_7D', dates, fwdCurveId=curveName)
    print '\nFixings for ', dates, ': ', fixings

def runDatesTest():
    print '\n\n'
    
    calendar = 'China.SSE'
    dates = [datetime.date(2018, 2, 16), datetime.date(2018,2,24)]
    periods = ['1D', '-1D']
    bdayConvention = 'MF'
    endOfMonth = False
    rc = p.py_CalendarAdvance(calendar, dates, periods, BusinessDayConvention=bdayConvention, endOfMonth=endOfMonth)
    print 'Advanced dates: ', rc
    
    periods = ['1D', '1M', '3M', '1Y']
    rc = p.py_FrequencyFromPeriod(periods)
    print 'Frequencies are: ', rc
    
    rc = p.py_CalendarIsBusinessDay(calendar, dates)
    print 'Are dates business days: ', rc
    
    days1 = [datetime.date(2018, 2, 23), datetime.date(2018, 4, 30)]
    days2 = [datetime.date(2018, 2, 9), datetime.date(2018, 5, 2)]
    rc = p.py_DaysBetween(days1, days2, calendar)
    print 'Days in between dates: ', rc
    
    rc = p.py_CalendarAdjust(calendar, dates, BusinessDayConvention=bdayConvention)
    print 'Adjusted business dates: ', rc
    
    rc = p.py_CalendarAdjust(calendar, dates, BusinessDayConvention='P')
    print 'Previous business dates: ', rc
    
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

def runBondFuncs():
    scheduleId = 'bond_schedule'
    startDate = datetime.date(2017, 8, 8)
    endDate = datetime.date(2023, 8, 8)
    tenor = '6M'
    calendar = 'China.IB'
    rc = p.py_Schedule(scheduleId, startDate, endDate, tenor, calendar)
    print rc
    bondId = 'Test_Bond'
    bondType = 'IB'
    notional = [100000000.0]
    coupons = [3.7]
    issueDate = startDate
    rc = p.py_FixedRateBond(bondId, 'Test bond', bondType, notional, coupons, scheduleId, issueDate, calendar)
    print 'Created Bond %s' % rc
    rc = p.py_BondNextCashflowDate(bondId)
    print 'Next payment date: %s' % rc
    rc = p.py_BondNextCashflowAmount(bondId)
    print 'Next coupon amount %.2d' % rc
    curve = p.py_BuildCfetsCurve(curveName, anchorDate, indexName, tenors, rates, method, discCurveName=discCurveName)
    print 'Curve created: %s' % curve
    rc = p.py_BondPV(bondId, curveName)
    print 'Bond PV is ', '{:,.2f}'.format(rc)
    rc = p.py_BondFlowAnalysis(bondId, datetime.date(2018, 1, 2))
    print rc

def runObjectTest():
#     rc = createSwap()
#     p.py_ObjectSave([swapId], "S:/Private/Ping.Zhou/Compass/swap")
#     res = p.py_ObjectLoad("S:/Private/Ping.Zhou/Compass", "swap.bin.gz")
    res = p.py_ObjectLoad("S:/Private/Ping.Zhou/Compass", "mma_fr007.bin.gz")
    print "Object load result: ", res

def runExample():
#     runDatesTest()
#     addFixings()
#     runIMMDates()
#     runBondFuncs()
    runObjectTest()
    
if __name__ == '__main__':
    runExample()
