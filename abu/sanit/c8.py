# -*- encoding:utf-8 -*-
from __future__ import print_function
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import warnings

# noinspection PyUnresolvedReferences
import abu_local_env

import abupy
from abupy import AbuFactorBuyBreak
from abupy import AbuFactorSellBreak
from abupy import AbuFactorSellKDJ
from abupy import AbuFactorSellCurveProjection
from abupy import AbuFactorAtrNStop
from abupy import AbuFactorPreAtrNStop
from abupy import AbuFactorCloseAtrNStop
from abupy import AbuBenchmark
from abupy import AbuPickTimeWorker
from abupy import AbuCapital
from abupy import AbuKLManager
from abupy import ABuTradeProxy
from abupy import ABuTradeExecute
from abupy import ABuPickTimeExecute
from abupy import AbuMetricsBase
from abupy import ABuMarket
from abupy import AbuPickTimeMaster
from abupy import ABuRegUtil
from abupy import AbuPickRegressAngMinMax
from abupy import AbuPickStockWorker
from abupy import ABuPickStockExecute
from abupy import AbuPickStockPriceMinMax
from abupy import AbuPickStockMaster
from abupy import AbuPickKDJ
from abupy import AbuFactorBuyKDJ

from abupy import EMarketDataFetchMode
from abupy import EMarketSourceType
from abupy import EMarketTargetType
from abupy import EDataCacheType
from abupy import ABuDateUtil

warnings.filterwarnings('ignore')
sns.set_context(rc={'figure.figsize': (14, 7)})


#kl_pd = ABuSymbolPd.make_kl_df('600309', n_folds=2)
#STOCK_NUM = '600309'
STOCK_NUM = '002236'
STOCK_CAPITAL = 100000



"""
    第八章 量化系统——开发

    abu量化系统github地址：https://github.com/bbfamily/abu (您的star是我的动力！)
    abu量化文档教程ipython notebook：https://github.com/bbfamily/abu/tree/master/abupy_lecture
"""


def sample_811():
    """
    8.1.1 买入因子的实现
    :return:
    """
    # buy_factors 60日向上突破，42日向上突破两个因子
    buy_factors = [{'xd': 60, 'class': AbuFactorBuyBreak},
                   {'xd': 42, 'class': AbuFactorBuyBreak}]
    benchmark = AbuBenchmark()
    capital = AbuCapital(STOCK_CAPITAL, benchmark)
    kl_pd_manager = AbuKLManager(benchmark, capital)
    # 获取TSLA的交易数据
    kl_pd = kl_pd_manager.get_pick_time_kl_pd(STOCK_NUM)
    abu_worker = AbuPickTimeWorker(capital, kl_pd, benchmark, buy_factors, None)
    abu_worker.fit()

    orders_pd, action_pd, _ = ABuTradeProxy.trade_summary(abu_worker.orders, kl_pd, draw=True)

    ABuTradeExecute.apply_action_to_capital(capital, action_pd, kl_pd_manager)
    capital.capital_pd.capital_blance.plot()
    plt.show()


def sample_812():
    """
    8.1.2 卖出因子的实现
    :return:
    """
    # 120天向下突破为卖出信号
    sell_factor1 = {'xd': 120, 'class': AbuFactorSellBreak}
    # 趋势跟踪策略止盈要大于止损设置值，这里0.5，3.0
    sell_factor2 = {'stop_loss_n': 0.5, 'stop_win_n': 3.0, 'class': AbuFactorAtrNStop}
    # 暴跌止损卖出因子形成dict
    sell_factor3 = {'class': AbuFactorPreAtrNStop, 'pre_atr_n': 1.0}
    # 保护止盈卖出因子组成dict
    sell_factor4 = {'class': AbuFactorCloseAtrNStop, 'close_atr_n': 1.5}
    # 四个卖出因子同时生效，组成sell_factors
    sell_factors = [sell_factor1, sell_factor2, sell_factor3, sell_factor4]
    # buy_factors 60日向上突破，42日向上突破两个因子
    buy_factors = [{'xd': 60, 'class': AbuFactorBuyBreak},
                   {'xd': 42, 'class': AbuFactorBuyBreak}]
    benchmark = AbuBenchmark()

    capital = AbuCapital(STOCK_CAPITAL, benchmark)
    orders_pd, action_pd, _ = ABuPickTimeExecute.do_symbols_with_same_factors(
        [STOCK_NUM], benchmark, buy_factors, sell_factors, capital, show=True)


