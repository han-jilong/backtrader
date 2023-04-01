import os
import sys
import baostock as bs
import pandas as pd

from utils.Utils import GetModPath

modpath = GetModPath()

if __name__ == '__main__':
    # 登陆系统
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:' + lg.error_code)
    print('login respond  error_msg:' + lg.error_msg)

    # 获取沪深300成分股
    rs = bs.query_hs300_stocks()
    print('query_deposit_rate_data respond error_code:' + rs.error_code)
    print('query_deposit_rate_data respond  error_msg:' + rs.error_msg)

    # 打印结果集
    hs300_stocks  = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        hs300_stocks .append(rs.get_row_data())
    result = pd.DataFrame(hs300_stocks , columns=rs.fields)

    # 结果集输出到csv文件
    file_name = "hs300_stocks.csv"
    datapath = os.path.join(modpath, '..\\datas\\' + file_name)
    result.to_csv(datapath)
    print("get deposit rate to hs300_stocks.csv done")

    # 登出系统
    bs.logout()
