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

columns = "date,code,open,high,low,close,preclose,volume,amount,pctChg"

def get_index_basic_info():
    datapath = os.path.join(modpath, '..\\datas\\一级行业指数.csv')
    df = pd.read_csv(datapath)
    # print(df.head())
    # print(df.tail())
    return df


def get_index_history_data(code, start_date, end_date):
    # 详细指标参数，参见“历史行情指标参数”章节；“周月线”参数与“日线”参数不同。
    # 周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg
    rs = bs.query_history_k_data_plus(code, columns, start_date=start_date, end_date=end_date, frequency="d")
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
    df = get_index_basic_info()
    i = 0
    for ind, row in df.iterrows():
        if i == 0:
            i = i + 1
            continue  # skip header
        i = i + 1
        index_code = row['指数代码']
        index_name = row['指数简称'].replace(" ", "")
        hist_data = get_index_history_data(index_code, start_date, end_date)
        file_name = index_code + "_" + index_name + ".csv"
        dir = os.path.join(modpath, '..\\datas\\IndustoryIndex\\')
        if not os.path.isdir(dir):
            os.makedirs(dir)
        datapath = os.path.join(modpath, '..\\datas\\IndustoryIndex\\' + file_name)
        hist_data.to_csv(datapath)
        print(index_name + " done")
    # 登出系统
    bs.logout()
    print("all done")