def sample_813():
    """
    8.1.3 滑点买入卖出价格确定及策略实现
    :return:
    """
    from abupy import AbuSlippageBuyBase

    # 修改g_open_down_rate的值为0.02
    g_open_down_rate = 0.02

    # noinspection PyClassHasNoInit
    class AbuSlippageBuyMean2(AbuSlippageBuyBase):
        def fit_price(self):
            if (self.kl_pd_buy.open / self.kl_pd_buy.pre_close) < (
                        1 - g_open_down_rate):
                # 开盘下跌K_OPEN_DOWN_RATE以上，单子失效
                print(self.factor_name + 'open down threshold')
                return np.inf
            # 买入价格为当天均价
            self.buy_price = np.mean(
                [self.kl_pd_buy['high'], self.kl_pd_buy['low']])
            return self.buy_price

    # 只针对60使用AbuSlippageBuyMean2
    buy_factors2 = [{'slippage': AbuSlippageBuyMean2, 'xd': 60, 'class': AbuFactorBuyBreak},
                    {'xd': 42, 'class': AbuFactorBuyBreak}]

    sell_factor1 = {'xd': 120, 'class': AbuFactorSellBreak}
    sell_factor2 = {'stop_loss_n': 0.5, 'stop_win_n': 3.0, 'class': AbuFactorAtrNStop}
    sell_factor3 = {'class': AbuFactorPreAtrNStop, 'pre_atr_n': 1.0}
    sell_factor4 = {'class': AbuFactorCloseAtrNStop, 'close_atr_n': 1.5}
    sell_factors = [sell_factor1, sell_factor2, sell_factor3, sell_factor4]
    benchmark = AbuBenchmark()
    capital = AbuCapital(STOCK_CAPITAL, benchmark)
    orders_pd, action_pd, _ = ABuPickTimeExecute.do_symbols_with_same_factors(
        [STOCK_NUM], benchmark, buy_factors2, sell_factors, capital, show=True)


def sample_814(show=True):
    """
    8.1.4 对多支股票进行择时
    :return:
    """

    sell_factor1 = {'xd': 120, 'class': AbuFactorSellBreak}
    sell_factor2 = {'stop_loss_n': 0.5, 'stop_win_n': 3.0, 'class': AbuFactorAtrNStop}
    sell_factor3 = {'class': AbuFactorPreAtrNStop, 'pre_atr_n': 1.0}
    sell_factor4 = {'class': AbuFactorCloseAtrNStop, 'close_atr_n': 1.5}
    sell_factors = [sell_factor1, sell_factor2, sell_factor3, sell_factor4]
    benchmark = AbuBenchmark()
    buy_factors = [{'xd': 60, 'class': AbuFactorBuyBreak},
                   {'xd': 42, 'class': AbuFactorBuyBreak}]

    #choice_symbols = ['usTSLA', 'usNOAH', 'usSFUN', 'usBIDU', 'usAAPL', 'usGOOG', 'usWUBA', 'usVIPS']
    choice_symbols = ['600309', '002236']
    #choice_symbols = ['600309']
    capital = AbuCapital(STOCK_CAPITAL, benchmark)
    orders_pd, action_pd, all_fit_symbols_cnt = ABuPickTimeExecute.do_symbols_with_same_factors(choice_symbols,
                                                                                                benchmark, buy_factors,
                                                                                                sell_factors, capital,
                                                                                                show=False)

    metrics = AbuMetricsBase(orders_pd, action_pd, capital, benchmark)
    metrics.fit_metrics()
    if show:
        print('orders_pd[:10]:\n', orders_pd[:10].filter(
            ['symbol', 'buy_price', 'buy_cnt', 'buy_factor', 'buy_pos', 'sell_date', 'sell_type_extra', 'sell_type',
             'profit']))
        print('action_pd[:10]:\n', action_pd[:10])
        metrics.plot_returns_cmp(only_show_returns=True)
    return metrics


