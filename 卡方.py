# -*- coding: utf-8 -*-
"""卡方.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16Iaaq4xTHDQSSq5CzfEGUl05E3RpUF9G
"""

import numpy as np
import pandas as pd
import copy
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

df_kf = pd.read_csv('algoActual.csv')
df_kf

df_kf['OrdStatus'] = df_kf['OrdStatus'].str.replace(r'\t', '')
df_kf['OrdType'] = df_kf['OrdType'].str.replace(r'\t', '')
df_kf

n = df_kf.nunique(axis=0)
print("No.of.unique values in each column :\n",n)

"""#### Q1: 每个股票的买/卖股票数量，金额，盈亏和收益率"""

def Q1(table):
  df = copy.deepcopy(table)
  stock_list = df["Symbol"].unique()
  column_names = ["B_AMT", "S_AMT", "CASH_AMT", "P&L", "Return(%)"]
  temp_table = df[(df["OrdStatus"] == "Filled") | (df["OrdStatus"] == "New")]
  df_final = pd.DataFrame(index = stock_list, columns = column_names)

  # 计算每个股票的买/卖股票数量，金额，盈亏和收益率
  for stock in stock_list:
    stock_table = temp_table[temp_table["Symbol"] == stock]

    if stock_table.shape[0] == 0:
      df_final.loc[stock] = [0, 0, 0, 0, 0]
    
    elif stock_table.shape[0] == 1:
      if stock_table["Side"].values[0] == "B":
        df_final.loc[stock] = [stock_table[stock_table["Side"] == "B"]["OrderQty"].values[0], 
                               0,
                               stock_table["FilledValue"].values[0], 
                               0, 
                               0]
      else:
        df_final.loc[stock] = [0, 
                               stock_table[stock_table["Side"] == "S"]["OrderQty"].values[0], 
                               stock_table["FilledValue"].values[0], 
                               0, 
                               0]

    else:
      B_amount = stock_table[stock_table["Side"] == "B"]["OrderQty"].sum()
      S_amount = stock_table[stock_table["Side"] == "S"]["OrderQty"].sum()
      C_amount = stock_table["FilledValue"].sum()
      P_L = stock_table[stock_table["Side"] == "S"]["FilledValue"].sum() - stock_table[stock_table["Side"] == "B"]["FilledValue"].sum()
      RTN = ((stock_table["Price"].tolist()[-1] - stock_table["Price"].tolist()[0]) / (stock_table["Price"].tolist()[-1]))
      RTN = round(RTN,5)*100
      df_final.loc[stock] = [B_amount, S_amount, C_amount, P_L, RTN]
    
  return df_final

df_Q1 = Q1(df_kf)
df_Q1

"""#### Q2: 每个股票总下单数， 撤单和成交的比例"""

def Q2(table):
  df = copy.deepcopy(table)
  stock_list = df["Symbol"].unique()
  column_names = ["Total_Order", "Total_WithDraw", "Compelete_Ratio"]
  df_final_Q2 = pd.DataFrame(index = stock_list, columns = column_names)

  # 每个股票总下单数， 撤单和成交的比例
  for stock in stock_list:
    stock_table = df[df["Symbol"] == stock]
    order_number = stock_table["CumQty"].sum()  # 计算每只股票的下单数
    withdraw_number = stock_table[(stock_table["OrdStatus"] == "Canceled") | (stock_table["OrdStatus"] == "Rejected")]["CumQty"].sum()
    ratio = 1 - (withdraw_number/order_number)
    df_final_Q2.loc[stock] = [order_number, withdraw_number, ratio]
    df_final_Q2 = df_final_Q2.fillna(0)
    
  return df_final_Q2

df_Q2 = Q2(df_kf)
df_Q2

"""#### Q3 每个股票交易费用，占盈亏的比例是多少？"""

def Q3(table):
  df = copy.deepcopy(table)
  stock_list = df["Symbol"].unique()
  column_names = ["Transaction_Fee", "P&L","占盈亏比例(%)"]
  df_final_Q3 = pd.DataFrame(index = stock_list, columns = column_names)

  # 计算每支股票的交易费用和占盈亏的比例
  for stock in stock_list:
    stock_table = df[df["Symbol"] == stock]
    Total_fee = stock_table["OtherFee"].sum()  # 计算每只股票的总交易费用
    P_L = stock_table[stock_table["Side"] == "S"]["FilledValue"].sum() - stock_table[stock_table["Side"] == "B"]["FilledValue"].sum() # 计算每只股票的盈亏
    ratio = round(Total_fee/abs(P_L)*100,5) 
    df_final_Q3.loc[stock] = [Total_fee, P_L, ratio]
    df_final_Q3 = df_final_Q3.fillna(0)
    
  return df_final_Q3

