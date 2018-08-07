import QuantLib as ql
import pandas as pd
import numpy as np
import datetime
from WindPy import w
import matplotlib.pyplot as plt
%matplotlib qt5

import pickle
f = open('s3mclosingdb.dat','rb')
s3mclosingdb = pickle.load(f)
f.close()
f = open('fr007closingdb.dat','rb')
fr007closingdb = pickle.load(f)
f.close()

currency = ql.CNYCurrency()
calendar = ql.China()
business_convention = ql.ModifiedFollowing
day_count = ql.Actual365Fixed()
float_day_count = ql.Actual360()
coupon_freq = ql.Quarterly
coupon_tenor = ql.Period('3M')

swap_helpers = []

def getDate():
    date = datetime.datetime(2018,7,9)
    calc_date = ql.Date(9,7,2018)
    return date, calc_date
def getDate2():
    date = datetime.datetime(2018,7,10)
    calc_date = ql.Date(10,7,2018)
    return date, calc_date
def getDate3():
    date = datetime.datetime(2018,7,11)
    calc_date = ql.Date(11,7,2018)
    return date, calc_date
def getDatetime(calc_date):
    return datetime.date(calc_date.year(), calc_date.month(), calc_date.dayOfMonth())
def getqlDate(date):
        return ql.Date(date.day,date.month,date.year)


def createSwap(calc_date, str, china_index, swap_engine):
    period = ql.Period(str)
    settle_date = calendar.advance(calc_date, 1, ql.Days, business_convention)
    maturity_date = calendar.advance(settle_date, period, ql.ModifiedFollowing)
    return createSwapWithDate(settle_date, maturity_date, china_index, swap_engine)
def createSwapDays(days, china_index, swap_engine):
    settle_date = calendar.advance(calc_date, 1, ql.Days, business_convention)
    maturity_date = calendar.advance(settle_date, days, ql.Days, ql.ModifiedFollowing)
    return createSwapWithDate(settle_date, maturity_date, china_index, swap_engine)
def createSwapMonths(months, china_index, swap_engine):
    settle_date = calendar.advance(calc_date, 1, ql.Days, business_convention)
    maturity_date = calendar.advance(settle_date, months, ql.Months, ql.ModifiedFollowing)
    return createSwapWithDate(settle_date, maturity_date, china_index, swap_engine)
    
def createSwapWithDate(settle_date, maturity_date, china_index, swap_engine):
    fixed_schedule = ql.Schedule(settle_date, maturity_date, 
                             coupon_tenor, calendar, business_convention,
                             business_convention, ql.DateGeneration.Forward,
                             False)
    float_schedule = ql.Schedule(settle_date, maturity_date,
                             coupon_tenor, calendar, business_convention,
                             business_convention, ql.DateGeneration.Forward,
                             False)
    notional = 100000000
    fixed_rate = 0.0
    mySwap = ql.VanillaSwap(ql.VanillaSwap.Payer, notional, fixed_schedule,
                         fixed_rate, day_count, float_schedule, china_index,
                         0,
                         float_day_count if 'Shibor' in china_index.name()
                         else day_count)
    mySwap.setPricingEngine(swap_engine)
    return mySwap

def createSwapForTrade(calc_date, str, china_index, swap_engine, notional, rate):
    
    period = ql.Period(str)
    settle_date = calendar.advance(calc_date, 1, ql.Days, business_convention)
    maturity_date = calendar.advance(settle_date, period, ql.ModifiedFollowing)
    
    fixed_schedule = ql.Schedule(settle_date, maturity_date, 
                             coupon_tenor, calendar, business_convention,
                             business_convention, ql.DateGeneration.Forward,
                             False)
    float_schedule = ql.Schedule(settle_date, maturity_date,
                             coupon_tenor, calendar, business_convention,
                             business_convention, ql.DateGeneration.Forward,
                             False)
    fixed_rate = rate/100
    mySwap = ql.VanillaSwap(
            ql.VanillaSwap.Receiver if notional > 0 else ql.VanillaSwap.Payer
            , abs(notional), fixed_schedule,
            fixed_rate, day_count, float_schedule, china_index,
            0,
            float_day_count if 'Shibor' in china_index.name()
                         else day_count
            )
    mySwap.setPricingEngine(swap_engine)
    print('engine set')
    #print('fixing of today ', china_index.fixing(calc_date))
    return mySwap

china_index = ""

def plotForwardCurve(yield_curve):
    l = []
    for i in range(0,40):
        l.append(yield_curve.forwardRate(i/4,i/4+0.25,ql.Compounded).rate())
    ts = pd.Series(l)
    ts.plot(drawstyle='steps-pre')

