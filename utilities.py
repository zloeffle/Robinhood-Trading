import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Calculates the daily percentage change in price of a stock, returns df with daily % change cl
def daily_pct_change(df):
    close = df[['Adj Close']]
    change = close.pct_change()
    change.dropna(inplace=True)
    df['Daily % Change'] = change
    return change

# calculates weekly percentage change in a stocks price
def weekly_pct_change(df):
    end = df['Adj Close'].iloc[-1]
    start = df['Adj Close'].iloc[-6]
    change = round((end-start)/start,3)
    return change

# calculates monthly percentage change in a stocks price
def monthly_pct_change(df):
    df = df['Adj Close'].resample('BM').last()
    start = df[-2]
    end = df[-1]
    change = round((end-start)/start,3)
    return change

# calculates daily return for a stock
def daily_return(df):
    ret = df['Close'] - df['Open']
    return ret

def simple_moving_avg(df,n):
    sma = df['Adj Close'].rolling(window=n).mean()
    sma = sma.fillna(0)
    return sma.round(2)

def exponential_moving_average(df,n):
    exp = df['Adj Close'].ewm(span=n,adjust=False).mean()
    return exp.round(2)    

############## INDICATORS ############## 
'''
moving average convergence divergence
- MACD line: Subtract the stocks 26day EMA from the 12day EMA
- Signal line: Calculate 9day EMA of the MACD line
Returns BUY signal if MACD line crosses above signal line and SELL signal if crosses below
'''
def macd(df):
    # 12 and 26 day exponential moving averages
    ema12 = exponential_moving_average(df,12)
    ema26 = exponential_moving_average(df,26)
     
    # create macd line
    mac = ema12-ema26
    mac.dropna(inplace=True)
    mac = mac.reset_index()
    
    # create signal line
    signal = mac['Adj Close'].ewm(span=9,adjust=False).mean()
    
    # plot signal and macd lines
    plt.plot(mac['Date'],mac['Adj Close'],label='MACD',color='r')
    plt.plot(mac['Date'],signal,label='Signal',color='b')
    plt.legend(loc='upper left')
    #plt.show()
    
    # put results in dataframe
    res = mac
    res['Signal Line'] = signal
    res['Indicator'] = res['Adj Close'] > res['Signal Line']
    return res

'''
Returns buy signal if 50day MA crosses above 200day MA, false otherwise
'''
def golden_cross(df):
    # 50 and 200 day moving averages
    fifty_day = simple_moving_avg(df,50)
    two_hun_day = simple_moving_avg(df,200)
  
    # check for crossover
    if fifty_day.iloc[-1] <= two_hun_day.iloc[-1]:
        return -1
    else:
        return 1

# Closer to upperband means market is more overbought, closer to lower band means market more oversold
def boiler_bands(df):
    df = df.reset_index()
    
    # calculate 20day sma and standard deviation
    sma = df.rolling(window=20).mean()
    sma.dropna(inplace=True)
    std = df.rolling(window=20).std()    
    std.dropna(inplace=True)
    
    # get upper and lower bands
    upper = sma['Adj Close'] + 2 * std['Adj Close']
    upper = upper.rename(columns={'Adj Close':'Upper'})
    lower = sma['Adj Close'] - 2 * std['Adj Close']
    lower = lower.rename(columns={'Adj Close':'Lower'})
    
    # add upper and lower bands to dataframe
    df['Upper'] = upper
    df['Lower'] = lower
    df.dropna(inplace=True)
    
    # plot
    plt.plot(df['Date'],df['Adj Close'],label='Adj Close')
    plt.plot(df['Date'],df['Upper'],label='Upper',color='g')
    plt.plot(df['Date'],df['Lower'],label='Lower',color='r')
    plt.fill_between(df['Date'],df['Lower'],df['Upper'],color='y')
    plt.legend(loc='upper left')
    #plt.show()
    
    df.set_index('Date')
    return df

'''
relative strength index
- momentum indicator that measures the magnitude of recent price changes to evaluate overbought
or oversold stock price conditions
'''
def relative_strength_index(df,periods=14):
    df = df.iloc[-periods-1:]
    df['Prev'] = df['Adj Close'].shift(1)
    df.dropna(inplace=True)
    
    df['Diff'] = df['Prev']-df['Adj Close']
    df['Gain'] = df['Diff']
    df['Loss'] = df['Diff']
    df['Gain'][df['Gain'] < 0] = 0
    df['Loss'][df['Loss'] > 0] = 0
    df['Loss'] = df['Loss'] * -1
    
    avg_gain = df['Gain'].sum()/periods
    avg_loss = df['Loss'].sum()/periods
    
    rsi = round(100 - (100/(1 + (avg_gain/avg_loss))),3)
    return rsi