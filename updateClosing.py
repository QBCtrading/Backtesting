def getShibor3MClosing(date):
    print('Shibor3M: ',date)
    data = w.edb("M1001858,\
                 M1004091,\
                 M1004092,\
                 M1004093,\
                 M1004094,\
                 M1004095,\
                 M1004096,\
                 M1004097,\
                 M1004098,\
                 M1004099"
                 ,date.strftime('%Y-%m-%d'), 
                 date.strftime('%Y-%m-%d'),"Fill=Previous")
    ret = []
    if len(data.Data[0]) != 10:
        ret = []
        for i in data.Data:
            ret.append(i[1])
    else:
        ret = data.Data[0]
    print('Cftes closing: ',ret)
    return ret

def getFR007Closing(date):
    print('FR007: ',date)
    data = w.edb("M1001846,\
M1004122,\
M1004123,\
M1004124,\
M1004125,\
M1004126,\
M1004127,\
M1004128,\
M1004129,\
M1004130,\
M1004131,\
M1004132"
                 ,date.strftime('%Y-%m-%d'), 
                 date.strftime('%Y-%m-%d'),"Fill=Previous")
    ret = []
    if len(data.Data[0]) != 12:
        ret = []
        for i in data.Data:
            ret.append(i[1])
    else:
        ret = data.Data[0]
    print('Cftes closing: ',ret)
    return ret

#***start to update closing

l = pd.Series()
start = ql.Date(10,8,2018)
end = ql.Date(14,8,2018)
#end = getqlDate(datetime.date.today())

schedule = ql.Schedule(start,end,ql.Period(ql.Daily),
                       calendar, business_convention, business_convention,
                       ql.DateGeneration.Forward, False)

for calc_date in schedule:
    date = getDatetime(calc_date)
    if date not in fr007closingdb.index:
        l[date] = getFR007Closing(date)
fr007closingdb = fr007closingdb.append(l)

l = pd.Series()
for calc_date in schedule:
    date = getDatetime(calc_date)
    if date not in s3mclosingdb.index:
        l[date] = getShibor3MClosing(date)
s3mclosingdb = s3mclosingdb.append(l)

#output
f = open('fr007.dat','wb')
pickle.dump(fr007closingdb,f)
f.close()
    
f = open('s3m.dat','wb')
pickle.dump(s3mclosingdb,f)
f.close()