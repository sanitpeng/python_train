#coding=utf-8

from __future__ import print_function
#需要安装 mysql-python
#macOS 安装方法
#sudo brew install mysql-connector-c
#pip install mysql-python

import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql import (INTEGER, CHAR, FLOAT, BIGINT)
from sqlalchemy import Column, Table, MetaData


import warnings

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# noinspection PyUnresolvedReferences
import abu_local_env
import abupy

from abupy import abu
from abupy import EMarketTargetType, EMarketSourceType, EDataCacheType
from abupy import EMarketDataFetchMode, EMarketDataSplitMode
from abupy import ABuSymbolPd
from abupy import kline_pd
from abupy import ABuDateUtil


host = 'localhost'
db = 'stock_db'
user = 'root'
password = '11111111'

engine = create_engine(str(r"mysql+mysqldb://%s:" + '%s' + "@%s/%s?charset=utf8") 
    % (user, password, host, db))

def get_last_day(table, engine):
    try:
        sql=r'select * from `{}` order by date desc limit 1;'.format(table)

        df = pd.read_sql(sql=sql, con=engine)
    except Exception as e:
        print(e.message)
        return None

    return df['date'][0]



def download(tab, engine):


    l = tab.split('#')
    symbol = l[0] + l[1]

    start = get_last_day(tab, engine)
    if (start is None):
        return

    start = ABuDateUtil.fmt_date(start)
    end = ABuDateUtil.current_str_date()

    tup = kline_pd(symbol, data_mode=EMarketDataSplitMode.E_DATA_SPLIT_UNDO,
        n_folds=2, start=start, end=end, save=False )

    df = tup[0]
    if (df is None):
        #有可能是指数，其他数据源没有
        print(tab, "Error, no date read from net work", start, end)
        return

    df.drop(columns=['pre_close', 'date_week', 'p_change'])

    #注意其他数据源无法读出成交量?，用close*volume模拟，不准确
    #ps. 指数的成交量，感觉是除以100， 所以，以后不处理指数, 大盘处理下
    if (symbol == 'SH000001'):
        df['volume'] = df['volume'] / 100

    count = df['close'] * df['volume']
    df['count'] = count
    #转化成整型
    df['count'] = df['count'].astype(np.int64)

    #重新排序 
    order = ['date', 'open', 'high', 'low', 'close', 'volume', 'count']
    write_df = df[order]
    #删除第一行，即删除start当天的


    if (write_df.shape[0] == 0):
        print("{} 可能停牌".format(tab))
        return

    write_df.drop(write_df.index[0], axis = 0, inplace=True)


    """
    测试代码
    #tab = tab + "_test"
    """

    try:
        write_df.to_sql(tab, con=engine, if_exists='append', index=False)
        return write_df
    except Exception as e:
        print(e.message)   
        return None



def file_list(file_dir):
    L=[]
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            fn, ext = os.path.splitext(file)
            if ext == '.csv':
                L.append((os.path.join(root, file), fn))
    return L



def init_env():
    #环境
    abupy.env.disable_example_env_ipython()
   
    #缺省使用网易，网易接口数据比较准确
    abupy.env.g_market_source = EMarketSourceType.E_MARKET_SOURCE_nt
    
    abupy.env.g_market_target = EMarketTargetType.E_MARKET_TARGET_CN
    abupy.env.g_data_cache_type = EDataCacheType.E_DATA_CACHE_CSV

    abupy.env.g_data_fetch_mode = EMarketDataFetchMode.E_DATA_FETCH_FORCE_NET

if __name__ == "__main__":

    init_env()

    fl = file_list('/Users/sanit/abu/data/tdx_csv/Volumes/export')

    len = len(fl)
    for i, l in enumerate(fl):
        _ = download(l[1], engine)
        #print("处理%s, 完成进度百分之%d" %( l[0], (float(i+1)/len)*100 ), end="\r" )
        print("处理%s, 完成进度百分之%d" %( l[0], (float(i+1)/len)*100 ) )
    
    print("\n")

