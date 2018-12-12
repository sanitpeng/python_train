# -*- encoding:utf-8 -*-
"""
    买入择时因子：KDJ
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import pandas as pd

from ..IndicatorBu import ABuNDKdj,ABuNDMfi
from ..UtilBu import ABuDateUtil, AbuMaSplit

from .ABuFactorBuyBase import AbuFactorBuyBase, AbuFactorBuyXD, BuyCallMixin, BuyPutMixin

__author__ = 'sanit.peng'
__weixin__ = 'sanit'


# noinspection PyAttributeOutsideInit
class AbuFactorBuyKDJ(AbuFactorBuyBase, BuyCallMixin):
    """买入择时类，混入BuyCallMixin，即突破触发买入event"""

    def _init_self(self, **kwargs):


        # 不要使用kwargs.pop('xd', 20), 明确需要参数xq


        self.mean_split = AbuMaSplit(self.kl_pd, **kwargs)

        self.fastk_period = 9
        if 'fastk_period' in kwargs:
            self.fastk_period = kwargs['fastk_period']

        self.slowk_period = 3
        if 'slowk_period' in kwargs:
            self.slowk_period = kwargs['slowk_period']

        self.fastd_period = 3
        if 'fastd_period' in kwargs:
            self.fastd_period = kwargs['fastd_period']

        """
        1) K线是快速确认线——数值在90以上为超买，数值在10以下为超卖；
            D线是慢速主干线——数值在80以上为超买，数值在20以下为超卖；
            J线为方向敏感线，当J值大于90，特别是连续5天以上，股价至少会形成短期头部，
            反之J值小于10时，特别是连续数天以上，股价至少会形成短期底部        
        """

        
        self.k_threshold = 10
        if 'k_threshold' in kwargs:
            self.k_threshold = kwargs['k_threshold']        

        self.d_threshold = 20
        if 'd_threshold' in kwargs:
            self.d_threshold = kwargs['d_threshold']        

        self.j_threshold = 0
        if 'j_threshold' in kwargs:
            self.j_threshold = kwargs['j_threshold']        

        self.mfi_threshold = 20
        if 'mfi_threshold' in kwargs:
            self.mfi_threshold = kwargs['mfi_threshold']        

        self.debug = False 
        if 'debug' in kwargs:
            self.debug = kwargs['debug']        



        #buld the symbol's kdj
        k, d, j = ABuNDKdj.calc_kdj(self.kl_pd, self.fastk_period, self.slowk_period, self.fastd_period)
        mfi = ABuNDMfi.calc_mfi(self.kl_pd)

        self._param_pd = pd.DataFrame({
                'KDJ_K': k,
                'KDJ_D': d,
                'KDJ_J': j,
                'MFI'  : mfi
        })


        self.mean_split.calc_trend_weight()
        self.kdj_buy_indicate = 0
        self.mfi_buy_indicate = 0


        # 在输出生成的orders_pd中显示的名字
        self.factor_name = '{}:j={},mfi={}'.format(self.__class__.__name__, 
            self.j_threshold, self.mfi_threshold )

    def _show_info(self, date, dict):
        if self.debug == False :
            return

        print(ABuDateUtil.fmt_date(date), ' buy signal, indicator: ')
        for key,value in dict.items():
            print('    {key}:{value}'.format(key = key, value = value))
        print(' ')


    def strategy_1(self, today):
        k_value = self.indicator['kdj'][0]
        d_value = self.indicator['kdj'][1]
        j_value = self.indicator['kdj'][2]
        mfi = self.indicator['mfi']

        if j_value < self.j_threshold and d_value < self.d_threshold and k_value < self.k_threshold :
            self.kdj_buy_indicate = self.kdj_buy_indicate + 1

            if (mfi < self.mfi_threshold):
                self.mfi_buy_indicate = 0
                self.kdj_buy_indicate = 0
                return True
                

        """
        if (mfi < self.mfi_threshold):
            self.mfi_buy_indicate = self.mfi_buy_indicate + 1


        if (self.mfi_buy_indicate and self.kdj_buy_indicate):
            self.mfi_buy_indicate = 0
            self.kdj_buy_indicate = 0
            return True
        """
        return False



    def strategy_2(self, today):
        #希望的策略，但是判断牛熊太不准确，包括人识别牛熊也不准确，暂时放弃

        """"
        #当前个股的牛熊权重-20 ---- 20, 说明在牛熊转换期间，并且很有可能是牛转熊，不参与交易
        weight = abs(self.indicator['bb_weight'])
        if (weight < 20):

            if (self.indicator['bb_weight'] > 10):    

                if (self.debug):
                    print(ABuDateUtil.fmt_date(today.date),
                        "牛熊交界，价格低于牛熊分界，倾向牛市上涨中继， 不参与交易 weight = %d"
                        %(self.indicator['bb_weight']))
                return None

            if (self.debug):
                print(ABuDateUtil.fmt_date(today.date), 
                    "牛熊交界,不参与交易 weight = %d" %(self.indicator['bb_weight']))

            return None

        
        if (self.indicator['bb_weight'] >= 20):
            #牛市策略
            #if j_value < 0 :
            if j_value < self.j_threshold and d_value < self.d_threshold and k_value < self.k_threshold :
                # 生成买入订单, 由于使用了今天的收盘价格做为策略信号判断，所以信号发出后，只能明天买
                self._show_info(today.date, self.indicator)
                return self.buy_tomorrow()
            return None 


        if (self.indicator['bb_weight'] <= -20):
            #熊市策略
            if j_value < self.j_threshold and d_value < self.d_threshold and k_value < self.k_threshold :
                # 生成买入订单, 由于使用了今天的收盘价格做为策略信号判断，所以信号发出后，只能明天买
                self._show_info(today.date, self.indicator)
                return self.buy_tomorrow()
            return None
        """ 
        return False

    def fit_day(self, today):
        """
        :param today: 当前驱动的交易日金融时间序列数据
        """
        
        mean_split = self.mean_split
        mean_split.today_ind = self.today_ind
        self.indicator = mean_split.fit_day(today)
        
        #use today
        k_value = self._param_pd.KDJ_K[self.today_ind]
        d_value = self._param_pd.KDJ_D[self.today_ind]
        j_value = self._param_pd.KDJ_J[self.today_ind]

        kdj = [k_value, d_value, j_value]
        self.indicator['kdj'] = kdj
        self.indicator['mfi'] = self._param_pd.MFI[self.today_ind]


        """
        一下这段是百度百科上的，参考，学习总是让人进步, sanit.peng

        实战研判
        1) K线是快速确认线——数值在90以上为超买，数值在10以下为超卖；
            D线是慢速主干线——数值在80以上为超买，数值在20以下为超卖；
            J线为方向敏感线，当J值大于90，特别是连续5天以上，股价至少会形成短期头部，
            反之J值小于10时，特别是连续数天以上，股价至少会形成短期底部。
        2) 当K值由较小逐渐大于D值，在图形上显示K线从下方上穿D线，
            所以在图形上K线向上突破D线时，俗称金叉，即为买进的讯号。
            实战时当K，D线在20以下交叉向上，此时的短期买入的信号较为准确；
            如果K值在50以下，由下往上接连两次上穿D值，形成右底比左底高的“W底”形态时，
            后市股价可能会有相当的涨幅。
        3) 当K值由较大逐渐小于D值，在图形上显示K线从上方下穿D线，显示趋势是向下的，
            所以在图形上K线向下突破D线时，俗称死叉，即为卖出的讯号。
            实战时当K，D线在80以上交叉向下，此时的短期卖出的信号较为准确；
            如果K值在50以上，由上往下接连两次下穿D值，形成右头比左头低的“M头”形态时，
            后市股价可能会有相当的跌幅。
        4) 通过KDJ与股价背离的走势，判断股价顶底也是颇为实用的方法：
            A) 股价创新高，而KD值没有创新高，为顶背离，应卖出； 
            B) 股价创新低，而KD值没有创新低，为底背离，应买入；
            需要注意的是KDJ顶底背离判定的方法，只能和前一波高低点时KD值相比，不能跳过去相比较。


        """

        #均线价格<=0，说明均线周期没有到
        if (self.indicator['ma'] <= 0): return None

        if (self.strategy_1(today)):
            self._show_info(today.date, self.indicator)
            return self.buy_tomorrow()

        return None