df_Q3 = Q3(df_kf)
df_Q3

"""#### Q4 是否有没有平掉的仓位？如有， 是那个股票？ 多少股？"""

def Q4(table):
  df = copy.deepcopy(table)
  stock_list = df["Symbol"].unique()
  column_names = ["Closed", "Stock_left"]
  temp_table = df[(df["OrdStatus"] == "Filled") | (df["OrdStatus"] == "New")]
  df_final_Q4 = pd.DataFrame(index = stock_list, columns = column_names)

  # 检查是否有尚未平仓的股票及其仓位
  for stock in stock_list:
    stock_table = temp_table[temp_table["Symbol"] == stock]

    if stock_table.shape[0] <= 1:
      df_final_Q4.loc[stock] = ["N", stock_table["OrderQty"].sum()]

    else:
      B_amount = stock_table[stock_table["Side"] == "B"]["OrderQty"].sum()
      S_amount = stock_table[stock_table["Side"] == "S"]["OrderQty"].sum()
      diff = B_amount - S_amount
      
      if diff == 0:
        df_final_Q4.loc[stock] = ["Y", 0]

      else:
        df_final_Q4.loc[stock] = ["N", diff]
    
  return df_final_Q4

df_Q4 = Q4(df_kf)
df_Q4

"""#### Q5:所有的股票，总的交易的金额， 按时间分布， 每10分钟的成交金额和收益是如何？"""

def Q5(table):
  df = copy.deepcopy(table)

  # 转换时间到分钟
  df["TransactTime"] = df["TransactTime"].astype(str)
  df['hours'] = df["TransactTime"].str[:-7]
  df['minutes'] = df["TransactTime"].str[-7:-5]
  df['seconds'] = df["TransactTime"].str[-5:-3]
  df['milseconds'] = df["TransactTime"].str[-3:]
  df["time"] = (df['milseconds'].astype(int)/1000 + df['seconds'].astype(int))/60 + df['minutes'].astype(int) + df['hours'].astype(int)*60

  temp_table = df[(df["OrdStatus"] == "Filled") | (df["OrdStatus"] == "New")]
  stock_list = temp_table["Symbol"].unique()
  column_names = ["time", "trading volume", "Return"]
  time_span = df["time"].tolist()
  df_final_Q5 = pd.DataFrame(index = time_span, columns = column_names)

  for time in range(round(time_span[0]), round(time_span[-1]), 10):
    stock_table = temp_table[(temp_table["time"] >= time) & (temp_table["time"] <= (time + 10))]
    TraVol = stock_table["FilledValue"].sum()
    B_value = stock_table[stock_table["Side"] == "B"]["FilledValue"].sum()
    S_value = stock_table[stock_table["Side"] == "S"]["FilledValue"].sum()
    RTN = S_value - B_value
    rate = RTN/B_value
    df_final_Q5.loc[time] = [time, TraVol, rate]
  
  df_final_Q5 = df_final_Q5.dropna()

  return df_final_Q5

df_Q5 = Q5(df_kf)
df_Q5

"""#### Q6：所有的股票，成交价格在5块钱以下的， 收益， 收益率， 赚钱、亏钱的股票个数是多少， 赚钱/亏钱总额是多少？"""

def Q6(table):
  df = copy.deepcopy(table)
  temp_table = df[(df["OrdStatus"] == "Filled") | (df["OrdStatus"] == "New")]
  temp_table = temp_table[temp_table["AvgPx"] <= 5]
  stock_list = temp_table["Symbol"].unique()
  column_names = ["total return", "Return(%)", "Postive_Return"]
  df_final_Q6 = pd.DataFrame(index = stock_list, columns = column_names)

  for stock in stock_list:
    stock_table = temp_table[temp_table["Symbol"] == stock]
    B_value = stock_table[stock_table["Side"] == "B"]["FilledValue"].sum()
    S_value = stock_table[stock_table["Side"] == "S"]["FilledValue"].sum()
    RTN = S_value - B_value
    rate = RTN/B_value
      
    if RTN > 0:
      df_final_Q6.loc[stock] = [RTN, rate, "Y"]

    elif RTN == 0:
      df_final_Q6.loc[stock] = [0, 0, 0]

    else:
      df_final_Q6.loc[stock] = [RTN, rate, "N"]

  return df_final_Q6

df_Q6 = Q6(df_kf)
print("赚钱的股票个数为： ", df_Q6[df_Q6["Postive_Return"] == "Y"].shape[0])
print("亏钱的股票个数为： ", df_Q6[df_Q6["Postive_Return"] == "N"].shape[0])
display(df_Q6)