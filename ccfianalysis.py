# -*- coding: utf-8 -*-
"""
Created on Thu Feb 10 11:35:26 2022

@author: Administrator
"""

#import requests
import pandas as pd
import os
import datetime

def getrouteclassification():
    #读取文件夹的内容
    path=os.path.join('h:',os.sep,'CCFI')
    #查看文件夹里所有文件
    docnames=os.listdir(path)
    #拼接完整文件路径
    docnameslist=[] 
    for i in docnames:
        b=os.path.join(path,i)
        docnameslist.append(b)
    #读取文件+拼接成一个数据框    
    historydata=pd.DataFrame()
    for i in docnameslist:
        data=pd.read_excel(i)
        historydata=pd.concat([historydata, data],ignore_index=True)
    
    #type(historydata['日期'][0])
    historydata['日期']=historydata['日期'].apply(lambda x:x.date())
    historydata.sort_values('日期',ascending=True,inplace=True)
    
    historydata=historydata[historydata['日期']>datetime.date(2020, 1, 1)]
    
    # historydata.info()
    routename=['地中海航线','欧洲航线','美东航线','美西航线',
                 '日本航线','韩国航线','东南亚航线',
                 '东西非航线','南美航线','南非航线','波红航线','澳新航线']
    routeweight=[10,20,10,20,7.5,2.5,10,2.5,5,2.5, 7.5,2.5]
    routeatt=['消费国','消费国','消费国','消费国',
                 '制造国','制造国','制造国',
                 '资源国','资源国','资源国', '资源国','资源国']
    routetype=pd.DataFrame({'航线':routename,'权重':routeweight,'分类':routeatt})
    routetype['分类合计权重']=routetype.groupby('分类').transform('sum')['权重']
    routetype['分类权重']=pd.to_numeric(routetype['权重']/routetype['分类合计权重'])
    
    
    def calculateindex(routetypename):
        grouproute=[0 for index in range(historydata.shape[0])]
        for i in routetype[routetype['分类']==routetypename]['航线']:
            #i='欧洲航线'i='地中海航线'
            singleroute=round(historydata[i]*routetype[routetype['航线']==i]['分类权重'].reset_index()['分类权重'][0],2)
            grouproute=grouproute+singleroute
        return grouproute
            
    historydata['消费国运价指数']=calculateindex(routetypename='消费国')
    historydata['制造国运价指数']=calculateindex(routetypename='制造国')
    historydata['资源国运价指数']=calculateindex(routetypename='资源国')
    
    routet=historydata[['日期','CCFI','消费国运价指数','制造国运价指数','资源国运价指数']]
    return routet
#historydata['消费国运价指数']=historydata['地中海航线']*routetype[routetype['航线']=='地中海航线']['分类权重'][0]+
