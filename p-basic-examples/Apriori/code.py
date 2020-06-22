#!/usr/bin/env python
# coding: utf-8
import itertools
import numpy as np
import pandas as pd
from tkinter import * #面向对象的GUI工具包
import tkinter.filedialog
import tkinter.messagebox

# 1：导入数据
# 2：过滤数据-不考虑多次购买同一件物品，删除重复数据
# 3：过滤数据-按订单分组，只有1件商品的没有意义，需要进行过滤
# 4：基础数据：标准化项集itemSets（需要分析的有效商品集按订单维度）
# 5: 基础数据： 有效商品集item
# 6：计算：频繁集商品的单独support率-Item_support_dict（字典对象）
# 7: 组合：频繁集商品组合
# 8：计算：计算各个组合支持度
# 9：计算：计算各个组合（主商品、相关商品）可信度
# 10:输出：满足关联支持度和可信度的商品列表

#算法Apriori
class Apriori(object):
  def __init__(self,itemSets,savePath,minSupport=0.04,minConf=0.7):
    self.itemSets=itemSets
    self.minSupport=minSupport
    self.minConf =minConf
    self.savePath = savePath
    self.__Initialize()

  def __Initialize(self):
    '''获取项目元素列表item'''
    self.item = []
    for itemSet in self.itemSets:
        for item in itemSet:
            if item not in self.item:
                self.item.append(item)
    self.item.sort()
    '''1将项集转为pandas.DataFrame数据类型'''
    '''2过滤掉非频繁项集的任何超集都不是频繁项集'''
    '''3计算频繁项集的单品的支持度'''
    self.data = pd.DataFrame(columns=self.item)
    for i in range(len(self.itemSets)):
      self.data.loc[i, self.itemSets[i]] = 1
    
    self.L1 = self.data.loc[:, self.data.sum(axis=0) / len(self.itemSets) >= self.minSupport]
    self.Item_support_dict = dict(self.L1.sum(axis=0) / len(self.itemSets))

    '''开始计算各个组合支持度-得到support_selects-P(Item,Recomend)'''
    self.__support_selects()

    '''item_Conf-单个商品支持度和组合支持度的集合-P(Item,Recomend),P(Item)'''
    self.item_Conf = self.Item_support_dict.copy()
    self.item_Conf.update(self.support_selects)

    '''开始计算各个组合可信度-得到confidence_selects-计算公式：P(Item,Recomend)/P(Item)'''
    self.__confidence_selects()

    '''输出表格'''
    self.printExcel()

  def __support_selects(self):
    '''随机组合，计算组合的支持度，留下符合minSupport的组合'''
    '''根据L1创建多项频繁项集Lk，非频繁项集的任何超集都不是频繁项集'''
    self.support_selects = {}  # 用于储存满足支持度的频繁项集
    last_support_selects_dict = self.Item_support_dict.copy()  # 第一轮两两组合，last_support_selects组合基本元素只一
    while last_support_selects_dict:
        new_support_selects_dict = {}
        for last_support_select in last_support_selects_dict.keys():
            for L1_support_name in set(self.L1.columns) - set(last_support_select.split(',')):
                columns = sorted([L1_support_name] + last_support_select.split(','))  # 新的列名：合并后排序
                count = (self.L1.loc[:, columns].sum(axis=1) == len(columns)).sum()
                if count / len(self.itemSets) >= self.minSupport:
                    new_support_selects_dict[','.join(columns)] = count / len(self.itemSets)
        self.support_selects.update(new_support_selects_dict)
        last_support_selects_dict = new_support_selects_dict.copy()  # 作为新的 Lk，进行下一轮更新

  def __confidence_selects(self):
    '''生成关联规则，其中support_selects已经按照长度大小排列'''
    self.confidence_selects = {}  # 用于储存满足自信度的关联规则
    for groups, Supp_groups in self.support_selects.items():
        groups_list = groups.split(',')
        for recommend_len in range(1, len(groups_list)):
            for recommend in itertools.combinations(groups_list, recommend_len): # combinations('ABCD', 2) --> AB AC AD BC BD CD
                items = ','.join(sorted(set(groups_list) - set(recommend)))
                Conf = Supp_groups / self.item_Conf[items]
                if Conf >= self.minConf:
                    self.confidence_selects.setdefault(items, {})
                    self.confidence_selects[items].setdefault(','.join(recommend),{'Support': Supp_groups, 'Confidence': Conf})
    
  def printExcel(self,**kwargs):
    if kwargs.get('data'):
      select = kwargs['data']
    else:
      select = self.confidence_selects
    
    items = [] # index
    value = [] # 值
    for ks, vs in select.items():
        items.extend(list(zip([ks] * vs.__len__(), vs.keys())))
        for v in vs.values():
            value.append([v['Support'], v['Confidence']])
    index = pd.MultiIndex.from_tuples(items, names=['Items', 'Recommend'])
    self.result = pd.DataFrame(value, index=index, columns=['Support', 'Confidence'])
    self.result.to_excel(r''+self.savePath)
    tkinter.messagebox.showinfo('提示', '分析成功！！！')

