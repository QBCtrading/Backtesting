# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 10:16:22 2018

@author: DUYONGLIANG366
"""
import numpy as np
import math

df = pd.DataFrame(np.random.randn(4, 5), columns=['A', 'B', 'C', 'D', 'E'])
df
df['Col_sum'] = df.apply(lambda x: x.sum(), axis=1)

df['Col_diff'] = df['A'] - df['A']
df['Col_inter'] = int(df['A'])

df['Col_inter'] = df['Col_sum'].apply(lambda x: x - math.floor(x))
df['Col_inter']


df['check'] = df['Col_sum'].apply(lambda x: isinstance(x, str))