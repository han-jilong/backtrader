import os
import sys


def GetDataName(filePath):
    '''
    :return get the data name from the data file name
    :param filePath:  os.path.join(modpath, '..\\datas\\sh.000104_380能源.csv')
    :return: 380能源
    '''
    baseName = os.path.basename(filePath) # sh.000104_380能源.csv
    tmpArr = baseName.split('_')
    name = tmpArr[1].split('.')[0]
    return name

def GetStartDate():
    return "2007-01-01"

def GetEndDate():
    return "2022-12-30"

def GetModPath():
    return os.path.dirname(os.path.abspath(sys.argv[0]))