# -*- coding: utf-8 -*-
"""
Created on Tue Jun 14 10:45:40 2022

@author: Administrator
"""

import streamlit as st
import numpy as np
import pandas as pd
import datetime

#import streamlit.components.v1 as components
# from pyecharts.charts import *
# from pyecharts.globals import ThemeType
# from pyecharts import options as opts
# from pyecharts.commons.utils import JsCode

#全局配置
st.set_page_config(
    page_title="million",    #页面标题
    page_icon=":herb:",        #icon:emoji":rainbow:"
    layout="wide",                #页面布局
    initial_sidebar_state="auto"  #侧边栏
)

#本地测试
# import os
#os.chdir(r'h:/git_pyecharts')
# st.write(os.getcwd())
###标题
st.header('行情数据分享')
st.markdown(datetime.date.today())

# with st.expander("See explanation"):
#      st.write("""
#          The chart above shows some numbers I picked for you.
#          I rolled actual dice for these, so they're *guaranteed* to
#          be random.
#      """)

# agree = st.checkbox('I agree') 

# if agree:
#      st.write('Great!')

     
from pyecharts.charts import Line,Grid,Pie
import streamlit_echarts
from pyecharts import options as opts
import xlrd
#print(pyecharts.__version__)
# 然后实例化一个pyecharts的图表对象
#excel字符串转日期
def estd(x):
    try:
     a=xlrd.xldate.xldate_as_datetime(int(x),0)
     return a
    except:
     a=np.nan
     return a




startdate=datetime.date(2020,1,1)
enddate=datetime.date.today()
monthstartdate=datetime.date(2022,6,1)
weekstartdate=datetime.date(2023,1,1)

#航线数据

from ccfianalysis import getrouteclassification
routedata =getrouteclassification(path="./CCFI")
#routedata.info()
for i in routedata.columns[1:]:
   routedata[i]=routedata[i].apply(lambda x:round(x,2))

#51不锈数据
def readbxdata(filename,plotstartdate,plotenddate):
    price=pd.read_excel(filename)
    #price=pd.read_excel(filename="h:/51不锈数据/不锈库存.xlsx")
    
    if isinstance(price['日期'][0],str):
        if (len(price['日期'][0])>5):
            price['日期']=price['日期'].apply(lambda x :datetime.datetime.strptime(x,"%Y-%m-%d").date())
        else:
            price['日期']=price['日期'].apply(lambda x :estd(x).date())
    else:
        price['日期']=price['日期'].apply(lambda x :estd(x).date())

    plotdata=(price
                .loc[lambda x :x['日期']>=plotstartdate]
                .loc[lambda x :x['日期']<=plotenddate]    
    ).drop_duplicates()
    return plotdata

#英为财情
def readivdata(filename,plotstartdate,plotenddate):
    price=pd.read_excel(filename)
    #type(price['日期'][0])
    price['日期']=price['日期'].apply(lambda x :x.date())
    price['收盘']=price['收盘'].apply(lambda x :pd.to_numeric(x.replace(",","")))
    plotdata=(price
                .loc[lambda x :x['日期']>=plotstartdate]
                .loc[lambda x :x['日期']<=plotenddate]    
    ).drop_duplicates()
    return plotdata

@st.cache_data
def load_data():
    niplotdata=readbxdata(filename="./data/镍铁价格.xlsx",plotstartdate=startdate,plotenddate=enddate)
    crplotdata=readbxdata(filename="./data/铬铁价格.xlsx",plotstartdate=startdate,plotenddate=enddate)
    feoplotdata=readivdata(filename="./data/铁矿石.xlsx",plotstartdate=startdate,plotenddate=enddate)
    cokeplotdata=readbxdata(filename="./data/焦炭价格.xlsx",plotstartdate=startdate,plotenddate=enddate)
    #不锈钢价格
    threepricedata=readbxdata(filename="./data/304北部湾新材毛边价.xlsx",plotstartdate=startdate,plotenddate=enddate)
    twopricedata=readbxdata(filename="./data/201宏旺毛边价.xlsx",plotstartdate=startdate,plotenddate=enddate)
    fourpricedata=readbxdata(filename="./data/430联众1.5切边价.xlsx",plotstartdate=startdate,plotenddate=enddate)
    #库存
    stockplotdata=readbxdata(filename="./data/不锈库存.xlsx",plotstartdate=startdate,plotenddate=enddate)
    
    #niprice.info()
    #merge库存数据和价格数据
    twoplotdata = pd.merge(twopricedata,stockplotdata,how='outer',on=['日期']).sort_values('日期',ascending=True,ignore_index=True)
    threeplotdata = pd.merge(threepricedata,stockplotdata,how='outer',on=['日期']).sort_values('日期',ascending=True,ignore_index=True)
    fourplotdata = pd.merge(fourpricedata,stockplotdata,how='outer',on=['日期']).sort_values('日期',ascending=True,ignore_index=True)
    return niplotdata,crplotdata,feoplotdata,cokeplotdata,twoplotdata,threeplotdata,fourplotdata

