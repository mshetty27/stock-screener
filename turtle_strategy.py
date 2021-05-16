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
import time
import os
from dotenv import load_dotenv

load_dotenv()

price_limit_percentage = 1 + int(os.getenv('PRICE_LIMIT_PERCENTAGE', 4)) / 100
min_volume = int(os.getenv('MIN_VOLUME', 250000))


def GetStockList(csv):
    column_names = ["Symbol"]
    df = pd.read_csv(csv, names=column_names)
    tickers = df.Symbol.to_list()
    return tickers

def FindTurtleStrategyEntry(stock_symbol, lastNDays, plot=False):
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
    
    #signal
    stock_df["buy_signal"] = 0.0
    stock_df['buy_signal'] = np.where( 
            (stock_df['Close'] > stock_df['high_20ma']) & 
            (stock_df['Close'] < (price_limit_percentage * stock_df['high_20ma'])) & 
            (stock_df['Volume'] > stock_df['vol_20ma']) &
            (stock_df['Volume'] > min_volume) &
            (stock_df['Close'] > stock_df['Open']) , 
            1.0, 0.0)
    stock_df['buy_position'] = stock_df['buy_signal'].diff()

    stock_df["sell_signal"] = 0.0
    stock_df['sell_signal'] = np.where(stock_df['Close'] < stock_df['close_10ma'], 1.0, 0.0)
    stock_df['sell_position'] = stock_df['sell_signal'].diff()

    stock_df[stock_df < 0] = 0
    stock_df = stock_df.fillna(0)

    #plot
    if plot == True:
        plt.figure(figsize = (20,10))
        plt.tick_params(axis = 'both', labelsize = 14)
        stock_df['Close'].plot(color = 'k', lw = 1, label = 'Close Price')  
        stock_df['high_20ma'].plot(color = 'b', lw = 1, label = 'High 20MA')
        stock_df['low_20ma'].plot(color = 'g', lw = 1, label = 'Low 20MA') 
        stock_df['close_10ma'].plot(color = 'r', lw = 1, label = 'Close 10MA') 

        plt.plot(stock_df[stock_df['buy_position'] == 1].index, 
            stock_df['close_10ma'][stock_df['buy_position'] == 1], 
            '^', markersize = 15, color = 'g', label = 'buy')

        plt.plot(stock_df[stock_df['sell_position'] == 1].index, 
            stock_df['close_10ma'][stock_df['sell_position'] == 1], 
            'v', markersize = 15, color = 'r', label = 'sell')

        plt.ylabel('Price in ₹', fontsize = 16 )
        plt.xlabel('Date', fontsize = 16 )
        plt.title(str(stock_symbol) + ' Turtle Strategy', fontsize = 20)
        plt.legend()
        plt.grid()
        plt.show()
    
    stock_df = stock_df[stock_df.buy_position != 0]
    if not stock_df.empty:
        stock_df["Date"] = stock_df.index
        stock_df["Ticker"] = stock_symbol
        records = stock_df[['Ticker','Date', 'Close']].to_records(index=False)
        lst =  list(records)
        return lst[0]
    else:
        return ()


def WriteFile(data):
    with open(f'.\output\screened-stocks-{time.strftime("%Y%m%d-%H%M%S")}.csv','w', newline='') as out:
        csv_out=csv.writer(out)
        csv_out.writerow(['ticker','buy_signal_date', 'price'])
        for row in data:
            csv_out.writerow(row)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Turtle Strategy NSE Stock Screener')
    parser.add_argument('--batchfile', metavar='path', required=True,
                        help='Name of the batch file present in input directory')
    parser.add_argument('--days', required=True,
                        help='Name of the trading days to consider for screening',
                        type=int)
    args = parser.parse_args()                        
    tickers = GetStockList(f'.\input\{args.batchfile}')
    list_of_tuples = []
    start = time.time()
    for ticker in tickers:
        print(f'Working on {ticker}')
        ticker_start = time.time()
        try:
            result = FindTurtleStrategyEntry(f'{ticker}.NS', args.days, False)
        except Exception as exception:
            print(exception)
        if len(result) > 0:
            list_of_tuples.append(result)
        ticker_end = time.time()
        print(f'Finished {ticker} in {ticker_end - ticker_start} sec')
    WriteFile(list_of_tuples)
    end = time.time()
    print(f'Total time taken : {end - start} sec')