def sample_815():
    """
    8.1.5 自定义仓位管理策略的实现
    :return:
    """
    metrics = sample_814(False)
    print('\nmetrics.gains_mean:{}, -metrics.losses_mean:{}'.format(metrics.gains_mean, -metrics.losses_mean))

    from abupy import AbuKellyPosition
    # 42d使用AbuKellyPosition，60d仍然使用默认仓位管理类
    buy_factors2 = [{'xd': 60, 'class': AbuFactorBuyBreak},
                    {'xd': 42, 'position': AbuKellyPosition, 'win_rate': metrics.win_rate,
                     'gains_mean': metrics.gains_mean, 'losses_mean': -metrics.losses_mean,
                     'class': AbuFactorBuyBreak}]

    sell_factor1 = {'xd': 120, 'class': AbuFactorSellBreak}
    sell_factor2 = {'stop_loss_n': 0.5, 'stop_win_n': 3.0, 'class': AbuFactorAtrNStop}
    sell_factor3 = {'class': AbuFactorPreAtrNStop, 'pre_atr_n': 1.0}
    sell_factor4 = {'class': AbuFactorCloseAtrNStop, 'close_atr_n': 1.5}
    sell_factors = [sell_factor1, sell_factor2, sell_factor3, sell_factor4]

    benchmark = AbuBenchmark()
    #choice_symbols = ['usTSLA', 'usNOAH', 'usSFUN', 'usBIDU', 'usAAPL', 'usGOOG', 'usWUBA', 'usVIPS']
    choice_symbols = ['600309', '002236']

    #capital = AbuCapital(1000000, benchmark)
    capital = AbuCapital(STOCK_CAPITAL, benchmark)


    orders_pd, action_pd, all_fit_symbols_cnt = ABuPickTimeExecute.do_symbols_with_same_factors(choice_symbols,
                                                                                                benchmark, buy_factors2,
                                                                                                sell_factors, capital,
                                                                                                show=False)
    print(orders_pd[:10].filter(['symbol', 'buy_cnt', 'buy_factor', 'buy_pos']))


def sample_816():
    """
    8.1.6 多支股票使用不同的因子进行择时
    :return:
    """
    # 选定noah和sfun
    #target_symbols = ['usSFUN', 'usNOAH']
    target_symbols = ['600309', '002236']
    # 针对sfun只使用42d向上突破作为买入因子
    buy_factors_sfun = [{'xd': 42, 'class': AbuFactorBuyBreak}]
    # 针对sfun只使用60d向下突破作为卖出因子
    sell_factors_sfun = [{'xd': 60, 'class': AbuFactorSellBreak}]

    # 针对noah只使用21d向上突破作为买入因子
    buy_factors_noah = [{'xd': 21, 'class': AbuFactorBuyBreak}]
    # 针对noah只使用42d向下突破作为卖出因子
    sell_factors_noah = [{'xd': 42, 'class': AbuFactorSellBreak}]

    #choice_symbols = ['600309', '002236']
    factor_dict = dict()
    # 构建SFUN独立的buy_factors，sell_factors的dict
    factor_dict['600309'] = {'buy_factors': buy_factors_sfun, 'sell_factors': sell_factors_sfun}
    # 构建NOAH独立的buy_factors，sell_factors的dict
    factor_dict['002236'] = {'buy_factors': buy_factors_noah, 'sell_factors': sell_factors_noah}
    # 初始化资金
    benchmark = AbuBenchmark()
    #capital = AbuCapital(1000000, benchmark)
    capital = AbuCapital(STOCK_CAPITAL, benchmark)
    # 使用do_symbols_with_diff_factors执行
    orders_pd, action_pd, all_fit_symbols = ABuPickTimeExecute.do_symbols_with_diff_factors(
        target_symbols, benchmark, factor_dict, capital)
    print('pd.crosstab(orders_pd.buy_factor, orders_pd.symbol):\n', pd.crosstab(orders_pd.buy_factor, orders_pd.symbol))


