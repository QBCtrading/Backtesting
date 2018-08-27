#===initialization===
import QuantLib as ql
import pandas as pd
import numpy as np
import datetime
from WindPy import w
import matplotlib.pyplot as plt
#%matplotlib qt5
w.start()

#read fr007, s3m cfets closing from file
#be careful of the working directory
import pickle
f = open('s3m.dat','rb')
s3mclosingdb = pickle.load(f)
f.close()
f = open('fr007.dat','rb')
fr007closingdb = pickle.load(f)
f.close()

currency = ql.CNYCurrency()
calendar = ql.China(ql.China.IB)
business_convention = ql.ModifiedFollowing
day_count = ql.Actual365Fixed()
float_day_count = ql.Actual360()
coupon_freq = ql.Quarterly
coupon_tenor = ql.Period('3M')
#===end of initialization===

#===frequently used functions===
def getDatetime(calc_date):
    return datetime.date(calc_date.year(), calc_date.month(), calc_date.dayOfMonth())
def getqlDate(date):
    return ql.Date(date.day,date.month,date.year)
#===end of frequently used functions===
        
#===curve building===
def buildHistCurve(date, index_type):
    swap_rates, curve_tenor, swap_helpers = [],[],[]
    calc_date = ql.Date(date.day, date.month,date.year)
    ql.Settings.instance().evaluationDate = calc_date
    #irs are settled T+1
    settle_date = calendar.advance(calc_date, 1, ql.Days, business_convention)
    if 'Shibor' in index_type:
        swap_rates = s3mclosingdb.loc[date]
    else:
        swap_rates = fr007closingdb.loc[date]
    if 'Shibor' in index_type:
        curve_tenor = [
            ql.Period('3M'),ql.Period('6M'),ql.Period('9M'),ql.Period('1Y'),
            ql.Period('2Y'),
            ql.Period('3Y'),ql.Period('4Y'),ql.Period('5Y'),ql.Period('7Y'),
            ql.Period('10Y')
            ]
    elif 'FR007' in index_type:
        curve_tenor = [
            ql.Period('1W'),ql.Period('1M'),ql.Period('3M'),ql.Period('6M'),
            ql.Period('9M'),
            ql.Period('1Y'),ql.Period('2Y'),ql.Period('3Y'),ql.Period('4Y'),
            ql.Period('5Y'),
            ql.Period('7Y'),ql.Period('10Y')
            ]
    #use a fake index so that swap helpers can produce correct target swaps
    fake_china_index = ql.IborIndex('fake',ql.Period('3M'),1,
                           currency,calendar,ql.ModifiedFollowing,
                           False,
                           float_day_count if 'Shibor' in index_type else day_count
                           )
    swap_helpers = []
    #create swap helpers for bootstrapping
    for rate,tenor in list(zip(swap_rates, curve_tenor)):
        swap_helpers.append(ql.SwapRateHelper(ql.QuoteHandle(ql.SimpleQuote(
                #only Shibor3M 3months tenor quote follows actual360 convention
                  rate/100 * (365/360 if 
                               ('Shibor' in index_type and tenor == ql.Period('3M'))
                              else 1
                            )
                )),
                                          tenor, calendar,
                                          coupon_freq,
                                          business_convention, 
                                          day_count,
                                          fake_china_index
        ))
        
    yield_curve = ql.PiecewiseLogCubicDiscount(settle_date, swap_helpers,
                                          day_count)
    
    discountTermStructure = ql.RelinkableYieldTermStructureHandle()
    forecastTermStructure = ql.RelinkableYieldTermStructureHandle()
    discountTermStructure.linkTo(yield_curve)
    forecastTermStructure.linkTo(yield_curve)
    
    swap_engine = ql.DiscountingSwapEngine(discountTermStructure)
    swap_index = ql.IborIndex(index_type+str(calc_date),ql.Period('3M'),1,
                           currency,calendar,ql.ModifiedFollowing,
                           False,
                           float_day_count if 'Shibor' in index_type
                           else day_count,
                           forecastTermStructure
                           )
    
    #add fixing
    closingdb = s3mclosingdb if 'Shibor' in index_type else fr007closingdb
    for fixingdate in closingdb.index:
        if fixingdate < date:
            swap_index.addFixing(getqlDate(fixingdate),
                                 closingdb.loc[fixingdate][0]/100)
    
    return (yield_curve, swap_engine, swap_index)
#===end of curve building===
    
#===create swaps===
def createSwap(calc_date, periodstr, histyc,
               notional = 100000000, fixed_rate = 0.0):
    settle_date = calendar.advance(calc_date, 1, ql.Days, business_convention)
    maturity_date = calendar.advance(settle_date, ql.Period(periodstr),
                                     ql.ModifiedFollowing)
    return createSwapWithDate(settle_date, maturity_date, histyc,
                              notional, fixed_rate)

