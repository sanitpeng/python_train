# -*- encoding:utf-8 -*-
from __future__ import print_function
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import warnings

# noinspection PyUnresolvedReferences
import abu_local_env
import abupy
from abupy import AbuMetricsBase
from abupy import AbuFactorBuyBreak
from abupy import AbuFactorAtrNStop
from abupy import AbuFactorPreAtrNStop
from abupy import AbuFactorCloseAtrNStop
# run_loop_back等一些常用且最外层的方法定义在abu中
from abupy import abu
from abupy import EMarketTargetType, EMarketSourceType, EDataCacheType
from abupy import EMarketDataFetchMode
from abupy import AbuBenchmark
#indicators 
from abupy import nd
from abupy import AbuCapital
from abupy import AbuKLManager
from abupy import ABuSymbolPd

from abupy import AbuPickStockWorker
from abupy import AbuPickKDJ

from abupy import query_stock_info

warnings.filterwarnings('ignore')
sns.set_context(rc={'figure.figsize': (14, 7)})


STOCK_CAPITAL = 100000
#STOCK_SYMBOLS = ['002236', '600309']
STOCK_SYMBOLS = ['002236']

# 设置选股因子，None为不使用选股因子
#kdj defaut (9, 3, 3) can be set use (fastk_period, slowk_period, fastd_period)
#also k_threshold, d_threshold, j_threshold choice threshold should use those params, 

stock_pickers = [{'class': AbuPickKDJ, 'reversed': False}]
#stock_pickers = [{'class': AbuPickKDJ, 'reversed': True}]

# 买入因子依然延用向上突破因子
buy_factors = [{'xd': 60, 'class': AbuFactorBuyBreak},
               {'xd': 42, 'class': AbuFactorBuyBreak}]


# 卖出因子继续使用上一章使用的因子
sell_factors = [
    {'stop_loss_n': 1.0, 'stop_win_n': 3.0,
     'class': AbuFactorAtrNStop},
    {'class': AbuFactorPreAtrNStop, 'pre_atr_n': 1.5},
    {'class': AbuFactorCloseAtrNStop, 'close_atr_n': 1.5}
]

"""
stock_pick.choice_symbols: ['sz002502', 'sz002751', 'sz002680', 'sz000040', 'sz002323', 'sh601009', 'sh600800', 'sz300510', 'sh600122', 'sz000538', 'sz000534', 'sz002411', 'sz002301', 'sz300041', 'sz300197', 'sz002485', 'sz300237', 'sz000981', 'sz002668', 'sz002665', 'sh600688', 'sz000545', 'sh603031', 'sz002558', 'sz000979', 'sz002408', 'sz300362', 'sz002602', 'sz300178', 'sz300280', 'sz002719', 'sz002711', 'sz300324', 'sz002769', 'sz300028', 'sh601118']

stock_pick.choice_symbols: ['sz002502', 'sz002751', 'sz002680', 'sz000040', 'sz002323', 'sh601009', 'sh600800', 'sz300510', 'sh600122', 'sz000538', 'sz000534', 'sz200761', 'sz002411', 'sz002301', 'sz300197', 'sz002485', 'sz300237', 'sz002450', 'sz002857', 'sh603828', 'sz000981', 'sz002665', 'sz300538', 'sh600688', 'sz000545', 'sh603031', 'sz000979', 'sz002408', 'sz300362', 'sz002602', 'sz300178', 'sz300280', 'sz002719', 'sz002711', 'sh600892', 'sz300324', 'sz002769', 'sz002369', 'sz300028', 'sh601118']

"""