niplotdata,crplotdata,feoplotdata,cokeplotdata,twoplotdata,threeplotdata,fourplotdata=load_data()

#单图
def linematerial(data,colx,coly,newstartdate,backcolor,overcolor,titlename):
    startdateindex=data[colx][data[colx]<=newstartdate].shape[0]-1
    enddateindex=data[colx][data[colx]<=enddate].shape[0]
    line=(Line()
       .add_xaxis(data[colx].tolist())
       .add_yaxis('',data[coly].tolist(),linestyle_opts=opts.LineStyleOpts(width=2)) 
       .set_series_opts(label_opts=opts.LabelOpts(is_show=True,margin = 20,))
       #.add_yaxis('',data.loc[lambda x :x[colx]<=newstartdate][coly].tolist(),linestyle_opts=opts.LineStyleOpts(color=backcolor))
       .set_global_opts(
           yaxis_opts=opts.AxisOpts(min_ = round(0.9*min(data[coly]),0)),
           title_opts=opts.TitleOpts(title=titlename,pos_left='center'),
           visualmap_opts=opts.VisualMapOpts(
               is_show= False,
                is_piecewise=True,
                dimension=0,
                pieces=[
                    {"lte": startdateindex, "color": backcolor},
                    {"gt": startdateindex, "lte": enddateindex, "color": overcolor},
                ],
            )
           )
       
    )
    grid=Grid()
    grid.add(line,grid_opts=opts.GridOpts(pos_left='18%'))
       
    #gridline.render('d:/eee.html')#
    return grid

lineccfi=linematerial(data=routedata,colx='日期',coly='CCFI',titlename='CCFI',newstartdate=weekstartdate,backcolor='midnightblue',overcolor='crimson')
lineconsume=linematerial(data=routedata,colx='日期',coly='消费国运价指数',titlename='消费国运价指数',newstartdate=weekstartdate,backcolor='midnightblue',overcolor='crimson')
lineproduce=linematerial(data=routedata,colx='日期',coly='制造国运价指数',titlename='制造国运价指数',newstartdate=weekstartdate,backcolor='midnightblue',overcolor='crimson')
lineresource=linematerial(data=routedata,colx='日期',coly='资源国运价指数',titlename='资源国运价指数',newstartdate=weekstartdate,backcolor='midnightblue',overcolor='crimson')


st.subheader('运价指数')
col1, col2= st.columns(2)
with col1:
#with st.container():
    #st.write('本周')
    streamlit_echarts.st_pyecharts(lineccfi,key='ccfi')
    streamlit_echarts.st_pyecharts(lineconsume,key='consumec')
with col2:
    streamlit_echarts.st_pyecharts(lineproduce,key='producec')
    streamlit_echarts.st_pyecharts(lineresource,key='resourcec')



lineni=linematerial(data=niplotdata,colx='日期',coly='山东价格',titlename='镍铁',newstartdate=weekstartdate,backcolor='midnightblue',overcolor='crimson')
linecr=linematerial(data=crplotdata,colx='日期',coly='内蒙价格',titlename='铬铁',newstartdate=weekstartdate,backcolor='midnightblue',overcolor='crimson')
linefeo=linematerial(data=feoplotdata,colx='日期',coly='收盘',titlename='铁矿石',newstartdate=weekstartdate,backcolor='midnightblue',overcolor='crimson')
linecoke=linematerial(data=cokeplotdata,colx='日期',coly='太原',titlename='焦炭',newstartdate=weekstartdate,backcolor='midnightblue',overcolor='crimson')


#feoplotdata.info()
#type(niplotdata['日期'][3000])
st.subheader('原料价格')
col1, col2= st.columns(2)
with col1:
    streamlit_echarts.st_pyecharts(lineni,key='ni')
    streamlit_echarts.st_pyecharts(linefeo,key='feo')
with col2:   
    streamlit_echarts.st_pyecharts(linecr,key='cr')
    streamlit_echarts.st_pyecharts(linecoke,key='coke')