def createSwapWithDate(settle_date, maturity_date, histyc,
                       notional = 100000000, fixed_rate = 0.0):
    yield_curve, swap_engine, swap_index = histyc[0], histyc[1], histyc[2]
    fixed_schedule = ql.Schedule(settle_date, maturity_date, 
                             coupon_tenor, calendar, business_convention,
                             business_convention, ql.DateGeneration.Forward,
                             False)
    float_schedule = ql.Schedule(settle_date, maturity_date,
                             coupon_tenor, calendar, business_convention,
                             business_convention, ql.DateGeneration.Forward,
                             False)
    mySwap = ql.VanillaSwap(
            ql.VanillaSwap.Receiver if notional > 0 else ql.VanillaSwap.Payer
            , abs(notional), fixed_schedule,
            fixed_rate, day_count, float_schedule, swap_index,
            0,
            float_day_count if 'Shibor' in swap_index.name()
                         else day_count
            )
    mySwap.setPricingEngine(swap_engine)
    return mySwap
#===end of create swaps===
    
#===calculate leg NPV with compounding===
def updateSwap(newswap, histyc):
    yield_curve, swap_engine, swap_index = histyc[0], histyc[1], histyc[2]
    swap, drct = newswap[1], newswap[2]
    updatedSwap = ql.VanillaSwap(
            ql.VanillaSwap.Receiver if drct == 1 else ql.VanillaSwap.Payer,
            swap.nominal(),
            swap.fixedSchedule(),
            swap.fixedRate(),
            day_count,
            swap.floatingSchedule(),
            swap_index,
            0,
            float_day_count if 'Shibor' in swap_index.name() else day_count
            ) 
    updatedSwap.setPricingEngine(swap_engine)
    return updatedSwap    

def calcFloatingLegNPV(calc_date, newswap, histyc):
    yield_curve, swap_engine, swap_index = histyc[0], histyc[1], histyc[2]
    swap, drct = newswap[1], newswap[2]
    swap = updateSwap(newswap, histyc)
    closingdb = s3mclosingdb if 'Shibor' in swap_index.name() else fr007closingdb
    #schedule for each quarter
    coupon_schedule = [x for x in swap.floatingSchedule()]
    floatingNPV = 0
    for i in range(0,len(coupon_schedule)-1):
        start_date = coupon_schedule[i]
        end_date = coupon_schedule[i+1]
        #schedule for each week
        accrual_schedule = [x for x in ql.Schedule(start_date,end_date,
                                                   ql.Period(ql.Weekly),
                                                   calendar,
                                   business_convention, business_convention,
                                   ql.DateGeneration.Forward, False)]
        accrual_rate = 1
        if 'Shibor' in swap_index.name():
            #simple interest for shibor irs so there is only one period 
            accrual_schedule = [start_date, end_date] 
        for j in range(0,len(accrual_schedule)-1):
                accrual_start_date = accrual_schedule[j]
                accrual_end_date = accrual_schedule[j+1]
                rate = 0.0
                if accrual_start_date > calc_date:
                    #get the forward rate within weekly period through fair rate
                    ss = createSwapWithDate(accrual_start_date, accrual_end_date, 
                                  histyc)
                    rate = ss.fairRate()
                    if 'Shibor' in swap_index.name():
                        rate = rate*360/365
                else:
                    #historical
                    rate = closingdb.loc[getDatetime(
                            calendar.advance(accrual_start_date,-1,ql.Days,business_convention)
                                                 )][0]/100
                rate = rate * (accrual_end_date - accrual_start_date) / (
                            360 if 'Shibor' in swap_index.name() else 365
                        )
                accrual_rate = accrual_rate * (1+rate)
        cf = swap.nominal()*(accrual_rate-1)
        df = 1
        if end_date > calendar.advance(calc_date,1,ql.Days,business_convention):
            df = yield_curve.discount(end_date)
        dsctcf = cf * df
        if drct == 1:
            dsctcf = dsctcf * -1
        floatingNPV = floatingNPV+dsctcf
    return floatingNPV

def calcFixedLegNPV(calc_date, newswap, histyc):
    yield_curve, swap_engine, swap_index = histyc[0], histyc[1], histyc[2]
    swap, drct = newswap[1], newswap[2]
    swap = updateSwap(newswap, histyc)
    coupon_schedule = [x for x in swap.floatingSchedule()]
    fixedNPV = 0
    for i in range(0,len(coupon_schedule)-1):
        start_date = coupon_schedule[i]
        end_date = coupon_schedule[i+1]
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

def calcNPV(calc_date, newswap, histyc):
    ql.Settings.instance().evaluationDate = calc_date
    return calcFloatingLegNPV(calc_date, newswap, histyc) + calcFixedLegNPV(calc_date, newswap, histyc)
#===end of calculate leg NPV with compounding===

#===backtesting tool===
def newSwap(calc_date, periodstr, histyc, notional = 100000000, fixed_rate = 0.0):
    newswap = createSwap(calc_date, periodstr, histyc,
                         notional = notional, fixed_rate = fixed_rate)
    index_type = 'Shibor3M' if 'Shibor' in histyc[2].familyName() else 'FR007'
    return (index_type, newswap, np.sign(notional))

