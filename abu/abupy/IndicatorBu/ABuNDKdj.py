# -*- encoding:utf-8 -*-

"""
kdj indicator

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .ABuNDBase import plot_from_order, g_calc_type, ECalcType
from ..CoreBu.ABuPdHelper import pd_rolling_mean, pd_rolling_std

__author__ = 'sanit.peng'
__weixin__ = 'sanit'


# noinspection PyUnresolvedReferences

# 同花顺和通达信等软件中的SMA
def _sma_cn(close, timeperiod) :
    close = np.nan_to_num(close)
    return reduce(lambda x, y: ((timeperiod - 1) * x + y) / timeperiod, close)

# 同花顺和通达信等软件中的KDJ
"""
  there are very little diff with sina kdj, no check why? by sanit.peng
"""
def _kdj_cn(high, low, close, fastk_period, slowk_period, fastd_period) :

    import talib
    kValue, dValue = talib.STOCHF(high, low, close, fastk_period, fastd_period=1, fastd_matype=0)

    kValue = np.array(map(lambda x : _sma_cn(kValue[:x], slowk_period), range(1, len(kValue) + 1)))
    dValue = np.array(map(lambda x : _sma_cn(kValue[:x], fastd_period), range(1, len(kValue) + 1)))


    jValue = 3 * kValue - 2 * dValue

    """
    #func = lambda arr : np.array([0 if x < 0 else (100 if x > 100 else x) for x in arr])
    # modify by pengxu , allow j < 0 and j > 100
    func = lambda arr : np.array([x if x < 0 else (x if x > 100 else x) for x in arr])

    kValue = func(kValue)
    dValue = func(dValue)
    jValue = func(jValue)
    """

    return kValue, dValue, jValue



def _calc_kdj_from_ta(prices, fastk_period, slowk_period, fastd_period):

    return _kdj_cn(prices.high, prices.low, prices.close, fastk_period, slowk_period, fastd_period)



"""通过在ABuNDBase中尝试import talib来统一确定指标计算方式, 外部计算只应该使用calc_kdj"""
"""
   always use from ta 
"""
calc_kdj = _calc_kdj_from_ta if g_calc_type == ECalcType.E_FROM_PD else _calc_kdj_from_ta


