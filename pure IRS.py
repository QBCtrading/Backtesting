#make sure start and end are weekdays
start = ql.Date(14,8,2018)
end = ql.Date(15,8,2018)
schedule = ql.Schedule(start,end,ql.Period(ql.Daily),calendar, business_convention, business_convention,
                       ql.DateGeneration.Forward, False)
swaps = []
pnl = pd.Series()

schedule = [ql.Date(14,8,2018)]

for calc_date in schedule:
    #building curves
    r007 = buildHistCurve(getDatetime(calc_date), 'FR007')
    s3m = buildHistCurve(getDatetime(calc_date), 'Shibor3M')
    
    #strategy
    
    # shibor 9m x 12m flatten
    swaps.append(
            newSwap(ql.Date(7,8,2018),'6M',s3m,
                   fixed_rate = 0.0311, notional = 1000000000)
            )
    swaps.append(
            newSwap(ql.Date(7,8,2018),'6M',s3m,
                   fixed_rate = 0.0309775, notional = -1000000000)
            )
    
    #end of strategy

    #calculate daily npv
    NPV = 0
    for newswap in swaps:
        if 'FR007' in newswap[0]:
            NPV = NPV + calcNPV(calc_date, newswap, r007)
        elif 'Shibor3M' in newswap[0]:
            NPV = NPV + calcNPV(calc_date, newswap, s3m)
    pnl[getDatetime(calc_date)] = NPV
    print(calc_date,' : ',NPV)