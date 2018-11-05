# -*- encoding:utf-8 -*-
from __future__ import print_function
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
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

warnings.filterwarnings('ignore')
sns.set_context(rc={'figure.figsize': (14, 7)})


STOCK_CAPITAL = 100000
#STOCK_SYMBOLS = ['002236', '600309']
STOCK_SYMBOLS = ['002236']

# 设置选股因子，None为不使用选股因子
stock_pickers = None

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




def run_kdj(show=True):
   
    """
    benchmark = AbuBenchmark()
    capital = AbuCapital(STOCK_CAPITAL, benchmark)
    kl_pd_manager = AbuKLManager(benchmark, capital)

    kl_pd = kl_pd_manager.get_pick_time_kl_pd('002236')
    """
   

    kl_pd = ABuSymbolPd.make_kl_df('002236', n_folds=1)

    print (kl_pd)

    k, d , j = nd.kdj.calc_kdj(kl_pd, 9, 3, 3)

    print ("k = ", k[-10:])
    print ("d = ", d[-10:])
    print ("j = ", j[-10:])




def init_env():
    #环境
    #abupy.env.enable_example_env_ipython()
    abupy.env.disable_example_env_ipython()
    abupy.env.g_market_source = EMarketSourceType.E_MARKET_SOURCE_bd
    #abupy.env.g_data_cache_type = EDataCacheType.E_DATA_CACHE_CSV
    #abupy.env.g_data_fetch_mode = EMarketDataFetchMode.E_DATA_FETCH_FORCE_LOCAL

    # 设置初始资金数
    init_cash = STOCK_CAPITAL
    # 择时股票池
    choice_symbols = STOCK_SYMBOLS
    
def download_all_data():
    from abupy import EMarketTargetType, EMarketSourceType, EDataCacheType

    # 关闭沙盒数据环境
    abupy.env.disable_example_env_ipython()
    abupy.env.g_market_source = EMarketSourceType.E_MARKET_SOURCE_bd
    abupy.env.g_data_cache_type = EDataCacheType.E_DATA_CACHE_CSV

    # 首选这里预下载市场中所有股票的7年数据(做5年回测，需要预先下载6年数据)
    abu.run_kl_update(start='2011-11-03', end='2018-11-03', market=EMarketTargetType.E_MARKET_TARGET_CN)



if __name__ == "__main__":
    init_env()
    run_kdj()
