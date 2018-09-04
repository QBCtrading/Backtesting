# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""


import pandas as pd
import os
import math
import numpy as np
import math
os.getcwd()

df = pd.read_csv('150201.IB.csv', header=0)
df.columns

df[(df.EventTime > 41100) & (df.EventTime < 43102)]


files = [XXXX,XXX]
list_ = []
for file in files:         
     with codecs.open(file, "r", "utf-8") as f:
            for line in f:
                content = line.strip().split('\t')
                # 对每一行的内容进行处理
                text = function_f(content)
                list_.append(pd.DataFrame(text,columns=[],index=[]))  # Series对象也可
raw_data = pd.concat(list_)



import os
import pandas as pd


timeRange = pd.read_csv(r'D:\git_root\issueTime.csv', header=None)

timeRange[0][0]
for row in timeRange.iterrows():
    print(row[1][0])
    print(row[1][1])
    print("=======")
    

path = os.listdir('D:\git_root\Backtesting\RawData\BondAdjustedData')
path[0]
domain = os.path.abspath(r'D:\git_root\Backtesting\RawData\BondAdjustedData')

info = os.path.join(domain,path[0])
info

result = pd.read_csv(info)


for info in os.listdir('D:\git_root\Backtesting\RawData\BondAdjustedData'):
    domain = os.path.abspath(r'D:\git_root\Backtesting\RawData\BondAdjustedData') #获取文件夹的路径
    info = os.path.join(domain,info) #将路径与文件名结合起来就是每个文件的完整路径  
    data = pd.read_csv(info)
    result = result.append(data)
    
result['check'] = result['adjMidTime'].apply(lambda x: isinstance(x, str))

result['check'][0] == False

result = result[result['check'] == False]
result
result.sort_values(['inst','adjMidTime'],ascending=[1,0],inplace=True)

result.to_csv ("rawResult.csv" , encoding = "utf-8")　


result['diffNum'] = result['adjMidTime'].apply(lambda x: x - math.floor(x))
result.diffNum

temp = result[(result.diffNum > 0.60764) & (result.diffNum < 0.625)]
temp

temp2 = result[(result.diffNum > 0.39931) & (result.diffNum < 0.41667)]
temp2

temp3 = result[(result.diffNum > 0.42708) & (result.diffNum < 0.44444)]
temp3

finalfinal = temp.append(temp2)
finalfinal = finalfinal.append(temp3)
finalfinal['date'] = finalfinal['adjMidTime'].apply(lambda x: math.floor(x))
finalfinal.sort_values(['inst','date'],ascending=[1,0],inplace=True)

finalfinal.to_csv ("finalfinal.csv" , encoding = "utf-8")　


grouped=finalfinal.groupby(['inst', 'date']).head(1)
grouped
grouped.to_csv ("grouped.csv" , encoding = "utf-8")　


timeRange[0][0]
final2 = result[(result.adjMidTime > 10000) & (result.adjMidTime < 0)]

for row in timeRange.iterrows():
    temp = result[(result.adjMidTime > row[1][0]) & (result.adjMidTime < row[1][1])]
    final2 = final2.append(temp)
final2[final2.inst == '150201.IB']

final2.sort_values(['inst','adjMidTime'],ascending=[1,0],inplace=True)
final2.to_csv ("testfoo2.csv" , encoding = "utf-8")　   

final2['diff'] = final2['adjMidTime'].apply(lambda x: x - math.floor(x))

final = result[(result.TimeDiff > 0.5) & (result.TimeDiff < 0.625)]



final2.sort_values(['inst','adjMidTime'],ascending=[1,0],inplace=True)

final2['date']
final2['inst', "date"]


grouped=final2.groupby(['inst', 'date']).head(1)
grouped

grouped.to_csv ("grouped.csv" , encoding = "utf-8")　
for key in grouped:
    print(key)
    
    
    