def sample_817():
    """
    8.1.7 使用并行来提升择时运行效率
    :return:
    """
    # 要关闭沙盒数据环境，因为沙盒里就那几个股票的历史数据, 下面要随机做50个股票
    from abupy import EMarketSourceType
    abupy.env.g_market_source = EMarketSourceType.E_MARKET_SOURCE_tx

    abupy.env.disable_example_env_ipython()

    # 关闭沙盒后，首先基准要从非沙盒环境换取，否则数据对不齐，无法正常运行
    benchmark = AbuBenchmark()
    # 当传入choice_symbols为None时代表对整个市场的所有股票进行回测
    # noinspection PyUnusedLocal
    choice_symbols = None
    # 顺序获取市场后300支股票
    # noinspection PyUnusedLocal
    choice_symbols = ABuMarket.all_symbol()[-50:]
    # 随机获取300支股票
    choice_symbols = ABuMarket.choice_symbols(50)
    #capital = AbuCapital(1000000, benchmark)
    capital = AbuCapital(STOCK_CAPITAL, benchmark)

    sell_factor1 = {'xd': 120, 'class': AbuFactorSellBreak}
    sell_factor2 = {'stop_loss_n': 0.5, 'stop_win_n': 3.0, 'class': AbuFactorAtrNStop}
    sell_factor3 = {'class': AbuFactorPreAtrNStop, 'pre_atr_n': 1.0}
    sell_factor4 = {'class': AbuFactorCloseAtrNStop, 'close_atr_n': 1.5}
    sell_factors = [sell_factor1, sell_factor2, sell_factor3, sell_factor4]
    buy_factors = [{'xd': 60, 'class': AbuFactorBuyBreak},
                   {'xd': 42, 'class': AbuFactorBuyBreak}]

    orders_pd, action_pd, _ = AbuPickTimeMaster.do_symbols_with_same_factors_process(
        choice_symbols, benchmark, buy_factors, sell_factors,
        capital)

    metrics = AbuMetricsBase(orders_pd, action_pd, capital, benchmark)
    metrics.fit_metrics()
    metrics.plot_returns_cmp(only_show_returns=True)

    abupy.env.enable_example_env_ipython()


"""
    注意所有选股结果等等与书中的结果不一致，因为要控制沙盒数据体积小于50mb， 所以沙盒数据有些symbol只有两年多一点，与原始环境不一致，
    直接达不到选股的min_xd，所以这里其实可以`abupy.env.disable_example_env_ipython()`关闭沙盒环境，直接上真实数据。
"""

from abupy import ABuFactorBuyCurveProjection

def pick_time_CurveProjection():
    
    #仓位控制 100%
    abupy.beta.atr.g_atr_pos_base = 1.0

    # buy factors
    buy_factors = [{'class': ABuFactorBuyCurveProjection, 
        'mfi_threshold':50,
        'k_threshold':50,
        'd_threshold':50,
        'j_threshold':0
        }]


    #sell factors
    #sell_factor1 = {'class': AbuFactorSellCurveProjection}

    sell_factor1 = {'class': AbuFactorSellCurveProjection,
        'mfi_threshold':80,
        'k_threshold':50,
        'd_threshold':50,
        'j_threshold':100
        }
    sell_factors = [sell_factor1]

    """
    # 120天向下突破为卖出信号
    sell_factor1 = {'xd': 120, 'class': AbuFactorSellBreak}
    # 趋势跟踪策略止盈要大于止损设置值，这里0.5，3.0
    sell_factor2 = {'stop_loss_n': 0.5, 'stop_win_n': 3.0, 'class': AbuFactorAtrNStop}
    # 暴跌止损卖出因子形成dict
    sell_factor3 = {'class': AbuFactorPreAtrNStop, 'pre_atr_n': 1.0}
    # 保护止盈卖出因子组成dict
    sell_factor4 = {'class': AbuFactorCloseAtrNStop, 'close_atr_n': 1.5}
    # 四个卖出因子同时生效，组成sell_factors
    sell_factors = [sell_factor1, sell_factor2, sell_factor3, sell_factor4]
    """


    #A股，永不可能，相当于不丢弃单子，这里缺省使用的均值滑点
    abupy.slippage.sbm.g_open_down_rate = 0.11

    benchmark = AbuBenchmark(n_folds = 11)
    capital = AbuCapital(STOCK_CAPITAL, benchmark)
    kl_pd_manager = AbuKLManager(benchmark, capital)

    # 获取symbol的交易数据
    #kl_pd = kl_pd_manager.get_pick_time_kl_pd('002236')
    #kl_pd = kl_pd_manager.get_pick_time_kl_pd('600309')
    #kl_pd = kl_pd_manager.get_pick_time_kl_pd('601398')
    kl_pd = kl_pd_manager.get_pick_time_kl_pd('601939')
   
    """
    print(kl_pd.columns)
    print(type(kl_pd.date[0]))
    return 0
    """

    abu_worker = AbuPickTimeWorker(capital, kl_pd, benchmark, buy_factors, sell_factors)
    abu_worker.fit()


    print (abu_worker.orders)

    if (not abu_worker.orders) :
        return

    orders_pd, action_pd, _ = ABuTradeProxy.trade_summary(abu_worker.orders, kl_pd, draw=True)



    ABuTradeExecute.apply_action_to_capital(capital, action_pd, kl_pd_manager)
    capital.capital_pd.capital_blance.plot()
    plt.show()



