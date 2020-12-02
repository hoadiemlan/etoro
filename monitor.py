#!/usr/bin/python
########### Python 2.7 #############
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


def showinfo(title, massage):
        root = tkinter.Tk()
        root.withdraw()
        messagebox.showinfo(title, massage)

class ema_info:
    def __init__(self):
        self.ema50 = None
        self.ema20 = None
        self.ema10 = None
        self.ema5  = None
        self.closeprice = None

class monitor:
    def __init__(self, id):
        # major and minor plot seetings
        self.majorLocator = MultipleLocator(200)
        self.majorFormatter = FormatStrFormatter('%d')
        self.minorLocator = MultipleLocator(50)

        self.majoryLocator = MultipleLocator(10)
        self.majoryFormatter = FormatStrFormatter('%d')
        self.minoryLocator = MultipleLocator(2)

        self.majorXLocator = MultipleLocator(24)
        self.majorXFormatter = FormatStrFormatter('%d')
        self.minorXLocator = MultipleLocator(6)

        #item infomation
        self.ema_OneMinute   = ema_info()
        self.ema_FiveMinutes = ema_info()
        self.ema_TenMinutes  = ema_info()
        self.ema_OneHour     = ema_info()
        self.item_id = id  #gold

        #state
        self.state_mua = None


    def history(self, a):
        body = a[2:-4]
        closeprice = []

        for key in body:
            if "Close" in key:
                c = key.split(':')
                close = float(re.findall('\d+\.\d+', c[1])[0])
                closeprice.append(close)

        return closeprice

    def moving_average(self, x, n, type='simple'):
        """
        compute an n period moving average.
        type is 'simple' | 'exponential'
        """
        x = np.asarray(x)
        if type == 'simple':
            weights = np.ones(n)
        else:
            weights = np.exp(np.linspace(-1., 0., n))

        weights /= weights.sum()

        a = np.convolve(x, weights, mode='full')[:len(x)]
        a[:n] = a[n]
        return a

    def plotcoin(self, duration):
        #get ema
        if   duration == "OneMinute":
            ema = self.ema_OneMinute
        elif duration == "FiveMinutes":
            ema = self.ema_FiveMinutes
        elif duration == "TenMinutes":
            ema = self.ema_TenMinutes
        elif duration == "OneHour":
            ema = self.ema_OneHour
        else:
            ema = self.ema_OneMinute

        N = 50
        fig, ax1 = plt.subplots()
        ax1.plot(ema.closeprice[-N:], 'g-')
        ax1.plot(ema.ema10[-N:], 'b-')
        ax1.plot(ema.ema5 [-N:], 'r-')
        ax1.set_title(' Pri ')
        ax1.set_xlabel('Time', color='k')
        ax1.set_ylabel('Close ', color='k')
        ax1.tick_params(colors='k')
        ax1.grid(color='k', linestyle='-', linewidth=0.5)
        ax1.yaxis.set_major_locator(self.majorLocator)
        ax1.yaxis.set_major_formatter(self.majorFormatter)
        ax1.yaxis.set_minor_locator(self.minorLocator)
        ax1.xaxis.set_major_locator(self.majorXLocator)
        ax1.xaxis.set_major_formatter(self.majorXFormatter)
        ax1.xaxis.set_minor_locator(self.minorXLocator)
        plt.savefig('pic.png')  # save the figure to file
        plt.close(fig)  # close the figure

    def cal_ema(self, duration):
        # create link
        if duration == "OneMinute":
            link = "/candles/desc.json/OneMinute/480/"+str(self.item_id)
        elif duration == "FiveMinutes":
            link = "/candles/desc.json/FiveMinutes/480/"+str(self.item_id)
        elif duration == "TenMinutes":
            link = "/candles/desc.json/TenMinutes/480/"+str(self.item_id)
        elif duration == "OneHour":
            link = "/candles/desc.json/OneHour/480/"+str(self.item_id)
        else:
            link = "/candles/desc.json/FiveMinutes/480/"+str(self.item_id)

        #get data from database
        conn = http.client.HTTPSConnection('candle.etoro.com')
        conn.request("GET", link)
        response = conn.getresponse()
        data = str(response.read())
        a = data.split(',')
        closeprice = self.history(a)
        closeprice = closeprice[::-1]
        conn.close()
        closeprice = db2.get("closeprice")
        closeprice = closeprice[-scan:]+closeprice[:-scan]
        # db2.set("closeprice", closeprice)
        # db2.dumpdb()

        #calculate ema
        ema50 = self.moving_average(closeprice, 50, type='simple')
        ema20 = self.moving_average(closeprice, 20, type='simple')
        ema10 = self.moving_average(closeprice, 10, type='simple')
        ema5  = self.moving_average(closeprice, 5 , type='simple')
        ema_total = ema_info()
        ema_total.ema50 = ema50
        ema_total.ema20 = ema20
        ema_total.ema10 = ema10
        ema_total.ema5  = ema5
        ema_total.closeprice = closeprice
        if duration == "OneMinute":
            self.ema_OneMinute = ema_total
        elif duration == "FiveMinutes":
            self.ema_FiveMinutes = ema_total
        elif duration == "TenMinutes":
            self.ema_TenMinutes = ema_total
        elif duration == "OneHour":
            self.ema_OneHour = ema_total
        else:
            self.ema_OneMinute = ema_total
        # print(closeprice)

    def check_uptrend(self, data):
        result = 1
        for i in range(1, len(data)):
            if (data[i-1] > data[i]):
                result = 0
        return result

    def check_above(self, data1, data2):
        result = 1
        for i in range(len(data1)):
            if (data1[i] < data2[i]):
                result = 0
        return result

    def check_signal(self, duration):
        # get ema
        if duration == "OneMinute":
            ema = self.ema_OneMinute
        elif duration == "FiveMinutes":
            ema = self.ema_FiveMinutes
        elif duration == "TenMinutes":
            ema = self.ema_TenMinutes
        elif duration == "OneHour":
            ema = self.ema_OneHour
        else:
            ema = self.ema_OneMinute

        end10 = ema.ema10[-1:]
        end5  = ema.ema5 [-1:]
        end10_10 = ema.ema10[-10:]
        end10_5 = ema.ema5[-10:]

        print(scan)
        if self.state_mua == 0 and self.check_above(end10, end5) and self.check_uptrend(end5) and ema.closeprice[-1]>=ema.ema10[-1]:
            self.state_mua = 1
            print("Tin hieu mua state " + str(self.state_mua))
            showinfo("info", "state 1")

        if self.state_mua == 1  and self.check_above(end5, end10):
            self.state_mua = 2
            print("Tin hieu mua state " + str(self.state_mua))
            showinfo("info", "state 2")

        if self.state_mua == 2  and self.check_above(end10, end5):
            self.state_mua = 0
            print("Tin hieu mua state " + str(self.state_mua))
            showinfo("info", "state 0")


        if ema.ema5[-2]<= ema.ema10[-2] and  ema.ema5[-1] > ema.ema10[-1] :
            showinfo("info", "Cat tang")
        if ema.ema5[-2] >= ema.ema10[-2] and  ema.ema5[-1] < ema.ema10[-1] :
            showinfo("info", "Cat giam")

    def start(self):
        # duration = "OneMinute"
        duration = "FiveMinutes"
        self.cal_ema(duration)
        self.plotcoin(duration)
        self.check_signal(duration)


#Request URL: https://candle.etoro.com/candles/desc.json/FiveMinutes/2/17?client_request_id=84b05e54-868a-47a4-ab23-f0eb5f5ecb5b
#Request URL: https://candle.etoro.com/candles/desc.json/OneMinute/2/17?client_request_id=f4c5fe46-4ad0-496b-a965-c62724f51a85
#Request URL: https://etorologsapi.etoro.com/api/v2/monitoring?applicationIdentifier=ReToro
#Request URL: https://candle.etoro.com/candles/desc.json/OneMinute/2/18?client_request_id=c058d294-cc6b-4f03-a5e5-b6aae2d1771e : Vang



# a = monitor(100000)
a = monitor(18)
scan = 44
a.start()
# for i in range (40,50):
#     scan = i
#     a.start()
# while (1):
#     a.start()
