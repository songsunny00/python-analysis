#!/usr/bin/env python
# coding: utf-8

# In[1]:


#1先算每个人的总账
#2理清每个人的关联人
#3就是从关联人里遍历
#dict.__contains__(key)
#list.append('Google')
#list.count(obj)

import pandas as pd
import numpy as np
df = pd.read_csv(r'D:\MyCode\Python\ljj\Task4_Transactions.csv')

#dict1总账
#dict2关联人
dict1, dict2 = {}, {}
for i in range(0, len(df)):
	name_out = df.iloc[i]['out_acc']
	name_in = df.iloc[i]['in_acc']
	money = df.iloc[i]['amount']
	#算总账\算关联人
	if dict1.__contains__(name_out):
		dict1[name_out] = dict1[name_out]-money
		if dict2[name_out] and dict2[name_out].count(name_in)<1:
			dict2[name_out].append(name_in)
	else:
		dict1[name_out] = -money
		dict2[name_out] = [name_in]
		
	if dict1.__contains__(name_in):
		dict1[name_in] = dict1[name_in]+money
		if dict2[name_in] and dict2[name_in].count(name_out)<1:
			dict2[name_in].append(name_out)
	else:
		dict1[name_in] = money
		dict2[name_in] = [name_out]
print(dict1)
#新建dataframe-final，用于存储最终结果
final = pd.DataFrame(columns=('out_acc', 'in_acc', 'amount'))

for name in dict2:
	if dict2[name]==0:
		continue
	for relative_name in dict2[name]:
		extra = dict1[name]+dict1[relative_name] #两者之间差额
		if extra==0:
			#刚好相加为0，互还即可，dict1里清0
			if dict1[name]>0: 
				final=final.append([{'in_acc':name,'out_acc':relative_name,'amount':dict1[name]}], ignore_index=True)
			if dict1[name]<0: 
				final=final.append([{'in_acc':relative_name,'out_acc':name,'amount':-dict1[name]}], ignore_index=True)
			dict1[name] = 0
			dict1[relative_name] = 0
			break
		elif dict1[name]>0 and extra<dict1[name]:
			#主帐号收钱，关联账号欠钱，从欠钱账号拿，直到dict1里清0
			if extra>0:
				final=final.append([{'in_acc':name,'out_acc':relative_name,'amount':-dict1[relative_name]}], ignore_index=True)
				dict1[relative_name] = 0
				dict1[name] = extra
			else:
				final=final.append([{'in_acc':name,'out_acc':relative_name,'amount':dict1[name]}], ignore_index=True)
				dict1[name] = 0
				dict1[relative_name] = extra
				break
		elif dict1[name]<0 and extra>dict1[name]:
			#主帐号欠钱，关联账号收钱，从收钱账号拿，直到dict1里清0
			if extra<0:
				final=final.append([{'in_acc':relative_name,'out_acc':name,'amount':dict1[relative_name]}], ignore_index=True)
				dict1[relative_name] = 0
				dict1[name] = extra
			else:
				final=final.append([{'in_acc':relative_name,'out_acc':name,'amount':-dict1[name]}], ignore_index=True)
				dict1[name] = 0
				dict1[relative_name] = extra
				break
final.drop_duplicates(subset=['out_acc','in_acc'],keep='first',inplace=True)#去除重复项
print(final)
final.to_csv(r'D:\MyCode\Python\ljj\Task4_Result.csv')
	


# In[ ]:




