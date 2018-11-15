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
from ..UtilBu import ABuRegUtil

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
        self.bear_bull_period = 60
        if 'bear_bull_period' in kwargs:
            self.bear_bull_period = kwargs['bear_bull_period']        

        # 在输出生成的orders_pd中显示的名字
        self.factor_name = '{}:period={}'.format(self.__class__.__name__, self.ma_period)


    def _calc_ma(self, time_period):
        """
            计算均线
        """
        ma_array = calc_ma(self.kl_pd.close, time_period) 
        
        #why nan_to_num is no use, by sanit.peng
        #np.nan_to_num(ma_array)
        ma_array[np.isnan(ma_array) == True] = 0


        return ma_array

    def _detect_peaks(self, ma_array, threshold = 1, min_dist = 30):
    
        # sample codes from https://github.com/MonsieurV/py-findpeaks
        # py-findpeaks/tests/lows_and_highs.py
        # install import peakutils, pip install PeakUtils

        import peakutils.peak

        cb = np.array(ma_array.tolist())

        #print(type(ma_array), type(ma_array.tolist()), type(np.array(ma_array.tolist())), type(cb)) 


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


    def _weight(self):
        print(self._degs)
        print(self._steps)
        
        degs = self._degs
        steps = self._steps

        for i, deg in enumerate(degs):
            #验证下斜率公式
            #y = kx + b, b 为切片开始点的值, k = tanα, α是弧度，先将角度转化成弧度
            b = self._slices[i].close[0]
            x = self._steps[i]
            k = math.tan(np.deg2rad(self._degs[i]))
            y = k * x + b
            y1 = self._slices[i].close[-1]
            
            print("y = kx + b, (k , x, b)", k, x, b)
            print("y = , y'= ", y, y1)

        for i in range(0, len(degs)):
            v = degs[i] / steps[i]
            print ("v = ", v)

        """
        v = deg / step
        step = deg / k
        """


        #print (self._slices)

    def calc_trend_weight(self):

        #计算均线
        #计算牛熊线 60日均线
        bear_bull_array = self._calc_ma(self.bear_bull_period)
        self.kl_pd.insert(len(self.kl_pd.columns.tolist()), 'ma_bear_bull', bear_bull_array)

        #计算n日均线
        ma_array = self._calc_ma(self.ma_period)
        self.kl_pd.insert(len(self.kl_pd.columns.tolist()), 'ma', ma_array)  

        #print(self.kl_pd)
        

        #找出牛熊线的拐点，但是不切片原始数据 source_pd = None
        self._bear_bull_peaks, _ = self.split_by_peak(bear_bull_array, source_pd = None, 
            threshold = 1, min_dist = 150)
        #根据拐点切片均线数据
        self._peaks, self._slices = self.split_by_peak(ma_array, source_pd = self.kl_pd,
            threshold = 1, min_dist = 30)

        print("symbol 's ma(%d) is sliced in %d slices" % (self.ma_period, len(self._slices)))
        print("bear bull marker peaks:")
        print(self._bear_bull_peaks)


        #计算每段数据的斜率等数据
        degs = np.array([])

        for slice in self._slices:
            close_deg = ABuRegUtil.calc_regress_deg(slice.close.values, False)
            ma_deg =    ABuRegUtil.calc_regress_deg(slice.ma.values, False)
            degs = np.append(degs, close_deg) 

            print('close 趋势角度:' + str(close_deg))
            print('ma 趋势角度:' + str(ma_deg))

        self._degs = degs
      
        #计算步长
        steps = np.array([]) 
        for i in range(0,len(self._peaks) - 1):
            step = self._peaks[i+1] - self._peaks[i]
            steps = np.append(steps, step)
        self._steps = steps

        self._weight()


    def split_by_peak(self, wave, threshold, min_dist, source_pd = None):

        #找出拐点,包含高点和低点
        highs, lows = self._detect_peaks(wave, threshold, min_dist)
        
        peaks = np.append(highs, lows)
        peaks = np.sort(peaks)


        if (peaks[0] > 0):
            peaks = np.insert(peaks, 0, [0])

        if (peaks[-1] < len(wave)):
            peaks = np.append(peaks, [len(wave) - 1])

        print("peak's is ", peaks)

        #只求出拐点
        if ((source_pd is None) or (source_pd.empty)):
            return peaks, None

        slices = []
        
        for i in range(0, len(peaks) - 1):
            #print(peaks[i] , peaks[i+1])
            slice = source_pd.iloc[peaks[i] : peaks[i+1]]
            slices.append(slice)

        """
        print(source_pd)
        print(slices);
        """
        
        return peaks, slices

    def _find_left(self, index):
        #返回 pre left, left

        """
        peaks = self._bear_bull_peaks
        for i, peak in enumerate(peaks):
            if ( i == 0 ): continue
            if index > peak :
                return peaks[i-1], peak
        """ 

        #先反转peaks, 这样，从后往前找，
        peaks = self._bear_bull_peaks.tolist()
        peaks.reverse()
        #print(peaks)
        #print("index = ", index)

        #我们补充了端点，所以，当前index等于最后一个peak
        for i, peak in enumerate(peaks):
            #print("i, peak, index", i, peak, index) 
            if index > peak :
                if (peak == 0 ):
                    return 0, peak
                else:
                    return peak, peaks[i+1]
 
        #如果到这里，说明错误
        return 0, 0
    
    def fit_day(self, today):
        kl_pd = self.kl_pd
        
        #寻找今天的左端点和左左端点
        pre_left, left = self._find_left(self.today_ind)
        print("pre_left, left:", pre_left, left)

        price = kl_pd.close[self.today_ind]

        #牛熊的权重，+-10,是均衡市场， > 20 - 100 牛市 <-(20 -100) 熊市
        self.bull_bear_weight = 0

        print(kl_pd.close[left], kl_pd.close[pre_left])

        if (kl_pd.close[left] > kl_pd.close[pre_left]):
            #目前在下降通道，熊市
            print("现在是熊市 :")
            self.bull_bear_weight = -20
        else:
            #目前在上升通道，牛市
            print("现在是牛市 :")
            self.bull_bear_weight = 20

            if (price < kl_pd.ma_bear_bull[self.today_ind]) :
                print("牛市，但今日价格低于牛熊分界，发出警告，weight < -50 不参与交易")
                self.bull_bear_weight = self.bull_bear_weight - 100

        print("bull bear weight: ", self.bull_bear_weight)

        
