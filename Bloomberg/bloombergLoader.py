# -*- coding: utf-8 -*-
"""
Created on Mon Sep  3 17:17:05 2018

@author: DUYONGLIANG366
"""

import blpapi
import datetime as dt
import pytz
import pandas as pd

def plotYld(ts):
    ts.index = [str(idx) for idx in ts.index]
    ts.plot()

sessionOptions = blpapi.SessionOptions()
sessionOptions.setServerHost('localhost')
sessionOptions.setServerPort(8194)

session = blpapi.Session(sessionOptions)
session.start()

session.openService("//blp/refdata")
refDataService = session.getService("//blp/refdata")

pytz.country_timezones('cn')
tz = pytz.timezone('Asia/Shanghai')
startTime = dt.datetime(2018,8,25,8,30, tzinfo=tz)
#startTime = dt.datetime(2018,8,31,1,32)
endTime = dt.datetime(2018,8,31,18,30, tzinfo=tz)
#endTime = dt.datetime(2018,8,31,17,32)


startTime += dt.timedelta(hours=-8)
endTime += dt.timedelta(hours=-8)
fmt = "%Y-%m-%d %H:%M:%S %Z%z"
startTime.strftime(fmt)
endTime.strftime(fmt)


tzUS = pytz.timezone('America/New_York')

securities = ['180204.IB']
sources = ['TPCY']
#sources = ['TPCY','CFIY','PTCN','CBBJ','CCTC']

tick = pd.DataFrame()

for security in securities:
    for source in sources:
        for TYPE in ['TRADE','BID','ASK']:
            try: 
                request = refDataService.createRequest("IntradayTickRequest")
                request.set("security", security+' @'+source+' Corp')
                request.getElement("eventTypes").appendValue(TYPE)
                request.set("includeConditionCodes", True)
                request.set("startDateTime", startTime)
                request.set("endDateTime", endTime)
                
                print "Sending Request:", request
                session.sendRequest(request)
            
                ret = pd.DataFrame()
                
                while(True):
                    ev = session.nextEvent(500)
                    if ev.eventType() == blpapi.Event.RESPONSE or ev.eventType() == blpapi.Event.PARTIAL_RESPONSE:
                        break

                ret = pd.DataFrame()
                for msg in ev:
                    rows = msg.getElement('tickData').getElement('tickData').values()
                    for row in rows:
                        tmp = {str(field.name()) : [field.getValue()] for field in row.elements()}
                        tmp = pd.DataFrame(tmp).set_index('time')
                        print(tmp.index[0].astimezone(tz))
                        ret = ret.append(tmp)
                ret.index = [idx.astimezone(tz) for idx in ret.index]
                ret['code'] = security
                ret['source'] = source
                ret['TYPE'] = TYPE
                ret = ret.drop(['type'], axis = 1)
                ret = ret[ret['value']!=0]
                tick = tick.append(ret)
            except:
                continue

tick = tick.sort_index()


session.stop()
