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
        
        #why nan_to_num is no use, by sanit.peng
        #np.nan_to_num(ma_array)
        ma_array[np.isnan(ma_array) == True] = 0

        self.kl_pd.insert(len(self.kl_pd.columns.tolist()), 'ma', ma_array)  
        #print(self.kl_pd)

        return ma_array

    def _detect_peaks(self, ma_array):
    
        # sample codes from https://github.com/MonsieurV/py-findpeaks
        # py-findpeaks/tests/lows_and_highs.py
        # install import peakutils, pip install PeakUtils

        import peakutils.peak

        cb = np.array(ma_array.tolist())

        #print(type(ma_array), type(ma_array.tolist()), type(np.array(ma_array.tolist())), type(cb)) 

        threshold = 0.02
        min_dist = 150


        print('Detect high peaks with minimum height and distance filters.')
        highs = peakutils.peak.indexes(
            np.array(cb),
            thres=threshold/max(cb), min_dist=min_dist
        )
        print('High peaks are: %s' % (highs))

        print('Detect low peaks with minimum height and distance filters.')
        # Invert the signal.
        cbInverted = cb * -1

        lows = peakutils.peak.indexes(
            np.array(cbInverted),
            thres=threshold/max(cbInverted), min_dist=min_dist
        )
        print('Low peaks are: %s' % (lows))        

        return highs, lows



    def calc_trend_weight(self):

        #计算均线
        ma_array = self._calc_ma(self.ma_period)
        #print(ma_array)

        self._peaks, self._slices = self.split_by_peak(ma_array, self.kl_pd)

        print("symbol 's ma(%d) is sliced in %d slices" % (self.ma_period, len(self._slices)))


    def split_by_peak(self, wave, source_pd = None):

        #找出拐点,包含高点和低点
        highs, lows = self._detect_peaks(wave)
        
        peaks = np.append(highs, lows)
        peaks = np.sort(peaks)


        #why ??
        #if ((source_pd == None) or (source_pd.empty)):
        if (source_pd.empty):
            return peaks, None


        if (peaks[0] > 0):
            peaks = np.insert(peaks, 0, [0])

        if (peaks[-1] < len(source_pd)):
            peaks = np.append(peaks, [len(source_pd)])

        print("peak's is ", peaks)

        slices = []
        
        for i in range(0, len(peaks) - 1):
            #print(peaks[i] , peaks[i+1])
            slice = source_pd.iloc[peaks[i] : peaks[i+1]]
            slices.append(slice)

        #print(slices);

        return peaks, slices


    def fit_day(self, today):
        pass