def pick_time_kdj():
    # buy factors 

    """
    #工商银行
    buy_factors = [{'class': AbuFactorBuyKDJ, 'ma_period': 10,
                    'k_threshold':20, 'd_threshold':20, 'j_threshold':20}]

    """

    """
    #大华股份，熊市的买点
    buy_factors = [{'class': AbuFactorBuyKDJ, 'ma_period': 10,
                    'k_threshold':25, 'd_threshold':25, 'j_threshold':25}]

    """

    #大华股份，牛市买点
    buy_factors = [{'class': AbuFactorBuyKDJ, 'ma_period': 10,
                    'k_threshold':60, 'd_threshold':60, 'j_threshold':0,
                    'debug':False}]

    #sell factors
    #sell_factor1 = {'class': AbuFactorSellKDJ}
        
    sell_factor1 = {'class': AbuFactorSellCurveProjection,
        'mfi_threshold':85,
        'k_threshold':50,
        'd_threshold':50,
        'j_threshold':90
        }

    # 趋势跟踪策略止盈要大于止损设置值，这里0.5，3.0
    sell_factor2 = {'stop_loss_n': 0.5, 'stop_win_n': 3.0, 'class': AbuFactorAtrNStop}
    # 暴跌止损卖出因子形成dict
    sell_factor3 = {'class': AbuFactorPreAtrNStop, 'pre_atr_n': 1.0}
    # 保护止盈卖出因子组成dict
    sell_factor4 = {'class': AbuFactorCloseAtrNStop, 'close_atr_n': 1.5}
    # 四个卖出因子同时生效，组成sell_factors
    sell_factors = [sell_factor1, sell_factor2, sell_factor3, sell_factor4]

    sell_factors = [sell_factor1]
    #sell_factors = [sell_factor1, sell_factor2]
    #sell_factors = [sell_factor1, sell_factor2, sell_factor3]


    #A股，永不可能，相当于不丢弃单子，这里缺省使用的均值滑点
    abupy.slippage.sbm.g_open_down_rate = 0.11
    #仓位控制 100%
    abupy.beta.position.g_pos_max = 1.0
    #系统缺省使用了atr仓位控制器
    abupy.beta.atr.g_atr_pos_base = 1.0

    
    #benchmark = AbuBenchmark()
    benchmark = AbuBenchmark(n_folds = 2)
    #benchmark = AbuBenchmark(start = "20161121", end="20161122")
    capital = AbuCapital(STOCK_CAPITAL, benchmark)
    kl_pd_manager = AbuKLManager(benchmark, capital)

    # 获取symbol的交易数据
    #symbol = '002236' #大华股份
    #symbol = '000002'
    symbol = '601939' #建设银行
    #symbol = '600309'
    #symbol = '601398' #工商银行
    #symbol = '601319'  #few datas
    kl_pd = kl_pd_manager.get_pick_time_kl_pd(symbol)

    """
    kl_pd = kl_pd[kl_pd.volume != 0]
    kl_pd.name = symbol
    print(kl_pd)
    """ 


    abu_worker = AbuPickTimeWorker(capital, kl_pd, benchmark, buy_factors, sell_factors)
    abu_worker.fit()
    """
    print("*************************")
    print("the are %d orders" %(len(abu_worker.orders)))
    print (abu_worker.orders)
    print("*************************")
    """

    factor = abu_worker.buy_factors[0]
    factor = factor.mean_split
    factor_summary = list()
    factor_summary.append(factor._peaks)
    factor_summary.append(factor._bear_bull_peaks)
    factor_summary.append(factor._slices)
    factor_summary.append(factor._degs)
    factor_summary.append(factor._steps)
    #print(factor_summary)
    #print("bear_bull peaks", factor._bear_bull_peaks)


    #print(abu_worker.orders)

    #合并相邻的订单
    new_orders = []
    new_orders.append(abu_worker.orders[0])

    for i, order in enumerate(abu_worker.orders):
        if (i == len(abu_worker.orders) - 1):
            break
        d = ABuDateUtil.diff(abu_worker.orders[i+1].buy_date, order.buy_date)
        #print(d)
        
        if (d > 3):
            new_orders.append(abu_worker.orders[i+1])

    abu_worker.orders = new_orders

    #计算收益
    profits = 0
    for i, order in enumerate(abu_worker.orders):
        if order.sell_date is None:
            print(order)
            continue
        profit = (order.sell_price - order.buy_price) * order.buy_cnt
        profits += profit

        print(order)
        print("this order profit ", profit)

    print("total profits = %.2f" %(profits))
    
    """
    orders = [abu_worker.orders[0]]
    orders_pd, action_pd, _ = ABuTradeProxy.trade_summary(orders, kl_pd, draw=True, 
        ext_list = factor_summary)

    """


    orders_pd, action_pd, _ = ABuTradeProxy.trade_summary(abu_worker.orders, kl_pd, draw=True, 
        ext_list = factor_summary)
    #orders_pd, action_pd, _ = ABuTradeProxy.trade_summary(abu_worker.orders, kl_pd, draw=False, 
    #    ext_list = factor_summary)
    #orders_pd, action_pd, _ = ABuTradeProxy.trade_summary(abu_worker.orders, kl_pd, draw=False)


    print(action_pd)
    ABuTradeExecute.apply_action_to_capital(capital, action_pd, kl_pd_manager)
    capital.capital_pd.capital_blance.plot()
    plt.show()


