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

from extends.DataFeeds import GenericCSV_BaoShare
from utils.Utils import GetDataName


class DoubleMA_Strategy(bt.Strategy):
    params = (
        ("sma5", 5),
        ("sma20", 20),
        ("smafv", 5),
        ("smasv", 10)
    )

    # 打印日志
    def log(self, txt, dt=None):
        dt = dt or self.data.datetime.date(0)
        print("%s, %s, " % (dt, txt))

    def __init__(self):
        # 用于保存订单
        self.order = None

        # 计算MA5
        self.sma5 = bt.ind.MovingAverageSimple(self.data.close, period=self.params.sma5)

        # 计算MA20
        self.sma20 = bt.ind.MovingAverageSimple(self.data.close, period=self.params.sma20)

        self.smafv = bt.ind.MovingAverageSimple(self.data.volume, period=self.params.smafv)
        self.smasv = bt.ind.MovingAverageSimple(self.data.volume, period=self.params.smasv)

    def notify_order(self, order):
        # 等待订单提交，订单被cerebro接受
        if order.status in [order.Submitted, order.Accepted]:
            return

        # 等待订单完成
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    '买入，价格: %.2f, 成本: %.2f, 佣金 %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm)
                )
            else:
                self.log(
                    '卖出，价格: %.2f, 成本: %.2f, 佣金 %.2f' %
                    (order.executed.price,
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

        self.log('盈利： %.2f, 手续费： %.2f\n' %
                 (trade.pnl, trade.pnlcomm))  # pnl：盈利  pnlcomm：手续费

    def next(self):
        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return
        # Check if we are in the market
        if not self.position:
            # 当今天的10日均线大于30日均线并且昨天的10日均线小于30日均线，则进入市场（买）
            if self.sma5[0] > self.sma20[0] and self.sma5[-1] < self.sma20[-1] \
                    and self.smafv[0] > self.smasv[0]:
                # 判断订单是否完成，完成则为None，否则为订单信息
                if self.order:
                    return

                # 若上一个订单处理完成，可继续执行买入操作
                self.order = self.buy()
        else:
            # 当今天的10日均线小于30日均线并且昨天的10日均线大于30日均线，则退出市场（卖）
            if self.sma5[0] < self.sma20[0] and self.sma5[-1] > self.sma20[-1]:
                # 卖出
                self.order = self.sell()


if __name__ == "__main__":
    cerebro = bt.Cerebro()  # 实例化大脑
    cerebro.addstrategy(DoubleMA_Strategy)  # 添加策略
    # 准备股票日线数据，输入到backtrader
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, '..\\datas\\sh.000104_380能源.csv')
    dataname = GetDataName(datapath)
    # Create a Data Feed
    data = GenericCSV_BaoShare(dataname=datapath)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data=data, name=dataname)

    cerebro.broker.setcash(1000000000.0)  # 初始资金
    cerebro.broker.setcommission(commission=0.0003)  # 佣金，双边各 0.0003
    # cerebro.broker.set_slippage_perc(perc=0.0001)  # 滑点：双边各 0.0001

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())  # 打印初始现金
    cerebro.run()  # 执行策略
    print('Ending Portfolio Value: %.2f' % cerebro.broker.getvalue())  # 打印策略运行结束后的现金

    cerebro.plot(style='candlestick', volume=True)  # 可视化
