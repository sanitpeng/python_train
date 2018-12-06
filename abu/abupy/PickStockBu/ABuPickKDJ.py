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

from ..CoreBu import ABuEnv
import logging

log_func = logging.info if ABuEnv.g_is_ipython else print

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
        if 'k_threshold' in kwargs:
            self.k_threshold = kwargs['k_threshold']

        self.d_threshold = 20
        if 'd_threshold' in kwargs:
            self.d_threshold = kwargs['d_threshold']

        self.j_threshold = 10
        if 'j_threshold' in kwargs:
            self.j_threshold = kwargs['j_threshold']



    @reversed_result
    def fit_pick(self, kl_pd, target_symbol):
        """开始根据自定义拟合角度边际参数进行选股"""

        k, d, j = ABuNDKdj.calc_kdj(kl_pd, self.fastk_period, self.slowk_period, self.fastd_period)
        kl_pd['KDJ_K'] = k
        kl_pd['KDJ_D'] = d
        kl_pd['KDJ_J'] = j

        #use last day 
        k_int = k[-1]
        d_int = d[-1]
        j_int = j[-1]


        #去除掉停牌的股票
        volume = kl_pd['volume'][-1]
        if volume == 0 :
            return False        
       
        # 根据参数进行条件判断
        if j_int < self.j_threshold:
            #log_func(u'kdj选中，[{},{},{}], j_threshold:{}'.format(k_int, 
            #    d_int, j_int, self.j_threshold))
            return True

        #log_func(u'kdj未选中，[{},{},{}], j_threshold:{}'.format(k_int, 
        #    d_int, j_int, self.j_threshold))
        return False

    def fit_first_choice(self, pick_worker, choice_symbols, *args, **kwargs):
        raise NotImplementedError('AbuPickKDJ fit_first_choice unsupported now!')
