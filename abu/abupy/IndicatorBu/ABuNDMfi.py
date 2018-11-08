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
__weixin__ = 'peng'


"""

计算方法
1.典型价格（TP）=当日最高价、最低价与收盘价的算术平均值
2.货币流量（MF）=典型价格（TP）×N日内成交量
3.如果当日MF>昨日MF，则将当日的MF值视为正货币流量（PMF）
4.如果当日MF<昨日MF，则将当日的MF值视为负货币流量（NMF）
5.MFI=100-[100/(1+PMF/NMF)]
6.参数N一般设为14日。

应用法则
1.显示超买超卖是MFI指标最基本的功能。当MFI>80时为超买，在其回头向下跌破80时，为短线卖出时机。
2.当MFI<20时为超卖，当其回头向上突破20时，为短线买进时机。
3.当MFI>80，而产生背离现象时，视为卖出信号。
4.当MFI<20，而产生背离现象时，视为买进信号。

注意要点
1.经过长期测试，MFI指标的背离讯号更能忠实的反应股价的反转现象。一次完整的波段行情，至少都会维持一定相当的时间，反转点出现的次数并不会太多。
2.将MFI指标的参数设定为14天时，其背离讯号产生的时机，大致上都能和股价的顶点吻合。因此在使用MFI指标时，参数设定方面应尽量维持14日的原则。


"""

# noinspection PyUnresolvedReferences

"""
use the talib's mfi
"""

def _calc_mfi_from_ta(pd, N = 14):

    import talib

    real = talib.MFI(pd.high, pd.low, pd.close, pd.volume, N)

    return real



"""通过在ABuNDBase中尝试import talib来统一确定指标计算方式, 外部计算只应该使用calc_kdj"""
"""
   always use from ta 
"""
calc_mfi = _calc_mfi_from_ta if g_calc_type == ECalcType.E_FROM_PD else _calc_mfi_from_ta