def buildHistCurve(date):
    
    global china_index
    
    calc_date = ql.Date(date.day, date.month,date.year)
    settle_date = calendar.advance(calc_date, 1, ql.Days, business_convention)
    ql.Settings.instance().evaluationDate = calc_date
    print('anchor date:',calc_date)
    #read Shibor3MClosing
    #swap_rates = getFR007/Shibor3MClosing(date).Data[0]
    swap_rates = []
    if 'Shibor' in china_index.name():
        swap_rates = s3mclosingdb[date]
    else:
        swap_rates = fr007closingdb[date]
    #end of read FR007/Shibor3MClosing
    curve_tenor = []
    if 'Shibor' in china_index.name():
        curve_tenor = [
            #ql.Period('1W'),
            #ql.Period('1M'),
            ql.Period('3M'),
            ql.Period('6M'),
            ql.Period('9M'),
            ql.Period('1Y'),
            ql.Period('2Y'),
            ql.Period('3Y'),
            ql.Period('4Y'),
            ql.Period('5Y'),
            ql.Period('7Y'),
            ql.Period('10Y')
            ]
    elif 'FR007' in china_index.name():
        curve_tenor = [
            ql.Period('1W'),
            ql.Period('1M'),
            ql.Period('3M'),
            ql.Period('6M'),
            ql.Period('9M'),
            ql.Period('1Y'),
            ql.Period('2Y'),
            ql.Period('3Y'),
            ql.Period('4Y'),
            ql.Period('5Y'),
            ql.Period('7Y'),
            ql.Period('10Y')
            ]
    fake_china_index = ql.IborIndex('fake',ql.Period('3M'),1,
                           currency,calendar,ql.ModifiedFollowing,
                           False,
                           float_day_count if 'Shibor' in china_index.name() else day_count
                           )
    swap_helpers = []
    for rate,tenor in list(zip(swap_rates, curve_tenor)):
        swap_helpers.append(ql.SwapRateHelper(ql.QuoteHandle(ql.SimpleQuote(
                  rate/100 * (365/360 if 
                               ('Shibor' in china_index.name() and tenor == ql.Period('3M'))
                              else 1
                            )
                )),
                                          tenor, calendar,
                                          coupon_freq,
                                          business_convention, 
                                          day_count,
                                          fake_china_index
        ))
        
    rate_helpers = swap_helpers
    yield_curve = ql.PiecewiseLogCubicDiscount(settle_date, rate_helpers,
                                          day_count)
    
    discountTermStructure = ql.RelinkableYieldTermStructureHandle()
    forecastTermStructure = ql.RelinkableYieldTermStructureHandle()
    discountTermStructure.linkTo(yield_curve)
    forecastTermStructure.linkTo(yield_curve)
    
    swap_engine = ql.DiscountingSwapEngine(discountTermStructure)
    china_index = china_index.clone(forecastTermStructure)    
    
    #fixing
    if len(fixings)!=0 :
        china_index.addFixings(fixingdays, fixings)
        #print('fixing added for ',calc_date,': ',fixingdays)
    fixingdays.append(calc_date)
    fixings.append(swap_rates[0]/100)
    #print('test0: ',china_index.fixing(calc_date))
    #end of fixing
    
    return yield_curve, swap_engine, rate_helpers

def calcFloatingLegNPV(swap, drct, yield_curve):
    
    coupon_schedule = [x for x in swap.floatingSchedule()]
    
    floatingNPV = 0
    
    for i in range(0,len(coupon_schedule)-1):
        #
        # discount future cashflow
        # 
        start_date = coupon_schedule[i]
        end_date = coupon_schedule[i+1]
        end_date = calendar.advance(end_date, -1, ql.Days, business_convention)
        accrual_schedule = [x for x in ql.Schedule(start_date,end_date,
                                                   ql.Period(ql.Weekly),
                                                   calendar,
                                   business_convention, business_convention,
                                   ql.DateGeneration.Forward, False)]
        accrual_rate = 1
        if 'Shibor' in china_index.name():
            accrual_schedule = [start_date, end_date]
        for j in range(0,len(accrual_schedule)-1):
                accrual_start_date = accrual_schedule[j]
                accrual_end_date = accrual_schedule[j+1]
                #print('accrual_start_date',' ',accrual_end_date)
                rate = 0.0
                if accrual_start_date > calc_date:
                    #print('accrual: using forcast fixing.')
                    ss = createSwapWithDate(accrual_start_date, accrual_end_date, 
                                  china_index, swap_engine)
                    rate = ss.fairRate()
                else:
                    #print('accrual: fixing exists.')
                    rate = fr007closingdb[getDatetime(
                                                  accrual_start_date
                                                 )][0]/100
                #print('fairrate = ',rate)
                rate = rate * (accrual_end_date - accrual_start_date) / (
                            365 if '365' in day_count.name() else 360
                        )
                #print('dates = ',accrual_end_date - accrual_start_date)
                #print('actualinterest = ',rate)
                accrual_rate = accrual_rate * (1+rate)
                #print('accrual_rate = ',accrual_rate)
        cf = swap.nominal()*(accrual_rate-1)
        df = 1
        if end_date > calendar.advance(calc_date,1,ql.Days,business_convention):
            df = yield_curve.discount(end_date)
        dsctcf = cf * df
        if drct == 1:
            dsctcf = dsctcf * -1
        #if end_date > calc_date:
            #print ('future cash flow. df = ',yield_curve.discount(end_date),', cash flow = ',dsctcf)
        #else:
            #print ('realized cash flow. df = ',1,', cash flow = ',dsctcf)
        floatingNPV = floatingNPV+dsctcf
    return floatingNPV


def calcFixedLegNPV(swap, drct, yield_curve):
    
    coupon_schedule = [x for x in swap.floatingSchedule()]
    
    fixedNPV = 0
    
    for i in range(0,len(coupon_schedule)-1):
        
        start_date = coupon_schedule[i]
        end_date = coupon_schedule[i+1]
        end_date = calendar.advance(end_date, -1, ql.Days, business_convention)
        
        rate = swap.fixedRate() * (end_date - start_date) / 365
        cf = swap.nominal() * rate
        df = 1
        if end_date > calendar.advance(calc_date,1,ql.Days,business_convention):
            df = yield_curve.discount(end_date)
        dsctcf = cf * df
        if drct == -1:
            dsctcf = dsctcf * -1
        fixedNPV = fixedNPV + dsctcf
    return fixedNPV

w.start()