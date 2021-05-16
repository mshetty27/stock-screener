import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from tabulate import tabulate
import warnings
warnings.filterwarnings('ignore')
import pandas_datareader.data as web

def TurtleStrategy(stock_symbol, start_date, end_date):
    print("hello")
    # stock_symbol - (str)stock ticker as on Yahoo finance. Eg: 'ULTRACEMCO.NS' 
    # start_date - (str)start analysis from this date (format: 'YYYY-MM-DD') Eg: '2018-01-01'
    # end_date - (str)end analysis on this date (format: 'YYYY-MM-DD') Eg: '2020-01-01'
    start = datetime.datetime(*map(int, start_date.split('-')))
    end = datetime.datetime(*map(int, end_date.split('-'))) 
    stock_df = web.DataReader(stock_symbol, 'yahoo', start = start, end = end)
    stock_df = pd.DataFrame(stock_df)
    stock_df.dropna(axis = 0, inplace = True) # remove any null rows 

    #High and Low moving averages (20MA)
    stock_df["high_20ma"] = stock_df['High'].rolling(window = 20, min_periods = 1).mean()
    stock_df["low_20ma"] = stock_df['Low'].rolling(window = 20, min_periods = 1).mean()
    stock_df["close_10ma"] = stock_df['Close'].rolling(window = 10, min_periods = 1).mean()

    #signal
    stock_df["buy_signal"] = 0.0
    stock_df['buy_signal'] = np.where(stock_df['Close'] > stock_df['high_20ma'], 1.0, 0.0)
    stock_df['buy_position'] = stock_df['buy_signal'].diff()

    stock_df["sell_signal"] = 0.0
    stock_df['sell_signal'] = np.where(stock_df['Close'] < stock_df['close_10ma'], 1.0, 0.0)
    stock_df['sell_position'] = stock_df['sell_signal'].diff()


    #plot
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

    #print(stock_df.head())

TurtleStrategy('ULTRACEMCO.NS', start_date="2020-05-15", end_date="2021-05-15")