#双坐标轴图
def linepricestock(data,colx,lefty,righty,newstartdate,leftcolor,rightcolor,titlename):
    line = (
        Line()
        .add_xaxis(data[colx].tolist())
        
        .add_yaxis(
            "价格",
            data[lefty].tolist(),
            is_connect_nones=True, yaxis_index=0,linestyle_opts=opts.LineStyleOpts(color=leftcolor))
        
        .extend_axis(yaxis=opts.AxisOpts(type_="value",name="库存", position="right",min_ = round(0.9*data[righty].min(),0)))
        .add_yaxis(
            "库存",
            data[righty].tolist(),
            is_connect_nones=True,
            yaxis_index=1,
            is_symbol_show = True,linestyle_opts=opts.LineStyleOpts(color=rightcolor) )
        
        .set_global_opts(
            yaxis_opts=opts.AxisOpts(name="价格",min_ = round(0.9*data[lefty].min(),0)),
            title_opts=opts.TitleOpts(title=titlename,pos_left='left')
        
        )
    )
    grid=Grid()
    grid.add(line,grid_opts=opts.GridOpts(pos_left='17%',pos_right='22%'), is_control_axis_index=True)
    #grid.render('d:/eee.html')#
    return grid

twostock=linepricestock(data=twoplotdata,colx='日期',lefty='报价',righty='库存200系',titlename='201',newstartdate=weekstartdate,leftcolor='red',rightcolor='black')
threestock=linepricestock(data=threeplotdata,colx='日期',lefty='报价',righty='库存300系',titlename='304',newstartdate=weekstartdate,leftcolor='red',rightcolor='black')
fourstock=linepricestock(data=fourplotdata,colx='日期',lefty='报价',righty='库存400系',titlename='430',newstartdate=weekstartdate,leftcolor='red',rightcolor='black')

st.subheader('不锈钢价格与库存')
col1, col2= st.columns(2)
with col1:
    streamlit_echarts.st_pyecharts(twostock,key='twostock')
    streamlit_echarts.st_pyecharts(fourstock,key='fourstock')
with col2:   
    streamlit_echarts.st_pyecharts(threestock,key='threestock')
    

# fn = """
#     function(params) {
#         if(params.name.length == 1)
#             return '';
#         return params.name + ' : ' + params.value ;
#     }
#     """


# from pyecharts.commons.utils import JsCode
# from pyecharts.globals import ThemeType

# import streamlit_echarts

# def new_label_opts():
#     return opts.LabelOpts(formatter=JsCode(fn), position="center",color="#016169")
# def new_Tooltip_opts():
#     return opts.TooltipOpts(formatter=JsCode(fn))
    
# skillpie = (
#     Pie()
#     .add(
#         "",
#         [list(z) for z in zip(["R ", "1"], [80, 20])],
#         center=["25%", "25%"],
#         radius=[40, 60],
#         label_opts=new_label_opts(),
       
#     )
#     .add(
#         "",
#         [list(z) for z in zip(["PYTHON", "2"], [60, 40])],
#         center=["50%", "25%"],
#         radius=[40, 60],
#         label_opts=new_label_opts(),
        
#     )
#     .add(
#         "",
#         [list(z) for z in zip(["AxureRP", "3"], [60, 40])],
#         center=["75%", "25%"],
#         radius=[40, 60],
#         label_opts=new_label_opts(),
        
#     )

#     .add(
#         "",
#         [list(z) for z in zip(["PPT", "4"], [75, 25])],
#         center=["25%", "75%"],
#         radius=[40, 60],
#         label_opts=new_label_opts(),
       
#     )
#     .add(
#         "",
#         [list(z) for z in zip(["EXCEL", "5"], [85, 15])],
#         center=["50%", "75%"],
#         radius=[40, 60],
#         label_opts=new_label_opts(), 
       
#     )
#     .add(
#         "",
#         [list(z) for z in zip(["Endraw", "6"], [85, 15])],
#         center=["75%", "75%"],
#         radius=[40, 60],
#         label_opts=new_label_opts(), 
       
#     )
#     .set_colors([ "#016169","#F2F2F2"])
    
#     .set_global_opts(
#         title_opts=opts.TitleOpts(title="software"),
#         tooltip_opts=new_Tooltip_opts(),
#         legend_opts=opts.LegendOpts(
#             is_show=False
#         ),
#     )

# )

# streamlit_echarts.st_pyecharts(
#     skillpie,
#     theme=ThemeType.VINTAGE
# )

    