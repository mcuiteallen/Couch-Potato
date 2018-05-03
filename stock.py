# coding=utf-8
import requests
from io import StringIO
import os.path
import pandas as pd
import numpy as np
import datetime
import time
import json
import talib
from talib import abstract
from decimal import *
#


def crawl_price(date):
    r = requests.post('http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + date + '&type=ALL')
    ret = pd.read_csv(StringIO("\n".join([i.translate({ord(c): None for c in ' '}) 
                                        for i in r.text.split('\n') 
                                        if len(i.split('",')) == 17 and i[0] != '='])), header=0)
    ret = ret.set_index(codename)
    ret[price] = ret[price].str.replace(',','')
    ret[volumep] = ret[volumep].str.replace(',','')
    return ret

def kdpointer(tsmc):
    kdvalue=[]
    try:
        kdvalue=talib.abstract.STOCH(tsmc,fastk_period=9)
        #print(talib.abstract.STOCH)
    except:
        print(tsmc)
     
    return kdvalue

def macdpointer(tsmc):
    macdvalue=[]
    try:
        macdvalue=talib.abstract.MACD(tsmc,fastk_period=9)
        #print(talib.abstract.STOCH)
    except:
        print(tsmc)

    return macdvalue


def bbandpointer():
    ret = 1
    return ret

def checkValue():
    ret = 1
    return ret

def tsmcdata(closeList,openList,highList,lowList,volumeList):
    tsmc = {}
    tsmc['close'] = np.array(closeList, dtype='f8')
    tsmc['open'] = np.array(openList, dtype='f8')
    tsmc['high'] = np.array(highList, dtype='f8')
    tsmc['low'] = np.array(lowList, dtype='f8')
    tsmc['volume'] = np.array(volumeList, dtype='f8')
    
    return tsmc

def createFile(data,codeList):
    for k1,d1 in data.items():
        for k2,d2 in d1['收盤價'].items():
            codeList.append(k2)
            if not os.path.exists(k2 + '.csv'):
                f = open(k2 + '.csv', 'w+')
                f.write("date,pe,volume,open,high,low,close,k,d,macd,bbandupper,bbandmiddle,bbandlower\n")
                f.close()
        break
    return codeList

float_formatter = lambda x: "%.2f" % x
np.set_printoptions(formatter={'float_kind':float_formatter})

price = '成交金額'
codename = '證券代號'
closep = '收盤價'
openp = '開盤價'
highp = '最高價'
lowp = '最低價'
volumep = '成交股數'
predatap = '本益比'
data = {}
tsmc = {}
n_days = 30
date = datetime.datetime.now()
fail_count = 0
allow_continuous_fail_count = 20
codeList=[]
closeList=[]
openList=[]
highList=[]
lowList=[]
volumeList=[]
while len(data) < n_days:
    # 使用 crawPrice 爬資料
    try:
        # 抓資料
        format_date_dash = str(date).split(' ')[0]
        format_date_no_dash = format_date_dash.replace('-','')
        print('parsing', format_date_no_dash)
        data[format_date_dash] = crawl_price(format_date_no_dash)
        print('success!')
        fail_count = 0
    except:
        # 假日爬不到
        print('fail! check the date is holiday')
        fail_count += 1
        if fail_count == allow_continuous_fail_count:
            raise
            break
    
    # 減一天
    date -= datetime.timedelta(days=1)
    time.sleep(1)
createFile(data,codeList)

for k1 in codeList:
    #print(k1)##每個代號
    closeList=[]
    openList=[]
    highList=[]
    lowList=[]
    volumeList=[]
    perdataList=[]
    for k2,d2 in data.items():
        #print(k2)
        day = k2
        try:
            closeList.append(data[k2][str('收盤價')][k1])
            openList.append(data[k2][str('開盤價')][k1])
            highList.append(data[k2][str('最高價')][k1])
            lowList.append(data[k2][str('最低價')][k1])
            volumeList.append(data[k2][str('成交股數')][k1])
            perdataList.append(data[k2][str('本益比')][k1])
        except:
            print(str(k2)+':'+str(k1)+'= no data')
    try:
        tsmcdata(closeList[::-1],openList[::-1],highList[::-1],lowList[::-1],volumeList[::-1])
    except:
        print(str(k1)+': no data')
    else:
        kdvalues=[]
        kdvalues=kdpointer(tsmcdata(closeList[::-1],openList[::-1],highList[::-1],lowList[::-1],volumeList[::-1]))
        macdvalues = macdpointer(tsmcdata(closeList[::-1],openList[::-1],highList[::-1],lowList[::-1],volumeList[::-1]))
        if k1 == '2456':
            print(closeList[::-1])
            print(str(k1)+':  k='+ str(kdvalues[0]))
            print(str(k1)+':  d='+ str(kdvalues[1]))
            print(str(k1)+':  macd='+ str(macdvalues))
            print(str(k1)+':  macd[0]='+ str(macdvalues[0]))
            print(str(k1)+':  macd[1]='+ str(macdvalues[1]))

        while len(closeList) > 0:
            closeValue = closeList.pop()
            openValue = openList.pop()
            highValue = highList.pop()
            lowValue = lowList.pop()
            volumeValue = volumeList.pop()
            perdataValue = perdataList.pop()
            kValueList = kdvalues[0].tolist()
            dValueList = kdvalues[1].tolist()
            kValue = kValueList.pop()
            dValue = dValueList.pop() 
            f = open(k1 + '.csv', 'a+')
            content = f.read()
            f.seek(0, 0)
            macdValueList = macdvalues[1].tolist()
            macdValue = macdValueList.pop()
            bbandupper = 1
            bbandmiddle = 1
            bbandlower = 1
            f.write(k2 + "," + str(perdataValue)  + "," + str(volumeValue) + "," + str(openValue) + "," + str(highValue) + "," + str(lowValue) + "," + str(closeValue) + "," + str(kValue)  + "," + str(dValue) + "," + str(macdValue) + "," + str(bbandupper) + "," + str(bbandmiddle) + "," + str(bbandlower) + "\n")
            f.close()
 
#close = pd.DataFrame({k:d['收盤價'] for k,d in data.items()}).transpose()
#close.index = pd.to_datetime(close.index)
#close.to_csv('stock.csv')
