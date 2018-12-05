# -*- encoding:utf-8 -*-
from __future__ import print_function

# noinspection PyUnresolvedReferences
import abu_local_env
import abupy
from abupy import crawl_stock_code

if __name__ == "__main__":
    #这个没有通过测试，因为没有chrome test driver, 这个使用了
    #selenium webdriver
    crawl_stock_code(markets=('CN'))