def pick_stock_by_kdj(show=True):

    #choice_symbols = ['002236']
    #choice_symbols = ['sh601118']
    #choice_symbols = ['sz002502', 'sz002751', 'sz002680', 'sz000040', 'sz002323', 'sh601009', 'sh600800', 'sz300510', 'sh600122', 'sz000538', 'sz000534', 'sz200761', 'sz002411', 'sz002301', 'sz300197', 'sz002485', 'sz300237', 'sz002450', 'sz002857', 'sh603828', 'sz000981', 'sz002665', 'sz300538', 'sh600688', 'sz000545', 'sh603031', 'sz000979', 'sz002408', 'sz300362', 'sz002602', 'sz300178', 'sz300280', 'sz002719', 'sz002711', 'sh600892', 'sz300324', 'sz002769', 'sz002369', 'sz300028', 'sh601118']

    # 选股都会是数量比较多的情况比如全市场股票
    choice_symbols = None

    benchmark = AbuBenchmark()
    capital = AbuCapital(STOCK_CAPITAL, benchmark)
    kl_pd_manager = AbuKLManager(benchmark, capital)
    stock_pick = AbuPickStockWorker(capital, benchmark, kl_pd_manager,
                                    choice_symbols=choice_symbols,
                                    stock_pickers=stock_pickers)
    stock_pick.fit()

    choiced_symbols = stock_pick.choice_symbols

    if show == True:
        for symbol in choiced_symbols:
            stock_info = query_stock_info(symbol)
            if stock_info is None or stock_info.empty:
                logging.info(symbol, "stock_info is none or empty")
                continue

            print (stock_info.co_name.values[0], stock_info.symbol.values[0], 
                stock_info.industry.values[0], stock_info.exchange.values[0])



def run_kdj():

    kl_pd = ABuSymbolPd.make_kl_df('002236', n_folds=3)
    #kl_pd = ABuSymbolPd.make_kl_df('000001', n_folds=3)
    #kl_pd = ABuSymbolPd.make_kl_df('600309', n_folds=3)

    print (kl_pd)

    #print (kl_pd[kl_pd['volume'] == 0]) 
    #print (kl_pd[kl_pd['close'] == 14.91]) 
    """
    print (kl_pd[kl_pd['date'] == 20171204]) 
    print (kl_pd[kl_pd['date'] == 20180604]) 
    print (kl_pd[kl_pd['date'] == 20180605]) 
    """

    k, d , j = nd.kdj.calc_kdj(kl_pd, 9, 3, 3)

    my_pd = pd.DataFrame({
                'KDJ_K': k,
                'KDJ_D': d,
                'KDJ_J': j
        })

    print (my_pd)


    mfi = nd.mfi.calc_mfi(kl_pd)
    
    print (mfi)



def init_env():
    #环境
    abupy.env.disable_example_env_ipython()
    #bd source have some data error, for example, 002236, some date error, for kdj
    #abupy.env.g_market_source = EMarketSourceType.E_MARKET_SOURCE_bd
    abupy.env.g_market_source = EMarketSourceType.E_MARKET_SOURCE_tx
    abupy.env.g_market_target = EMarketTargetType.E_MARKET_TARGET_CN    
    abupy.env.g_data_cache_type = EDataCacheType.E_DATA_CACHE_CSV

    #abupy.env.g_data_fetch_mode = EMarketDataFetchMode.E_DATA_FETCH_FORCE_LOCAL
    #abupy.env.g_data_fetch_mode = EMarketDataFetchMode.E_DATA_FETCH_NORMAL
    abupy.env.g_data_fetch_mode = EMarketDataFetchMode.E_DATA_FETCH_FORCE_NET

    
def download_all_data():
    from abupy import EMarketTargetType, EMarketSourceType, EDataCacheType

    # 关闭沙盒数据环境
    abupy.env.disable_example_env_ipython()
    abupy.env.g_data_fetch_mode = EMarketDataFetchMode.E_DATA_FETCH_FORCE_NET
    abupy.env.g_market_source = EMarketSourceType.E_MARKET_SOURCE_bd
    abupy.env.g_data_cache_type = EDataCacheType.E_DATA_CACHE_CSV

    # 首选这里预下载市场中所有股票的7年数据(做5年回测，需要预先下载6年数据)
    abu.run_kl_update(start='2011-11-03', end='2018-11-06', market=EMarketTargetType.E_MARKET_TARGET_CN)



if __name__ == "__main__":
    init_env()
    run_kdj()
    #pick_stock_by_kdj()
    #download_all_data()