#图形化类-输入：excel路径，最小支持度，最小自信度
class MY_GUI():
  def __init__(self,init_window_tk):
    self.init_window_tk=init_window_tk
    
    #文件路径
    self.get_value = StringVar()
    
    #获取最小支持度
    self.get_support_value = StringVar()
    
    #获取最小自信度
    self.get_confidence_value = StringVar()
    
  #设置窗口
  def set_init_window(self):
    self.init_window_tk.title("Apriori")
    self.center_window(self.init_window_tk,400,240)
    
    labelframe = LabelFrame(text="配置")
    labelframe.grid(column=4, row=8, padx=20, pady=20)
    
    self.label = Label(labelframe,text="选择Excel：").grid(column=0,row=1)
    self.path = Entry(labelframe,width=30,textvariable = self.get_value).grid(column=1,row=1)
    self.file = Button(labelframe,text="浏览",command=self.add_mm_file,width=6).grid(column=2,row=1,pady=5,padx=2)
        
    self.min_support_text = Label(labelframe,text="最小支持度：").grid(column=0,row=2)
    self.min_support_input = Entry(labelframe,width=30,textvariable = self.get_support_value)
    self.min_support_input.bind("<KeyRelease>",lambda event:self.validateText('get_support_value'))
    self.min_support_input.grid(column=1,row=2,pady=5)
    
    self.min_conf_text = Label(labelframe,text="最小自信度：").grid(column=0,row=3)
    self.min_conf_input = Entry(labelframe,width=30,textvariable = self.get_confidence_value)
    self.min_conf_input.bind("<KeyRelease>",lambda event:self.validateText('get_confidence_value'))
    self.min_conf_input.grid(column=1,row=3,pady=5)

    self.submit = Button(labelframe,text="开始分析",command=self.startAnalysis,width=40).grid(column=0,row=4,columnspan=3,ipady=5,pady=10)
  
  #校验数据
  def validateText(self,attr):
    try:
      float(self.__dict__[attr].get())#获取e1的值，转为浮点数，如果不能转捕获异常
    except:
      messagebox.showwarning('格式错误','请输入数字')

  #窗口居中
  def center_window(self,root, width, height):
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()
    size = '%dx%d+%d+%d' % (width, height, (screenwidth - width)/2, (screenheight - height)/2)
    print(size)
    root.geometry(size)
  
  #添加文件目录
  def add_mm_file(self):
    self.filename = tkinter.filedialog.askopenfilename()
    self.get_value.set(self.filename)

  #开始分析
  def startAnalysis(self):
    excalPath = self.get_value.get()
    minSupport = self.get_support_value.get()
    minConf = self.get_confidence_value.get()
    if(len(excalPath)==0 or len(minSupport)==0 or len(minConf)==0):
      messagebox.showwarning('提示','请输入完整信息')
      return
    

    print(minSupport,minConf)
    pathList = excalPath.split('/')
    saveList = pathList[0:len(pathList)-1]
    savePath = '/'.join(saveList)+'/result.xlsx' #存储路径

    data = pd.read_excel(r''+excalPath, index=False)
    data = data.drop_duplicates()

    itemSets = []
    groups = data.groupby(by='销售单明细')
    for name,group in groups:
      if(len(group))>=2:
        itemSets.append(group['商品编码'].tolist())

    ap = Apriori(itemSets,savePath,minSupport=float(minSupport), minConf=float(minConf))




#开始GUI
def gui_start():
  init_window = Tk()
  popup = MY_GUI(init_window)
  popup.set_init_window()
  init_window.mainloop()

#入口启动
if __name__ == '__main__':
  '''GUI输入界面'''
  gui_start()
  


  
  

