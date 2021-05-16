import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from tabulate import tabulate
# import warnings
# warnings.filterwarnings('ignore')
import pandas_datareader.data as web
import math
import io
import requests
import csv
import time
import argparse
#define - last N days - check if there is a buy signal - say 5 days. 
#take historical data upto 35 days + N
#additional check - volume > last 20 day moving average for buy signal
#only check if there is a buy signal in the last N days
# Stock list obtained from
# smallcaps = "https://niftyindices.com/IndexConstituent/ind_niftysmallcap100list.csv"
# large_and_midcaps = "https://niftyindices.com/IndexConstituent/ind_niftylargemidcap250list.csv"
   

def GetStockList(csv):
    column_names = ["Symbol"]
    df = pd.read_csv(csv, names=column_names)
    tickers = df.Symbol.to_list()
    return tickers
    #print(tickers)

def FindTurtleStrategyEntry(stock_symbol, lastNDays):
    end = datetime.now().date()
    start = end - timedelta(35 + lastNDays) #we need more data for moving average calculations
    
    stock_df = web.DataReader(stock_symbol, 'yahoo', start = start, end = end)
    stock_df = pd.DataFrame(stock_df)
    stock_df.dropna(axis = 0, inplace = True) # remove any null rows 

    #High and Low moving averages (20MA)
    stock_df["high_20ma"] = stock_df['High'].rolling(window = 20, min_periods = 1).mean()
    stock_df["low_20ma"] = stock_df['Low'].rolling(window = 20, min_periods = 1).mean()
    stock_df["vol_20ma"] = stock_df['Volume'].rolling(window = 20, min_periods = 1).mean()
    stock_df["close_10ma"] = stock_df['Close'].rolling(window = 10, min_periods = 1).mean()

    #Take only last N records
    stock_df = stock_df.tail(lastNDays)
    #print(stock_df.head(lastNDays))

    #signal
    stock_df["buy_signal"] = 0.0
    stock_df['buy_signal'] = np.where( (stock_df['Close'] > stock_df['high_20ma']) & (stock_df['Volume'] > stock_df['vol_20ma']), 1.0, 0.0)
    stock_df['buy_position'] = stock_df['buy_signal'].diff()
    stock_df[stock_df < 0] = 0
    stock_df = stock_df.fillna(0)
    #print(stock_df.head(20))
    
    stock_df = stock_df[stock_df.buy_position != 0]
    if not stock_df.empty:
        # print(stock_df_filtered.head(20))
        #print(list(stock_df.columns))
        stock_df["Date"] = stock_df.index
        stock_df["Ticker"] = stock_symbol
        records = stock_df[['Ticker','Date', 'Close']].to_records(index=False)
        lst =  list(records)
        # print(lst)
        return lst[0]
    else:
        return ()
    # result = list(records)

    #print(stock_df_filtered.head(20))

#FindTurtleStrategyEntry('GLAXO.NS', 7)

#TurtleStrategy('ULTRACEMCO.NS', start_date="2020-05-15", end_date="2021-05-15", plot=False)
#TurtleStrategy('BAJFINANCE.NS', start_date="2020-05-15", end_date="2021-05-15", plot=True)
#Test()

def WriteFile(data):
    with open(f'.\output\screened-stocks-{time.strftime("%Y%m%d-%H%M%S")}.csv','w', newline='') as out:
        csv_out=csv.writer(out)
        csv_out.writerow(['ticker','buy_signal_date', 'price'])
        for row in data:
            # print(row)
            csv_out.writerow(row)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Turtle Strategy NSE Stock Screener')
    parser.add_argument('--batchfile', metavar='path', required=True,
                        help='Name of the batch file present in input directory')
    args = parser.parse_args()                        
    tickers = GetStockList(f'.\input\{args.batchfile}')
    list_of_tuples = []
    for ticker in tickers:
        print(f'Working on {ticker}')
        result = FindTurtleStrategyEntry(f'{ticker}.NS', 5)
        if len(result) > 0:
            list_of_tuples.append(result)
        print(f'Finished {ticker}')
    WriteFile(list_of_tuples)