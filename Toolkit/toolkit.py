


def plotForwardCurve(calc_date,histyc):
    step = 0.01
    yield_curve, swap_engine, swap_index = histyc[0], histyc[1], histyc[2]
    print('yield_curve dates:',yield_curve.dates()[0])
    l = []
    for i in np.arange(0,10,step):
        l.append(yield_curve.forwardRate(i,i+step,ql.Compounded).rate())
    ts = pd.Series(l)
    ts.index = np.arange(0,10,step)
    plt.subplot(211)
    plt.plot(ts,drawstyle='steps-pre')
    
    l = []
    for i in range(1,121):
        l.append(createSwap(calc_date, str(i)+'M', histyc).fairRate())
    ts = pd.Series(l)
    ts.index = np.arange(0.0833,10,0.08333)
    plt.subplot(212)
    plt.plot(ts,drawstyle='steps-pre')
    plt.subplot(211)
    plt.title('Forward and Swap Curve: '+str(calc_date))

def checkCalibration(start_date, end_date, index_type):
    schedule = ql.Schedule(start,end,ql.Period(ql.Daily),calendar, business_convention, business_convention,
                           ql.DateGeneration.Forward, False)
    calc_dates = [x for x in schedule]
    dates = [datetime.date(x.year(), x.month(), x.dayOfMonth()) for x in calc_dates]
    
    for date in dates:
        print(date)
        calc_date = ql.Date(date.day, date.month,date.year)
        histyc = buildHistCurve(date,index_type)
        #for tenor in ['3M']:
        for tenor in ['3M','1Y','2Y','3Y','4Y','5Y']:
            swap = createSwap(calc_date,tenor,histyc,
                              fixed_rate = createSwap(calc_date,tenor,histyc).fairRate()
                              )
            print('npv: ',swap.NPV())
            npv = calcNPV(calc_date,swap,1,histyc)
            print(tenor,' fairRate: ',swap.fairRate()*100,', npv = ',npv)


    
    




start = ql.Date(9,7,2018)
end = ql.Date(10,7,2018)
schedule = ql.Schedule(start,end,ql.Period(ql.Daily),calendar, business_convention, business_convention,
                       ql.DateGeneration.Forward, False)
for calc_date in schedule:
    if(calc_date.dayOfMonth()==15): print(calc_date)
    r7d = buildHistCurve(getDatetime(calc_date), 'FR007')
    plotForwardCurve(calc_date, r7d)
    plt.pause(0.001)
    plt.clf()

df = pd.DataFrame()
for calc_date in schedule:
    if(calc_date.dayOfMonth()==15): print(calc_date)
    yield_curve, swap_engine, swap_index = buildHistCurve(getDatetime(calc_date), 'FR007')
    df.loc[getDatetime(calc_date), 'yield_curve'] = yield_curve
    df.loc[getDatetime(calc_date), 'swap_engine'] = swap_engine
    df.loc[getDatetime(calc_date), 'swap_index'] = swap_index
    
    
    

start = ql.Date(7,3,2017)
end = ql.Date(10,7,2017)
schedule = ql.Schedule(start,end,ql.Period(ql.Daily),calendar, business_convention, business_convention,
                       ql.DateGeneration.Forward, False)
swaps = []
pnl,bp = [],[]
for calc_date in schedule:
    print(calc_date,' 5Y closing: ',fr007closingdb[getDatetime(calc_date)][9])
    r007 = buildHistCurve(getDatetime(calc_date), 'FR007')
    if calc_date == ql.Date(7,3,2017):
        swaps.append(
                (createSwap(calc_date,'5Y',r007, fixed_rate = fr007closingdb[getDatetime(calc_date)][9]/100), 1)
                )
        print('dv01: ',swaps[0][0].floatingLegBPS())
    NPV = 0
    for swap in swaps:
        drct = swap[1]
        swap = (updateSwap(swap[0],swap[1],r007),drct)
        NPV = NPV + calcNPV(calc_date, swap[0], swap[1], r007)
    pnl.append(NPV)
    bp.append(fr007closingdb[getDatetime(calc_date)][9])
    print(calc_date,' : ',NPV)
    
pnlst = pd.Series(pnl)
pnlst = pnlst.diff()
bpst = pd.Series(bp)
bpst = bpst.diff()*100
pnlst/bpst