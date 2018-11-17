# -*- encoding:utf-8 -*-
"""
    卖出择时因子：KDJ
"""


from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import pandas as pd

from .ABuFactorSellBase import AbuFactorSellBase, ESupportDirection
from ..IndicatorBu import ABuNDKdj
from ..UtilBu import ABuDateUtil

__author__ = 'sanit.peng'
__weixin__ = 'peng'


class AbuFactorSellKDJ(AbuFactorSellBase):

    def _init_self(self, **kwargs):

        self.fastk_period = kwargs.pop('fastk_period', 9)
        self.slowk_period = kwargs.pop('slowk_period', 3)
        self.fastd_period = kwargs.pop('fastd_period', 3)


        self.k_threshold = kwargs.pop('k_threshold', 80)
        self.d_threshold = kwargs.pop('d_threshold', 80)
        self.j_threshold = kwargs.pop('j_threshold', 100)

        #buld the symbol's kdj
        k, d, j = ABuNDKdj.calc_kdj(self.kl_pd, self.fastk_period, self.slowk_period, self.fastd_period)
        self.kdj = pd.DataFrame({
                'KDJ_K': k,
                'KDJ_D': d,
                'KDJ_J': j
        })

        #print (self.kl_pd)
        print (self.kl_pd[-20:-1])

        self.sell_type_extra = '{}:sell_n={}'.format(self.__class__.__name__, self.j_threshold)


    def support_direction(self):
        """因子支持两个方向"""
        return [ESupportDirection.DIRECTION_CAll.value, ESupportDirection.DIRECTION_PUT.value]

    def fit_day(self, today, orders):
        """
        :param today: 当前驱动的交易日金融时间序列数据
        :param orders: 买入择时策略中生成的订单序列
        :return:
        """

        """
        debug codes, for why enter 
        import traceback
        traceback.print_stack()   #mark for debug, sanit.peng
        """

        #use today
        k_value = self.kdj.KDJ_K[self.today_ind]
        d_value = self.kdj.KDJ_D[self.today_ind]
        j_value = self.kdj.KDJ_J[self.today_ind]

        #当同一个股票，或者多个股票有很多个订单的时候，len(orders) > 1 这个时候就会被调用
        #执行很多次。
        #不太明白的是，是否会出现，多个股票的情况，
        #因为这卖出因子是按照一个股票来实现的。
        #todo: 需要深入理解这个部分。

        for i, order in enumerate(orders):
            #已经卖出的不判断
            if order.sell_type != 'keep' : continue
           
            if j_value >= self.j_threshold:
                #print(order)
                print (ABuDateUtil.fmt_date(today.date), ' sell order %d (k, d, j) = (%f, %f, %f) ' 
                    %(i, k_value, d_value, j_value))

                #self.sell_today(order) if self.is_sell_today else self.sell_tomorrow(order)
                self.sell_tomorrow(order)

