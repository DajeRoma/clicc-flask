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

from FateAndTransport import FateAndTransport
from CLiCC_O_March import FT_Old

test_book = 'SF_glycerin_beta.xlsx'

L = FateAndTransport()
L.load_chem(test_book)
L.load_environment(test_book)
Lout = L.run()
L.write_output(Lout)

D = FT_Old()
D.run(test_book)


workbook_title = "new_output"
main_workbook = xlrd.open_workbook(workbook_title)
L_average_output = main_workbook.sheet_by_name('Average_output')
L_comp_names = L_average_output.col_values(0, start_rowx=0,end_rowx=None)
L_comp_averages = L_average_output.col_values(1, start_rowx=0,end_rowx=None)
L_chem_params = main_workbook.sheet_by_name('Chem_Parameters')
L_chem_names = L_chem_params.col_values(0, start_rowx=0,end_rowx=None)
L_chem_values = L_chem_params.col_values(1, start_rowx=0,end_rowx=None)

l_hash = {}
for idx, name in enumerate(L_comp_names):
	l_hash[name + '_avg'] = L_comp_averages[idx]

for idx, name in enumerate(L_chem_names):
	l_hash[name] = L_chem_values[idx]
# print l_hash

# Load in org model's output #
workbook_title = "old_output"
main_workbook = xlrd.open_workbook(workbook_title)
D_average_output = main_workbook.sheet_by_name('Average_output')
D_comp_names = D_average_output.col_values(0, start_rowx=0,end_rowx=None)
D_comp_averages = D_average_output.col_values(1, start_rowx=0,end_rowx=None)
D_chem_params = main_workbook.sheet_by_name('Chem_Parameters')
D_chem_names = D_chem_params.col_values(1, start_rowx=0,end_rowx=None)
D_chem_values = D_chem_params.col_values(2, start_rowx=0,end_rowx=None)

d_hash = {}
for idx, name in enumerate(D_comp_names):
	d_hash[name] = D_comp_averages[idx]

for idx, name in enumerate(D_chem_names):
	d_hash[name] = D_chem_values[idx]
# print d_hash

for key in d_hash.keys():
	try:
		if l_hash[key] == d_hash[key]:
			print "Good Result", key
			print "#########"
		else:
			print "Non match", key, (l_hash[key] / d_hash[key])
			print "#########"
	except KeyError:
		print 'key mismatch: ', key
