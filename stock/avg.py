#!/usr/bin/env python
import numpy as np
import os
from decimal import Decimal

STAMP_TAX = 0.001
POUNDAGE = 0.00025

def get_stock_number():
	try:
		number = raw_input("please input stoke number('Enter' to exit):")
		number = int(number)
	except:
		return -2

	if number < 0:
		return -1
	return number


def get_stock_price():
	try:
		price = raw_input("please input stoke price:")
		price = float(price)
	except:
		return -1

	if price < 0:
		return -1
	return price	



on = True

numbers  = list()
prices = list()
values = list()

i = 0
while on:
	stock_number = get_stock_number()
	if stock_number == -2:
		on = False
		break
	elif stock_number == -1:
		print "input ERROR, stock number MUST >= 0"
		continue


	stock_price = get_stock_price()
	while stock_price < 0:
		print "input ERROR, stock price MUST >= 0"
		stock_price = get_stock_price()
		continue

	numbers.append(stock_number)
	prices.append(stock_price)
	values.append(stock_number * stock_price)

	
	os.system('clear')

	total = 0
	buy = 0
	sell = 0
	org = 0

	print "sotck cost program by sanit.peng"
	print "---------------------------------------------------------------"
	print "  number      price      value       stamp_tax   poundage  fee"
	print "---------------------------------------------------------------"

	for index in range(0,len(numbers)):
		tax = round(values[index] * STAMP_TAX, 2)
		fee = round(values[index] * POUNDAGE, 2)
		if fee < 5.0: fee = 5.0
		transfer_fee = 1 * (numbers[index] // 1000)
		if transfer_fee < 1.0: transfer_fee = 1.0

		print "  %-11d %-10.2f %-11.2f %-11.2f %-9.2f %-8.2f" \
			%(numbers[index], prices[index], values[index], \
			tax, fee, transfer_fee)
 
		total = total + numbers[index]
		org = org + values[index]
		buy = buy + values[index] + fee #buy
		sell = sell + values[index] + tax + fee + transfer_fee #sell
	


	print "---------------------------------------------------------------"
	print "  final cost:"
	print "---------------------------------------------------------------"


	final_cost = buy / total



	print "  %-11d %-10.3f %-11.2f %-6.2f buy cost" \
		%(total, final_cost, buy, buy - org)

	delta = org - sell
	#print "  %-11d %-10.3f %-11.2f %-6.2f sell cost"\
	#	%(total, (sell / total), org + (org - sell) , org - sell)
	
	print "  %-11d %-10.3f %-11.2f %-6.2f sell cost"\
		%(total, ((org + delta) / total), org + delta , delta)
		
	print ""


	