def getClosing(calc_date, index_type, periodstr):
    fr007index = {'1W':0,'1M':1,'3M':2,'6M':3,'9M':4,
                  '1Y':5,'2Y':6,'3Y':7,'4Y':8,'5Y':9,'7Y':10,'10Y':11}
    s3mindex = {'3M':0,'6M':1,'9M':2,'1Y':3,'2Y':4,
                '3Y':5,'4Y':6,'5Y':7,'7Y':8,'10Y':9}
    if index_type == 'FR007':
        return fr007closingdb[getDatetime(calc_date)][fr007index[periodstr]]/100
    elif index_type == 'Shibor3M':
        return s3mclosingdb[getDatetime(calc_date)][s3mindex[periodstr]]/100

#
#printFixedLegCF printFloatingLegCF and printCashflow are designed to print
#the cashflow detail of a given swap
#

def printFixedLegCF(calc_date, newswap, histyc):
    yield_curve, swap_engine, swap_index = histyc[0], histyc[1], histyc[2]
    swap, drct = newswap[1], newswap[2]
    swap = updateSwap(newswap, histyc)
    coupon_schedule = [x for x in swap.floatingSchedule()]
    for i in range(0,len(coupon_schedule)-1):
        start_date = coupon_schedule[i]
        end_date = coupon_schedule[i+1]
        rate = swap.fixedRate() * (end_date - start_date) / 365
        cf = swap.nominal() * rate
        print(start_date,'->',end_date,'(%.0fd)'%(end_date - start_date),', rate = %.4f'%(swap.fixedRate()*100),
              '%%, cf = %.2f'%cf)

def printFloatingLegCF(calc_date, newswap, histyc):
    yield_curve, swap_engine, swap_index = histyc[0], histyc[1], histyc[2]
    swap, drct = newswap[1], newswap[2]
    swap = updateSwap(newswap, histyc)
    daycount = 360 if 'Shibor' in swap_index.name() else 365
    closingdb = s3mclosingdb if 'Shibor' in swap_index.name() else fr007closingdb
    #schedule for each quarter
    coupon_schedule = [x for x in swap.floatingSchedule()]
    for i in range(0,len(coupon_schedule)-1):
        start_date = coupon_schedule[i]
        end_date = coupon_schedule[i+1] 
        #schedule for each week
        accrual_schedule = [x for x in ql.Schedule(start_date,end_date,
                                                   ql.Period(ql.Weekly),
                                                   calendar,
                                   business_convention, business_convention,
                                   ql.DateGeneration.Forward, False)]
        accrual_rate = 1
        if 'Shibor' in swap_index.name():
            #simple interest for shibor irs so there is only one period 
            accrual_schedule = [start_date, end_date] 
        for j in range(0,len(accrual_schedule)-1):
                accrual_start_date = accrual_schedule[j]
                accrual_end_date = accrual_schedule[j+1]
                fixing_date = calendar.advance(accrual_start_date,-1,ql.Days,
                                               business_convention)
                rate = 0.0
                if accrual_start_date > calc_date:
                    #get the forward rate within weekly period through fair rate
                    ss = createSwapWithDate(accrual_start_date, accrual_end_date, 
                                  histyc)
                    rate = ss.fairRate()
                    if 'Shibor' in swap_index.name():
                        rate = rate*360/365
                else:
                    #historical
                    rate = closingdb.loc[getDatetime(
                            calendar.advance(accrual_start_date,-1,ql.Days,
                                             business_convention)
                                                 )][0]/100
                rate = rate * (accrual_end_date - accrual_start_date) / daycount
                accrual_rate = accrual_rate * (1+rate)
                print(accrual_start_date,' -> ',accrual_end_date,
                      '(%.0fd)'%(accrual_end_date - accrual_start_date),
                      ', fixing = %.4f'%(rate/(accrual_end_date - accrual_start_date)
                      *daycount*100),
                      '%, fixing_date = ',fixing_date,
                      end = '')
                fixing_date = getDatetime(fixing_date)
                if fixing_date.weekday() == 5 or fixing_date.weekday() == 6:
                    print ('(%s)'%('saturdaty' if fixing_date.weekday()==5 else 'sunday'),
                      end = '')
                if accrual_start_date <= calc_date:
                    print('(historical)')
                else:
                    print()
        cf = swap.nominal()*(accrual_rate-1)
        print('sum: ',start_date,' -> ',end_date,'(%.0fd)'%(end_date - start_date),', rate = %.4f'%((accrual_rate-1)/(end_date - start_date)*
                               daycount*100),'%%, cf = %.2f'%cf)

def printCashflow(calc_date, newswap, histyc):
    ql.Settings.instance().evaluationDate = calc_date
    yield_curve, swap_engine, swap_index = histyc[0], histyc[1], histyc[2]
    swap, drct = newswap[1], newswap[2]
    print('cashflows of fixed leg: ')
    printFixedLegCF(calc_date, newswap, histyc)
    print('cashflows of floating leg: ')
    printFloatingLegCF(calc_date, newswap, histyc)
    
def saveClosing():
    f = open('fr007.dat','wb')
    pickle.dump(fr007closingdb,f)
    f.close()
        
    f = open('s3m.dat','wb')
    pickle.dump(s3mclosingdb,f)
    f.close()
    
#===end of backtesting tool===