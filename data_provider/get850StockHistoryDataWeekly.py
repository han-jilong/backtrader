import os
import sys
import baostock as bs
import pandas as pd

from utils.Utils import GetStartDate
from utils.Utils import GetEndDate
from utils.Utils import GetModPath

modpath = GetModPath()
start_date = GetStartDate()
end_date = GetEndDate()
# peTTM    滚动市盈率
# psTTM    滚动市销率
# pcfNcfTTM    滚动市现率
# pbMRQ    市净率
# columns = "date,code,open,high,low,close,preclose,volume,amount,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM"
columns = "date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg"
def get_stock_basic_info():
    stock_codes = []
    datapath = os.path.join(modpath, '..\\datas\\hs300_stocks.csv')
    df = pd.read_csv(datapath)
    stock_codes.extend(get_stock_codes(df))

    datapath = os.path.join(modpath, '..\\datas\\sz50_stocks.csv')
    df = pd.read_csv(datapath)
    stock_codes.extend(get_stock_codes(df))

    datapath = os.path.join(modpath, '..\\datas\\zz500_stocks.csv')
    df = pd.read_csv(datapath)
    stock_codes.extend(get_stock_codes(df))
    # 去重
    new_list = list(set(stock_codes))
    print("old count %d, new count %d" % (len(stock_codes), len(new_list)))
    return new_list

def get_stock_codes(df):
    codes = []
    for ind, row in df.iterrows():
        code = row['code']
        code_name = row['code_name']
        codes.append(code + "@" + code_name)
    return codes


def get_stock_history_data(code, start_date, end_date):
    # 详细指标参数，参见“历史行情指标参数”章节；“周月线”参数与“日线”参数不同。
    # adjustflag：复权类型，默认不复权：3；1：后复权；2：前复权。已支持分钟线、日线、周线、月线前后复权
    # 周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg
    rs = bs.query_history_k_data_plus(code, columns, start_date=start_date, end_date=end_date, adjustflag="1", frequency="w")
    # 打印结果集
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)
    return result


if __name__ == '__main__':
    # 登陆系统
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:' + lg.error_code)
    print('login respond  error_msg:' + lg.error_msg)
    stockCodes = get_stock_basic_info()
    dir = os.path.join(modpath, '..\\datas\\850stocks_weekly\\')
    if not os.path.isdir(dir):
        os.makedirs(dir)

    for stock in stockCodes:
        code, name = stock.split("@")
        hist_data = get_stock_history_data(code, start_date, end_date)
        file_name = code + "_" + name + ".csv"
        datapath = os.path.join(modpath, '..\\datas\\850stocks_weekly\\' + file_name)
        hist_data.to_csv(datapath)
        print(stock + " done")

    # 登出系统
    bs.logout()
    print("all done")
