# -*- encoding:utf-8 -*-
"""
    买入择时因子：动态自适应双均线策略, 用于趋势判断和切片，参考我的曲线投影理论
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import math

import numpy as np

from .ABuFactorBuyBase import AbuFactorBuyBase, BuyCallMixin
from ..IndicatorBu.ABuNDMa import calc_ma_from_prices, calc_ma
from ..CoreBu.ABuPdHelper import pd_resample
from ..TLineBu.ABuTL import AbuTLine

__author__ = 'sanit.peng'
__weixin__ = 'sanit'


class AbuMaSplit(AbuFactorBuyBase, BuyCallMixin):
    """示例买入动态自适应双均线策略"""

    def _init_self(self, **kwargs):
        """
            kwargs中可选参数：ma_period: 均线周期，默认不设置，使用自适应动态快线
        """

        # 均线周期，默认使用30天均线
        self.ma_period = 30
        if 'ma_period' in kwargs:
            self.ma_period = kwargs['ma_period']        

        # 在输出生成的orders_pd中显示的名字
        self.factor_name = '{}:period={}'.format(self.__class__.__name__, self.ma_period)


    def _calc_ma(self, time_period):
        """
            动态决策慢线的值，规则如下：

            切片最近一段时间的金融时间序列，对金融时间序列进行变换周期重新采样，
            对重新采样的结果进行pct_change处理，对pct_change序列取abs绝对值，
            对pct_change绝对值序列取平均，即算出重新采样的周期内的平均变化幅度，

            上述的变换周期由10， 15，20，30....进行迭代, 直到计算出第一个重新
            采样的周期内的平均变化幅度 > 0.12的周期做为slow的取值
        """
        ma_array = calc_ma(self.kl_pd.close, time_period) 

        self.kl_pd.insert(len(self.kl_pd.columns.tolist()), 'ma', ma_array)  

        print(self.kl_pd)

        return ma_array

    def _detect_peaks_stub(self, ma_pd):
        
        NUM = 3
        splits = None;
        len = ma_pd.shape[0]

        len = (len / NUM)

        #print (ma_pd)

        """
        splits = ma_pd[0:len]

        for i in rang(1, NUM-1):
            splits.append(i*len, (i+1)*len)

        print(splits)
        return splits
        """
        return None



    def calc_trend_weight(self):
        
        ma_pd = self._calc_ma(self.ma_period)
        peaks = self._detect_peaks_stub(ma_pd)

         

        return


    def fit_day(self, today):
        pass
