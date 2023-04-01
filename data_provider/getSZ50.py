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

    # 获取上证50成分股
    rs = bs.query_sz50_stocks()
    print('query_deposit_rate_data respond error_code:' + rs.error_code)
    print('query_deposit_rate_data respond  error_msg:' + rs.error_msg)

    # 打印结果集
    sz50_stocks = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        sz50_stocks.append(rs.get_row_data())
    result = pd.DataFrame(sz50_stocks, columns=rs.fields)

    # 结果集输出到csv文件
    file_name = "sz50_stocks.csv"
    datapath = os.path.join(modpath, '..\\datas\\' + file_name)
    result.to_csv(datapath)
    print("get deposit rate to sz50_stocks.csv done")

    # 登出系统
    bs.logout()
