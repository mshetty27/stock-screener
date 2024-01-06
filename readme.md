# Instructions

Finds entry in stocks using the turtle trading strategy which is a trend following strategy

- Enter when
  - Stock closes above the 20 MA of HIGH on the daily chart. Additional checks satisfies: the close price at entry has not shot up more than 4% of the 20MA HIGH
  - Associated volume is higher than 20 day average volume. Associated volume is atleast 2,50,000
- Exit when
  - Stock price closes below 10 MA of CLOSE price

Here we are just finding the entry
Stock list in the 'input' folder is a combination of stocks covered by following indexes.

- smallcaps = "https://niftyindices.com/IndexConstituent/ind_niftysmallcap100list.csv"
- large_and_midcaps = "https://niftyindices.com/IndexConstituent/ind_niftylargemidcap250list.csv"
  There are a total of 350 stocks. Input can be provided as batches as well. Stocks are split into 4 files.

## Execution steps

Install required modules

```
pip install NSEDownload/dist/NSEDownload-5.0.6.tar.gz
pip install -r requirements.txt

```

Run the program:

```
python .\turtle_strategy.py --batchfile=stocks.csv --days=3

```

Stocks where entry is found would be dumped into 'output' folder after the program completes. What to do with the list of output stocks? - Do your further filtering - Check the trend, in those stocks - pick 3-4, find your entry and exit & invest for a short term (swing). Discretion is advised.

Thanks Jinit24 for this library - NSEDownload which helps in downloading stock data: https://github.com/NSEDownload/NSEDownload
