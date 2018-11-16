# -*- encoding:utf-8 -*-
"""
    买入择时因子：动态自适应双均线策略, 用于趋势判断和切片，参考我的曲线投影理论
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import math

import numpy as np
import pandas as pd

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
        print("bear bull marker peaks: ",)
        print(self._bear_bull_peaks)

        #根据拐点切片均线数据
        self._peaks, self._slices = self.split_by_peak(ma_array, source_pd = self.kl_pd,
            threshold = 1, min_dist = 30)

        print("symbol 's ma(%d) is sliced in %d slices" % (self.ma_period, len(self._slices)))



        #这些数据中包含将来数据，所以，没有办法估计天数。
        #但是，估计天数需要用全体数据作为经验值，所以先计算出来

        #计算每段数据的斜率等数据
        degs = np.array([])

        for slice in self._slices:
            close_deg = ABuRegUtil.calc_regress_deg(slice.close.values, False)
            ma_deg =    ABuRegUtil.calc_regress_deg(slice.ma.values, False)
            degs = np.append(degs, close_deg) 

            #print('close 趋势角度:' + str(close_deg))
            #print('ma 趋势角度:' + str(ma_deg))

        self._degs = degs
      
        #计算步长
        steps = np.array([]) 
        for i in range(0,len(self._peaks) - 1):
            step = self._peaks[i+1] - self._peaks[i]
            steps = np.append(steps, step)
        self._steps = steps

        """
        #验证性质代码，用来验证，角度的可信度，从现在的结果看是可信的
        #但是，需要有个量度参数对，可信度进行打分（置信度）
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
        
        self._bull_peak_step, self._bear_peak_step = self._split_deg_step_by_bear_bull()


    def _judge_bb(self, peak):
        
        bb_peaks = self._bear_bull_peaks
        kl_pd = self.kl_pd
        

        for i, bb_peak in enumerate(bb_peaks, 1):
            left_peak = bb_peaks[i-1]
            bb_peak = bb_peaks[i]
            if (kl_pd.close[bb_peak] > kl_pd.close[left_peak]):
                #牛市
                if (peak >= left_peak and peak <= bb_peak):
                    return 1 
            else:
                #熊市
                if (peak >= left_peak and peak <= bb_peak):
                    return -1 

        #如果到这里，是不是出差？
        print("why is here")
        return 0

    def _split_deg_step_by_bear_bull(self):
        ma_peaks = self._peaks

        print("ma_peaks")
        print(ma_peaks)

        bull_degs = []
        bull_steps = []
        bear_degs = []
        bear_steps = []
       
        print("ma_peaks len=, degs len = ", len(ma_peaks), len(self._degs))

        for i, ma_peak in enumerate(ma_peaks, 0): 
            print("******i = ma_peak = ", i, ma_peak) 
            if (i == 0): continue

            if (self._judge_bb(ma_peak) > 0):
                #牛市
                bull_degs.append(self._degs[i-1])
                bull_steps.append(self._steps[i-1])
            else:
                bear_degs.append(self._degs[i-1])
                bear_steps.append(self._steps[i-1])
        

        bull = pd.DataFrame({'deg':bull_degs, 'step':bull_steps})
        bear = pd.DataFrame({'deg':bear_degs, 'step':bear_steps})

        print("bull market arc values list:")
        print(bull)
        print("bear market arc values list:")
        print(bear)

        return bull, bear 

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

    def _find_left(self, index, peaks):
        #返回 pre left, left

        """
        for i, peak in enumerate(peaks):
            if ( i == 0 ): continue
            if index > peak :
                return peaks[i-1], peak
        """ 

        #先反转peaks, 这样，从后往前找，
        peaks = peaks.tolist()
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
  
    def _guess_steps(self, deg, bear_bull):
        #now，使用查表？？？这个是个经验公式？？？
        #这个算法比较复杂，理论上应该是某个数学模型，
        #哎，可惜数学都忘记了，这里算法如下：
        """
            1. 使用 牛熊的拐点，把均线的角度分段，视觉意义：在牛市的时候，使用
            历史的牛市角度和持续时间的比例。熊市的时候使用熊市的比例。
            2. 用这个比例来推测当天以后延续的天数
        """
        bull = self._bull_peak_step
        bear = self._bear_peak_step


        #牛熊权重，现在只是简单判断是否是牛熊
        if (bear_bull > 10):
            markets = bull.sort_values(by="deg")
        else:
            markets = bear.sort_values(by="deg")

        #print(markets)


        print(len(markets))

        for i, market in enumerate(markets):
            if (i == (len(markets) - 1)):
                #说明当前的角度是历史极大值，警告，并赋予，最大的值
                print("历史极大角度，上升极大")
                ret = markets.step[i]
                break

            if (deg < markets.deg[0]):
                #说明当前的角度是历史极小值，警告，并赋予，最小的值
                print("历史极小角度，下降极大")
                ret = markets.step[0]
                break


            if (markets.deg[i] <= deg and deg <= markets.deg[i+1]):
                print("----i = %d, deg = %f, left = %f, right = %f" %(i, deg, markets.deg[i], markets.deg[i+1]))
                #在历史的角度中，选择一个角度相差最近的？？？？
                #这个地方应该用比例或者其他算法，
                #todo: list
                d1 = abs(abs(deg) - abs(markets.deg[i]))
                d2 = abs(abs(deg) - abs(markets.deg[i+1]))

                print("d1 = %f, d2 = %f" %(d1, d2))
                #print("deg = %f, left = %f, right = %f" %(deg, markets.deg[i], markets.deg[i+1]))
                
                if (d1 < d2):
                    ret = markets.step[i]
                else:
                    ret = markets.step[i+1]
                break
            else:
                print("+++i = %d, deg = %f, left = %f, right = %f" %(i, deg, markets.deg[i], markets.deg[i+1]))

            print("i = %d, deg = %f, left = %f, right = %f" %(i, deg, markets.deg[i], markets.deg[i+1]))

        print("select step = ", ret)
        return ret



    def _day_weight(self, left, bear_bull):

        """
        r = []
        for i, deg in enumerate(degs):
            ratio = deg / steps[i]
            r.append(ratio)

        ratios = np.array(r)

        all_pd = pd.DataFrame({'deg': degs, 'step':steps, 'ratio':ratios})
        print("**************")
        print(all_pd)

        for i, deg in enumerate(all_pd.deg):
            print(deg, all_pd.step[i])

        test = all_pd.sort_values(by="deg")
        """

        kl_pd = self.kl_pd
        degs = self._degs
        steps = self._steps
        price = kl_pd.close[self.today_ind]
            
        #需要计算当天的斜率，因为，分段数据里面使用了将来数据

        
        values = kl_pd.close[left:self.today_ind]
        if ((self.today_ind - left)  == 0):
            print("left, today ", left, self.today_ind)
            #todo list
            return

        #print("left, today ", left, self.today_ind)
        deg = ABuRegUtil.calc_regress_deg(values, False)
        #print("today 's arc ", self.today_ind, deg)
        self._guess_steps(deg, bear_bull)



    def fit_day(self, today):
        kl_pd = self.kl_pd
       
        #根据牛熊均线判断牛熊
        #寻找今天的左端点和左左端点
        pre_left, left = self._find_left(self.today_ind, self._bear_bull_peaks)
        #print("pre_left, left:", pre_left, left)
        #print(kl_pd.close[pre_left], kl_pd.close[left])

        price = kl_pd.close[self.today_ind]

        #牛熊的权重，+-10,是均衡市场， > 20 - 100 牛市 <-(20 -100) 熊市
        self.bull_bear_weight = 0

        if (kl_pd.close[left] > kl_pd.close[pre_left]):
            #目前在下降通道，熊市
            #print("现在是熊市 :")
            self.bull_bear_weight = -20
        else:
            #目前在上升通道，牛市
            #print("现在是牛市 :")
            self.bull_bear_weight = 20

            if (price < kl_pd.ma_bear_bull[self.today_ind]) :
                print("牛市，但今日价格低于牛熊分界，发出警告，weight < -50 不参与交易")
                self.bull_bear_weight = self.bull_bear_weight - 100

        #print("bull bear weight: ", self.bull_bear_weight)

        _, left = self._find_left(self.today_ind, self._peaks)
        self._day_weight(left, self.bull_bear_weight)