def pick_stock_kdj():
    abupy.env.disable_example_env_ipython()
    
    from abupy import EMarketTargetType
    abupy.env.g_market_target = EMarketTargetType.E_MARKET_TARGET_CN
    #stock_pickers = [{'class': AbuPickKDJ, 'reversed': True}]

    stock_pickers = [{'class': AbuPickKDJ,
                      'threshold_ang_min': 0.0, 'reversed': False}]

    # 从这几个股票里进行选股，只是为了演示方便
    # 一般的选股都会是数量比较多的情况比如全市场股票
    #choice_symbols = ['002236']
    choice_symbols = ['600309']

    benchmark = AbuBenchmark()
    capital = AbuCapital(STOCK_CAPITAL, benchmark)
    kl_pd_manager = AbuKLManager(benchmark, capital)
    stock_pick = AbuPickStockWorker(capital, benchmark, kl_pd_manager,
                                    choice_symbols=choice_symbols,
                                    stock_pickers=stock_pickers)
    stock_pick.fit()
    # 打印最后的选股结果
    print('stock_pick.choice_symbols:', stock_pick.choice_symbols)


   # 从kl_pd_manager缓存中获取选股走势数据，注意get_pick_stock_kl_pd为选股数据，get_pick_time_kl_pd为择时
    kl_pd_noah = kl_pd_manager.get_pick_stock_kl_pd(stock_pick.choice_symbols[0])
    print(kl_pd_noah)

    # 绘制并计算角度
    deg = ABuRegUtil.calc_regress_deg(kl_pd_noah.close)
    print('noah 选股周期内角度={}'.format(round(deg, 3)))

