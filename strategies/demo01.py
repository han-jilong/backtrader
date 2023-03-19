from __future__ import (absolute_import, division, print_function,unicode_literals)
import datetime
import os
import sys

import backtrader as bt
import pandas as pd

from extends.DataFeeds import GenericCSV_BaoShare
from utils.Utils import GetDataName


class TestSizer(bt.Sizer):
    '''
    https://zhuanlan.zhihu.com/p/114782214
    海龟交易具体策略
    入场：最新价格为20日价格高点，买入一单元股票
    加仓：最新价格>上一次买入价格+0.5*ATR，买入一单元股票，最多3次加仓
    出场：最新价格为10日价格低点，清空仓位
    止损：最新价格<上一次买入价格-2*ATR，清空仓位
    '''
    params = (('stake', 1),)
    def _getsizing(self, comminfo, cash, data, isbuy):
        if isbuy:
            return self.p.stake
        position = self.broker.getposition(data)
        if not position.size:
            return 0
        else:
            return position.size
        return self.p.stake

class TestStrategy(bt.Strategy):
    params = ( ('maperiod', 15),  ('printlog', True), )
    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):

        self.dataclose = self.datas[0].close
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low

        self.order = None
        self.buyprice = 0
        self.buycomm = 0
        self.newstake = 0
        self.buytime = 0
        # n日均线
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0].close, period=self.params.maperiod, subplot=False)
        # 参数计算，唐奇安通道上轨、唐奇安通道下轨、ATR
        self.DonchianHi = bt.indicators.Highest(self.datahigh(-1), period=20, subplot=False)
        self.DonchianLo = bt.indicators.Lowest(self.datalow(-1), period=10, subplot=False)
        self.TR = bt.indicators.Max((self.datahigh(0)- self.datalow(0)), abs(self.dataclose(-1) -   self.datahigh(0)), abs(self.dataclose(-1)  - self.datalow(0) ))
        self.ATR = bt.indicators.SimpleMovingAverage(self.TR, period=14, subplot=True)
        # 唐奇安通道上轨突破、唐奇安通道下轨突破
        self.CrossoverHi = bt.ind.CrossOver(self.dataclose(0), self.DonchianHi, plot=False, subplot=False)
        self.CrossoverLo = bt.ind.CrossOver(self.dataclose(0), self.DonchianLo, plot=False, subplot=False)
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                (order.executed.price,
                order.executed.value,
                order.executed.comm),doprint=True)
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                     (order.executed.price,
                     order.executed.value,
                     order.executed.comm),doprint=True)
                self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (trade.pnl, trade.pnlcomm))

    def next(self):
        if self.order:
            return
        #入场
        if self.CrossoverHi > 0 and self.buytime == 0:
            self.newstake = self.broker.getvalue() * 0.01 / self.ATR
            self.newstake = int(self.newstake / 100) * 100
            self.sizer.p.stake = self.newstake
            self.buytime = 1
            self.order = self.buy()
        #加仓
        elif self.datas[0].close >self.buyprice+0.5*self.ATR[0] and self.buytime > 0 and self.buytime < 5:
            self.newstake = self.broker.getvalue() * 0.01 / self.ATR
            self.newstake = int(self.newstake / 100) * 100
            self.sizer.p.stake = self.newstake
            self.order = self.buy()
            self.buytime = self.buytime + 1
        #出场
        elif self.CrossoverLo < 0 and self.buytime > 0:
            self.order = self.sell()
            self.buytime = 0
        #止损
        elif self.datas[0].close < (self.buyprice - 2*self.ATR[0]) and self.buytime > 0:
            self.buytime = 0
            self.order = self.sell()
        else:
            self.log('none')

    def stop(self):
        self.log('(MA Period %2d) Ending Value %.2f' % (self.params.maperiod, self.broker.getvalue()), doprint=True)

if __name__ == '__main__':
    # 创建主控制器
    cerebro = bt.Cerebro()
    # 加入策略
    cerebro.addstrategy(TestStrategy)
    # 准备股票日线数据，输入到backtrader
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, '..\\datas\\sh.000104_380能源.csv')
    dataname = GetDataName(datapath)
    # Create a Data Feed
    data = GenericCSV_BaoShare(dataname=datapath)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data=data, name=dataname)

    # broker设置资金、手续费
    cerebro.broker.setcash(100000000.0)
    cerebro.broker.setcommission(commission=0.001)
    # 设置买入策略
    cerebro.addsizer(TestSizer)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # 启动回测
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # 曲线绘图输出
    cerebro.plot(style='candlestick')