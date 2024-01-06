import pandas as pd
import numpy as np 
from dotenv import load_dotenv
from NSEDownload import stocks

import argparse
import os
import csv
import time
from datetime import datetime, timedelta


pd.set_option('display.max_columns', None)

#constants
HIGH = "High Price"
LOW = "Low Price"
OPEN = "Open Price"
CLOSE = "Close Price"
VOLUME = "Total Traded Value"

#variables
lastNDays = 3
price_limit_percentage = 1 + int(os.getenv('PRICE_LIMIT_PERCENTAGE', 4)) / 100
min_volume = int(os.getenv('MIN_VOLUME', 250000))

def LoadStockTickers(csv):
    column_names = ["Symbol"]
    df = pd.read_csv(csv, names=column_names)
    tickers = df.Symbol.to_list()
    # print(tickers)
    return tickers

def GetStockData(stock_symbol):
    end = datetime.now().date()
    start = end - timedelta(35 + lastNDays) #we need more data for moving average calculations
    # print(start.strftime("%d-%m-%Y"))
    stock_df = stocks.get_data(stock_symbol, start_date=start.strftime("%d-%m-%Y"), end_date=end.strftime("%d-%m-%Y"))
    stock_df = pd.DataFrame(stock_df)
    stock_df.dropna(axis = 0, inplace = True) # remove any null rows 
    # print(stock_df)
    return stock_df

def FindEntry(stock_symbol, stock_df):
    #High and Low moving averages (20MA)
    stock_df["high_20ma"] = stock_df[HIGH].rolling(window = 20, min_periods = 1).mean()
    stock_df["low_20ma"] = stock_df[LOW].rolling(window = 20, min_periods = 1).mean()
    stock_df["vol_20ma"] = stock_df[VOLUME].rolling(window = 20, min_periods = 1).mean()
    stock_df["close_10ma"] = stock_df[CLOSE].rolling(window = 10, min_periods = 1).mean()
    
    #Take only last N records
    stock_df = stock_df.tail(lastNDays)
    
    #signal
    stock_df["buy_signal"] = 0.0
    stock_df['buy_signal'] = np.where( 
            (stock_df[CLOSE] > stock_df['high_20ma']) & # Price Closed above 20MA of High
            (stock_df[CLOSE] < (price_limit_percentage * stock_df['high_20ma'])) & # Price has not jumped too much
            (stock_df[VOLUME] > stock_df['vol_20ma']) & # Volume > 20MA average
            (stock_df[VOLUME] > min_volume) & # Atleast some significant volume
            (stock_df[CLOSE] > stock_df[OPEN]), # It is a green candle
            1.0, 0.0)
    
    stock_df['buy_position'] = stock_df['buy_signal'].diff()
    stock_df = stock_df.fillna(0)

    stock_df["sell_signal"] = 0.0
    stock_df['sell_signal'] = np.where(stock_df[CLOSE] < stock_df['close_10ma'], 1.0, 0.0)
    stock_df['sell_position'] = stock_df['sell_signal'].diff()

    stock_df = stock_df.fillna(0)
    stock_df = stock_df[stock_df.buy_position != 0]
    # print(stock_df)
    if not stock_df.empty:
        stock_df["Date"] = stock_df.index
        stock_df["Ticker"] = stock_symbol
        records = stock_df[['Ticker','Date', CLOSE]].to_records(index=False)
        lst =  list(records)
        return lst[0]
    else:
        return ()

def WriteFile(data):
    with open(f'.\\output\\screened-stocks-{time.strftime("%Y%m%d-%H%M%S")}.csv','w', newline='') as out:
        csv_out=csv.writer(out)
        csv_out.writerow(['ticker','buy_signal_date', 'price'])
        for row in data:
            csv_out.writerow(row)

if __name__ == "__main__":
    # Read Arguments
    parser = argparse.ArgumentParser(description='Turtle Strategy NSE Stock Screener')
    parser.add_argument('--batchfile', metavar='path', required=True,
                        help='Name of the batch file present in input directory')
    parser.add_argument('--days', required=True,
                        help='Name of the trading days to consider for screening',
                        type=int)
    args = parser.parse_args()     

    #Set args
    lastNDays = args.days

    # Load Tickers                   
    tickers = LoadStockTickers(f'.\\input\\{args.batchfile}')
    list_of_tuples = []
    for ticker in tickers:
        print(f'Working on {ticker}')
        try:
            stock_df = GetStockData(f'{ticker}')
            result = FindEntry(ticker, stock_df)
            time.sleep(2)
        except Exception as exception:
            print(exception)
        if len(result) > 0:
            list_of_tuples.append(result)
        print(f'Finished {ticker} at {datetime.now()}')

    WriteFile(list_of_tuples)