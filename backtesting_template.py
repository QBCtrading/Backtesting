#make sure start and end are weekdays
start = ql.Date(16,3,2018)
end = ql.Date(24,3,2018)
schedule = ql.Schedule(start,end,ql.Period(ql.Daily),calendar, business_convention, business_convention,
                       ql.DateGeneration.Forward, False)
swaps = []
pnl = pd.Series()

for calc_date in schedule:
    #building curves
    r007 = buildHistCurve(getDatetime(calc_date), 'FR007')
    s3m = buildHistCurve(getDatetime(calc_date), 'Shibor3M')
    
    #strategy code
    
    if calc_date == start:
        rate = getClosing(calc_date, 'FR007', '1Y')/100
        swap = newSwap(calc_date, '1Y', r007, fixed_rate = rate)
        swaps.append(swap)
    


    #calculate daily npv
    NPV = 0
    for swap in swaps:
        if 'FR007' in swap[0]:
            NPV = NPV + calcNPV(calc_date, swap[1], swap[2], r007)
        elif 'Shibor3M' in swap[0]:
            NPV = NPV + calcNPV(calc_date, swap[1], swap[2], s3m)
    pnl[getDatetime(calc_date)] = NPV
    
    print(calc_date,' : ',NPV)