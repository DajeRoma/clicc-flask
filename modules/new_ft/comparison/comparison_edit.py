#!/usr/bin/env python
import xlrd
import numpy as np
import scipy as sp
from scipy import integrate
from scipy.integrate import ode
from xlrd import open_workbook
from datetime import date, time, timedelta
import datetime
from astropy.table import Table, Column
import csv
from math import exp, sqrt
import xlwt
import itertools
from itertools import tee, islice, chain, izip

time1 = datetime.datetime.now()
print time1, "1"

# Load in Lawrence's output #
workbook_names = "SF_glycerin_beta_output_Mar_03_16-17_51_11"
print workbook_names
workbook_title = "%s.xls" %(workbook_names)
print workbook_title
main_workbook = xlrd.open_workbook(workbook_title)
L_average_output = main_workbook.sheet_by_name('Average_output')
L_comp_names = L_average_output.col_values(0, start_rowx=0,end_rowx=None)
L_comp_averages = L_average_output.col_values(1, start_rowx=0,end_rowx=None)

l_hash = {}
for idx, name in enumerate(L_comp_names):
	l_hash[(name + "_avg")] = L_comp_averages[idx]
# print l_hash
# Load in org model's output #
workbook_names = "SF_glycerin_beta_output_new"
print workbook_names

workbook_title = "%s.xls" %(workbook_names)
print workbook_title
main_workbook = xlrd.open_workbook(workbook_names)
D_average_output = main_workbook.sheet_by_name('Average_output')
D_comp_names = D_average_output.col_values(0, start_rowx=0,end_rowx=None)
D_comp_averages = D_average_output.col_values(1, start_rowx=0,end_rowx=None)

d_hash = {}
for idx, name in enumerate(D_comp_names):
	d_hash[name] = D_comp_averages[idx]
# print d_hash

for key in l_hash.keys():
	try:
		if l_hash[key] == d_hash[key]:
			print "Good Result", key
			print "#########"
		else:
			print "Non match", key, l_hash[key], d_hash[key]
			print "#########"
	except KeyError:
		print 'key mismatch: ', key
