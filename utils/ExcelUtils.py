import datetime
import os
import sys
import time
import xlwt


def Write_result(details_info, annual_info, total_info):
    import time
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    sheet_details = book.add_sheet('details', cell_overwrite_ok=True)
    sheet_details_cols = ('日期', '股票', '买卖', '价格', '成本', '佣金')
    writeList2Sheet(sheet_details, details_info, sheet_details_cols)

    sheet_annual = book.add_sheet('annual', cell_overwrite_ok=True)
    sheet_annual_cols = ('股票', '日期', '年化收益率')
    writeList2Sheet(sheet_annual, annual_info, sheet_annual_cols)

    sheet_total = book.add_sheet('total', cell_overwrite_ok=True)
    sheet_total_cols = ('股票', '开始资金', '结束资金', '收益', '收益百分比')
    writeList2Sheet(sheet_total, total_info, sheet_total_cols)

    path = os.path.abspath(os.path.dirname(sys.argv[0]))
    time_now = datetime.datetime.now()
    strDate = time_now.strftime('%Y%m%d')
    strTime = time_now.strftime('%H%M%S')
    time = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    # file_path = path+'\\'+str(time) +'.xls'
    file_path = path + '\\' + strDate + "_" + strTime + '.xls'
    book.save(file_path)

def writeList2Sheet(sheet, list, cols):
    for i in range(len(cols)):
        sheet.write(0, i, cols[i])

    for i in range(len(list)):
        for j in range(len(list[i])):
            sheet.write(i+1, j, list[i][j])