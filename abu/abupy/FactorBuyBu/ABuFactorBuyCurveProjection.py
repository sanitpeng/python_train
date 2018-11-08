# -*- encoding:utf-8 -*-
"""
    买入择时因子：参见我的空间曲线投影理论
    时间-价平面：选择指标，KDJ
    量-价平面  ：选择指标，MFI
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import pandas as pd

from ..IndicatorBu import ABuNDKdj
from ..IndicatorBu import ABuNDMfi
from ..UtilBu import ABuDateUtil

from .ABuFactorBuyBase import AbuFactorBuyBase, AbuFactorBuyXD, BuyCallMixin, BuyPutMixin

__author__ = 'sanit.peng'
__weixin__ = 'sanit'


# noinspection PyAttributeOutsideInit
class ABuFactorBuyCurveProjection(AbuFactorBuyBase, BuyCallMixin):
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


        self.k_threshold = 50
        self.d_threshold = 50
        self.j_threshold = 0
       

        #buld the symbol's pd
        k, d, j = ABuNDKdj.calc_kdj(self.kl_pd, self.fastk_period, self.slowk_period, self.fastd_period)
        mfi = ABuNDMfi.calc_mfi(self.kl_pd)
        self._param_pd = pd.DataFrame({
                'KDJ_K': k,
                'KDJ_D': d,
                'KDJ_J': j,
                'MFI'  : mfi
        })


        print (self._param_pd)

        # 在输出生成的orders_pd中显示的名字
        self.factor_name = '{}:{}'.format(self.__class__.__name__, self.j_threshold )


    def strategy_1(self, today):
        
        
        k_value = self._param_pd.KDJ_K[self.today_ind]
        d_value = self._param_pd.KDJ_D[self.today_ind]
        j_value = self._param_pd.KDJ_J[self.today_ind]
        mfi = self._param_pd.MFI[self.today_ind]
       

        if (self.kl_pd.iloc[self.today_ind].date == 20180706) :
            print (ABuDateUtil.fmt_date(today.date), '(k, d, j, mfi) = (%f, %f, %f, %f) ' %(k_value, d_value, j_value, mfi))
            

        if j_value < self.j_threshold and d_value < self.d_threshold and k_value < self.k_threshold :
            #print (today)
            print (ABuDateUtil.fmt_date(today.date), '(k, d, j) = (%f, %f, %f) ' %(k_value, d_value, j_value))


            print (self._param_pd.MFI[self.today_ind - 5:self.today_ind + 5])
            if (mfi < 25) :
                return True

        return False



    def fit_day(self, today):
        """
        :param today: 当前驱动的交易日金融时间序列数据
        """



        if self.strategy_1(today) : 
            return self.buy_tomorrow()
        return None

