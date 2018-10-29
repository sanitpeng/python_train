#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import numpy as np
import os
from decimal import Decimal

STAMP_TAX = 0.001
POUNDAGE = 0.00025
TRANSFER_FEE = 0.00002
GOLDEN_RATE = 0.618
RATE_LIMIT = 0.100

def get_stock_increase():
	try:
		increase = raw_input("please input stock increase:(MUST >0 and <= 0.1)")
		increase = float(increase)
	except:
		return -2

	if (increase < 0 or increase > 0.1) :
		return -1
	return increase


def get_stock_price():
	try:
		price = raw_input("please input stock price (MUST >= 0, 'Enter to exit'):")
		price = float(price)
	except:
		return -2

	if price < 0:
		return -1
	return price	



on = True

numbers  = list()
prices = list()
values = list()

while on:
	stock_price = get_stock_price()
	if stock_price < -1: #stop program
		on = False
		break
	elif stock_price < 0:
		continue

	'''
	stock_increase = get_stock_increase()
	while stock_increase < 0:
		stock_increase = get_stock_increase()
		continue
	'''
	
	os.system('clear')


	print "sotck delta program by sanit.peng"
	print "-----------------------------------------------------------------"
	print "  price   increase(%)    sell_price  buy_price   +delta   -delta"
	print "-----------------------------------------------------------------"
	print "  %-6.2f     0.00        0.00        0.00        0.00     0.00" %(stock_price)

	increases = [0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05,\
		 0.055, 0.06, 0.065, 0.07, 0.075, 0.08, 0.085, 0.09, 0.095, 0.10]
	
	buy_hi = (1 - RATE_LIMIT) + (RATE_LIMIT * (GOLDEN_RATE))
	buy_low = (1 - RATE_LIMIT) + (RATE_LIMIT * (1 - GOLDEN_RATE))
	sell_hi = (1) + (RATE_LIMIT * ( GOLDEN_RATE))
	sell_low = (1) + (RATE_LIMIT * (1 - GOLDEN_RATE))

	#print "buy_hi = %.4f, buy_low = %.4f, sell_hi = %.4f, sell_low = %.4f" %(buy_hi, buy_low, sell_hi, sell_low)

	print "-----------------------------------------------------------------"
	print "  黄金分割点(不含交易费用)"
	print "-----------------------------------------------------------------"

	print "  %-10.2f %-11.2f %-11.2f %-11.2f %-8.5f %-8.5f"\
		 %(stock_price, (1 - GOLDEN_RATE) * 10, stock_price * sell_low, \
		stock_price * buy_hi, sell_low, buy_hi)
	print "  %-10.2f %-11.2f %-11.2f %-11.2f %-8.5f %-8.5f"\
		 %(stock_price, (1 - GOLDEN_RATE + 0.005) * 10, stock_price * (sell_low + 0.005), \
		stock_price * (buy_hi - 0.005), sell_low + 0.005, buy_hi - 0.005)

	print "  %-10.2f %-11.2f %-11.2f %-11.2f %-8.5f %-8.5f"\
		 %(stock_price, (GOLDEN_RATE) * 10, stock_price * sell_hi, \
		stock_price * buy_low, sell_hi, buy_low)
	print "  %-10.2f %-11.2f %-11.2f %-11.2f %-8.5f %-8.5f"\
		 %(stock_price, (GOLDEN_RATE + 0.005) * 10, stock_price * (sell_hi + 0.005), \
		stock_price * (buy_low - 0.005), sell_hi + 0.005, buy_low - 0.005)
	print "-----------------------------------------------------------------"

	for increase in increases:
		buy_delta = POUNDAGE + TRANSFER_FEE
		sell_delta = POUNDAGE + STAMP_TAX + TRANSFER_FEE
	
		sell_price = 1 + increase + buy_delta + sell_delta
		buy_price = 1 - (increase + buy_delta + sell_delta)

		print "  %-10.2f %-11.2f %-11.2f %-11.2f %-8.5f %-8.5f"\
			 %(stock_price, increase * 100, stock_price * sell_price, \
			stock_price * buy_price, sell_price, buy_price)




	print "---------------------------------------------------------------"
	print "  final cost:"
	print "---------------------------------------------------------------"


	on = False		


	
