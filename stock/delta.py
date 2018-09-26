#!/usr/bin/env python
import numpy as np
import os
from decimal import Decimal

STAMP_TAX = 0.001
POUNDAGE = 0.00025
TRANSFER_FEE = 0.00002

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


	