def sample_821_1():
    """
    8.2.1_1 选股使用示例
    :return:
    """
    #使用沙盒， 因为这个就是个简单的例子
    #abupy.env.enable_example_env_ipython()
    abupy.env.disable_example_env_ipython()

    # 选股条件threshold_ang_min=0.0, 即要求股票走势为向上上升趋势
    stock_pickers = [{'class': AbuPickRegressAngMinMax,
                      'threshold_ang_min': 0.0, 'reversed': False}]

    # 从这几个股票里进行选股，只是为了演示方便
    # 一般的选股都会是数量比较多的情况比如全市场股票
    choice_symbols = ['usNOAH', 'usSFUN', 'usBIDU', 'usAAPL', 'usGOOG',
                      'usTSLA', 'usWUBA', 'usVIPS']
    benchmark = AbuBenchmark()
    capital = AbuCapital(STOCK_CAPITAL, benchmark)
    kl_pd_manager = AbuKLManager(benchmark, capital)
    stock_pick = AbuPickStockWorker(capital, benchmark, kl_pd_manager,
                                    choice_symbols=choice_symbols,
                                    stock_pickers=stock_pickers)
    stock_pick.fit()
    # 打印最后的选股结果
    print('stock_pick.choice_symbols:', stock_pick.choice_symbols)

    # 从kl_pd_manager缓存中获取选股走势数据，注意get_pick_stock_kl_pd为选股数据，get_pick_time_kl_pd为择时
    kl_pd_noah = kl_pd_manager.get_pick_stock_kl_pd(stock_pick.choice_symbols[0])
    print(kl_pd_noah)

    # 绘制并计算角度
    deg = ABuRegUtil.calc_regress_deg(kl_pd_noah.close)
    print('noah 选股周期内角度={}'.format(round(deg, 3)))
    abupy.env.disable_example_env_ipython()


def sample_821_2():
    """
    8.2.1_2 ABuPickStockExecute
    :return:
    """
    abupy.env.enable_example_env_ipython()

    """
    stock_pickers = [{'class': AbuPickRegressAngMinMax,
                      'threshold_ang_min': 0.0, 'threshold_ang_max': 10.0,
                      'reversed': False}]
    """
    # sample_821_3
    stock_pickers = [{'class': AbuPickRegressAngMinMax,
                      'threshold_ang_min': 0.0, 'threshold_ang_max': 10.0,
                      'reversed': True}]

    choice_symbols = ['usNOAH', 'usSFUN', 'usBIDU', 'usAAPL', 'usGOOG',
                      'usTSLA', 'usWUBA', 'usVIPS']
    benchmark = AbuBenchmark()
    capital = AbuCapital(1000000, benchmark)
    kl_pd_manager = AbuKLManager(benchmark, capital)

    #print('ABuPickStockExecute.do_pick_stock_work:\n', ABuPickStockExecute.do_pick_stock_work(choice_symbols, benchmark,
    target_symbols = ABuPickStockExecute.do_pick_stock_work(choice_symbols, benchmark,
                                                                                              capital, stock_pickers)

    print (target_symbols)
    kl_pd_sfun = kl_pd_manager.get_pick_stock_kl_pd(target_symbols[-1])
    #kl_pd_sfun = kl_pd_manager.get_pick_stock_kl_pd('usVIPS')
    print('sfun 选股周期内角度={}'.format(round(ABuRegUtil.calc_regress_deg(kl_pd_sfun.close), 3)))

    abupy.env.disable_example_env_ipython()

