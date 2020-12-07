import pandas_datareader as pdr
import matplotlib.pyplot as plt
import datetime
import pandas as pd
import numpy as np
import http.client, urllib, base64, re
import matplotlib as mpl
# from myform import *
from FoobarDB import *
db2 = FoobarDB("./etoro_db.json")
scan = 50
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import time
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import tkinter
from tkinter import messagebox
from tkinter import filedialog
import requests
import matplotlib
matplotlib.use('TkAgg')



def history(a):
    body = a[2:-4]
    closeprice = []

    for key in body:
        if "Close" in key:
            c = key.split(':')
            close = float(re.findall('\d+\.\d+', c[1])[0])
            closeprice.append(close)
    return closeprice

def telegram_bot_sendtext(bot_message):

   bot_token = '1495511574:AAEXKD5LND4FpYFJCY-z6vG0h15kPGT1TOc'
   bot_chatID = '1080795442' #Duong
   send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
   response = requests.get(send_text)
   return response.json()

stop =0
while (stop !=1):
    duration =   "OneMinute"
    item_id  = 18
    # create link
    if duration == "OneMinute":
        link = "/candles/desc.json/OneMinute/480/"+str(item_id)
    elif duration == "FiveMinutes":
        link = "/candles/desc.json/FiveMinutes/480/"+str(item_id)
    elif duration == "TenMinutes":
        link = "/candles/desc.json/TenMinutes/480/"+str(item_id)
    elif duration == "OneHour":
        link = "/candles/desc.json/OneHour/480/"+str(item_id)
    else:
        link = "/candles/desc.json/FiveMinutes/480/"+str(item_id)

    #get data from database
    conn = http.client.HTTPSConnection('candle.etoro.com')
    conn.request("GET", link)
    response = conn.getresponse()
    data = str(response.read())
    a = data.split(',')
    closeprice = history(a)
    closeprice = closeprice[::-1]
    conn.close()

    # aapl = pdr.get_data_yahoo('AAPL',
    #                           start=datetime.datetime(2006, 10, 1),
    #                           end=datetime.datetime(2011, 1, 1))

    stock = pd.DataFrame(closeprice, columns = ['Close'])

    # Initialize the short and long windows
    short_window = 5
    long_window = 10

    # Initialize the `signals` DataFrame with the `signal` column
    signals = pd.DataFrame(closeprice, columns = ['Close'])
    signals['signal'] = 0.0

    # Create short simple moving average over the short window
    signals['short_mavg'] = stock['Close'].rolling(window=short_window, min_periods=1, center=False).mean()

    # Create long simple moving average over the long window
    signals['long_mavg'] = stock['Close'].rolling(window=long_window, min_periods=1, center=False).mean()

    # Create signals
    signals['signal'][short_window:] = np.where(signals['short_mavg'][short_window:]
                                                > signals['long_mavg'][short_window:], 1.0, 0.0)

    # Generate trading orders
    signals['positions'] = signals['signal'].diff()

    # last_one = int(list(signals['positions'][-15:])[3])
    try:
        signals_en10 =list(signals['positions'][-10:])
        last_one = int(signals_en10[-1])
    except:
        last_one = 0

    if (last_one==1):
        telegram_bot_sendtext("Mua vao di")
    elif (last_one==-1):
        telegram_bot_sendtext("Ban ra di")
    pass

    # # Print `signals`
    # print(signals)

# # Import `pyplot` module as `plt`
# import matplotlib.pyplot as plt
#
# # Initialize the plot figure
# fig = plt.figure()
#
# # Add a subplot and label for y-axis
# ax1 = fig.add_subplot(111,  ylabel='Price in $')
#
# # Plot the closing price
# stock['Close'].plot(ax=ax1, color='r', lw=2.)
#
#
# # Plot the short and long moving averages
# signals[['short_mavg', 'long_mavg']].plot(ax=ax1, lw=2.)
#
# # Plot the buy signals
# ax1.plot(signals.loc[signals.positions == 1.0].index,
#          signals.short_mavg[signals.positions == 1.0],
#          '^', markersize=10, color='m')
#
# # Plot the sell signals
# ax1.plot(signals.loc[signals.positions == -1.0].index,
#          signals.short_mavg[signals.positions == -1.0],
#          'v', markersize=10, color='k')
#
# # Show the plot
# plt.show()


