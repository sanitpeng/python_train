# -*- encoding:utf-8 -*-
"""
    选股因子：kdj
"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import numpy as np

from ..UtilBu import ABuRegUtil
from .ABuPickStockBase import AbuPickStockBase, reversed_result
from ..IndicatorBu import ABuNDKdj 

__author__ = 'sanit.peng'
__weixin__ = 'peng'


class AbuPickKDJ(AbuPickStockBase):
    def _init_self(self, **kwargs):
        # 暂时与base保持一致不使用kwargs.pop('a', default)方式

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


    @reversed_result
    def fit_pick(self, kl_pd, target_symbol):
        """开始根据自定义拟合角度边际参数进行选股"""

        k, d, j = ABuNDKdj.calc_kdj(kl_pd, self.fastk_period, self.slowk_period, self.fastd_period)
        #use last day 
        v = j[-1]
       
        # 根据参数进行条件判断
        if v < self.j_threshold:
            return True
        return False

    def fit_first_choice(self, pick_worker, choice_symbols, *args, **kwargs):
        raise NotImplementedError('AbuPickKDJ fit_first_choice unsupported now!')