def sample_821_3():
    """
    8.2.1_3 reversed
    :return:
    """
    # 和上面的代码唯一的区别就是reversed=True
    stock_pickers = [{'class': AbuPickRegressAngMinMax,
                      'threshold_ang_min': 0.0, 'threshold_ang_max': 10.0, 'reversed': True}]

    choice_symbols = ['usNOAH', 'usSFUN', 'usBIDU', 'usAAPL', 'usGOOG',
                      'usTSLA', 'usWUBA', 'usVIPS']
    benchmark = AbuBenchmark()
    capital = AbuCapital(1000000, benchmark)

    print('ABuPickStockExecute.do_pick_stock_work:\n',
          ABuPickStockExecute.do_pick_stock_work(choice_symbols, benchmark, capital, stock_pickers))


def sample_822():
    """
    8.2.2 多个选股因子并行执行
    :return:
    """
    abupy.env.enable_example_env_ipython()

    # 选股list使用两个不同的选股因子组合，并行同时生效
    stock_pickers = [{'class': AbuPickRegressAngMinMax,
                      'threshold_ang_min': 0.0, 'reversed': False},
                     {'class': AbuPickStockPriceMinMax, 'threshold_price_min': 50.0,
                      'reversed': False}]

    choice_symbols = ['usNOAH', 'usSFUN', 'usBIDU', 'usAAPL', 'usGOOG',
                      'usTSLA', 'usWUBA', 'usVIPS']
    benchmark = AbuBenchmark()
    capital = AbuCapital(1000000, benchmark)

    print('ABuPickStockExecute.do_pick_stock_work:\n',
          ABuPickStockExecute.do_pick_stock_work(choice_symbols, benchmark, capital, stock_pickers))

    abupy.env.disable_example_env_ipython()

def sample_823():
    """
    8.2.3 使用并行来提升回测运行效率
    :return:
    """
    from abupy import EMarketSourceType
    abupy.env.g_market_source = EMarketSourceType.E_MARKET_SOURCE_tx
    abupy.env.disable_example_env_ipython()

    benchmark = AbuBenchmark()
    capital = AbuCapital(1000000, benchmark)

    # 首先随抽取50支股票
    choice_symbols = ABuMarket.choice_symbols(50)
    # 股价在15-50之间
    stock_pickers = [
        {'class': AbuPickStockPriceMinMax, 'threshold_price_min': 15.0,
         'threshold_price_max': 50.0, 'reversed': False}]
    cs = AbuPickStockMaster.do_pick_stock_with_process(capital, benchmark,
                                                       stock_pickers,
                                                       choice_symbols)
    print('len(cs):', len(cs))
    print('cs:\n', cs)

def init_env():
    #环境
    abupy.env.disable_example_env_ipython()
    #bd source have some data error, for example, 002236, some date error, for kdj
    #abupy.env.g_market_source = EMarketSourceType.E_MARKET_SOURCE_bd
    #abupy.env.g_market_source = EMarketSourceType.E_MARKET_SOURCE_tx
    #abupy.env.g_market_source = EMarketSourceType.E_MARKET_SOURCE_nt
    #abupy.env.g_market_source = EMarketSourceType.E_MARKET_SOURCE_tdx
    abupy.env.g_market_source = EMarketSourceType.E_MARKET_SOURCE_tdx_db
    abupy.env.g_market_target = EMarketTargetType.E_MARKET_TARGET_CN
    abupy.env.g_data_cache_type = EDataCacheType.E_DATA_CACHE_CSV

    #abupy.env.g_data_fetch_mode = EMarketDataFetchMode.E_DATA_FETCH_FORCE_LOCAL
    #abupy.env.g_data_fetch_mode = EMarketDataFetchMode.E_DATA_FETCH_NORMAL
    abupy.env.g_data_fetch_mode = EMarketDataFetchMode.E_DATA_FETCH_FORCE_NET


if __name__ == "__main__":
    init_env()
    # from abupy import  ABuSymbolPd
    # kl_pd = ABuSymbolPd.make_kl_df('601939', n_folds=11)
    # sample_811()
    # sample_812()
    # sample_813()
    # sample_814()
    # sample_815()
    # sample_816()
    # sample_817()

    # sample_821_1()
    # sample_821_2()
    # sample_821_3()
    # sample_822()
    # sample_823()
    pick_stock_kdj()
    # pick_time_kdj()
    # pick_time_CurveProjection()
