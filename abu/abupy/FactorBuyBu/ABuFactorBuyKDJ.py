# -*- encoding:utf-8 -*-
"""
    买入择时因子：KDJ
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import pandas as pd

from ..IndicatorBu import ABuNDKdj
from ..UtilBu import ABuDateUtil

from .ABuFactorBuyBase import AbuFactorBuyBase, AbuFactorBuyXD, BuyCallMixin, BuyPutMixin

__author__ = 'sanit.peng'
__weixin__ = 'sanit'


# noinspection PyAttributeOutsideInit
class AbuFactorBuyKDJ(AbuFactorBuyBase, BuyCallMixin):
    """买入择时类，混入BuyCallMixin，即突破触发买入event"""

    def _init_self(self, **kwargs):
        # 不要使用kwargs.pop('xd', 20), 明确需要参数xq

        self.fastk_period = 9
        if 'fastk_period' in kwargs:
            self.fastk_period = kwargs['fastk_period']

        self.slowk_period = 3
        if 'slowk_period' in kwargs:
            self.slowk_period = kwargs['slowk_period']

        self.fastd_period = 3
        if 'fastd_period' in kwargs:
            self.fastd_period = kwargs['fastd_period']


        self.k_threshold = 20
        self.d_threshold = 20
        self.j_threshold = 0
       

        #buld the symbol's kdj
        k, d, j = ABuNDKdj.calc_kdj(self.kl_pd, self.fastk_period, self.slowk_period, self.fastd_period)
        self.kdj = pd.DataFrame({
                'KDJ_K': k,
                'KDJ_D': d,
                'KDJ_J': j
        })


        #print (self.kl_pd)

        # 在输出生成的orders_pd中显示的名字
        self.factor_name = '{}:{}'.format(self.__class__.__name__, self.j_threshold )

    def fit_day(self, today):
        """
        :param today: 当前驱动的交易日金融时间序列数据
        """

        #use today
        k_value = self.kdj.KDJ_K[self.today_ind]
        d_value = self.kdj.KDJ_D[self.today_ind]
        j_value = self.kdj.KDJ_J[self.today_ind]

        
        if j_value < self.j_threshold and d_value < self.d_threshold and k_value < self.k_threshold :
            # 生成买入订单, 由于使用了今天的收盘价格做为策略信号判断，所以信号发出后，只能明天买
            print (ABuDateUtil.fmt_date(today.date), '(k, d, j) = (%f, %f, %f) ' %(k_value, d_value, j_value))
            return self.buy_tomorrow()
        return None

