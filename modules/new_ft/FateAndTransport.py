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
import os.path
import inspect

class FateAndTransport:
    def __init__(self):
        class_directory = os.path.dirname(os.path.abspath(
            inspect.getfile(inspect.currentframe())))
        self.directory = class_directory
        self.workbooks = os.path.join(class_directory, "workbooks")

    def load_environment(self, title):
        self.env_name = title
        # try:
        main_workbook = xlrd.open_workbook(os.path.join(self.workbooks, (title + ".xlsx")))
        # except:
        #     main_workbook = xlrd.open_workbook(os.path.join(self.workbooks, (title + ".xls")))
        environment_worksheet = main_workbook.sheet_by_name('ENV_final')
        env_codes = environment_worksheet.col_values(1, start_rowx=1,end_rowx=None)
        env_values = environment_worksheet.col_values(2, start_rowx=1,end_rowx=None)
        # environment
        self.env = {}
        for idx, code in enumerate(env_codes):
            self.env[code] = env_values[idx]

        climate_worksheet = main_workbook.sheet_by_name('Climate')
        new_datetime = []
        climate_month = climate_worksheet.col_values(0, start_rowx=1,end_rowx=None)
        climate_day = climate_worksheet.col_values(1, start_rowx=1,end_rowx=None)
        climate_year = climate_worksheet.col_values(2, start_rowx=1,end_rowx=None)
        new_month = [int(i) for i in climate_month]
        new_day = [int(i) for i in climate_day]
        new_year = [int(i) for i in climate_year]
        dt = zip(new_year, new_month, new_day)
        for val in dt:
            mystring = ' '.join(map(str, val))
            dt = datetime.datetime.strptime(mystring, "%Y %m %d")
            new_datetime.append(dt)

        # CLIMATE PARAMETER LOADING #
        self.climate = {
            'date': new_datetime,
            'precip': climate_worksheet.col_values(3, start_rowx=1,end_rowx=None),
            'windspeed': climate_worksheet.col_values(4, start_rowx=1,end_rowx=None),
            'flow': climate_worksheet.col_values(5, start_rowx=1,end_rowx=None),
            'temp': climate_worksheet.col_values(6, start_rowx=1,end_rowx=None)
        }

        # RELEASE PARAMETER LOADING #
        release_worksheet = main_workbook.sheet_by_name('Releases')
        self.release = {
            'date': new_datetime,
            'air': release_worksheet.col_values(3, start_rowx=1,end_rowx=None),
            'freshwater': release_worksheet.col_values(4, start_rowx=1,end_rowx=None),
            'seawater': release_worksheet.col_values(5, start_rowx=1,end_rowx=None),
            'soil1': release_worksheet.col_values(6, start_rowx=1,end_rowx=None),
            'soil2': release_worksheet.col_values(7, start_rowx=1,end_rowx=None),
            'soil3': release_worksheet.col_values(8, start_rowx=1,end_rowx=None),
            'fwsediment': release_worksheet.col_values(9, start_rowx=1,end_rowx=None),
            'swsediment': release_worksheet.col_values(10, start_rowx=1,end_rowx=None),
            'dsoil1': release_worksheet.col_values(11, start_rowx=1,end_rowx=None),
            'dsoil2': release_worksheet.col_values(12, start_rowx=1,end_rowx=None),
            'dsoil3': release_worksheet.col_values(13, start_rowx=1,end_rowx=None)
        }


        # BACKGROUND CONCENTRATION LOADING #
        background_worksheet = main_workbook.sheet_by_name('bgConc')
        # compartment_names = background_worksheet.col_values(1, start_rowx=2,end_rowx=None)
        bg_codes = background_worksheet.col_values(2, start_rowx=2,end_rowx=None)
        bg_values = background_worksheet.col_values(3, start_rowx=2,end_rowx=None)
        self.bg = {}
        for idx, code in enumerate(bg_codes):
            self.bg[code] = bg_values[idx]

        # CHEMICAL PROPERTY PARAMETER LOADING #
        # chemProp_worksheet = main_workbook.sheet_by_name('chemProp')
        # propCodes = chemProp_worksheet.col_values(1, start_rowx=2,end_rowx=None)
        # propValues = chemProp_worksheet.col_values(2, start_rowx=2,end_rowx=None)
        # chem_Prop = zip(propCodes, propValues)

        # DETERMINE COMPARTMENT EXISTENCE #
        self.comp = {}
        comp_worksheet = main_workbook.sheet_by_name('Compartments')
        comp_codes = comp_worksheet.col_values(1, start_rowx=1,end_rowx=None)
        comp_values = comp_worksheet.col_values(2, start_rowx=1,end_rowx=None)
        self.comp = {}
        for idx, code in enumerate(comp_codes):
            self.comp[code] = comp_values[idx]


        # VISCOSITY LOADING #
        visc_worksheet = main_workbook.sheet_by_name('Viscosities')
        self.visc = {
            'temp': visc_worksheet.col_values(0, start_rowx=1,end_rowx=None),
            'vals': visc_worksheet.col_values(1, start_rowx=1,end_rowx=None),
            'vals_air': visc_worksheet.col_values(3, start_rowx=1,end_rowx=None)
        }

        def attempt_float(value):
            try:
                return float(value)
            except:
                return value

        for imported in [self.release, self.climate, self.env,
                self.bg, self.comp, self.visc]:
            for prop, val in imported.iteritems():
                if isinstance(val, list):
                    imported[prop] = map(attempt_float, val)
                else:
                    imported[prop] = attempt_float(val)

    def load_chem(self, workbook):
        main_workbook = xlrd.open_workbook(os.path.join(self.workbooks, workbook))
        chemProp_worksheet = main_workbook.sheet_by_name('chemProp')
        prop_names = chemProp_worksheet.col_values(1, start_rowx=2,end_rowx=None)
        prop_values = chemProp_worksheet.col_values(2, start_rowx=2,end_rowx=None)
        chem_prop = {}
        for idx, name in enumerate(prop_names):
            chem_prop[name] = float(prop_values[idx])

        self.chem_prop = chem_prop
        print self.chem_prop
        return chem_prop

    def run(self, workbook):

        # for a, b in chem_Prop:
        #     if a == 'kOctWater':
        kOctanolWater = self.chem_prop['kOctWater']
        #     if a == 'kOrgWater':
        kOrganicWater = self.chem_prop['kOrgWater']
        #     if a == 'kAirWater':
        kAirWater = self.chem_prop['kAirWater']
        #     if a == 'kAerAir':
        kAerosolAir = self.chem_prop['kAerAir']

        kDegredationInAir = np.multiply(np.true_divide(1, (self.chem_prop['kDegAir'] / .693)), 24)
        kDegredationInWater = np.multiply(np.true_divide(1, (self.chem_prop['kDegWater'] / .693)), 24)
        kDegredationInSoil = np.multiply(np.true_divide(1, (self.chem_prop['kDegSoil'] / .693)), 24)
        kDegredationInSediment = np.multiply(np.true_divide(1, (self.chem_prop['kDegSed'] / .693)), 24)
        kDegredationInAerosol = np.multiply(np.true_divide(1, (self.chem_prop['kDegAero'] / .693)), 24)
        kDegredationInSSediment = np.multiply(np.true_divide(1, (self.chem_prop['kDegSSed'] / .693)), 24)

        molecular_volume = np.true_divide(self.chem_prop['MW'], self.chem_prop['MD'])
        molecular_mass = np.true_divide(self.chem_prop['MW'], 1000)

        time1 = datetime.datetime.now()
        #print time1, "1"

        # ENVIRONMENTAL PARAMETER LOADING #
        workbook_title = os.path.join(self.workbooks, workbook)
        #print workbook_names

        #print workbook_title
        main_workbook = xlrd.open_workbook(workbook_title)
        environment_worksheet = main_workbook.sheet_by_name('Environment')
        environment_code = environment_worksheet.col_values(1, start_rowx=0,end_rowx=None)
        environment_value = environment_worksheet.col_values(2, start_rowx=0,end_rowx=None)
        environment = zip(environment_code, environment_value)

        # CLIMATE PARAMETER LOADING #
        climate_worksheet = main_workbook.sheet_by_name('Climate')
        climate_month = climate_worksheet.col_values(0, start_rowx=1,end_rowx=None)
        climate_day = climate_worksheet.col_values(1, start_rowx=1,end_rowx=None)
        climate_year = climate_worksheet.col_values(2, start_rowx=1,end_rowx=None)
        climate_precip = climate_worksheet.col_values(3, start_rowx=1,end_rowx=None)
        climate_windspeed = climate_worksheet.col_values(4, start_rowx=1,end_rowx=None)
        climate_flow = climate_worksheet.col_values(5, start_rowx=1,end_rowx=None)
        climate_temp = climate_worksheet.col_values(6, start_rowx=1,end_rowx=None)

        # CREATE DATETIME OBJECTS #
        new_datetime = []
        new_month = [int(i) for i in climate_month]
        new_day = [int(i) for i in climate_day]
        new_year = [int(i) for i in climate_year]
        dt = zip(new_year, new_month, new_day)
        for val in dt:
            mystring = ' '.join(map(str, val))
            dt = datetime.datetime.strptime(mystring, "%Y %m %d")
            new_datetime.append(dt)
        climate = zip(new_datetime, climate_precip, climate_windspeed, climate_flow, climate_temp)

        # RELEASE PARAMETER LOADING #
        release_worksheet = main_workbook.sheet_by_name('Releases')
        release_month = release_worksheet.col_values(0, start_rowx=1,end_rowx=None)
        release_day = release_worksheet.col_values(1, start_rowx=1,end_rowx=None)
        release_year = release_worksheet.col_values(2, start_rowx=1,end_rowx=None)
        release_air = release_worksheet.col_values(3, start_rowx=1,end_rowx=None)
        release_freshwater = release_worksheet.col_values(4, start_rowx=1,end_rowx=None)
        release_seawater = release_worksheet.col_values(5, start_rowx=1,end_rowx=None)
        release_soil1 = release_worksheet.col_values(6, start_rowx=1,end_rowx=None)
        release_soil2 = release_worksheet.col_values(7, start_rowx=1,end_rowx=None)
        release_soil3 = release_worksheet.col_values(8, start_rowx=1,end_rowx=None)
        release_fwsediment = release_worksheet.col_values(9, start_rowx=1,end_rowx=None)
        release_swsediment = release_worksheet.col_values(10, start_rowx=1,end_rowx=None)
        release_dsoil1 = release_worksheet.col_values(11, start_rowx=1,end_rowx=None)
        release_dsoil2 = release_worksheet.col_values(12, start_rowx=1,end_rowx=None)
        release_dsoil3 = release_worksheet.col_values(13, start_rowx=1,end_rowx=None)
        release = zip(new_datetime, release_air, release_freshwater, release_seawater, release_soil1, release_soil2,  release_soil3, release_fwsediment, release_swsediment, release_dsoil1, release_dsoil2, release_dsoil3)

        # BACKGROUND CONCENTRATION LOADING #
        background_worksheet = main_workbook.sheet_by_name('bgConc')
        compartment_names = background_worksheet.col_values(1, start_rowx=2,end_rowx=None)
        code = background_worksheet.col_values(2, start_rowx=2,end_rowx=None)
        compartment_values = background_worksheet.col_values(3, start_rowx=2,end_rowx=None)
        background = zip(compartment_names, code, compartment_values)

        # CHEMICAL PROPERTY PARAMETER LOADING #
        chemProp_worksheet = main_workbook.sheet_by_name('chemProp')
        propCodes = chemProp_worksheet.col_values(1, start_rowx=2,end_rowx=None)
        propValues = chemProp_worksheet.col_values(2, start_rowx=2,end_rowx=None)
        chem_Prop = zip(propCodes, propValues)

        # DETERMINE COMPARTMENT EXISTENCE #
        comp_worksheet = main_workbook.sheet_by_name('Compartments')
        compCodes = comp_worksheet.col_values(1, start_rowx=1,end_rowx=None)
        compValues = comp_worksheet.col_values(2, start_rowx=1,end_rowx=None)
        comp_existence = zip(compCodes,compValues)

        # VISCOSITY LOADING #
        visc_worksheet = main_workbook.sheet_by_name('Viscosities')
        visc_temp = visc_worksheet.col_values(0, start_rowx=1,end_rowx=None)
        visc_vals = visc_worksheet.col_values(1, start_rowx=1,end_rowx=None)
        visc_vals_air = visc_worksheet.col_values(3, start_rowx=1,end_rowx=None)
        viscosities = zip(visc_temp, visc_vals)
        viscosities_air = zip(visc_temp, visc_vals_air)


        ##########CLIMATE PROPERTIES##########
        airTemp = climate_temp
        airSpeed = [x for x in climate_windspeed]
        airSpeed = np.multiply(airSpeed,86400)
        fwSpeed = [x for x in climate_flow]
        fwSpeed = np.multiply(fwSpeed,86400)
        swSpeed = np.zeros([1, len(new_datetime)])
        precipR = [x for x in climate_precip]
        precipR = [(x/1000) for x in precipR]
        #precipR = np.multiply(precipR,0.6095996708)



        ########## RUSLE ##########

        # Load in the K factors
        for a, b in environment:
            #print a, b
            if a == 'kffact1':
                kffact1 = float(b)
            if a == 'kffact2':
                kffact2 = float(b)
            if a == 'kffact3':
                kffact3 = float(b)

        # NOT NEEDED - ANNUAL PRECIP SUMS WHILE ACCOUNTING FOR LEAP YEARS#
        R_precip = [x for x in climate_precip]

        #date_store = []
        #first_date = new_datetime[0]
        #date_store.append(first_date)

        #year = timedelta(days=365)
        #year_l = timedelta(days=366)

        #for i, val in enumerate(date_store):
        #    if val <= new_datetime[-1]:
        #        bound = val + year
        #        if bound.day == val.day:
        #            date_store.append(bound)
        #        else:
        #            bound = val + year_l
        #            date_store.append(bound)

        #def previous_and_next(some_iterable):
        #    prevs, items, nexts = tee(some_iterable, 3)
        #    prevs = chain([None], prevs)
        #    nexts = chain(islice(nexts, 1, None), [None])
        #    return izip(prevs, items, nexts)

        #def indexfunc(n):
        #    for prev, item, next in previous_and_next(date_store):
        #        for i, val in enumerate(new_datetime):
        #            if val == item:
        #                yield i
        #date_indices = np.fromiter(indexfunc(1),dtype=int)

        #new_precips = []
        #for prev, item, next in previous_and_next(date_indices):
        #    x = R_precip[item:next]
        #    new_precips.append(x)

        #annual_sums = []
        #for val in new_precips:
        #    x = np.sum(val)
        #    annual_sums.append(x)


        ##### NEW RUSLE #####
        leng = len(R_precip)
        factor = np.true_divide(leng,365)
        years = round(factor)

        factor = np.true_divide(R_precip,24)
        factor2 = np.multiply(factor,-0.05)
        factor3 = []
        for val in factor2:
            calc = exp(val)
            factor3.append(calc)
        factor4 = np.multiply(factor3,0.72)
        factor5 = np.subtract(1,factor4)
        e = np.multiply(0.29,factor5)

        factor = np.true_divide(R_precip,24)
        factor2 = np.multiply(factor,R_precip)
        Ei = np.multiply(e,factor2)

        factor = np.true_divide(7375.6,2000)
        factor2 = np.multiply(factor,365)
        factor3 = np.true_divide(1,25.4)
        factor4 = np.multiply(factor2,factor3)
        factor5 = np.true_divide(1,2.471)
        factor6 = np.multiply(Ei,factor5)
        R = np.multiply(factor4,factor6)


        # Load in nlcd relative proportions to calculate crop factor (C)
        #for a, b in environment:
        #    if a == 'statsgo_area':
        #        statsgo_area = float(b)
        #    if a == 'Forest_Area':
        #        Forest_Area = float(b)
        #    if a == 'Big_Ag':
        #        Big_Ag = float(b)
        #    if a == 'Pasture_Ag':
        #        Pasture_Ag = float(b)
        #    if a == 'Scrub_Area':
        #        Scrub_Area = float(b)
        #    if a == 'Barren_Area':
        #        Barren_Area = float(b)
        #    if a == 'Urban_Area':
        #        Urban_Area = float(b)

        C_urban = 0.15
        C_forest = 0.01
        C_big_ag = 0.3
        C_small_ag = 0.21
        C_scrub = 0.05
        C_barren = 0.3
        C_pasture = 0.1

        # C Urban
        C_fact_urban = C_urban

        for a, b in environment:
            if a == 'area':
                area = float(b)

        # C Agriculture
        #if area == 14253299516:
        #    C_fact_ag = C_big_ag
        #if area == 4648561687.33:
        #    C_fact_ag = C_big_ag
        #if area == 10675996369.4:
        #    C_fact_ag = C_big_ag

        #if area == 20040408427.5:
        #    C_fact_ag = C_small_ag
        #if area == 681843:
        #    C_fact_ag = C_small_ag
        #if area == 694638:
        #    C_fact_ag = C_small_ag

        # C Natural
        #natural_area = Forest_Area + Scrub_Area + Barren_Area
        #forest_prop = np.true_divide(Forest_Area,natural_area)
        #scrub_prop = np.true_divide(Scrub_Area,natural_area)
        #barren_prop = np.true_divide(Barren_Area,natural_area)

        #C_forest_prop = np.multiply(forest_prop,C_forest)
        #C_scrub_prop = np.multiply(scrub_prop,C_scrub)
        #C_barren_prop = np.multiply(barren_prop,C_barren)

        #C_fact_natural = C_forest_prop + C_scrub_prop + C_barren_prop


        # Crop Factor (C)
        for a, b in environment:
            if a == 'C1':
                urban_crop_factor = float(b)
            if a == 'C2':
                natural_crop_factor = float(b)
            if a == 'C3':
                agricultural_crop_factor = float(b)

        # LS Calculations
        for a, b in environment:
            if a == 'slope1':
                slope1 = float(b)
            if a == 'slope2':
                slope2 = float(b)
            if a == 'slope3':
                slope3 = float(b)

        slopes = np.array([0.2, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0,
                   14.0, 16.0, 20.0, 25.0, 30.0, 40.0, 50.0, 60.0])

        lengths = np.array([0.06, 0.1, 0.2, 0.47, 0.8, 1.19, 1.63, 2.11, 3.15, 4.56, 6.28, 8.11, 10.02, 13.99, 19.13, 24.31, 34.48, 44.02, 52.7])


        LS = zip(slopes,lengths)

        urban_slope = round(slope1)
        natural_slope = round(slope2)
        ag_slope = round(slope3)

        def find_nearest(array,value):
            idx = (np.abs(array-value)).argmin()
            return array[idx]

        urban_match = find_nearest(slopes,urban_slope)
        natural_match = find_nearest(slopes,natural_slope)
        ag_match = find_nearest(slopes,ag_slope)

        for a, b in LS:
            if a == urban_match:
                urban_LS = b
            if a == natural_match:
                natural_LS = b
            if a == ag_match:
                ag_LS = b



        # Best Management Factor (P)
        for a, b in environment:
            if a == 'P1':
                urban_P = float(b)
            if a == 'P2':
                 natural_P = float(b)
            if a == 'P3':
                agricultural_P = float(b)

        years = round(len(precipR)/365)
        factor = np.sum(precipR)
        factor2 = np.true_divide(factor,years)
        factor_for_RUSLE = np.true_divide(precipR,factor2)

        RUSLE_urban = kffact1 * urban_LS * urban_crop_factor * urban_P
        factor = np.multiply(RUSLE_urban,R)
        RUSLE_urban = np.multiply(factor,factor_for_RUSLE)
        RUSLE_urban = np.true_divide(RUSLE_urban,4046.86)
        RUSLE_urban = np.multiply(907.185,RUSLE_urban)

        RUSLE_natural = kffact2 * natural_LS * natural_crop_factor * natural_P
        factor = np.multiply(RUSLE_natural,R)
        RUSLE_natural = np.multiply(factor,factor_for_RUSLE)
        RUSLE_natural = np.true_divide(RUSLE_natural,4046.86)
        RUSLE_natural = np.multiply(907.185,RUSLE_natural)

        RUSLE_agricultural = kffact3 * ag_LS * agricultural_crop_factor * agricultural_P
        factor = np.multiply(RUSLE_agricultural,R)
        RUSLE_agricultural = np.multiply(factor,factor_for_RUSLE)
        RUSLE_agricultural = np.true_divide(RUSLE_agricultural,4046.86)
        RUSLE_agricultural = np.multiply(907.185,RUSLE_agricultural)

        # Liquid runoff
        #for a, b in environment:
        #    if a == 'urban_hydgrp':
        #        urban_hydgrp = float(b)
        #        if urban_hydgrp == 4.0:
        #            CN_urban = 77.5
        #        if urban_hydgrp == 3.0:
        #            CN_urban = 65
        #        if urban_hydgrp == 2.0:
        #            CN_urban = 52.5
        #        if urban_hydgrp == 1.0:
        #            CN_urban = 40
        #    if a == 'natural_hydgrp':
        #        natural_hydgrp = float(b)
        #        if natural_hydgrp == 4.0:
        #            CN_natural = 77.5
         #        if natural_hydgrp == 3.0:
        #            CN_natural = 65
        #        if natural_hydgrp == 2.0:
        #            CN_natural = 52.5
        #        if natural_hydgrp == 1.0:
        #            CN_natural = 40
        #    if a == 'ag_hydgrp':
        #        ag_hydgrp = float(b)
        #        if ag_hydgrp == 4.0:
        #            CN_ag = 77.5
        #        if ag_hydgrp == 3.0:
        #            CN_ag = 65
        #        if ag_hydgrp == 2.0:
        #            CN_ag = 52.5
        #        if ag_hydgrp == 1.0:
        #            CN_ag = 40

                    #factor = np.true_divide(CN,CN_urban)

        # New CN calculation #
        #open_space = [("A",49),("B",69),("C",79),("D",84)]
        #impervious = [("A",98),("B",98),("C",98),("D",98)]
        #urban_desert = [("A",63),("B",77),("C",85),("D",88)]
        #commercial = [("A",89),("B",92),("C",94),("D",95)]
        #residential = [("A",61),("B",75),("C",83),("D",87)]
        #row_crops = [("A",70),("B",80),("C",86),("D",90)]
        #hetero_ag = [("A",64),("B",75),("C",82),("D",86)]
        #pasture = [("A",49),("B",69),("C",79),("D",84)]
        #meadow = [("A",30),("B",58),("C",71),("D",78)]
        #brush = [("A",35),("B",56),("C",70),("D",77)]
        #woods = [("A",36),("B",60),("C",73),("D",79)]
        #herbaceous = [("A",0),("B",71),("C",81),("D",89)]

        #for a, b in environment:
        #    if a == 'statsgo_area':
        #        statsgo_area = float(b)
        #    if a == 'Forest_Area':
        #        Forest_Area = float(b)
        #    if a == 'Big_Ag':
        #        Big_Ag = float(b)
        #    if a == 'Pasture_Ag':
        #        Pasture_Ag = float(b)
        #    if a == 'Scrub_Area':
        #        Scrub_Area = float(b)
        #    if a == 'Barren_Area':
        #        Barren_Area = float(b)
        #    if a == 'Urban_Area':
        #        Urban_Area = float(b)
        #    if a == 'urban_hydgrp':
        #        urban_hydgrp = str(b)
        #    if a == 'natural_hydgrp':
        #        natural_hydgrp = str(b)
        #    if a == 'ag_hydgrp':
        #        ag_hydgrp = str(b)

        #def urban_landuse_func(n):
        #    urban_landuse = [open_space,impervious,commercial,residential]
        #    for val in urban_landuse:
        #        for a, b in val:
        #            if a == urban_hydgrp:
        #                yield b
        #urban_landuse = np.fromiter(urban_landuse_func(1), dtype=float)
        #CN_urban = np.mean(urban_landuse)

        #def natural_landuse_func(n):
        #    natural_landuse = [urban_desert,meadow,brush,woods,herbaceous]
        #    for val in natural_landuse:
        #        for a, b in val:
        #            if a == natural_hydgrp:
        #                yield b
        #natural_landuse = np.fromiter(natural_landuse_func(1),dtype=float)
        #CN_natural = np.mean(natural_landuse)

        #forest_prop = np.true_divide(Forest_Area,statsgo_area)
        #big_ag_prop = np.true_divide(Big_Ag,statsgo_area)
        #pasture_ag_prop = np.true_divide(Pasture_Ag,statsgo_area)
        #scrub_prop = np.true_divide(Scrub_Area,statsgo_area)
        #barren_prop = np.true_divide(Barren_Area,statsgo_area)
        #urban_prop = np.true_divide(Urban_Area,statsgo_area)

        #def ag_landuse_func(n):
        #    big_ag_landuse = [row_crops]
        #    ag_areas = [14253299516, 4648561687.33, 10675996369.4]
        #    for val in ag_areas:
        #        if val == area:
        #            for a,b in row_crops:
        #                if a == ag_hydgrp:
        #                    yield b
        #    ag_areas = [20040408427.5, 681843, 694638]
        #    for val in ag_areas:
        #        if val == area:
        #            for a, b in hetero_ag:
        #                if a == ag_hydgrp:
        #                    yield b
        #agricultural_landuse = np.fromiter(ag_landuse_func(1), dtype=float)
        #CN_ag = np.mean(agricultural_landuse)


        #if area == 20040408427.4543:
        #    C_fact_ag = C_small_ag
        #if area == 681843:
        #    C_fact_ag = C_small_ag
        #if area == 694638:
        #    C_fact_ag = C_small_ag

        for a, b in environment:
            if a == "CN_ag":
                CN_ag = float(b)
            if a == "CN_natural":
                CN_natural = float(b)
            if a == "CN_urban":
                CN_urban = float(b)


        ##########LIPID CONENT FOR BIOTA##########
        for a, b in environment:
            if a == 'soilOC1':
                soilOC1 = float(b)
            if a == 'soilOC2':
                soilOC2 = float(b)
            if a == 'soilOC3':
                soilOC3 = float(b)
            if a == 'sedFWOC':
                fsedOC = float(b)
            if a == 'sedSWOC':
                ssedOC = float(b)
            if a == 'dsoilOC1':
                dsoilOC1 = float(b)
            if a == 'dsoilOC2':
                dsoilOC2 = float(b)
            if a == 'dsoilOC3':
                dsoilOC3 = float(b)
            if a == 'spOC':
                spOC = float(b)

        ##########DENSITIES##########
        for a, b in environment:
            if a == 'freshssP':
                densityFreshSSed = float(b)
            if a == 'seassP':
                densitySeaSSed = float(b)
            if a == 'sedFWP':
                densityFreshSed = float(b)
            if a == 'sedSWP':
                densitySeaSed = float(b)
            if a == 'soilP1':
                densitySoil1 = float(b)
            if a == 'soilP2':
                densitySoil2 = float(b)
            if a == 'soilP3':
                densitySoil3 = float(b)
            if a == 'dsoilP1':
                densityDSoil1 = float(b)
            if a == 'dsoilP2':
                densityDSoil2 = float(b)
            if a == 'dsoilP3':
                densityDSoil3 = float(b)
            if a == 'dSS1':
                densitySolidSoil1 = float(b)
            if a == 'dSS2':
                densitySolidSoil2 = float(b)
            if a == 'dSS3':
                densitySolidSoil3 = float(b)
            if a == 'dFWSedS':
                densityFWSedSolid = float(b)
            if a == 'dSWSedS':
                densitySWSedSolid = float(b)
            if a == 'dSA1':
                densityAirSoil1 = float(b)
            if a == 'dSA2':
                densityAirSoil2 = float(b)
            if a == 'dSA3':
                densityAirSoil3 = float(b)
            if a == 'dSW1':
                densityWaterSoil1 = float(b)
            if a == 'dSW2':
                densityWaterSoil2 = float(b)
            if a == 'dSW3':
                densityWaterSoil3 = float(b)
            if a == 'airP':
                airP = float(b)
            if a == 'waterP':
                waterP = float(b)
            if a == 'freshwP':
                freshwP = float(b)
            if a == 'seawP':
                seawP = float(b)

        ##########PERCENT COMPOSITION OF SOIL##########
        for a, b in environment:
            if a == 'soilWC1':
                soilpercWater1 = float(b)
            if a == 'soilWC2':
                soilpercWater2 = float(b)
            if a == 'soilWC3':
                soilpercWater3 = float(b)
            if a == 'deepsWC1':
                dsoilpercWater1 = float(b)
            if a == 'deepsWC2':
                dsoilpercWater2 = float(b)
            if a == 'deepsWC3':
                dsoilpercWater3 = float(b)
            if a == 'soilAC1':
                soilpercAir1 = float(b)
            if a == 'soilAC2':
                soilpercAir2 = float(b)
            if a == 'soilAC3':
                soilpercAir3 = float(b)
            if a == 'deepsAC1':
                dsoilpercAir1 = float(b)
            if a == 'deepsAC2':
                dsoilpercAir2 = float(b)
            if a == 'deepsAC3':
                dsoilpercAir3 = float(b)
        soilpercSolid1 = 1 - soilpercWater1 - soilpercAir1
        soilpercSolid2 = 1 - soilpercWater2 - soilpercAir2
        soilpercSolid3 = 1 - soilpercWater3 - soilpercAir3
        dsoilpercSolid1 = 1 - dsoilpercWater1 - dsoilpercAir1
        dsoilpercSolid2 = 1 - dsoilpercWater2 - dsoilpercAir2
        dsoilpercSolid3 = 1 - dsoilpercWater3 - dsoilpercAir3

        ##########PERCENT SOLIDS IN SEDIMENT##########
        for a, b in environment:
            if a == 'fsedpercSolid':
                fsedpercSolid = float(b)
            if a == 'ssedpercSolid':
                ssedpercSolid = float(b)

        ##########NEW COMPARTMENT AREAS##########
        for a, b in environment:
            if a == 'area':
                area = float(b)
            if a == 'waterPerc':
                waterPerc = float(b)
            if a == 'freshwD':
                freshwD = float(b)
            if a == 'seawPerc':
                seawPerc = float(b)
            if a == 'seawD':
                seawD = float(b)
            if a == 'seawPerc':
                seawPerc = float(b)
            if a == 'soilPerc1':
                soilPerc1 = float(b)
            if a == 'soilPerc2':
                soilPerc2 = float(b)
            if a == 'soilPerc3':
                soilPerc3 = float(b)
            if a == 'deepsD1':
                deepsD1 = float(b)
            if a == 'deepsD2':
                deepsD2 = float(b)
            if a == 'deepsD3':
                deepsD3 = float(b)
            if a == 'area_1000_buffer':
                area_1000_buffer = float(b)
        #airA = area

        for a, b in environment:
            if a == 'freshwA':
                freshwA = float(b)
            if a == 'seawA':
                seawA = float(b)
            if a == 'soilA1':
                soilA1 = float(b)
            if a == 'soilA2':
                soilA2 = float(b)
            if a == 'soilA3':
                soilA3 = float(b)
        area = freshwA + seawA + soilA1 + soilA2 + soilA3
        airA = area

        waterA = np.add(freshwA,seawA)


        for a, b in environment:
            if a == 'soilA1':
                soilA1 = float(b)
            if a == 'soilA2':
                soilA2 = float(b)
            if a == 'soilA3':
                soilA3 = float(b)

        dsoilA1 = soilA1
        dsoilA2 = soilA2
        dsoilA3 = soilA3

        sedFWA = freshwA
        sedSWA = seawA

        ##########NEW COMPARTMENT VOLUMES##########
        for a, b in environment:
            if a == 'airH':
                airH = float(b)
            if a == 'soilD1':
                soilD1 = float(b)
            if a == 'soilD2':
                soilD2 = float(b)
            if a == 'soilD3':
                soilD3 = float(b)
            if a == 'sedFWD':
                sedFWD = float(b)
            if a == 'sedSWD':
                sedSWD = float(b)
            if a == 'aerC':
                aerC = float(b)
            if a == 'aerP':
                aerP = float(b)
            if a == 'seassC':
                seassC = float(b)
            if a == 'freshssC':
                freshssC = float(b)

        airV = np.multiply(area,airH)
        freshwV = np.multiply(freshwA,freshwD)
        seawV = np.multiply(seawA,seawD)

        sedFWV = np.multiply(sedFWA,sedFWD)
        sedSWV = np.multiply(sedSWA,sedSWD)

        soilV1 = np.multiply(soilA1,soilD1)
        soilV2 = np.multiply(soilA2,soilD2)
        soilV3 = np.multiply(soilA3,soilD3)

        deepsV1 = np.multiply(dsoilA1,deepsD1)
        deepsV2 = np.multiply(dsoilA2,deepsD2)
        deepsV3 = np.multiply(dsoilA3,deepsD3)

        factor = np.multiply(aerC,airV)
        aerV = np.true_divide(factor,aerP)

        factor = np.multiply(seassC,seawV)
        swSSedV = np.true_divide(factor,densitySeaSSed)

        factor = np.multiply(freshssC,freshwV)
        fwSSedV = np.true_divide(factor,densityFreshSSed)
        freshssPerc = np.true_divide(fwSSedV,freshwV)
        seassPerc = np.true_divide(swSSedV,seawV)
        FWpercSS = freshssPerc
        FWpercWater = np.subtract(1,FWpercSS)
        SWpercSS = seassPerc
        SWpercWater = np.subtract(1,SWpercSS)

        aerVf = np.true_divide(aerV,airV)

        ##########PERCENT COMPOSITION OF FRESHWATER##########
        for a, b in environment:
            if a == 'freshssPerc':
                FWpercSS = float(b)
            if a == 'FWbiotaPerc':
                FWpercBiota = float(b)
        FWpercWater = 1 - FWpercSS

        ##########PERCENT COMPOSITION OF SEAWATER##########
        for a, b in environment:
            if a == 'seassPerc':
                SWpercSS = float(b)
            if a == 'SWbiotaPerc':
                SWpercBiota = float(b)
        SWpercWater = 1 - SWpercSS

        ##########NEW MASS TRANSFER COEFFICIENTS##########
        N = 6.023e23
        pi = 3.14
        R = 8.314
        c_vol = np.true_divide(molecular_volume,N)


        ###### Viscosity for water ######

        temp = [round(x) for x in airTemp]
        neg_temp = np.arange(-30,0)

        s = len(neg_temp)

        neg_visc = []

        for i in range(s):
            val = neg_temp[i]
            new_visc = 0.0017602-2.74517338e-5*val
            neg_visc.append(new_visc)

        visc_temp = [a for a, b in viscosities]
        viscosity = [b for a, b in viscosities]
        visc_temp = np.concatenate((neg_temp,visc_temp), axis=0)
        viscosity = np.concatenate((neg_visc,viscosity), axis=0)

        s = len(temp)

        visclist = []

        for i in range(s):
            val = temp[i]
            visc_index = np.where(val == visc_temp)
            viscnew = viscosity[visc_index]
            for val in viscnew:
                thing = val
            visclist.append(thing)

        ###### Viscosity for air ######

        temp_air = [round(x) for x in airTemp]
        neg_temp_air = np.arange(-30,0)

        s_air = len(neg_temp_air)

        neg_visc_air = []

        for i in range(s_air):
            val = neg_temp_air[i]
            new_visc_air = 3.3888e-7+4.3988e-10*val
            neg_visc_air.append(new_visc_air)

        # converting from lb*s/ft^2 to kg/m*hour
        neg_visc_air = [(x*1.72e5) for x in neg_visc_air]

        visc_temp_air = [a for a, b in viscosities_air]
        viscosity_air = [b for a, b in viscosities_air]
        visc_temp_air = np.concatenate((neg_temp_air,visc_temp_air), axis=0)
        viscosity_air = np.concatenate((neg_visc_air,viscosity_air), axis=0)

        # viscosity of air is in kg/m*s
        viscosity_air = [(x/3600) for x in viscosity_air]

        def format_func(n):
            for val in viscosity_air:
                yield val
        viscosity_air = np.fromiter(format_func(1),dtype=float)

        s_air = len(temp_air)

        visclist_air = []

        for i in range(s_air):
            val = temp_air[i]
            visc_index_air = np.where(val == visc_temp_air)
            viscnew_air = viscosity_air[visc_index_air]
            visclist_air.append(viscnew_air)

        radius = (0.75*(c_vol/pi))**(0.33333)
        radius = radius/100

        airMD = []
        awMTCair = []
        waterMD = []
        awMTCwater = []
        sedfwMTC = []
        sedswMTC = []

        visclist = [float(x) for x in visclist]

        for i in range(s):

        #AIR DIFFUSIVITY#
            airmd = 2.35*molecular_volume**(-0.73)
            airMD.append(airmd)
            awmtcair = 0.0292*((airSpeed[i]/365/24)**0.78)*(sqrt(waterA)**-0.11)*((visclist_air[i]/(airP*(airMD[i]/10000)))**-0.69)
            for val in awmtcair:
                test = val
            awMTCair.append(test)

        #WATER DIFFUSIVITY#
            fric_velocity = 0.01*(airSpeed[i]/365/24)*((6.1+(0.63*(airSpeed[i]/365/24)))**0.5)
            watermd = ((R*(273.15+airTemp[i]))/(6*pi*N*(visclist[i])*(radius)))*10000
            waterMD.append(watermd)
            awmtcwater = 1e-6 + 1.44e-2*(fric_velocity*(fric_velocity**2.2)*(((visclist[i])/(waterP*(waterMD[i]/10000))))**-0.5);
            awMTCwater.append(awmtcwater)

        #FW MTC#
            Rp = (1- fsedpercSolid)**(-1/3)
            K23 = fsedOC*kOrganicWater
            Rc = 1 + ((densityFWSedSolid/1000)/(1-fsedpercSolid))*K23
            D_sed1 = waterMD[i]*0.36/(Rc*Rp)
            D_sed_dis1 = D_sed1*2
            sedfwmtc = D_sed1/sqrt(D_sed_dis1)
            sedfwMTC.append(sedfwmtc)

        #SW MTC#
            Rp = (1-ssedpercSolid)**(-1/3);
            K23 = kOrganicWater*ssedOC;
            Rc = 1 + ((densitySWSedSolid/1000)/(1-ssedpercSolid))*K23;
            D_sed2 = waterMD[i]*0.36/(Rc*Rp);
            D_sed_dis2 = D_sed2*2;
            sedswmtc = D_sed2/sqrt(D_sed_dis2);
            sedswMTC.append(sedswmtc)

        #Mackay Handbook of Chemical Mass Transport in the Environment, pg 327#
            a = 0.0872142857
            b = 0.6886666667
            Scf = ((visclist[i]/1000)/(freshwP*(waterMD[i]/10000)))
            Scs = ((visclist[i]/1000)/(seawP*(waterMD[i]/10000)))
        #Manning roughness coefficient, pg 330 (0.403/21)#
            n = 0.0191904762
            Cd = 5*9.81*(n**2)
            FWvelocity = (climate_flow[i])/freshwA;
            #SWvelocity = (climate_flow[i])/seawA;
            #uf = sqrt(Cd)*FWvelocity;
            #us = sqrt(Cd)*SWvelocity;

        factor = np.multiply(airMD,0.36)
        factor2 = np.multiply(factor,24)
        asMTC1 = np.true_divide(factor2,0.005)
        asMTC2 = asMTC1
        asMTC3 = asMTC1

        factor = np.multiply(airMD,0.36)
        airMD = np.multiply(factor,24)

        factor = np.multiply(waterMD,0.36)
        waterMD = np.multiply(factor,24)

        awMTCair = np.multiply(awMTCair,24)

        factor = np.multiply(awMTCwater,3600)
        awMTCwater = np.multiply(factor,24)

        sedfwMTC = np.multiply(sedfwMTC,24)

        sedswMTC = np.multiply(sedswMTC,24)

        #print "yes"
        for a, b in environment:
            if a == 'soilpathlen':
                soilpathlen = float(b)

        ##########RATE TRANSFER CONSTANTS##########
        for a, b in environment:
            if a == 'aerDepR':
                aerDepR = float(b)*24
            if a == 'precipScavR':
                precipScavR = float(b)
            if a == 'leachR':
                leachR = float(b)*24
            if a == 'soilRunS':
                soilRunS = float(b)*24
            if a == 'soilRunW':
                soilRunW = float(b)*24
            if a == 'freshssDepR':
                freshssDepR = float(b)*24
            if a == 'seassDepR':
                seassDepR = float(b)*24
            if a == 'freshssSusR':
                freshssSusR = float(b)*24
            if a == 'seassSusR':
                seassSusR = float(b)*24
            if a == 'freshssBurR':
                freshssBurR = float(b)*24
            if a == 'seassBurR':
                seassBurR = float(b)*24

        ##########COMPARTMENT FLOWS##########
        #airrestime = 20
        #waterrestime = 4400
        #sedrestime = 4400000

        #for a, b in environment:
        #    if a == 'airrestime':
        #        airrestime = float(b)
        #    if a == 'waterrestime':
        #        waterrestime = float(b)
        #    if a == 'sedrestime':
        #        sedrestime = float(b)

        #aerosolflow = np.true_divide(aerV,airrestime)

        #SSedFWflow = np.true_divide(fwSSedV,waterrestime)
        #SSedSWflow = np.true_divide(swSSedV,waterrestime)

        #sedFWflow = np.true_divide(sedFWV,sedrestime)
        #sedSWflow = np.true_divide(sedSWV,sedrestime)

        factor = sqrt(airA)
        factor2 = np.multiply(factor,airSpeed)
        airFlow = np.multiply(factor2,airH)


        ##########LOAD BACKGROUND CONCENTRATION##########
        for a, b, c in background:
            if b == 'A':
                bgConcAir = float(c)
            if b == 'fW':
                bgConcFW = float(c)
            if b == 'sW':
                bgConcSW = float(c)
            if b == 'S1':
                bgConcSoil1 = float(c)
            if b == 'S2':
                bgConcSoil2 = float(c)
            if b == 'S3':
                bgConcSoil3 = float(c)
            if b == 'fwSed':
                bgConcFWsed = float(c)
            if b == 'swSed':
                bgConcSWsed = float(c)
            if b == 'dS1':
                bgConcDSoil1 = float(c)
            if b == 'dS2':
                bgConcDSoil2 = float(c)
            if b == 'dS3':
                bgConcDSoil3 = float(c)

        ##########LOAD RELEASES##########

        Arelease = np.true_divide(release_air,molecular_mass)
        SWrelease = np.true_divide(release_seawater,molecular_mass)
        FWrelease = np.true_divide(release_freshwater,molecular_mass)
        S1release = np.true_divide(release_soil1,molecular_mass)
        S2release = np.true_divide(release_soil2,molecular_mass)
        S3release = np.true_divide(release_soil3,molecular_mass)
        FSedrelease = np.true_divide(release_fwsediment,molecular_mass)
        SSedrelease = np.true_divide(release_swsediment,molecular_mass)
        DS1release = np.true_divide(release_dsoil1,molecular_mass)
        DS2release = np.true_divide(release_dsoil2,molecular_mass)
        DS3release = np.true_divide(release_dsoil3,molecular_mass)

        ##########CHANGE RELEASES TO CONCENTRATION VALUES##########
        #Arelease = [x / airV for x in Arelease]
        #FWrelease = [x/ freshwV for x in FWrelease]
        #SWrelease = [x/ seawV for x in SWrelease]
        #Srelease1 = [x/ soilV1 for x in Srelease]
        #Srelease2 = [x/ soilV2 for x in Srelease]
        #Srelease3 = [x/ soilV3 for x in Srelease]
        #FSedrelease = [x/ sedFWV for x in FSedrelease]
        #SSedrelease = [x/ sedSWV for x in SSedrelease]
        #DSrelease1 = [x/ deepsV1 for x in Srelease]

        ##########CONSTANTS##########
        R = 8.314


        ###########INPUT LOADING COMPLETE##########

        #ZAIRSUB#
        sub1 = [x + 273.15 for x in airTemp]
        sub2 = np.multiply(sub1,R)
        zAirSub = np.true_divide(1,sub2)

        #ZWATERSUB#
        zWaterSub = np.true_divide(zAirSub,kAirWater)

        #ZOCTANOLSUB#
        zOctanolSub = np.multiply(kOctanolWater,zWaterSub)


        #ZAEROSOLSUB#
        zAerosolSub = np.multiply(kAerosolAir,zAirSub)

        #ZSUSPENDEDFRESHSUB#
        factor = np.true_divide(densityFreshSSed,1000)
        factor2 = np.multiply(zWaterSub,kOrganicWater)
        factor3 = np.multiply(factor2,factor)
        zSuspendedFreshSub = np.multiply(factor3,spOC)

        #ZSUSPENDEDSEASUB#
        factor = np.true_divide(densitySeaSSed,1000)
        factor2 = np.multiply(zWaterSub,kOrganicWater)
        factor3 = np.multiply(factor2,factor)
        zSuspendedSeaSub = np.multiply(factor3,spOC)

        #ZSOILSUB1#
        #factor = np.true_divide(densitySoil1,1000)
        #factor2 = np.multiply(zWaterSub,kOrganicWater)
        #factor3 = np.multiply(factor2,factor)
        #factor4 = np.true_divide(factor3,1000)
        #zSoilSub1 = np.multiply(factor4,soilOC1)
        #zSoilSub1 = np.multiply(zSoilSub1,1000)

        #ZSOILSUB1#
        factor = np.true_divide(densitySolidSoil1,1000)
        factor2 = np.multiply(zWaterSub,kOrganicWater)
        factor3 = np.multiply(factor2,factor)
        factor4 = np.true_divide(factor3,1000)
        zSoilSub1 = np.multiply(factor4,soilOC1)
        zSoilSub1 = np.multiply(zSoilSub1,1000)

        #ZSOILSUBAIR1#
        zSoilAirSub1 = zAirSub

        #ZSOILSUBWATER1#
        zSoilWaterSub1 = zWaterSub

        #ZSOILSUBSOLID1#
        factor = np.true_divide(densitySolidSoil1,1000)
        factor2 = np.multiply(zWaterSub,kOrganicWater)
        factor3 = np.multiply(factor2,factor)
        zSoilSubSolid1 = np.multiply(factor3,soilOC1)

        #ZSOILSUB2#
        #factor = np.true_divide(densitySoil2,1000)
        #factor2 = np.multiply(zWaterSub,kOrganicWater)
        #factor3 = np.multiply(factor2,factor)
        #factor4 = np.true_divide(factor3,1000)
        #zSoilSub2 = np.multiply(factor4,soilOC2)
        #zSoilSub2 = np.multiply(zSoilSub2,1000)

        #ZSOILSUB2#
        factor = np.true_divide(densitySolidSoil2,1000)
        factor2 = np.multiply(zWaterSub,kOrganicWater)
        factor3 = np.multiply(factor2,factor)
        factor4 = np.true_divide(factor3,1000)
        zSoilSub2 = np.multiply(factor4,soilOC2)
        zSoilSub2 = np.multiply(zSoilSub2,1000)

        #ZSOILSUBAIR2#
        zSoilAirSub2 = zAirSub

        #ZSOILSUBWATER2#
        zSoilWaterSub2 = zWaterSub

        #ZSOILSUBSOLID2#
        factor = np.true_divide(densitySolidSoil2,1000)
        factor2 = np.multiply(zWaterSub,kOrganicWater)
        factor3 = np.multiply(factor2,factor)
        zSoilSubSolid2 = np.multiply(factor3,soilOC2)

        #ZSOILSUB3#
        #factor = np.true_divide(densitySoil3,1000)
        #factor2 = np.multiply(zWaterSub,kOrganicWater)
        #factor3 = np.multiply(factor2,factor)
        #factor4 = np.true_divide(factor3,1000)
        #zSoilSub3 = np.multiply(factor4,soilOC3)
        #zSoilSub3 = np.multiply(zSoilSub3,1000)

        #ZSOILSUB3#
        factor = np.true_divide(densitySolidSoil3,1000)
        factor2 = np.multiply(zWaterSub,kOrganicWater)
        factor3 = np.multiply(factor2,factor)
        factor4 = np.true_divide(factor3,1000)
        zSoilSub3 = np.multiply(factor4,soilOC3)
        zSoilSub3 = np.multiply(zSoilSub3,1000)

        #ZSOILSUBAIR3#
        zSoilAirSub3 = zAirSub

        #ZSOILSUBWATER3#
        zSoilWaterSub3 = zWaterSub

        #ZSOILSUBSOLID3#
        factor = np.true_divide(densitySolidSoil3,1000)
        factor2 = np.multiply(zWaterSub,kOrganicWater)
        factor3 = np.multiply(factor2,factor)
        zSoilSubSolid3 = np.multiply(factor3,soilOC3)

        #ZSEDIMENTFRESHSUB#
        factor = np.true_divide(densityFreshSed,1000)
        factor2 = np.multiply(zWaterSub,kOrganicWater)
        factor3 = np.multiply(factor2,factor)
        factor4 = np.true_divide(factor3,1000)
        zSedimentFreshSub = np.multiply(factor4,fsedOC)
        zSedimentFreshSub = np.multiply(zSedimentFreshSub,1000)

        #ZSEDIMENTFRESHSUBWATER#
        zSedimentFreshSubWater = zWaterSub

        #ZSEDIMENTFRESHSUBSOLID#
        factor = np.true_divide(densityFWSedSolid,1000)
        factor2 = np.multiply(zWaterSub,kOrganicWater)
        factor3 = np.multiply(factor2,factor)
        zSedimentFreshSubSolid = np.multiply(factor3,fsedOC)

        #ZSEDIMENTSEASUB#
        factor = np.true_divide(densitySeaSed,1000)
        factor2 = np.multiply(zWaterSub,kOrganicWater)
        factor3 = np.multiply(factor2,factor)
        factor4 = np.true_divide(factor3,1000)
        zSedimentSeaSub = np.multiply(factor4,ssedOC)
        zSedimentSeaSub = np.multiply(zSedimentSeaSub,1000)

        #ZSEDIMENTSEASUBWATER#
        zSedimentSeaSubWater = zWaterSub

        #ZSEDIMENTSEASUBSOLID#
        factor = np.true_divide(densitySWSedSolid,1000)
        factor2 = np.multiply(zWaterSub,kOrganicWater)
        factor3 = np.multiply(factor2,factor)
        zSedimentSeaSubSolid = np.multiply(factor3,ssedOC)

        #ZDEEPSOILSUB1#
        factor = np.true_divide(densityDSoil1,1000)
        factor2 = np.multiply(zWaterSub,kOrganicWater)
        factor3 = np.multiply(factor2,factor)
        zDeepSoilSub1 = np.multiply(factor3,dsoilOC1)

        #ZDEEPSOILSUB2#
        factor = np.true_divide(densityDSoil2,1000)
        factor2 = np.multiply(zWaterSub,kOrganicWater)
        factor3 = np.multiply(factor2,factor)
        zDeepSoilSub2 = np.multiply(factor3,dsoilOC2)

        #ZDEEPSOILSUB3#
        factor = np.true_divide(densityDSoil3,1000)
        factor2 = np.multiply(zWaterSub,kOrganicWater)
        factor3 = np.multiply(factor2,factor)
        zDeepSoilSub3 = np.multiply(factor3,dsoilOC3)

        #ZSOILPARTICLESUB1#
        factor = np.multiply(kOrganicWater,soilOC1)
        factor2 = np.multiply(factor,densitySolidSoil1)
        factor3 = np.true_divide(factor2,1000)
        zSoilParticleSub1 = np.multiply(factor3,zWaterSub)

        #ZSOILPARTICLESUB2#
        factor = np.multiply(kOrganicWater,soilOC2)
        factor2 = np.multiply(factor,densitySolidSoil1)
        factor3 = np.true_divide(factor2,1000)
        zSoilParticleSub2 = np.multiply(factor3,zWaterSub)

        #ZSOILPARTICLESUB3#
        factor = np.multiply(kOrganicWater,soilOC3)
        factor2 = np.multiply(factor,densitySolidSoil1)
        factor3 = np.true_divide(factor2,1000)
        zSoilParticleSub3 = np.multiply(factor3,zWaterSub)

        #ZSEDPARTICLESUB#
        factor = np.multiply(kOrganicWater,fsedOC)
        factor2 = np.multiply(factor,densityFWSedSolid)
        factor3 = np.true_divide(factor2,1000)
        zSedParticleSub = np.multiply(factor3,zWaterSub)

        #ZSUSPARTICLESUB#
        factor = np.multiply(kOrganicWater,spOC)
        factor2 = np.multiply(factor,densityFreshSSed)
        factor3 = np.true_divide(factor2,1000)
        zSusParticleSub = np.multiply(factor3,zWaterSub)

        #PER-COMPARTMENT Z VALUES#

        #ZAIR#
        factor3 = np.multiply(zAerosolSub,aerVf)
        zAir = np.add(zAirSub,factor3)

        #ZWATERFRESH#
        #factor = np.multiply(zWaterSub,FWpercWater)
        #factor2 = np.multiply(zBiotaSeaSub,FWpercBiota)
        #factor3 = np.add(factor,factor2)
        #factor4 = np.multiply(zSuspendedFreshSub,FWpercSS)
        #zWaterFresh = np.add(factor3,factor4)
        factor = np.multiply(zWaterSub,FWpercWater)
        factor2 = np.multiply(zSuspendedFreshSub,FWpercSS)
        zWaterFresh = np.add(factor,factor2)


        #ZWATERSEA#
        #factor = np.multiply(zWaterSub,SWpercWater)
        #factor2 = np.multiply(zBiotaSeaSub,SWpercBiota)
        #factor3 = np.multiply(zSuspendedSeaSub,SWpercSS)
        #factor4 = np.add(factor,factor2)
        #zWaterSea = np.add(factor3,factor4)
        factor = np.multiply(zWaterSub,SWpercWater)
        factor2 = np.multiply(zSuspendedSeaSub,SWpercSS)
        zWaterSea = np.add(factor,factor2)

        #ZSOIL1#
        factor = np.multiply(zWaterSub,soilpercWater1)
        factor2 = np.multiply(zAirSub,soilpercAir1)
        factor3 = np.multiply(zSoilSub1,soilpercSolid1)
        factor4 = np.add(factor,factor2)
        zSoil1 = np.add(factor3,factor4)

        #ZSOIL2#
        factor = np.multiply(zWaterSub,soilpercWater2)
        factor2 = np.multiply(zAirSub,soilpercAir2)
        factor3 = np.multiply(zSoilSub2,soilpercSolid2)
        factor4 = np.add(factor,factor2)
        zSoil2 = np.add(factor3,factor4)

        #ZSOIL3#
        factor = np.multiply(zWaterSub,soilpercWater3)
        factor2 = np.multiply(zAirSub,soilpercAir3)
        factor3 = np.multiply(zSoilSub3,soilpercSolid3)
        factor4 = np.add(factor,factor2)
        zSoil3 = np.add(factor3,factor4)

        #ZSEDIMENTFRESH#
        factor = np.subtract(1,fsedpercSolid)
        factor2 = np.multiply(zWaterSub,factor)
        factor3 = np.multiply(zSedimentFreshSubSolid,fsedpercSolid)
        zSedimentFresh = np.add(factor2,factor3)

        #ZSEDIMENTSEA#
        factor = np.subtract(1,ssedpercSolid)
        factor2 = np.multiply(zWaterSub,factor)
        factor3 = np.multiply(zSedimentSeaSubSolid,ssedpercSolid)
        zSedimentSea = np.add(factor2,factor3)

        #ZDEEPSOIL1#
        factor = np.multiply(zWaterSub,dsoilpercWater1)
        factor2 = np.multiply(zAirSub,dsoilpercAir1)
        factor3 = np.multiply(zDeepSoilSub1,dsoilpercSolid1)
        factor4 = np.add(factor,factor2)
        zDeepSoil1 = np.add(factor3,factor4)

        #ZDEEPSOIL2#
        factor = np.multiply(zWaterSub,dsoilpercWater2)
        factor2 = np.multiply(zAirSub,dsoilpercAir2)
        factor3 = np.multiply(zDeepSoilSub2,dsoilpercSolid2)
        factor4 = np.add(factor,factor2)
        zDeepSoil2 = np.add(factor3,factor4)

        #ZDEEPSOIL3#
        factor = np.multiply(zWaterSub,dsoilpercWater3)
        factor2 = np.multiply(zAirSub,dsoilpercAir3)
        factor3 = np.multiply(zDeepSoilSub3,dsoilpercSolid3)
        factor4 = np.add(factor,factor2)
        zDeepSoil3 = np.add(factor3,factor4)


        ########## D Calculation ##########


        # URBAN EROSION #
        factor = np.true_divide(1,densitySoil1)
        factor2 = np.multiply(RUSLE_urban,factor)
        factor3 = np.true_divide(factor2,365)
        factor4 = np.multiply(factor3,soilA1)
        RUSLE_urban = np.multiply(factor4,zSoilParticleSub1)

        # NATURAL EROSION #
        factor = np.true_divide(1,densitySoil2)
        factor2 = np.multiply(RUSLE_natural,factor)
        factor3 = np.true_divide(factor2,365)
        factor4 = np.multiply(factor3,soilA2)
        RUSLE_natural = np.multiply(factor4,zSoilParticleSub2)

        # AGRICULTURAL EROSION #
        factor = np.true_divide(1,densitySoil3)
        factor2 = np.multiply(RUSLE_agricultural,factor)
        factor3 = np.true_divide(factor2,365)
        factor4 = np.multiply(factor3,soilA3)
        RUSLE_agricultural = np.multiply(factor4,zSoilParticleSub3)

        # URBAN RUNOFF #
        factor = np.true_divide(1000,CN_urban)
        S_urban = factor - 10
        limit = np.multiply(0.2,S_urban)

        Qs_urban = []

        for val in precipR:
            units = val * 0.0393701
            if units > limit:
                Q=((units-0.2*S_urban)**2)/((units+0.8*S_urban))
                Qs_urban.append(Q)
            else:
                Q=0
                Qs_urban.append(Q)

        factor = np.true_divide(Qs_urban,39.3701)
        Q_urban = np.multiply(factor,soilA1)


        factor = np.true_divide(1000,CN_natural)
        S_natural = factor - 10
        limit = np.multiply(0.2,S_natural)

        Qs_natural = []

        for val in precipR:
            units = val * 0.0393701
            if units > limit:
                Q=((units-0.2*S_natural)**2)/((units+0.8*S_natural))
                Qs_natural.append(Q)
            else:
                Q=0
                Qs_natural.append(Q)

        factor = np.true_divide(Qs_natural,39.3701)
        Q_natural = np.multiply(factor,soilA2)


        factor = np.true_divide(1000,CN_ag)
        S_agricultural = factor - 10
        limit = np.multiply(0.2,S_agricultural)

        Qs_agricultural = []

        for val in precipR:
            units = val * 0.0393701
            if units > limit:
                Q=((units-0.2*S_agricultural)**2)/((units+0.8*S_agricultural))
                Qs_agricultural.append(Q)
            else:
                Q=0
                Qs_agricultural.append(Q)

        factor = np.true_divide(Qs_agricultural,39.3701)
        Q_agricultural = np.multiply(factor,soilA3)


        #####REACTION D VALUES#####

        #DAIRREACT#
        factor = np.multiply(airV,kDegredationInAir)
        dAirReact = np.multiply(factor,zAir)

        #DAEROSOLREACT#
        factor = np.multiply(aerV,kDegredationInAerosol)
        dAerosolReact = np.multiply(factor,zAerosolSub)

        #DWATERFRESHREACT#
        factor = np.multiply(freshwV,kDegredationInWater)
        dWaterFreshReact = np.multiply(factor,zWaterFresh)

        #DFRESHSSEDREACT#
        factor = np.multiply(fwSSedV, kDegredationInSSediment)
        dFreshSSedReact = np.multiply(factor,zSuspendedFreshSub)

        #DWATERSEAREACT#
        factor = np.multiply(seawV,kDegredationInWater)
        dWaterSeaReact = np.multiply(factor,zWaterSea)

        #DSEASSEDREACT#
        factor = np.multiply(swSSedV, kDegredationInSSediment)
        dSeaSSedReact = np.multiply(factor,zSuspendedSeaSub)

        #DSOILREACT1#
        factor = np.multiply(soilV1,kDegredationInSoil)
        dSoilReact1 = np.multiply(factor,zSoil1)

        #DSOILREACT2#
        factor = np.multiply(soilV2,kDegredationInSoil)
        dSoilReact2 = np.multiply(factor,zSoil2)

        #DSOILREACT3#
        factor = np.multiply(soilV3,kDegredationInSoil)
        dSoilReact3 = np.multiply(factor,zSoil3)

        #DSEDIMENTFRESHREACT#
        factor = np.multiply(sedFWV,kDegredationInSediment)
        dSedimentFreshReact = np.multiply(factor,zSedimentFresh)

        #DSEDIMENTSEAREACT#
        factor = np.multiply(sedSWV,kDegredationInSediment)
        dSedimentSeaReact = np.multiply(factor,zSedimentSea)

        #DDEEPSOILREACT1#
        factor = np.multiply(deepsV1,kDegredationInSoil)
        dDeepSoilReact1 = np.multiply(factor,zDeepSoil1)

        #DDEEPSOILREACT2#
        factor = np.multiply(deepsV2,kDegredationInSoil)
        dDeepSoilReact2 = np.multiply(factor,zDeepSoil2)

        #DDEEPSOILREACT3#
        factor = np.multiply(deepsV3,kDegredationInSoil)
        dDeepSoilReact3 = np.multiply(factor,zDeepSoil3)

        #####ADVECTION D VALUES#####

        #DAIRADVECTION#
        dAiradvection = np.multiply(airFlow,zAir)

        #DAEROSOLADVECTION#
        #dAerosoladvection = np.multiply(aerosolflow,zAerosolSub)

        #DFWADVECTION#
        dFWadvection = np.multiply(fwSpeed,zWaterFresh)

        #DSWADVECTION#
        dSWadvection = np.multiply(swSpeed,zWaterSea)

        #DFWSEDADVECTION#
        #dFWSedadvection = np.multiply(sedFWflow,zSedimentFresh)

        #DFWSSEDADVECTION#
        #FWSSedadvection = np.multiply(SSedFWflow,zSuspendedFreshSub)

        #DSWSEDADVECTION#
        #dSWSedadvection = np.multiply(sedSWflow,zSedimentSea)

        #DSWSSEDADVECTION#
        #dSWSSedadvection = np.multiply(SSedSWflow,zSuspendedSeaSub)


        #####AIR FRESHWATER INTERFACE#####

        #DAFWDIFFUCSION#
        factor = np.multiply(awMTCair,freshwA)
        factor2 = np.multiply(factor, zAirSub)
        factor3 = np.true_divide(1,factor2)
        factor4 = np.multiply(awMTCwater,freshwA)
        factor5 = np.multiply(factor4,zWaterSub)
        factor6 = np.true_divide(1,factor5)
        factor7 = np.add(factor3,factor6)
        dAFWdiffusion = np.true_divide(1,factor7)

        #DASWWETDEP#
        factor = np.multiply(precipR,freshwA)
        factor2 = np.multiply(aerVf,precipScavR)
        factor3 = np.multiply(factor2,zAerosolSub)
        dAFWwetdep = np.multiply(factor,factor3)

        #DAFWDRYDEP#
        factor = np.multiply(aerDepR,freshwA)
        factor2 = np.multiply(aerVf,zAerosolSub)
        dAFWdrydep = np.multiply(factor,factor2)

        #DAFWPRECIP#
        factor = np.multiply(precipR,freshwA)
        dAFWprecip = np.multiply(factor,zWaterSub)

        #####AIR SEAWATER INTERFACE#####

        #DASWDIFFUSION#
        factor = np.multiply(awMTCair,seawA)
        factor2 = np.multiply(factor,zAirSub)
        factor3 = np.true_divide(1,factor2)
        factor4 = np.multiply(awMTCwater,seawA)
        factor5 = np.multiply(factor4,zWaterSub)
        factor6 = np.true_divide(1,factor5)
        factor7 = np.add(factor3,factor6)
        dASWdiffusion = np.true_divide(1,factor7)

        #DASWWETDEP#
        factor = np.multiply(precipR,seawA)
        factor2 = np.multiply(aerVf,precipScavR)
        factor3 = np.multiply(factor2,zAerosolSub)
        dASWwetdep = np.multiply(factor,factor3)

        #DASWDRYDEP#
        factor = np.multiply(aerDepR,seawA)
        factor2 = np.multiply(aerVf,zAerosolSub)
        dASWdrydep = np.multiply(factor,factor2)

        #DASWPRECIP#
        factor = np.multiply(precipR,seawA)
        dASWprecip = np.multiply(factor,zWaterSub)

        #####AIR SOIL INTERFACE#####

        #DASDIFFUSION1#
        factor = np.multiply(asMTC1,soilA1)
        factor2 = np.multiply(factor,zAirSub)
        factor3 = np.true_divide(1,factor2)

        factor4 = np.multiply(airMD,zAirSub)
        factor5 = np.multiply(waterMD,zWaterSub)
        factor6 = np.add(factor4,factor5)
        factor7 = np.multiply(soilA1,factor6)
        factor8 = np.true_divide(soilpathlen,factor7)

        factor9 = np.add(factor3,factor8)
        dASdiffusion1 = np.true_divide(1,factor9)

        #DASDIFFUSION2#
        factor = np.multiply(asMTC2,soilA2)
        factor2 = np.multiply(factor,zAirSub)
        factor3 = np.true_divide(1,factor2)

        factor4 = np.multiply(airMD,zAirSub)
        factor5 = np.multiply(waterMD,zWaterSub)
        factor6 = np.add(factor4,factor5)
        factor7 = np.multiply(soilA2,factor6)
        factor8 = np.true_divide(soilpathlen,factor7)

        factor9 = np.add(factor3,factor8)
        dASdiffusion2 = np.true_divide(1,factor9)

        #DASDIFFUSION3#
        factor = np.multiply(asMTC3,soilA3)
        factor2 = np.multiply(factor,zAirSub)
        factor3 = np.true_divide(1,factor2)

        factor4 = np.multiply(airMD,zAirSub)
        factor5 = np.multiply(waterMD,zWaterSub)
        factor6 = np.add(factor4,factor5)
        factor7 = np.multiply(soilA3,factor6)
        factor8 = np.true_divide(soilpathlen,factor7)

        factor9 = np.add(factor3,factor8)
        dASdiffusion3 = np.true_divide(1,factor9)

        #DASWETDEP1#
        factor = np.multiply(precipR,soilA1)
        factor2 = np.multiply(aerVf,precipScavR)
        factor3 = np.multiply(factor2,zAerosolSub)
        dASwetdep1 = np.multiply(factor,factor3)

        #DASWETDEP2#
        factor = np.multiply(precipR,soilA2)
        factor2 = np.multiply(aerVf,precipScavR)
        factor3 = np.multiply(factor2,zAerosolSub)
        dASwetdep2 = np.multiply(factor,factor3)

        #DASWETDEP3#
        factor = np.multiply(precipR,soilA3)
        factor2 = np.multiply(aerVf,precipScavR)
        factor3 = np.multiply(factor2,zAerosolSub)
        dASwetdep3 = np.multiply(factor,factor3)

        #DASDRYDEP1#
        factor = np.multiply(aerDepR,soilA1)
        factor2 = np.multiply(aerVf,zAerosolSub)
        dASdrydep1 = np.multiply(factor,factor2)

        #DASDRYDEP2#
        factor = np.multiply(aerDepR,soilA2)
        factor2 = np.multiply(aerVf,zAerosolSub)
        dASdrydep2 = np.multiply(factor,factor2)

        #DASDRYDEP3#
        factor = np.multiply(aerDepR,soilA3)
        factor2 = np.multiply(aerVf,zAerosolSub)
        dASdrydep3 = np.multiply(factor,factor2)

        #DASPRECIP1#
        factor = np.multiply(precipR,soilA1)
        dASprecip1 = np.multiply(factor,zWaterSub)

        #DASPRECIP2#
        factor = np.multiply(precipR,soilA2)
        dASprecip2 = np.multiply(factor,zWaterSub)

        #DASPRECIP3#
        factor = np.multiply(precipR,soilA3)
        dASprecip3 = np.multiply(factor,zWaterSub)

        #####SOIL FRESHWATER INTERFACE#####

        #DSFWRUNS1#
        factor = np.multiply(soilA1,soilRunS)
        dSFWrunS1 = np.multiply(factor,zSoilParticleSub1)
        dSFWrunS1 = RUSLE_urban

        #DSFWRUNS2#
        factor = np.multiply(soilA2,soilRunS)
        dSFWrunS2 = np.multiply(factor,zSoilParticleSub2)
        dSFWrunS2 = RUSLE_natural

        #DSFWRUNS3#
        factor = np.multiply(soilA3,soilRunS)
        dSFWrunS3 = np.multiply(factor,zSoilParticleSub3)
        dSFWrunS3 = RUSLE_agricultural

        #DSFWRUNW1#
        factor = np.multiply(soilA1,soilRunW)
        dSFWrunW1 = np.multiply(factor,zWaterSub)
        factor = np.multiply(Q_urban,zWaterSub)
        dSFWrunW1 = np.multiply(factor,24)

        #DSFWRUNW2#
        factor = np.multiply(soilA2,soilRunW)
        dSFWrunW2 = np.multiply(factor,zWaterSub)
        factor = np.multiply(Q_natural,zWaterSub)
        dSFWrunW2 = np.multiply(factor,24)

        #DSFWRUNW3#
        factor = np.multiply(soilA3,soilRunW)
        dSFWrunW3 = np.multiply(factor,zWaterSub)
        factor = np.multiply(Q_agricultural,zWaterSub)
        dSFWrunW3 = np.multiply(factor,24)

        #DSFWLEACH1#
        factor = np.multiply(soilA1,leachR)
        dSFWleach1 = np.multiply(factor,zWaterSub)

        #DSFWLEACH2#
        factor = np.multiply(soilA2,leachR)
        dSFWleach2 = np.multiply(factor,zWaterSub)

        #DSFWLEACH3#
        factor = np.multiply(soilA3,leachR)
        dSFWleach3 = np.multiply(factor,zWaterSub)

        #####FRESHWATER SEDIMENT INTERFACE#####

        #DSEDFWDIFFUSION# - MATLAB AND PYTHON ROUND THE VISCOSITIES OFF TO A DIFFERRENT NUMBER OF
                           #SIGNIFICANT DIGITS, THUS THE MASS TRANSFER COEFFICIENTS ARE SLIGHTLY
                           #DIFFERENT IN BOTH MODELS.  THIS CHANGES THE D VALUES IN BOTH MODELS SLIGHTLY
                           #AS WELL
        factor = np.multiply(freshwA,sedfwMTC)
        dSedFWdiffusion = np.multiply(factor,zWaterSub)

        #DSEDFWDEP#
        factor = np.multiply(freshwA,freshssDepR)
        dSedFWdep = np.multiply(factor,zSusParticleSub)

        #DSEDFWSUS#
        factor = np.multiply(freshwA,freshssSusR)
        dSedFWsus = np.multiply(factor,zSedParticleSub)

        #DSEDFWBUR#
        factor = np.multiply(freshwA,freshssBurR)
        dSedFWbur = np.multiply(factor,zWaterSub)

        #####SEAWATER SEDIMENT INTERFACE#####

        #DSEDSWDIFFUSION#
        factor = np.multiply(seawA,sedswMTC)
        dSedSWdiffusion = np.multiply(factor,zWaterSub)

        #DSEDSWDEP#
        factor = np.multiply(seawA,seassDepR)
        dSedSWdep = np.multiply(factor,zSusParticleSub)

        #DSEDSWSUS#
        factor = np.multiply(seawA,seassSusR)
        dSedSWsus = np.multiply(factor,zSedParticleSub)

        #DSEDSWBUR#
        factor = np.multiply(seawA,seassBurR)
        dSedSWbur = np.multiply(factor,zWaterSub)

        #####GENERAL DEEP SOIL INTERFACE#####

        ###AIR###

        #DADEEPSDIFFUSION1#
        factor = np.multiply(asMTC1,dsoilA1)
        factor2 = np.multiply(factor,zAirSub)
        factor3 = np.true_divide(1,factor2)

        factor4 = np.multiply(airMD,zAirSub)
        factor5 = np.multiply(waterMD,zWaterSub)
        factor6 = np.add(factor4,factor5)
        factor7 = np.multiply(dsoilA1,factor6)
        factor8 = np.true_divide(soilpathlen,factor7)

        factor9 = np.add(factor3,factor8)
        dADeepSdiffusion1 = np.true_divide(1,factor9)

        #####SOIL-DEEP SOIL INTERFACE#####
        factor = np.multiply(dsoilA1,leachR)
        dS1toDeepS1leach = np.multiply(factor,zWaterSub)

        factor = np.multiply(dsoilA2,leachR)
        dS2toDeepS2leach = np.multiply(factor,zWaterSub)

        factor = np.multiply(dsoilA3,leachR)
        dS3toDeepS3leach = np.multiply(factor,zWaterSub)

        ###FRESHWATER###

        #DDEEPSFWRUNS1#
        factor = np.multiply(dsoilA1,soilRunS)
        dDeepSFWrunS1 = np.multiply(factor,zDeepSoilSub1)

        #DDEEPSFWRUNW1#
        factor = np.multiply(dsoilA1,soilRunW)
        dDeepSFWrunW1 = np.multiply(factor,zWaterSub)

        #DDEEPSFWLEACH1#
        #factor = np.multiply(dsoilA1,leachR)
        #dDeepSFWleach1 = np.multiply(factor,zWaterSub)
        ##########NET D VALUES##########


        ###AIR###

        #DAREMOVAL#
        dAremoval = np.add(dAirReact,dAiradvection)

        #DATOFW#
        factor = np.add(dAFWdiffusion,dAFWprecip)
        factor2 = np.add(dAFWwetdep,dAFWdrydep)
        dAtoFW = np.add(factor,factor2)

        #DATOSW#
        factor = np.add(dASWdiffusion,dASWprecip)
        factor2 = np.add(dASWwetdep,dASWdrydep)
        dAtoSW = np.add(factor,factor2)

        #DATOS1#
        factor = np.add(dASdiffusion1,dASprecip1)
        factor2 = np.add(dASwetdep1,dASdrydep1)
        dAtoS1 = np.add(factor,factor2)

        #DATOS2#
        factor = np.add(dASdiffusion2,dASprecip2)
        factor2 = np.add(dASwetdep2,dASdrydep2)
        dAtoS2 = np.add(factor,factor2)

        #DATOS3#
        factor = np.add(dASdiffusion3,dASprecip3)
        factor2 = np.add(dASwetdep3,dASdrydep3)
        dAtoS3 = np.add(factor,factor2)

        #DATOFSED#
        dAtoFSed = np.zeros([1, len(new_datetime)])

        #DATOSSED#
        dAtoSSed = np.zeros([1, len(new_datetime)])

        #DATODEEPS1#
        dAtoDeepS1 = np.zeros([1, len(new_datetime)])

        #DATODEEPS2#
        dAtoDeepS2 = np.zeros([1, len(new_datetime)])

        #DATODEEPS3#
        dAtoDeepS3 = np.zeros([1, len(new_datetime)])


        ###AEROSOL###



        ###FRESHWATER###

        #DFWTOA#
        dFWtoA = dAFWdiffusion

        #DFWREMOVAL#
        dFWremoval = np.add(dWaterFreshReact,dFWadvection)

        #DFWTOSW#
        dFWtoSW = dFWadvection

        #DFWTOS1#
        dFWtoS1 = np.zeros([1, len(new_datetime)])

        #DFWTOS2#
        dFWtoS2 = np.zeros([1, len(new_datetime)])

        #DFWTO3S#
        dFWtoS3 = np.zeros([1, len(new_datetime)])

        #DFWTOFSED#
        dFWtoFSed = np.add(dSedFWdiffusion,dSedFWdep)

        #DFWTOSSED#
        dFWtoSSed = np.zeros([1, len(new_datetime)])

        #DFWTODEEPS1#
        dFWtoDeepS1 = np.zeros([1, len(new_datetime)])

        #DFWTODEEPS2#
        dFWtoDeepS2 = np.zeros([1, len(new_datetime)])

        #DFWTODEEPS3#
        dFWtoDeepS3 = np.zeros([1, len(new_datetime)])

        ###SEAWATER###

        #DSWTOA#
        dSWtoA = dASWdiffusion

        #dSWTOFW#
        dSWtoFW = np.zeros([1, len(new_datetime)])

        #DSWREMOVAL#
        dSWremoval = np.add(dWaterSeaReact,dSWadvection)

        #DSWTOS1#
        dSWtoS1 = np.zeros([1, len(new_datetime)])

        #DSWTOS2#
        dSWtoS2 = np.zeros([1, len(new_datetime)])

        #DSWTOS3#
        dSWtoS3 = np.zeros([1, len(new_datetime)])

        #DSWTOFSED#
        dSWtoFSed = np.zeros([1, len(new_datetime)])

        #DSWTOSSED#
        dSWtoSSed = np.add(dSedSWdiffusion,dSedSWdep)

        #DSWTODEEPS1#
        dSWtoDeepS1 = np.zeros([1, len(new_datetime)])

        #DSWTODEEPS2#
        dSWtoDeepS2 = np.zeros([1, len(new_datetime)])

        #DSWTODEEPS3#
        dSWtoDeepS3 = np.zeros([1, len(new_datetime)])

        ###SOIL1###

        #DS1TOA#
        dS1toA = dASdiffusion1

        #DS1TOFW#
        dS1toFW = np.add(dSFWrunS1,dSFWrunW1)

        #DS1TOSW#
        dS1toSW = np.zeros([1, len(new_datetime)])

        #DS1REMOVAL#
        dS1removal = np.add(dSoilReact1,dSFWleach1)

        #DS1TOS2#
        dS1toS2 = np.zeros([1, len(new_datetime)])

        #DS1TOS3#
        dS1toS3 = np.zeros([1, len(new_datetime)])

        #DS1TOFSED#
        dS1toFSed = np.zeros([1, len(new_datetime)])

        #DS1TOSSED#
        dS1toSSed = np.zeros([1, len(new_datetime)])

        #DS1TODEEPS1#
        dS1toDeepS1 = dS1toDeepS1leach

        #DS1TODEEPS2#
        dS1toDeepS2 = np.zeros([1, len(new_datetime)])

        #DS1TODEEPS3#
        dS1toDeepS3 = np.zeros([1, len(new_datetime)])

        ###SOIL2###

        #DS2TOA#
        dS2toA = dASdiffusion2

        #DS2TOFW#
        dS2toFW = np.add(dSFWrunS2,dSFWrunW2)

        #DS2TOSW#
        dS2toSW = np.zeros([1, len(new_datetime)])

        #DS2TOS1#
        dS2toS1 = np.zeros([1, len(new_datetime)])

        #DSREMOVAL2#
        dS2removal = np.add(dSoilReact2,dSFWleach2)

        #DS2TOS3#
        dS2toS3 = np.zeros([1, len(new_datetime)])

        #DS2TOFSED#
        dS2toFSed = np.zeros([1, len(new_datetime)])

        #DS2TOSSED#
        dS2toSSed = np.zeros([1, len(new_datetime)])

        #DS2TODEEPS1#
        dS2toDeepS1 = np.zeros([1, len(new_datetime)])

        #DS2TODEEPS2#
        dS2toDeepS2 = dS2toDeepS2leach

        #DS2TODEEPS3#
        dS2toDeepS3 = np.zeros([1, len(new_datetime)])

        ###SOIL3###

        #DS3TOA#
        dS3toA = dASdiffusion3

        #DS3TOFW#
        dS3toFW = np.add(dSFWrunS3,dSFWrunW3)

        #DS3TOSW#
        dS3toSW = np.zeros([1, len(new_datetime)])

        #DS3TOS1#
        dS3toS1 = np.zeros([1, len(new_datetime)])

        #DS3TOS2#
        dS3toS2 = np.zeros([1, len(new_datetime)])

        #DS3REMOVAL#
        dS3removal = np.add(dSoilReact3,dSFWleach3)

        #DS3TOFSED#
        dS3toFSed = np.zeros([1, len(new_datetime)])

        #DS3TOSSED#
        dS3toSSed = np.zeros([1, len(new_datetime)])

        #DS3TODEEPS1#
        dS3toDeepS1 = np.zeros([1, len(new_datetime)])

        #DS3TODEEPS2#
        dS3toDeepS2 = np.zeros([1, len(new_datetime)])

        #DS3TODEEPS1#
        dS3toDeepS3 = dS3toDeepS3leach

        ###FRESHWATER SEDIMENT###

        #DFSEDTOA#
        dFSedtoA = np.zeros([1, len(new_datetime)])

        #DFSEDTOFW#
        dFSedtoFW = np.add(dSedFWdiffusion,dSedFWsus)

        #DFSEDTOSW#
        dFSedtoSW = np.zeros([1, len(new_datetime)])

        #DFSEDTOS1#
        dFSedtoS1 = np.zeros([1, len(new_datetime)])

        #DFSEDTOS2#
        dFSedtoS2 = np.zeros([1, len(new_datetime)])

        #DFSEDTOS3#
        dFSedtoS3 = np.zeros([1, len(new_datetime)])

        #DFSEDREMOVAL#
        dFSedremoval = np.add(dSedimentFreshReact,dSedFWbur)

        #DFSEDTOSSED#
        dFSedtoSSed = np.zeros([1, len(new_datetime)])

        #DFSEDTODEEPS1#
        dFSedtoDeepS1 = np.zeros([1, len(new_datetime)])

        #DFSEDTODEEPS2#
        dFSedtoDeepS2 = np.zeros([1, len(new_datetime)])

        #DFSEDTODEEPS3#
        dFSedtoDeepS3 = np.zeros([1, len(new_datetime)])

        ###SEAWATER SEDIMENT###

        #DSSEDTOA#
        dSSedtoA = np.zeros([1, len(new_datetime)])

        #DSSEDTOFW#
        dSSedtoFW = np.zeros([1, len(new_datetime)])

        #DSSEDTOSW#
        dSSedtoSW = np.add(dSedSWdiffusion,dSedSWsus)

        #DSSEDTOS1#
        dSSedtoS1 = np.zeros([1, len(new_datetime)])

        #DSSEDTOS2#
        dSSedtoS2 = np.zeros([1, len(new_datetime)])

        #DSSEDTOS3#
        dSSedtoS3 = np.zeros([1, len(new_datetime)])

        #DSSEDTOFSED#
        dSSedtoFSed = np.zeros([1, len(new_datetime)])

        #DSSEDREMOVAL#
        dSSedremoval = np.add(dSedimentSeaReact,dSedSWbur)

        #DSSEDTODEEPS1#
        dSSedtoDeepS1 = np.zeros([1, len(new_datetime)])

        #DSSEDTODEEPS2#
        dSSedtoDeepS2 = np.zeros([1, len(new_datetime)])

        #DSSEDTODEEPS3#
        dSSedtoDeepS3 = np.zeros([1, len(new_datetime)])



        ###DEEP SOIL1###

        #DDEEPS1TOA#
        dDeepS1toA = np.zeros([1, len(new_datetime)])

        #DDEEPS1TOFW#
        dDeepS1toFW = np.zeros([1, len(new_datetime)])

        #DDEEPS1TOSW#
        dDeepS1toSW = np.zeros([1, len(new_datetime)])

        #DDEEPS1TOS1#
        dDeepS1toS1 = np.zeros([1, len(new_datetime)])

        #DDEEPS1TOS2#
        dDeepS1toS2 = np.zeros([1, len(new_datetime)])

        #DDEEPS1TOS3#
        dDeepS1toS3 = np.zeros([1, len(new_datetime)])

        #DDEEPS1TOFSED#
        dDeepS1toFSed = np.zeros([1, len(new_datetime)])

        #DDEEPS1TOSSED#
        dDeepS1toSSed = np.zeros([1, len(new_datetime)])

        #DDEEPS1REMOVAL#
        dDeepS1removal = dDeepSoilReact1

        #DDEEPS1TODEEPS2
        dDeepS1toDeepS2 = np.zeros([1, len(new_datetime)])

        #DDEEPS1TODEEPS3
        dDeepS1toDeepS3 = np.zeros([1, len(new_datetime)])




        ###DEEP SOIL2###

        #DDEEPS2TOA#
        dDeepS2toA = np.zeros([1, len(new_datetime)])

        #DDEEPS2TOFW#
        dDeepS2toFW = np.zeros([1, len(new_datetime)])

        #DDEEPS2TOSW#
        dDeepS2toSW = np.zeros([1, len(new_datetime)])

        #DDEEPS2TOS1#
        dDeepS2toS1 = np.zeros([1, len(new_datetime)])

        #DDEEPS2TOS2#
        dDeepS2toS2 = np.zeros([1, len(new_datetime)])

        #DDEEPS2TOS3#
        dDeepS2toS3 = np.zeros([1, len(new_datetime)])

        #DDEEPS2TOFSED#
        dDeepS2toFSed = np.zeros([1, len(new_datetime)])

        #DDEEPS2TOSSED#
        dDeepS2toSSed = np.zeros([1, len(new_datetime)])

        #DDEEPS2TODEEPS1
        dDeepS2toDeepS1 = np.zeros([1, len(new_datetime)])

        #DDEEPS2REMOVAL#
        dDeepS2removal = dDeepSoilReact2

        #DDEEPS2TODEEPS3
        dDeepS2toDeepS3 = np.zeros([1, len(new_datetime)])




        ###DEEP SOIL3###

        #DDEEPS3TOA#
        dDeepS3toA = np.zeros([1, len(new_datetime)])

        #DDEEPS3TOFW#
        dDeepS3toFW = np.zeros([1, len(new_datetime)])

        #DDEEPS3TOSW#
        dDeepS3toSW = np.zeros([1, len(new_datetime)])

        #DDEEPS3TOS1#
        dDeepS3toS1 = np.zeros([1, len(new_datetime)])

        #DDEEPS3TOS2#
        dDeepS3toS2 = np.zeros([1, len(new_datetime)])

        #DDEEPS3TOS3#
        dDeepS3toS3 = np.zeros([1, len(new_datetime)])

        #DDEEPS3TOFSED#
        dDeepS3toFSed = np.zeros([1, len(new_datetime)])

        #DDEEPS3TOSSED#
        dDeepS3toSSed = np.zeros([1, len(new_datetime)])

        #DDEEPS3TODEEPS1
        dDeepS3toDeepS1 = np.zeros([1, len(new_datetime)])

        #DDEEPS3TODEEPS2
        dDeepS3toDeepS2 = np.zeros([1, len(new_datetime)])

        #DDEEPS3REMOVAL#
        dDeepS3removal = dDeepSoilReact3



        #RECALCULATE REMOVAL VALUES TO INCLUDE AMOUNTS LOST TO OTHER COMPARTMENTS

        indices = []

        airchoice = compValues[0]
        indices.append(airchoice)

        fwchoice = compValues[1]
        indices.append(fwchoice)

        swchoice = compValues[2]
        indices.append(swchoice)

        s1choice = compValues[3]
        indices.append(s1choice)

        s2choice = compValues[4]
        indices.append(s2choice)

        s3choice = compValues[5]
        indices.append(s3choice)

        fwsedchoice = compValues[6]
        indices.append(fwsedchoice)

        swsedchoice = compValues[7]
        indices.append(swsedchoice)

        ds1choice = compValues[8]
        indices.append(ds1choice)

        ds2choice = compValues[9]
        indices.append(ds2choice)

        ds3choice = compValues[10]
        indices.append(ds3choice)

        indices = np.array(indices)
        matrix_index = np.where(indices > 0)

        r_one = np.vstack((dAremoval,dAtoFW,dAtoSW,dAtoS1,dAtoS2,dAtoS3,dAtoFSed,dAtoSSed,dAtoDeepS1,dAtoDeepS2,dAtoDeepS3))
        new_r_one = []
        if airchoice == 1:
            for i in matrix_index:
                rows = r_one[i]
                for val in rows:
                    new_r_one.append(val)
        dAremoval = np.sum(new_r_one, axis=0)
        dAremoval = np.multiply(-1,dAremoval)
        #print dAremoval[0], "dAremoval"

        r_two = np.vstack((dFWtoA,dFWremoval,dFWtoSW,dFWtoS1,dFWtoS2,dFWtoS3,dFWtoFSed,dFWtoSSed,dFWtoDeepS1,dFWtoDeepS2,dFWtoDeepS3))
        new_r_two = []
        if fwchoice == 1:
            for i in matrix_index:
                rows = r_two[i]
                for val in rows:
                    new_r_two.append(val)
            if swchoice == 0:
                new_r_two.append(dFWadvection)
            if fwsedchoice == 0:
                new_r_two.append(dSedFWdep)
        dFWremoval = np.sum(new_r_two, axis=0)
        dFWremoval = np.multiply(-1,dFWremoval)
        #print dFWremoval[0], "dFWremoval"

        r_three = np.vstack((dSWtoA,dSWtoFW,dSWremoval,dSWtoS1,dSWtoS2,dSWtoS3,dSWtoFSed,dSWtoSSed,dSWtoDeepS1,dSWtoDeepS2,dSWtoDeepS3))
        new_r_three = []
        if swchoice == 1:
            for i in matrix_index:
                rows = r_three[i]
                for val in rows:
                    new_r_three.append(val)
            if s1choice == 1 and fwchoice == 0:
                new_r_three.append(dS1toFW)
            if s2choice == 1 and fwchoice == 0:
                new_r_three.append(dS2toFW)
            if s3choice == 1 and fwchoice == 0:
                new_r_three.append(dS3toFW)
            if swsedchoice == 0:
                new_r_three.append(dSedSWdep)
        dSWremoval = np.sum(new_r_three, axis=0)
        dSWremoval = np.multiply(-1,dSWremoval)
        #print "dSWremoval"

        r_four = np.vstack((dS1toA,dS1toFW,dS1toSW,dS1removal,dS1toS2,dS1toS3,dS1toFSed,dS1toSSed,dS1toDeepS1,dS1toDeepS2,dS1toDeepS3))
        new_r_four = []
        if s1choice == 1:
            for i in matrix_index:
                rows = r_four[i]
                for val in rows:
                    new_r_four.append(val)
            if fwchoice == 0:
                new_r_four.append(dS1toFW)
        dS1removal = np.sum(new_r_four, axis=0)
        dS1removal = np.multiply(-1,dS1removal)
        #print dS1removal[0], "dS1removal"

        r_five = np.vstack((dS2toA,dS2toFW,dS2toSW,dS2toS1,dS2removal,dS2toS3,dS2toFSed,dS2toSSed,dS2toDeepS1,dS2toDeepS2,dS2toDeepS3))
        new_r_five = []
        if s2choice == 1:
            for i in matrix_index:
                rows = r_five[i]
                for val in rows:
                    new_r_five.append(val)
            if fwchoice == 0:
                new_r_five.append(dS2toFW)
        dS2removal = np.sum(new_r_five, axis=0)
        dS2removal = np.multiply(-1,dS2removal)
        #print dS2removal[0], "dS2removal"

        r_six = np.vstack((dS3toA,dS3toFW,dS3toSW,dS3toS1,dS3toS2,dS3removal,dS3toFSed,dS3toSSed,dS3toDeepS1,dS3toDeepS2,dS3toDeepS3))
        new_r_six = []
        if s3choice == 1:
            for i in matrix_index:
                rows = r_six[i]
                for val in rows:
                    new_r_six.append(val)
            if fwchoice == 0:
                new_r_six.append(dS3toFW)
        dS3removal = np.sum(new_r_six, axis=0)
        dS3removal = np.multiply(-1,dS3removal)
        #print dS3removal[0], "dS3removal"

        r_seven = np.vstack((dFSedtoA,dFSedtoFW,dFSedtoSW,dFSedtoS1,dFSedtoS2,dFSedtoS3,dFSedremoval,dFSedtoSSed,dFSedtoDeepS1,dFSedtoDeepS2,dFSedtoDeepS3))
        new_r_seven = []
        if fwsedchoice == 1:
            for i in matrix_index:
                rows = r_seven[i]
                for val in rows:
                    new_r_seven.append(val)
            if fwchoice == 0:
                new_r_seven.append(dSedFWsus)
        dFSedremoval = np.sum(new_r_seven, axis=0)
        dFSedremoval = np.multiply(-1,dFSedremoval)
        #print dFSedremoval[0], "dFSedremoval"

        r_eight = np.vstack((dSSedtoA,dSSedtoFW,dSSedtoSW,dSSedtoS1,dSSedtoS2,dSSedtoS3,dSSedtoFSed,dSSedremoval,dSSedtoDeepS1,dSSedtoDeepS2,dSSedtoDeepS3))
        new_r_eight = []
        if swsedchoice == 1:
            for i in matrix_index:
                rows = r_eight[i]
                for val in rows:
                    new_r_eight.append(val)
            if swchoice == 0:
                new_r_eight.append(dSedSWsus)
        dSSedremoval = np.sum(new_r_eight, axis=0)
        dSSedremoval = np.multiply(-1,dSSedremoval)
        #print "dSSedremoval"

        r_nine =  np.vstack((dDeepS1toA,dDeepS1toFW,dDeepS1toSW,dDeepS1toS1,dDeepS1toS2,dDeepS1toS3,dDeepS1toFSed,dDeepS1toSSed,dDeepS1removal,dDeepS1toDeepS2,dDeepS1toDeepS3))
        new_r_nine = []
        if ds1choice == 1:
            for i in matrix_index:
                rows = r_nine[i]
                for val in rows:
                    new_r_nine.append(val)
        dDeepS1removal = np.sum(new_r_nine, axis=0)
        dDeepS1removal = np.multiply(-1,dDeepS1removal)
        #print dDeepS1removal[0], "dDeepS1removal"

        r_ten = np.vstack((dDeepS2toA,dDeepS2toFW,dDeepS2toSW,dDeepS2toS1,dDeepS2toS2,dDeepS2toS3,dDeepS2toFSed,dDeepS2toSSed,dDeepS2toDeepS1,dDeepS2removal,dDeepS2toDeepS3))
        new_r_ten = []
        if ds2choice == 1:
            for i in matrix_index:
                rows = r_ten[i]
                for val in rows:
                    new_r_ten.append(val)
        dDeepS2removal = np.sum(new_r_ten, axis=0)
        dDeepS2removal = np.multiply(-1,dDeepS2removal)
        #print dDeepS2removal[0], "dDeepS2removal"

        r_eleven = np.vstack((dDeepS3toA,dDeepS3toFW,dDeepS3toSW,dDeepS3toS1,dDeepS3toS2,dDeepS3toS3,dDeepS3toFSed,dDeepS3toSSed,dDeepS3toDeepS1,dDeepS3toDeepS2,dDeepS3removal))
        new_r_eleven = []
        if ds3choice == 1:
            for i in matrix_index:
                rows = r_eleven[i]
                for val in rows:
                    new_r_eleven.append(val)
        dDeepS3removal = np.sum(new_r_eleven, axis=0)
        dDeepS3removal = np.multiply(-1,dDeepS3removal)
        #print dDeepS3removal[0], "dDeepS3removal"



        if len(new_r_one) !=0:
            pass
        else:
            dAremoval = np.zeros([1, len(new_datetime)])

            def A_comp(n):
                for val in dAremoval:
                    for i in val:
                        yield i
            dAremoval = np.fromiter(A_comp(1), dtype=float)

        if len(new_r_two) !=0:
            pass
        else:
            dFWremoval = np.zeros([1, len(new_datetime)])

            def FW_comp(n):
                for val in dFWremoval:
                    for i in val:
                        yield i
            dFWremoval = np.fromiter(FW_comp(1), dtype=float)

        if len(new_r_three) !=0:
            pass
        else:
            dSWremoval = np.zeros([1, len(new_datetime)])

            def SW_comp(n):
                for val in dSWremoval:
                    for i in val:
                        yield i
            dSWremoval = np.fromiter(SW_comp(1), dtype=float)

        if len(new_r_four) !=0:
            pass
        else:
            dS1removal = np.zeros([1, len(new_datetime)])

            def S1_comp(n):
                for val in dS1removal:
                    for i in val:
                        yield i
            dS1removal = np.fromiter(S1_comp(1), dtype=float)

        if len(new_r_five) !=0:
            pass
        else:
            dS2removal = np.zeros([1, len(new_datetime)])

            def S2_comp(n):
                for val in dS2removal:
                    for i in val:
                        yield i
            dS2removal = np.fromiter(S2_comp(1), dtype=float)

        if len(new_r_six) !=0:
            pass
        else:
            dS3removal = np.zeros([1, len(new_datetime)])

            def S3_comp(n):
                for val in dS3removal:
                    for i in val:
                        yield i
            dS3removal = np.fromiter(S3_comp(1), dtype=float)

        if len(new_r_seven) !=0:
            pass
        else:
            dFSedremoval = np.zeros([1, len(new_datetime)])

            def FSed_comp(n):
                for val in dFSedremoval:
                    for i in val:
                        yield i
            dFSedremoval = np.fromiter(FSed_comp(1), dtype=float)

        if len(new_r_eight) !=0:
            pass
        else:
            dSSedremoval = np.zeros([1, len(new_datetime)])

            def SSed_comp(n):
                for val in dSSedremoval:
                    for i in val:
                        yield i
            dSSedremoval = np.fromiter(SSed_comp(1), dtype=float)

        if len(new_r_nine) !=0:
            pass
        else:
            dDeepS1removal = np.zeros([1, len(new_datetime)])

            def DeepS1_comp(n):
                for val in dDeepS1removal:
                    for i in val:
                        yield i
            dDeepS1removal = np.fromiter(DeepS1_comp(1), dtype=float)

        if len(new_r_ten) !=0:
            pass
        else:
            dDeepS2removal = np.zeros([1, len(new_datetime)])

            def DeepS2_comp(n):
                for val in dDeepS2removal:
                    for i in val:
                        yield i
            dDeepS2removal = np.fromiter(DeepS2_comp(1), dtype=float)

        if len(new_r_eleven) !=0:
            pass
        else:
            dDeepS3removal = np.zeros([1, len(new_datetime)])

            def DeepS3_comp(n):
                for val in dDeepS3removal:
                    for i in val:
                        yield i
            dDeepS3removal = np.fromiter(DeepS3_comp(1), dtype=float)




        #DAREMOVAL#
        factor = np.add(dAremoval,dAtoFW)
        factor2 = np.add(dAtoSW,dAtoS1)
        factor3 = np.add(dAtoS2,dAtoS3)
        factor4 = np.add(dAtoFSed,dAtoSSed)
        factor5 = np.add(dAtoDeepS1,dAtoDeepS2)
        factor6 = np.add(dAtoDeepS3,factor5)
        factor7 = np.add(factor,factor2)
        factor8 = np.add(factor3,factor4)
        factor9 = np.add(factor7,factor8)
        factor10 = np.add(factor6,factor9)
        #dAremoval = np.multiply(-1,factor10)


        #DFWREMOVAL#
        factor = np.add(dFWremoval,dFWtoA)
        factor2 = np.add(dFWtoSW,dFWtoS1)
        factor3 = np.add(dFWtoS2,dFWtoS3)
        factor4 = np.add(dFWtoFSed,dFWtoSSed)
        factor5 = np.add(dFWtoDeepS1,dFWtoDeepS2)
        factor6 = np.add(dFWtoDeepS3,factor5)
        factor7 = np.add(factor,factor2)
        factor8 = np.add(factor3,factor4)
        factor9 = np.add(factor7,factor8)
        factor10 = np.add(factor6,factor9)
        #dFWremoval = np.multiply(-1,factor10)

        #DSWREMOVAL#
        factor = np.add(dSWremoval,dSWtoA)
        factor2 = np.add(dSWtoFW,dSWtoS1)
        factor3 = np.add(dSWtoS2,dSWtoS3)
        factor4 = np.add(dSWtoFSed,dSWtoSSed)
        factor5 = np.add(dSWtoDeepS1,dSWtoDeepS2)
        factor6 = np.add(dSWtoDeepS3,factor5)
        factor7 = np.add(factor,factor2)
        factor8 = np.add(factor3,factor4)
        factor9 = np.add(factor7,factor8)
        factor10 = np.add(factor6,factor9)
        #dSWremoval = np.multiply(-1,factor10)

        #DS1REMOVAL#
        factor = np.add(dS1removal,dS1toA)
        factor2 = np.add(dS1toFW,dS1toSW)
        factor3 = np.add(dS1toS2,dS1toS3)
        factor4 = np.add(dS1toFSed,dS1toSSed)
        factor5 = np.add(dS1toDeepS1,dS1toDeepS2)
        factor6 = np.add(dS1toDeepS3,factor5)
        factor7 = np.add(factor,factor2)
        factor8 = np.add(factor3,factor4)
        factor9 = np.add(factor7,factor8)
        factor10 = np.add(factor6,factor9)
        #dS1removal = np.multiply(-1,factor10)

        #DS2REMOVAL#
        factor = np.add(dS2removal,dS2toA)
        factor2 = np.add(dS2toFW,dS2toSW)
        factor3 = np.add(dS2toS1,dS2toS3)
        factor4 = np.add(dS2toFSed,dS2toSSed)
        factor5 = np.add(dS2toDeepS1,dS2toDeepS2)
        factor6 = np.add(dS2toDeepS3,factor5)
        factor7 = np.add(factor,factor2)
        factor8 = np.add(factor3,factor4)
        factor9 = np.add(factor7,factor8)
        factor10 = np.add(factor6,factor9)
        #dS2removal = np.multiply(-1,factor10)

        #DS3REMOVAL#
        factor = np.add(dS3removal,dS3toA)
        factor2 = np.add(dS3toFW,dS3toSW)
        factor3 = np.add(dS3toS1,dS3toS2)
        factor4 = np.add(dS3toFSed,dS3toSSed)
        factor5 = np.add(dS3toDeepS1,dS3toDeepS2)
        factor6 = np.add(dS3toDeepS3,factor5)
        factor7 = np.add(factor,factor2)
        factor8 = np.add(factor3,factor4)
        factor9 = np.add(factor7,factor8)
        factor10 = np.add(factor6,factor9)
        #dS3removal = np.multiply(-1,factor10)

        #DFSEDREMOVAL#
        factor = np.add(dFSedremoval,dFSedtoA)
        factor2 = np.add(dFSedtoFW,dFSedtoSW)
        factor3 = np.add(dFSedtoS1,dFSedtoS2)
        factor4 = np.add(dFSedtoS3,dFSedtoSSed)
        factor5 = np.add(dFSedtoDeepS1,dFSedtoDeepS2)
        factor6 = np.add(dFSedtoDeepS3,factor5)
        factor7 = np.add(factor,factor2)
        factor8 = np.add(factor3,factor4)
        factor9 = np.add(factor7,factor8)
        factor10 = np.add(factor6,factor9)
        #dFSedremoval = np.multiply(-1,factor10)

        #DSSEDREMOVAL#
        factor = np.add(dSSedremoval,dSSedtoA)
        factor2 = np.add(dSSedtoFW,dSSedtoSW)
        factor3 = np.add(dSSedtoS1,dSSedtoS2)
        factor4 = np.add(dSSedtoS3,dSSedtoFSed)
        factor5 = np.add(dSSedtoDeepS1,dSSedtoDeepS2)
        factor6 = np.add(dSSedtoDeepS3,factor5)
        factor7 = np.add(factor,factor2)
        factor8 = np.add(factor3,factor4)
        factor9 = np.add(factor7,factor8)
        factor10 = np.add(factor6,factor9)
        #dSSedremoval = np.multiply(-1,factor10)

        #DDEEPS1REMOVAL#
        factor = np.add(dDeepS1removal,dDeepS1toA)
        factor2 = np.add(dDeepS1toFW,dDeepS1toSW)
        factor3 = np.add(dDeepS1toS1,dDeepS1toS2)
        factor4 = np.add(dDeepS1toS3,dDeepS1toFSed)
        factor5 = np.add(dDeepS1toSSed,dDeepS1toDeepS2)
        factor6 = np.add(dDeepS1toDeepS3,factor5)
        factor7 = np.add(factor,factor2)
        factor8 = np.add(factor3,factor4)
        factor9 = np.add(factor7,factor8)
        factor10 = np.add(factor6,factor9)
        #dDeepS1removal = np.multiply(-1,factor10)

        #DDEEPS2REMOVAL#
        factor = np.add(dDeepS2removal,dDeepS2toA)
        factor2 = np.add(dDeepS2toFW,dDeepS2toSW)
        factor3 = np.add(dDeepS2toS1,dDeepS2toS2)
        factor4 = np.add(dDeepS2toS3,dDeepS2toFSed)
        factor5 = np.add(dDeepS2toSSed,dDeepS2toDeepS1)
        factor6 = np.add(dDeepS2toDeepS3,factor5)
        factor7 = np.add(factor,factor2)
        factor8 = np.add(factor3,factor4)
        factor9 = np.add(factor7,factor8)
        factor10 = np.add(factor6,factor9)
        #dDeepS2removal = np.multiply(-1,factor10)

        #DDEEP32REMOVAL#
        factor = np.add(dDeepS3removal,dDeepS3toA)
        factor2 = np.add(dDeepS3toFW,dDeepS3toSW)
        factor3 = np.add(dDeepS3toS1,dDeepS3toS2)
        factor4 = np.add(dDeepS3toS3,dDeepS3toFSed)
        factor5 = np.add(dDeepS3toSSed,dDeepS3toDeepS1)
        factor6 = np.add(dDeepS3toDeepS2,factor5)
        factor7 = np.add(factor,factor2)
        factor8 = np.add(factor3,factor4)
        factor9 = np.add(factor7,factor8)
        factor10 = np.add(factor6,factor9)
        #dDeepS3removal = np.multiply(-1,factor10)



        #print "#############################"

        days = len(new_datetime)
        #print days, "days"

        bg0 = np.array([bgConcAir, bgConcFW, bgConcSW, bgConcSoil1, bgConcSoil2, bgConcSoil3, bgConcFWsed, bgConcSWsed, bgConcSoil1, bgConcSoil2, bgConcSoil3])

        zAir = zAir[0]
        zWaterFresh = zWaterFresh[0]
        zWaterSea = zWaterSea[0]
        zSoil1 = zSoil1[0]
        zSoil2 = zSoil2[0]
        zSoil3 = zSoil3[0]
        zSedimentFresh = zSedimentFresh[0]
        zSedimentSea = zSedimentSea[0]


        ##### SELECT COMPARTMENTS #####

        dmat_store = []
        dmatrix = []
        indices = []

        airchoice = compValues[0]
        indices.append(airchoice)

        fwchoice = compValues[1]
        indices.append(fwchoice)

        swchoice = compValues[2]
        indices.append(swchoice)

        s1choice = compValues[3]
        indices.append(s1choice)

        s2choice = compValues[4]
        indices.append(s2choice)

        s3choice = compValues[5]
        indices.append(s3choice)

        fwsedchoice = compValues[6]
        indices.append(fwsedchoice)

        swsedchoice = compValues[7]
        indices.append(swsedchoice)

        ds1choice = compValues[8]
        indices.append(ds1choice)

        ds2choice = compValues[9]
        indices.append(ds2choice)

        ds3choice = compValues[10]
        indices.append(ds3choice)

        time1 = datetime.datetime.now()
        #print time1, "1"

        indices = np.array(indices)
        matrix_index = np.where(indices > 0)

        bg0 = bg0[matrix_index]



        fresults = []
        f_calcs = []
        fresults.append(bg0)
        for i in range(days):
            index = i
            #print index

            #print "####### d1 #######"

            dAremoval_val = [dAremoval[index]]
            dFWtoA_val = [dFWtoA[index]]
            dSWtoA_val = [dSWtoA[index]]
            dS1toA_val =  [dS1toA[index]]
            dS2toA_val =  [dS2toA[index]]
            dS3toA_val =  [dS3toA[index]]
            dFSedtoA_val = [x[index] for x in dFSedtoA]
            dSSedtoA_val = [x[index] for x in dSSedtoA]
            dDeepS1toA_val = [x[index] for x in dDeepS1toA]
            dDeepS2toA_val = [x[index] for x in dDeepS2toA]
            dDeepS3toA_val = [x[index] for x in dDeepS3toA]


            def d1_func(n):
                d1_matrix = [dAremoval_val, dFWtoA_val, dSWtoA_val, dS1toA_val, dS2toA_val, dS3toA_val, dFSedtoA_val, dSSedtoA_val, dDeepS1toA_val, dDeepS2toA_val, dDeepS3toA_val]
                for val in d1_matrix:
                    for i in val:
                        yield i
            dm1 = np.fromiter(d1_func(1), dtype=float)
            d1 = dm1[matrix_index]


            #print "####### d2 #######"

            dAtoFW_val = [dAtoFW[index]]
            dFWremoval_val = [dFWremoval[index]]
            dSWtoFW_val = [x[index] for x in dSWtoFW]
            dS1toFW_val = [dS1toFW[index]]
            dS2toFW_val = [dS2toFW[index]]
            dS3toFW_val = [dS3toFW[index]]
            dFSedtoFW_val = [dFSedtoFW[index]]
            dSSedtoFW_val = [x[index] for x in dSSedtoFW]
            dDeepS1toFW_val = [x[index] for x in dDeepS1toFW]
            dDeepS2toFW_val = [x[index] for x in dDeepS2toFW]
            dDeepS3toFW_val = [x[index] for x in dDeepS3toFW]


            def d2_func(n):
                d2_matrix = [dAtoFW_val, dFWremoval_val, dSWtoFW_val, dS1toFW_val, dS2toFW_val, dS3toFW_val, dFSedtoFW_val, dSSedtoFW_val, dDeepS1toFW_val, dDeepS2toFW_val, dDeepS3toFW_val]
                for val in d2_matrix:
                    for i in val:
                        yield i
            dm2 = np.fromiter(d2_func(1), dtype=float)
            d2 = dm2[matrix_index]

            #print "####### d3 #######"

            dAtoSW_val = [dAtoSW[index]]
            dFWtoSW_val = [dFWtoSW[index]]
            dSWremoval_val = [dSWremoval[index]]
            dS1toSW_val = [x[index] for x in dS1toSW]
            dS2toSW_val = [x[index] for x in dS2toSW]
            dS3toSW_val = [x[index] for x in dS3toSW]
            dFSedtoSW_val = [x[index] for x in dFSedtoSW]
            dSSedtoSW_val = [dSSedtoSW[index]]
            dDeepS1toSW_val = [x[index] for x in dDeepS1toSW]
            dDeepS2toSW_val = [x[index] for x in dDeepS2toSW]
            dDeepS3toSW_val = [x[index] for x in dDeepS3toSW]

            def d3_func(n):
                d3_matrix = [dAtoSW_val, dFWtoSW_val, dSWremoval_val, dS1toSW_val, dS2toSW_val, dS3toSW_val, dFSedtoSW_val, dSSedtoSW_val, dDeepS1toSW_val, dDeepS2toSW_val, dDeepS3toSW_val]
                for val in d3_matrix:
                    for i in val:
                        yield i
            dm3 = np.fromiter(d3_func(1), dtype=float)
            d3 = dm3[matrix_index]

            #print "####### d4 #######"

            dAtoS1_val = [dAtoS1[index]]
            dFWtoS1_val = [x[index] for x in dFWtoS1]
            dSWtoS1_val = [x[index] for x in dSWtoS1]
            dS1removal_val = [dS1removal[index]]
            dS2toS1_val = [x[index] for x in dS2toS1]
            dS3toS1_val = [x[index] for x in dS3toS1]
            dFSedtoS1_val = [x[index] for x in dFSedtoS1]
            dSSedtoS1_val = [x[index] for x in dSSedtoS1]
            dDeepS1toS1_val = [x[index] for x in dDeepS1toS1]
            dDeepS2toS1_val = [x[index] for x in dDeepS2toS1]
            dDeepS3toS1_val = [x[index] for x in dDeepS3toS1]


            def d4_func(n):
                d4_matrix = [dAtoS1_val, dFWtoS1_val, dSWtoS1_val, dS1removal_val, dS2toS1_val, dS3toS1_val, dFSedtoS1_val, dSSedtoS1_val, dDeepS1toS1_val, dDeepS2toS1_val, dDeepS3toS1_val]
                for val in d4_matrix:
                    for i in val:
                        yield i
            dm4 = np.fromiter(d4_func(1), dtype=float)
            d4 = dm4[matrix_index]

            #print "####### d5 #######"

            dAtoS2_val = [dAtoS2[index]]
            dFWtoS2_val = [x[index] for x in dFWtoS2]
            dSWtoS2_val = [x[index] for x in dSWtoS2]
            dS1toS2_val = [x[index] for x in dS1toS2]
            dS2removal_val = [dS2removal[index]]
            dS3toS2_val = [x[index] for x in dS3toS2]
            dFSedtoS2_val = [x[index] for x in dFSedtoS2]
            dSSedtoS2_val = [x[index] for x in dSSedtoS2]
            dDeepS1toS2_val = [x[index] for x in dDeepS1toS2]
            dDeepS2toS2_val = [x[index] for x in dDeepS2toS2]
            dDeepS3toS2_val = [x[index] for x in dDeepS3toS2]


            def d5_func(n):
                d5_matrix = [dAtoS2_val, dFWtoS2_val, dSWtoS2_val, dS1toS2_val, dS2removal_val, dS3toS2_val, dFSedtoS2_val, dSSedtoS2_val, dDeepS1toS2_val, dDeepS2toS2_val, dDeepS3toS2_val]
                for val in d5_matrix:
                    for i in val:
                        yield i
            dm5 = np.fromiter(d5_func(1), dtype=float)
            d5 = dm5[matrix_index]

            #print "####### d6 #######"

            dAtoS3_val = [dAtoS3[index]]
            dFWtoS3_val = [x[index] for x in dFWtoS3]
            dSWtoS3_val = [x[index] for x in dSWtoS3]
            dS1toS3_val = [x[index] for x in dS1toS3]
            dS2toS3_val = [x[index] for x in dS2toS3]
            dS3removal_val = [dS3removal[index]]
            dFSedtoS3_val = [x[index] for x in dFSedtoS3]
            dSSedtoS3_val = [x[index] for x in dSSedtoS3]
            dDeepS1toS3_val = [x[index] for x in dDeepS1toS3]
            dDeepS2toS3_val = [x[index] for x in dDeepS2toS3]
            dDeepS3toS3_val = [x[index] for x in dDeepS3toS3]

            def d6_func(n):
                d6_matrix = [dAtoS3_val, dFWtoS3_val, dSWtoS3_val, dS1toS3_val, dS2toS3_val, dS3removal_val, dFSedtoS3_val, dSSedtoS3_val, dDeepS1toS3_val, dDeepS2toS3_val, dDeepS3toS3_val]
                for val in d6_matrix:
                    for i in val:
                        yield i
            dm6 = np.fromiter(d6_func(1), dtype=float)
            d6 = dm6[matrix_index]

            #print "####### d7 #######"

            dAtoFSed_val = [x[index] for x in dAtoFSed]
            dFWtoFSed_val =  [dFWtoFSed[index]]
            dSWtoFSed_val = [x[index] for x in dSWtoFSed]
            dS1toFSed_val = [x[index] for x in dS1toFSed]
            dS2toFSed_val = [x[index] for x in dS2toFSed]
            dS3toFSed_val = [x[index] for x in dS3toFSed]
            dFSedremoval_val = [dFSedremoval[index]]
            dSSedtoFSed_val = [x[index] for x in dSSedtoFSed]
            dDeepS1toFSed_val = [x[index] for x in dDeepS1toFSed]
            dDeepS2toFSed_val = [x[index] for x in dDeepS2toFSed]
            dDeepS3toFSed_val = [x[index] for x in dDeepS3toFSed]

            def d7_func(n):
                d7_matrix = [dAtoFSed_val, dFWtoFSed_val, dSWtoFSed_val, dS1toFSed_val, dS2toFSed_val, dS3toFSed_val, dFSedremoval_val, dSSedtoFSed_val, dDeepS1toFSed_val, dDeepS2toFSed_val, dDeepS3toFSed_val]
                for val in d7_matrix:
                    for i in val:
                        yield i
            dm7 = np.fromiter(d7_func(1), dtype=float)
            d7 = dm7[matrix_index]

            #print "####### d8 #######"

            dAtoSSed_val = [x[index] for x in dAtoSSed]
            dFWtoSSed_val = [x[index] for x in dFWtoSSed]
            dSWtoSSed_val = [dSWtoSSed[index]]
            dS1toSSed_val = [x[index] for x in dS1toSSed]
            dS2toSSed_val = [x[index] for x in dS2toSSed]
            dS3toSSed_val = [x[index] for x in dS3toSSed]
            dFSedtoSSed_val = [x[index] for x in dFSedtoSSed]
            dSSedremoval_val = [dSSedremoval[index]]
            dDeepS1toSSed_val = [x[index] for x in dDeepS1toSSed]
            dDeepS2toSSed_val = [x[index] for x in dDeepS2toSSed]
            dDeepS3toSSed_val = [x[index] for x in dDeepS3toSSed]

            def d8_func(n):
                d8_matrix = [dAtoSSed_val, dFWtoSSed_val, dSWtoSSed_val, dS1toSSed_val, dS2toSSed_val, dS3toSSed_val, dFSedtoSSed_val, dSSedremoval_val, dDeepS1toSSed_val, dDeepS2toSSed_val, dDeepS3toSSed_val]
                for val in d8_matrix:
                    for i in val:
                        yield i
            dm8 = np.fromiter(d8_func(1), dtype=float)
            d8 = dm8[matrix_index]

            #print "####### d9 #######"

            dAtoDeepS1_val = [x[index] for x in dAtoDeepS1]
            dFWtoDeepS1_val = [x[index] for x in dFWtoDeepS1]
            dSWtoDeepS1_val = [x[index] for x in dSWtoDeepS1]
            dS1toDeepS1_val = [dS1toDeepS1[index]]
            dS2toDeepS1_val = [x[index] for x in dS2toDeepS1]
            dS3toDeepS1_val = [x[index] for x in dS3toDeepS1]
            dFSedtoDeepS1_val = [x[index] for x in dFSedtoDeepS1]
            dSSedtoDeepS1_val = [x[index] for x in dSSedtoDeepS1]
            dDeepS1removal_val = [dDeepS1removal[index]]
            dDeepS2toDeepS1_val = [x[index] for x in dDeepS2toDeepS1]
            dDeepS3toDeepS1_val = [x[index] for x in dDeepS3toDeepS1]


            def d9_func(n):
                d9_matrix = [dAtoDeepS1_val, dFWtoDeepS1_val, dSWtoDeepS1_val, dS1toDeepS1_val, dS2toDeepS1_val, dS3toDeepS1_val, dFSedtoDeepS1_val, dSSedtoDeepS1_val, dDeepS1removal_val, dDeepS2toDeepS1_val, dDeepS3toDeepS1_val]
                for val in d9_matrix:
                    for i in val:
                        yield i
            dm9 = np.fromiter(d9_func(1), dtype=float)
            d9 = dm9[matrix_index]

            #print "####### d10 #######"

            dAtoDeepS2_val = [x[index] for x in dAtoDeepS2]
            dFWtoDeepS2_val = [x[index] for x in dFWtoDeepS2]
            dSWtoDeepS2_val = [x[index] for x in dSWtoDeepS2]
            dS1toDeepS2_val = [x[index] for x in dS1toDeepS2]
            dS2toDeepS2_val = [dS2toDeepS2[index]]
            dS3toDeepS2_val = [x[index] for x in dS3toDeepS2]
            dFSedtoDeepS2_val = [x[index] for x in dFSedtoDeepS2]
            dSSedtoDeepS2_val = [x[index] for x in dSSedtoDeepS2]
            dDeepS1toDeepS2_val = [x[index] for x in dDeepS1toDeepS2]
            dDeepS2removal_val = [dDeepS2removal[index]]
            dDeepS3toDeepS2_val = [x[index] for x in dDeepS3toDeepS2]

            def d10_func(n):
                d10_matrix = [dAtoDeepS2_val, dFWtoDeepS2_val, dSWtoDeepS2_val, dS1toDeepS2_val, dS2toDeepS2_val, dS3toDeepS2_val, dFSedtoDeepS2_val, dSSedtoDeepS2_val, dDeepS1toDeepS2_val, dDeepS2removal_val, dDeepS3toDeepS2_val]
                for val in d10_matrix:
                    for i in val:
                        yield i
            dm10 = np.fromiter(d10_func(1), dtype=float)
            d10 = dm10[matrix_index]

            #print "####### d10 #######"

            dAtoDeepS3_val = [x[index] for x in dAtoDeepS3]
            dFWtoDeepS3_val = [x[index] for x in dFWtoDeepS3]
            dSWtoDeepS3_val = [x[index] for x in dSWtoDeepS3]
            dS1toDeepS3_val = [x[index] for x in dS1toDeepS3]
            dS2toDeepS3_val = [x[index] for x in dS2toDeepS3]
            dS3toDeepS3_val = [dS3toDeepS3[index]]
            dFSedtoDeepS3_val = [x[index] for x in dFSedtoDeepS3]
            dSSedtoDeepS3_val = [x[index] for x in dSSedtoDeepS3]
            dDeepS1toDeepS3_val = [x[index] for x in dDeepS1toDeepS3]
            dDeepS2toDeepS3_val = [x[index] for x in dDeepS2toDeepS3]
            dDeepS3removal_val = [dDeepS3removal[index]]

            def d11_func(n):
                d11_matrix = [dAtoDeepS3_val, dFWtoDeepS3_val, dSWtoDeepS3_val, dS1toDeepS3_val, dS2toDeepS3_val, dS3toDeepS3_val, dFSedtoDeepS3_val, dSSedtoDeepS3_val, dDeepS1toDeepS3_val, dDeepS2toDeepS3_val, dDeepS3removal_val]
                for val in d11_matrix:
                    for i in val:
                        yield i
            dm11 = np.fromiter(d11_func(1), dtype=float)
            d11 = dm11[matrix_index]

            #print "####### d11 #######"

            ######## SELECT COMPARTMENTS #######

            if airchoice == 1:
                dmatrix.append(d1)
            if fwchoice == 1:
                dmatrix.append(d2)
            if swchoice == 1:
                dmatrix.append(d3)
            if s1choice == 1:
                dmatrix.append(d4)
            if s2choice == 1:
                dmatrix.append(d5)
            if s3choice == 1:
                dmatrix.append(d6)
            if fwsedchoice == 1:
                dmatrix.append(d7)
            if swsedchoice == 1:
                dmatrix.append(d8)
            if ds1choice == 1:
                dmatrix.append(d9)
            if ds2choice == 1:
                dmatrix.append(d10)
            if ds3choice == 1:
                dmatrix.append(d11)
            dmatrix2 = np.array(dmatrix)
            dmatrix = []




            #print "####### ODE SOLVER #######"


            def ode_solv(t, bg, dmat, releasevec):
                yyy = dmat.dot(bg)
                return yyy + releasevec

            def jac(t, bg, dmat, releasevec):
                return dmat + releasevec

            dmat = np.array([dm1, dm2, dm3, dm4, dm5, dm6, dm7, dm8, dm9, dm10, dm11])

            releasevec = np.array([Arelease[index], FWrelease[index], SWrelease[index], S1release[index], S2release[index], S3release[index],
                          FSedrelease[index], SSedrelease[index], DS1release[index], DS2release[index], DS3release[index]])
            releasevec = releasevec[matrix_index]

            t0 = 0.0
            t1 = 1
            time = len(new_datetime)

            last = fresults[-1]
            soln = ode(ode_solv, jac).set_integrator('vode', method='bdf', order = 5, with_jacobian=True)
            soln.set_initial_value(last, t0)
            soln.set_f_params(dmatrix2, releasevec).set_jac_params(dmatrix2, releasevec)
            bg = soln.integrate(t1)
            #print index, index, index, index
            fresults.append(bg)
            f_calcs.append(bg)




        ######### DATA OUTPUT ##########

        air_fugacity = []
        fw_fugacity = []
        sw_fugacity = []
        soil1_fugacity = []
        soil2_fugacity = []
        soil3_fugacity = []
        fw_sed_fugacity = []
        sw_sed_fugacity = []
        deep_soil1_fugacity = []
        deep_soil2_fugacity = []
        deep_soil3_fugacity = []


        test = np.transpose(f_calcs)
        new = np.delete(test, 1, 0)

        if indices[0] == 1:
            air_fugacity = test[0]
            new_test = np.delete(test, 0, 0)
        if indices[1] == 1:
            fw_fugacity = new_test[0]
            new_test = np.delete(new_test, 0, 0)
        if indices[2] == 1:
            sw_fugacity = new_test[0]
            new_test = np.delete(new_test, 0, 0)
        if indices[3] == 1:
            soil1_fugacity = new_test[0]
            new_test = np.delete(new_test, 0, 0)
        if indices[4] == 1:
            soil2_fugacity = new_test[0]
            new_test = np.delete(new_test, 0, 0)
        if indices[5] == 1:
            soil3_fugacity = new_test[0]
            new_test = np.delete(new_test, 0, 0)
        if indices[6] == 1:
            fw_sed_fugacity = new_test[0]
            new_test = np.delete(new_test, 0, 0)
        if indices[7] == 1:
            sw_sed_fugacity = new_test[0]
            new_test = np.delete(new_test, 0, 0)
        if indices[8] == 1:
            deep_soil1_fugacity = new_test[0]
            new_test = np.delete(new_test, 0, 0)
        if indices[9] == 1:
            deep_soil2_fugacity = new_test[0]
            new_test = np.delete(new_test, 0 ,0)
        if indices[10] == 1:
            deep_soil3_fugacity = new_test[0]
            new_test = np.delete(new_test, 0, 0)




        rowtitles = ['new_datetime']
        rowtitles2 = ['new_datetime']
        rowtitles3 = ['new_datetime']
        data_columns = [(new_datetime)]
        data_columns2 = [(new_datetime)]
        data_columns3 = [(new_datetime)]

        #chem_book = xlwt.Workbook()
        #output_name = "%s_ouput" % (workbook_names)
        #chem_parameters = chem_book.add_sheet('Chem_Parameters')

        #for i, val in enumerate(propCodes):
        #    chem_parameters.write(i, 0, val)
        #for i, val in enumerate(propValues):
        #    chem_parameters.write(i, 1, val)

        #raw_output = chem_book.add_sheet('Raw_output')

        #soil_output = chem_book.add_sheet('Soil_output')


        time2 = datetime.datetime.now()
        #print time2, "2"
        total_time = time2 - time1
        #print "Run time", total_time

        ############################################## NEW OUTPUTS ##############################################

        if len(air_fugacity) !=0:

            aerosol_fugacity = air_fugacity

            # Bulks #
            factor = np.multiply(air_fugacity,zAirSub)
            air_conc = np.multiply(factor,molecular_mass)

            factor = np.multiply(aerosol_fugacity,zAerosolSub)
            aerosol_conc = np.multiply(factor,molecular_mass)

            factor = np.add(airV,aerV)
            air_factor = np.true_divide(airV,factor)

            factor = np.add(airV,aerV)
            aer_factor = np.true_divide(aerV,factor)

            bulk_air_conc = (air_conc * air_factor) + (aerosol_conc * aer_factor)


        if len(fw_sed_fugacity) !=0:

            # Bulks Freshwater #

            fwSusSed_fugacity = fw_fugacity

            fw_sed_water_fugacity = fw_sed_fugacity

            fw_sed_solid_fugacity = fw_sed_fugacity


            factor = np.multiply(fw_fugacity,zWaterSub)
            fw_conc = np.multiply(factor,molecular_mass)

            factor = np.multiply(fwSusSed_fugacity,zSuspendedFreshSub)
            fw_sus_sed_conc = np.multiply(factor,molecular_mass)

            factor = np.multiply(fw_sed_water_fugacity,zSedimentFreshSubWater)
            fw_sed_water = np.multiply(factor,molecular_mass)

            factor = np.multiply(fw_sed_solid_fugacity,zSedimentFreshSubSolid)
            fw_sed_solid = np.multiply(factor,molecular_mass)

        #################### NEW WATER BULKS ####################

        # Freshwater #

            column_factor = freshwV + fwSSedV
            col_water_factor = np.true_divide(freshwV,column_factor)
            col_SusSed_factor = np.true_divide(fwSSedV,column_factor)
            bulk_freshwater_column = ((fw_conc * col_water_factor)
                + (fw_sus_sed_conc * col_SusSed_factor))

            fsedpercWater = 1 - fsedpercSolid
            sedFWVsolid = np.multiply(sedFWV,fsedpercSolid)
            sedFWVwater = np.multiply(sedFWV,fsedpercWater)

            sed_solid_factor = np.true_divide(sedFWVsolid,sedFWV)
            sed_water_factor = np.true_divide(sedFWVwater,sedFWV)
            bulk_freshwater_sediment = ((fw_sed_solid * sed_solid_factor)
                + (fw_sed_water * sed_water_factor))


        if len(sw_sed_fugacity) !=0:

            swSusSed_fugacity = sw_fugacity

            sw_sed_water_fugacity = sw_sed_fugacity

            sw_sed_solid_fugacity = sw_sed_fugacity

            # Bulks Seawater #
            factor = np.multiply(sw_fugacity,zWaterSub)
            sw_conc = np.multiply(factor,molecular_mass)

            factor = np.multiply(swSusSed_fugacity,zSuspendedSeaSub)
            sw_sus_sed_conc = np.multiply(factor,molecular_mass)

            factor = np.multiply(sw_sed_water_fugacity,zSedimentSeaSubWater)
            sw_sed_water = np.multiply(factor,molecular_mass)

            factor = np.multiply(sw_sed_solid_fugacity,zSedimentSeaSubSolid)
            sw_sed_solid = np.multiply(factor,molecular_mass)

            factor = seawV + sedSWV + swSSedV
            sea_factor = np.true_divide(seawV,factor)

            sw_sed_factor = np.true_divide(sedSWV,factor)

            sw_sus_sed_factor = np.true_divide(swSSedV,factor)

            bulk_seawater = ((sw_conc * sea_factor) + (sw_sed_water * sw_sed_factor)
                + (sw_sed_solid * sw_sed_factor)
                + (sw_sus_sed_conc * sw_sus_sed_factor))

        #################### NEW WATER BULKS ####################

        # Seawater #

            column_factor = seawV + swSSedV
            col_water_factor = np.true_divide(seawV,column_factor)
            col_SusSed_factor = np.true_divide(swSSedV,column_factor)
            bulk_seawater_column = ((sw_conc * col_water_factor)
                + (sw_sus_sed_conc * col_SusSed_factor))

            ssedpercWater = 1 - ssedpercSolid
            bulk_seawater_sediment = ((sw_sed_solid * ssedpercSolid)
                + (sw_sed_water * ssedpercWater))


        if len(deep_soil1_fugacity) !=0:

            # Total Urban Soil Calculations #

            soil1_air_fugacity = soil1_fugacity

            soil1_water_fugacity = soil1_fugacity

            soil1_solid_fugacity = soil1_fugacity

            ############################################

            factor = np.multiply(soil1_air_fugacity,zAirSub)
            urban_soil_air = np.multiply(factor,molecular_mass)

            factor = np.multiply(soil1_water_fugacity,zWaterSub)
            urban_soil_water = np.multiply(factor,molecular_mass)

            factor = np.multiply(soil1_solid_fugacity,zSoilSubSolid1)
            urban_soil_solid = np.multiply(factor,molecular_mass)

            factor = np.multiply(deep_soil1_fugacity,zDeepSoil1)
            deep_urban_soil = np.multiply(factor,molecular_mass)

            ############################################

            air_vol = np.multiply(soilV1,soilpercAir1)
            water_vol = np.multiply(soilV1,soilpercWater1)
            solid_vol = np.multiply(soilV1,soilpercSolid1)

            s1_total = air_vol + water_vol + solid_vol + deepsV1

            air_factor = np.true_divide(air_vol,s1_total)
            water_factor = np.true_divide(water_vol,s1_total)
            solid_factor = np.true_divide(solid_vol,s1_total)
            deep1_factor = np.true_divide(deepsV1,s1_total)

            bulk_total_urban_soil = ((urban_soil_air * air_factor)
                + (urban_soil_water * water_factor)
                + (urban_soil_solid * solid_factor)
                + (deep_urban_soil * deep1_factor))

            # Urban Surface Soil Calculations #

            factor = air_vol + water_vol + solid_vol

            sur_air_factor = np.true_divide(air_vol,factor)
            sur_water_factor = np.true_divide(water_vol,factor)
            sur_solid_factor = np.true_divide(solid_vol,factor)

            bulk_urban_surface_soil = ((urban_soil_air * sur_air_factor)
                + (urban_soil_water * sur_water_factor)
                + (urban_soil_solid * sur_solid_factor))

            # Total Natural Soil Calculations #

            soil2_air_fugacity = soil2_fugacity

            soil2_water_fugacity = soil2_fugacity

            soil2_solid_fugacity = soil2_fugacity

            ############################################

            factor = np.multiply(soil2_air_fugacity,zAirSub)
            natural_soil_air = np.multiply(factor,molecular_mass)

            factor = np.multiply(soil2_water_fugacity,zWaterSub)
            natural_soil_water = np.multiply(factor,molecular_mass)

            factor = np.multiply(soil2_solid_fugacity,zSoilSubSolid2)
            natural_soil_solid = np.multiply(factor,molecular_mass)

            factor = np.multiply(deep_soil2_fugacity,zDeepSoil2)
            deep_natural_soil = np.multiply(factor,molecular_mass)

            ############################################

            air_vol = np.multiply(soilV2,soilpercAir2)
            water_vol = np.multiply(soilV2,soilpercWater2)
            solid_vol = np.multiply(soilV2,soilpercSolid2)

            s2_total = air_vol + water_vol + solid_vol + deepsV2

            air_factor = np.true_divide(air_vol,s2_total)
            water_factor = np.true_divide(water_vol,s2_total)
            solid_factor = np.true_divide(solid_vol,s2_total)
            deep2_factor = np.true_divide(deepsV2,s2_total)

            bulk_total_natural_soil = ((natural_soil_air * air_factor)
                + (natural_soil_water * water_factor)
                + (natural_soil_solid * solid_factor)
                + (deep_natural_soil * deep2_factor))

            # Natural Surface Soil Calculations #

            factor = air_vol + water_vol + solid_vol

            sur_air_factor = np.true_divide(air_vol,factor)
            sur_water_factor = np.true_divide(water_vol,factor)
            sur_solid_factor = np.true_divide(solid_vol,factor)

            bulk_natural_surface_soil = ((natural_soil_air * sur_air_factor)
                + (natural_soil_water * sur_water_factor)
                + (natural_soil_solid * sur_solid_factor))


        if len(deep_soil3_fugacity) !=0:

            # Total Agricultural Soil Calculations #

            soil3_air_fugacity = soil3_fugacity

            soil3_water_fugacity = soil3_fugacity

            soil3_solid_fugacity = soil3_fugacity

            ############################################

            factor = np.multiply(soil3_air_fugacity,zAirSub)
            agricultural_soil_air = np.multiply(factor,molecular_mass)

            factor = np.multiply(soil3_water_fugacity,zWaterSub)
            agricultural_soil_water = np.multiply(factor,molecular_mass)

            factor = np.multiply(soil3_solid_fugacity,zSoilSubSolid3)
            agricultural_soil_solid = np.multiply(factor,molecular_mass)

            factor = np.multiply(deep_soil3_fugacity,zDeepSoil3)
            deep_agricultural_soil = np.multiply(factor,molecular_mass)

            ############################################

            air_vol = np.multiply(soilV3,soilpercAir3)
            water_vol = np.multiply(soilV3,soilpercWater3)
            solid_vol = np.multiply(soilV3,soilpercSolid3)

            s3_total = air_vol + water_vol + solid_vol + deepsV3

            air_factor = np.true_divide(air_vol,s3_total)
            water_factor = np.true_divide(water_vol,s3_total)
            solid_factor = np.true_divide(solid_vol,s3_total)
            deep3_factor = np.true_divide(deepsV3,s3_total)

            bulk_total_agricultural_soil = ((agricultural_soil_air * air_factor)
                + (agricultural_soil_water * water_factor)
                + (agricultural_soil_solid * solid_factor)
                + (deep_agricultural_soil * deep3_factor))

            # Agricultural Surface Soil Calculations #

            factor = air_vol + water_vol + solid_vol

            sur_air_factor = np.true_divide(air_vol,factor)
            sur_water_factor = np.true_divide(water_vol,factor)
            sur_solid_factor = np.true_divide(solid_vol,factor)

            bulk_agricultural_surface_soil = ((agricultural_soil_air * sur_air_factor)
                + (agricultural_soil_water * sur_water_factor) +
                (agricultural_soil_solid * sur_solid_factor))

            output = {}
            output["bulk_air_conc"] = {"values": bulk_air_conc}
            output["air_conc"] = {"values": air_conc}
            output["aerosol_conc"] = {"values": aerosol_conc}

            output["bulk_freshwater_column"] = {"values": bulk_freshwater_column}
            output["fw_conc"] = {"values": fw_conc}
            output["fw_sus_sed_conc"] = {"values": fw_sus_sed_conc}
            output["bulk_freshwater_sediment"] = {"values": bulk_freshwater_sediment}
            output["fw_sed_water"] = {"values": fw_sed_water}
            output["fw_sed_solid"] = {"values": fw_sed_solid}

            output["bulk_seawater_column"] = {"values": bulk_seawater_column}
            output["sw_conc"] = {"values": sw_conc}
            output["sw_sus_sed_conc"] = {"values": sw_sus_sed_conc}
            output["bulk_seawater_sediment"] = {"values": bulk_seawater_sediment}
            output["sw_sed_water"] = {"values": sw_sed_water}
            output["sw_sed_solid"] = {"values": sw_sed_solid}

            output["bulk_total_urban_soil"] = {"values": bulk_total_urban_soil}
            output["bulk_urban_surface_soil"] = {"values": bulk_urban_surface_soil}
            output["urban_soil_air"] = {"values": urban_soil_air}
            output["urban_soil_water"] = {"values": urban_soil_water}
            output["urban_soil_solid"] = {"values": urban_soil_solid}
            output["deep_urban_soil"] = {"values": deep_urban_soil}

            output["bulk_total_natural_soil"] = {"values": bulk_total_natural_soil}
            output["bulk_natural_surface_soil"] = {"values": bulk_natural_surface_soil}
            output["natural_soil_air"] = {"values": natural_soil_air}
            output["natural_soil_water"] = {"values": natural_soil_water}
            output["natural_soil_solid"] = {"values": natural_soil_solid}
            output["deep_natural_soil"] = {"values": deep_natural_soil}

            output["bulk_total_agricultural_soil"] = {"values": bulk_total_agricultural_soil}
            output["bulk_agricultural_surface_soil"] = {"values": bulk_agricultural_surface_soil}
            output["agricultural_soil_air"] = {"values": agricultural_soil_air}
            output["agricultural_soil_water"] = {"values": agricultural_soil_water}
            output["agricultural_soil_solid"] = {"values": agricultural_soil_solid}
            output["deep_agricultural_soil"] = {"values": deep_agricultural_soil}

        for prop, vals in output.iteritems():
            time_at_equil = vals['values'][365:]
            vals['avg'] = np.mean(time_at_equil)
            vals['values'] = list(vals['values'])

        # add required environment variable for exposure
        # for env_var in ['soilP2']:
        #     self.chem_prop[env_var] = self.env[env_var]

        ft_out = {
            'results': output,
            'chem_prop': self.chem_prop
        }

        return ft_out

    def write_output(self, ft_out):
        chem_book = xlwt.Workbook()

        output_name = "new_output"
        # output_name = ("%s_output_" % (self.env_name) +
        #     datetime.datetime.now().strftime("%b_%d_%y-%H_%M_%S") + ".xls")
        chem_parameters = chem_book.add_sheet('Chem_Parameters')
        raw_output = chem_book.add_sheet('Raw_output')
        average_output = chem_book.add_sheet('Average_output')

        i = 0
        for prop, vals in ft_out['results'].iteritems():
            average_output.write(i, 0, prop)
            if 'avg' in vals.keys():
                average_output.write(i, 1, vals['avg'])
            raw_output.write(0, i, prop)
            for idx, v in enumerate(vals['values']):
                raw_output.write(idx + 1, i, v)
            i += 1

        i = 0
        for prop, val in ft_out['chem_prop'].iteritems():
            chem_parameters.write(i, 0, prop)
            chem_parameters.write(i, 1, val)
            i += 1

        chem_book.save(output_name)
