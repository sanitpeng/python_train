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

from .ABuFactorSellBase import AbuFactorSellBase, ESupportDirection

__author__ = 'sanit.peng'
__weixin__ = 'peng'


class AbuFactorSellCurveProjection(AbuFactorSellBase):

    def _init_self(self, **kwargs):

        self.fastk_period = kwargs.pop('fastk_period', 9)
        self.slowk_period = kwargs.pop('slowk_period', 3)
        self.fastd_period = kwargs.pop('fastd_period', 3)


        self.k_threshold = kwargs.pop('k_threshold', 80)
        self.d_threshold = kwargs.pop('d_threshold', 80)
        self.j_threshold = kwargs.pop('j_threshold', 100)
        self.mfi_threshold = kwargs.pop('mfi_threshold', 80)

        #buld the symbol's kdj
        k, d, j = ABuNDKdj.calc_kdj(self.kl_pd, self.fastk_period, self.slowk_period, self.fastd_period)
        mfi = ABuNDMfi.calc_mfi(self.kl_pd)

        self._param_pd = pd.DataFrame({
                'KDJ_K': k,
                'KDJ_D': d,
                'KDJ_J': j,
                'MFI'  : mfi
        })

        print (self._param_pd)
        self.mfi_sell_indicate = 0
        self.kdj_sell_indicate = 0



        self.sell_type_extra = '{}:sell_n={}'.format(self.__class__.__name__, self.j_threshold)


    def support_direction(self):
        """因子支持两个方向"""
        return [ESupportDirection.DIRECTION_CAll.value, ESupportDirection.DIRECTION_PUT.value]

    def strategy_1(self, today):
        """
        :param today: 当前驱动的交易日金融时间序列数据
        :return:
        """

        #use today
        k_value = self._param_pd.KDJ_K[self.today_ind]
        d_value = self._param_pd.KDJ_D[self.today_ind]
        j_value = self._param_pd.KDJ_J[self.today_ind]
        mfi = self._param_pd.MFI[self.today_ind]

        if j_value >= self.j_threshold:
            print (ABuDateUtil.fmt_date(today.date), '(k, d, j) = (%f, %f, %f) ' %(k_value, d_value, j_value))
            #print (self._param_pd.MFI[self.today_ind - 5:self.today_ind + 5])
            print("********mfi, j indicate ", self.mfi_sell_indicate, self.kdj_sell_indicate)
            self.kdj_sell_indicate = self.kdj_sell_indicate + 1

        if (mfi > self.mfi_threshold):
            print (self._param_pd.MFI[self.today_ind])
            #print (ABuDateUtil.fmt_date(today.date), '(k, d, j) = (%f, %f, %f) ' %(k_value, d_value, j_value))
            print("------mfi, j indicate ", self.mfi_sell_indicate, self.kdj_sell_indicate)

            self.mfi_sell_indicate = self.mfi_sell_indicate + 1


        if (self.mfi_sell_indicate and self.kdj_sell_indicate):

            self.mfi_sell_indicate = 0
            self.kdj_sell_indicate = 0
            print("--- Sell stock at ", ABuDateUtil.fmt_date(today.date), "(j, mfi) = ", j_value, mfi)
            print("mfi, j indicate ", self.mfi_sell_indicate, self.kdj_sell_indicate)
            return True

        return False

    def fit_day(self, today, orders):
        
        print("order len =======", len(orders))
        for order in orders:
            print("*********", type(order))
            if order.sell_date != None:
                continue
            if self.strategy_1(today):
                print("######## sell tomorrow")
                print(ABuDateUtil.fmt_date(today.date), order)
                self.sell_tomorrow(order)
                #self.sell_today(order) if self.is_sell_today else self.sell_tomorrow(order)



