'''
# 双均线策略
————————————————
版权声明：本文为CSDN博主「数据分析小鹏友」的原创文章，遵循CC
4.0
BY - SA版权协议，转载请附上原文出处链接及本声明。
原文链接：https: // blog.csdn.net / small__roc / article / details / 128052713
'''
import os
import sys

import pandas as pd
import backtrader as bt
from matplotlib import pyplot as plt

from extends.DataFeeds import GenericCSV_BaoShare
from utils.Utils import GetDataName

plt.rcParams['font.sans-serif']=['SimHei'] #显示中文标签
plt.rcParams['axes.unicode_minus']=False
class DoubleMA_Strategy(bt.Strategy):
    params = (
        ("smaFast", 20),
        ("smaSlow", 60),
        ("smafv", 5),
        ("smasv", 10)
    )
    def nextstart(self):
        print('--------------------------------------------------')
        print('nextstart called with len', len(self))
        print('--------------------------------------------------')

    # 打印日志
    def log(self, txt, dt=None):
        dt = dt or self.data.datetime.date(0)
        print("%s, %s, " % (dt, txt))

    def __init__(self):
        # 用于保存订单
        self.order = None

        # 计算快均线
        self.smaFast = bt.ind.ExponentialMovingAverage(self.data.close, period=self.params.smaFast)

        # 计算慢均线
        self.smaSlow = bt.ind.ExponentialMovingAverage(self.data.close, period=self.params.smaSlow)

        # self.smafv = bt.ind.ExponentialMovingAverage(self.data.volume, period=self.params.smafv)
        # self.smasv = bt.ind.ExponentialMovingAverage(self.data.volume, period=self.params.smasv)

    def notify_order(self, order):
        # 等待订单提交，订单被cerebro接受
        if order.status in [order.Submitted, order.Accepted]:
            return

        # 等待订单完成
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    '买入 %s，价格: %.2f, 成本: %.2f, 佣金 %.2f' %
                    (self.data._name,
                     order.executed.price,
                     order.executed.value,
                     order.executed.comm)
                )
            else:
                self.log(
                    '卖出 %s，价格: %.2f, 成本: %.2f, 佣金 %.2f' %
                    (self.data._name,
                     order.executed.price,
                     order.executed.value,
                     order.executed.comm)
                )

        # 如果订单保证金不足，将不会执行，而是执行以下拒绝程序
        elif order.status in [order.Cancled, order.Margin, order.Rejected]:
            self.log("Order Canceled(取消)/Margin()/Rejected(拒绝)")

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('盈利： %.2f, 净利润： %.2f\n' %
                 (trade.pnl, trade.pnlcomm))  # pnl：盈利  pnlcomm：手续费

    def next(self):
        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return
        # Check if we are in the market
        if not self.position:
            # 当今天的10日均线大于30日均线并且昨天的10日均线小于30日均线，则进入市场（买）
            if self.smaFast[0] > self.smaSlow[0] and self.smaFast[-1] < self.smaSlow[-1] \
                    and self.data.close[0] > self.smaSlow[0]:
                # 判断订单是否完成，完成则为None，否则为订单信息
                if self.order:
                    return

                # 若上一个订单处理完成，可继续执行买入操作
                self.order = self.buy()
        else:
            # 当今天的10日均线小于30日均线并且昨天的10日均线大于30日均线，则退出市场（卖）
            if (self.smaFast[0] < self.smaSlow[0] and self.smaFast[-1] > self.smaSlow[-1]) or self.data.close[0] < self.smaSlow[0]:
                # 卖出
                self.order = self.sell()


if __name__ == "__main__":
    start_cash = float(10000000.0)
    cerebro = bt.Cerebro()  # 实例化大脑
    cerebro.addstrategy(DoubleMA_Strategy)  # 添加策略
    # 准备股票日线数据，输入到backtrader
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    modpath = os.path.abspath(os.path.join(modpath, ".."))
    datapath = modpath + '\\datas\\IndustoryIndexWeekly\\sh.000104_380能源_weekly.csv'
    dataname = GetDataName(datapath)
    # Create a Data Feed
    data = GenericCSV_BaoShare(dataname=datapath)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data=data, name=dataname)

    cerebro.broker.setcash(start_cash)  # 初始资金
    cerebro.broker.setcommission(commission=0.0003)  # 佣金，双边各 0.0003
    # cerebro.broker.set_slippage_perc(perc=0.0001)  # 滑点：双边各 0.0001
    cerebro.addsizer(bt.sizers.PercentSizer, percents=70)
    cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.Years)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())  # 打印初始现金
    results = cerebro.run()  # 执行策略
    print('tested result on %s: ' % dataname)
    strat0 = results[0]
    # If no name has been specified, the name is the class name lowercased
    tret_analyzer = strat0.analyzers.getbyname('timereturn').get_analysis()
    for key in tret_analyzer:
        print('date %s : result %s' % (key, tret_analyzer[key]))
    end_cash = float(cerebro.broker.getvalue())
    diff = end_cash - start_cash
    print('Ending Portfolio Value: %.2f' % cerebro.broker.getvalue())  # 打印策略运行结束后的现金
    print('total win or loss: %.2f percent' % (diff*100/start_cash))

    # cerebro.plot(style='candlestick', volume=True)  # 可视化
