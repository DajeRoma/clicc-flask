#!/usr/bin/env python
import xlrd
import numpy as np
import scipy as sp
from scipy import integrate
from scipy.integrate import ode
import matplotlib.pyplot as plt
from xlrd import open_workbook
import matplotlib.pyplot as plt
from datetime import date, time
import datetime
# from astropy.table import Table, Column
# import csv
from math import exp, sqrt
import inspect
import os.path
import copy



class FateAndTransport:
    def __init__(self):
        class_directory = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        self.directory = class_directory

    def run(self, inputs={}):
        time1 = datetime.datetime.now()
        print time1, "1"
        #DETERMINE COMPARTMENT EXISTENCE
        main_workbook = xlrd.open_workbook( self.directory + '/Environment_SF_Organics_PCB_input_new5.xlsx')
        environment_worksheet = main_workbook.sheet_by_name('Environment')
        environment_code = environment_worksheet.col_values(2, start_rowx=2,end_rowx=None)
        environment_value = environment_worksheet.col_values(3, start_rowx=2,end_rowx=None)
        environment_code2 = environment_worksheet.col_values(7, start_rowx=2,end_rowx=None)
        environment_value2 = environment_worksheet.col_values(8, start_rowx=2,end_rowx=None)
        environment_code_final = np.concatenate([environment_code, environment_code2])
        environment_value_final = np.concatenate([environment_value, environment_value2])
        environment = zip(environment_code_final, environment_value_final)

        climate_worksheet = main_workbook.sheet_by_name('Climate')
        climate_month = climate_worksheet.col_values(0, start_rowx=1,end_rowx=None)
        climate_day = climate_worksheet.col_values(1, start_rowx=1,end_rowx=None)
        climate_year = climate_worksheet.col_values(2, start_rowx=1,end_rowx=None)
        climate_precip = climate_worksheet.col_values(3, start_rowx=1,end_rowx=None)
        climate_windspeed = climate_worksheet.col_values(4, start_rowx=1,end_rowx=None)
        climate_flow = climate_worksheet.col_values(5, start_rowx=1,end_rowx=None)
        climate_temp = climate_worksheet.col_values(6, start_rowx=1,end_rowx=None)

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


        background_worksheet = main_workbook.sheet_by_name('bgConc')
        compartment_names = background_worksheet.col_values(1, start_rowx=2,end_rowx=None)
        code = background_worksheet.col_values(2, start_rowx=2,end_rowx=None)
        compartment_values = background_worksheet.col_values(3, start_rowx=2,end_rowx=None)
        background = zip(compartment_names, code, compartment_values)


        chemProp_worksheet = main_workbook.sheet_by_name('chemProp')
        propCodes = chemProp_worksheet.col_values(1, start_rowx=2,end_rowx=None)
        propValues = chemProp_worksheet.col_values(2, start_rowx=2,end_rowx=None)
        chem_Prop = zip(propCodes, propValues)

        comp_worksheet = main_workbook.sheet_by_name('Compartments')
        compCodes = comp_worksheet.col_values(1, start_rowx=1,end_rowx=None)
        compValues = comp_worksheet.col_values(2, start_rowx=1,end_rowx=None)
        comp_existence = zip(compCodes,compValues)

        visc_worksheet = main_workbook.sheet_by_name('Viscosities')
        visc_temp = visc_worksheet.col_values(0, start_rowx=1,end_rowx=None)
        visc_vals = visc_worksheet.col_values(1, start_rowx=1,end_rowx=None)
        viscosities = zip(visc_temp, visc_vals)

        #BEGIN LOADING INPUTS

        ##########CHEMICAL PROPERTIES##########
        if inputs:
            for a, b in inputs[0].iteritems():
                if a == 'kOctWater':
                    kOctanolWater = float(b)
                if a == 'kOrgWater':
                    kOrganicWater = float(b)
                if a == 'kAirWater':
                    kAirWater = float(b)
                if a == 'kAerAir':
                    kAerosolAir = float(b)
                if a == 'kDegAir':
                    kDegredationInAir = float(b)/.693
                    kDegredationInAir = np.true_divide(1,kDegredationInAir)
                    kDegredationInAir = np.multiply(kDegredationInAir,24)
                if a == 'kDegWater':
                    kDegredationInWater = float(b)/.693
                    kDegredationInWater = np.true_divide(1,kDegredationInWater)
                    kDegredationInWater = np.multiply(kDegredationInWater,24)
                if a == 'kDegSoil':
                    kDegredationInSoil = float(b)/.693
                    kDegredationInSoil = np.true_divide(1,kDegredationInSoil)
                    kDegredationInSoil = np.multiply(kDegredationInSoil,24)
                if a == 'kDegSed':
                    kDegredationInSediment = float(b)/.693
                    kDegredationInSediment = np.true_divide(1,kDegredationInSediment)
                    kDegredationInSediment = np.multiply(kDegredationInSediment,24)
                if a == 'kDegAero':
                    if b:
                        kDegredationInAerosol = float(b)/.693
                        kDegredationInAerosol = np.true_divide(1,kDegredationInAerosol)
                        kDegredationInAerosol = np.multiply(kDegredationInAerosol,24)
                    else:
                        kDegredationInAerosol = kDegredationInSediment
                if a == 'kDegSSed':
                    if b:
                        kDegredationInSSediment = float(b)/.693
                        kDegredationInSSediment = np.true_divide(1,kDegredationInSSediment)
                        kDegredationInSSediment = np.multiply(kDegredationInSSediment,24)
                    else:
                        kDegredationInSSediment = kDegredationInSediment
                if a == 'MW':
                    molecular_mass = float(b)
                if a == 'MD':
                    molecular_density = float(b)

        else:
            for a, b in chem_Prop:
                if a == 'kOctWater':
                    kOctanolWater = float(b)
                if a == 'kOrgWater':
                    kOrganicWater = float(b)
                if a == 'kAirWater':
                    kAirWater = float(b)
                if a == 'kAerAir':
                    kAerosolAir = float(b)
                if a == 'kDegAir':
                    kDegredationInAir = float(b)/.693
                    kDegredationInAir = np.true_divide(1,kDegredationInAir)
                    kDegredationInAir = np.multiply(kDegredationInAir,24)
                if a == 'kDegWater':
                    kDegredationInWater = float(b)/.693
                    kDegredationInWater = np.true_divide(1,kDegredationInWater)
                    kDegredationInWater = np.multiply(kDegredationInWater,24)
                if a == 'kDegSoil':
                    kDegredationInSoil = float(b)/.693
                    kDegredationInSoil = np.true_divide(1,kDegredationInSoil)
                    kDegredationInSoil = np.multiply(kDegredationInSoil,24)
                if a == 'kDegSed':
                    kDegredationInSediment = float(b)/.693
                    kDegredationInSediment = np.true_divide(1,kDegredationInSediment)
                    kDegredationInSediment = np.multiply(kDegredationInSediment,24)
                if a == 'kDegAero':
                    kDegredationInAerosol = float(b)/.693
                    kDegredationInAerosol = np.true_divide(1,kDegredationInAerosol)
                    kDegredationInAerosol = np.multiply(kDegredationInAerosol,24)
                if a == 'kDegSSed':
                    kDegredationInSSediment = float(b)/.693
                    kDegredationInSSediment = np.true_divide(1,kDegredationInSSediment)
                    kDegredationInSSediment = np.multiply(kDegredationInSSediment,24)
                if a == 'MW':
                    molecular_mass = float(b)
                if a == 'MD':
                    molecular_density = float(b)
        molecular_volume = np.true_divide(molecular_mass,molecular_density)
        molecular_mass = np.true_divide(molecular_mass,1000)



        ##########CLIMATE PROPERTIES##########
        airTemp = climate_temp
        airSpeed = [x for x in climate_windspeed]
        airSpeed = np.multiply(airSpeed,86400)
        fwSpeed = [x for x in climate_flow]
        fwSpeed = np.multiply(fwSpeed,86400)
        swSpeed = np.zeros([1, len(new_datetime)])
        precipR = [x for x in climate_precip]
        precipR = np.multiply(precipR,0.6095996708)

        ##########LIPID CONENT FOR BIOTA##########
        for a, b in environment:
            if a == 'biotaFWlc':
                biotaFWlc = float(b)
            if a == 'biotaSWlc':
                biotaSWlc = float(b)
            if a == 'biotaFSedlc':
                biotaFSedlc = float(b)
            if a == 'biotaSSedlc':
                biotaSSedlc = float(b)
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
        airA = area
        waterA = np.multiply(area,waterPerc)

        factor = np.subtract(1,seawPerc)
        factor2 = np.multiply(factor,freshwD)
        factor3 = np.multiply(seawD,seawPerc)
        waterD = np.add(factor2,factor3)

        seawA = np.multiply(waterA,seawPerc)
        freshwA = np.multiply(waterA,(1-seawPerc))

        soilA = np.subtract(area,waterA)
        soilA1 = np.multiply(soilA,soilPerc1)
        soilA2 = np.multiply(soilA,soilPerc2)
        soilA3 = np.multiply(soilA,soilPerc3)

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

        temp = [round(x) for x in airTemp]
        neg_temp = np.arange(-30,0)

        s = len(neg_temp)

        neg_visc = []

        for i in range(s):
            val = neg_temp[i]
            new_visc = 1.7884*(exp(-0.029*val))
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
            visclist.append(viscnew)

        radius = (0.75*(c_vol/pi))**(0.33333)

        airMD = []
        awMTCair = []
        waterMD = []
        awMTCwater = []
        sedfwMTC = []
        sedswMTC = []

        for i in range(s):

        #AIR DIFFUSIVITY#
            airmd = 2.35*molecular_volume**(-0.73)
            airMD.append(airmd)
            awmtcair = 0.0292*((((airSpeed[i]/24))**0.78)*((sqrt(waterA))**-0.11)*(((visclist[i]/1000)/(airP*(airMD[i]/10000)))**-0.67))
            awMTCair.append(awmtcair)

        #WATER DIFFUSIVITY#
            fric_velocity = 0.01*(airSpeed[i]/86400)*((6.1+(0.63*(airSpeed[i]/86400)))**0.5)
            watermd = ((R*(273.15+airTemp[i]))/(6*pi*N*(visclist[i]/1e9)*radius))
            waterMD.append(watermd)
            awmtcwater = 1e-6 + 1.44e-2*(fric_velocity*(fric_velocity**2.2)*(((visclist[i]/1000)/(waterP*(molecular_density/10000))))**-0.5);
            awMTCwater.append(awmtcwater)


        #FW MTC#
            Rp = (1- fsedpercSolid)**(1/3)
            K23 = fsedOC*kOrganicWater
            Rc = 1 + ((densityFWSedSolid/1000)/(1-fsedpercSolid))*K23
            D_sed1 = waterMD[i]*0.36/(Rc*Rp)
            D_sed_dis1 = D_sed1*2
            sedfwmtc = D_sed1/sqrt(D_sed_dis1)
            sedfwMTC.append(sedfwmtc)

        #SW MTC#
            Rp = (1-ssedpercSolid)**(-0.333333);
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
            SWvelocity = (climate_flow[i])/seawA;
            uf = sqrt(Cd)*FWvelocity;
            us = sqrt(Cd)*SWvelocity;

        asMTC1 = (airMD[i]*0.36*24)/0.005
        asMTC2 = (airMD[i]*0.36*24)/0.005
        asMTC3 = (airMD[i]*0.36*24)/0.005

        airMD = airMD[i]*0.36*24
        waterMD = waterMD[i]*0.36*24
        awMTCair = awMTCair[i]*24
        awMTCwater = awMTCwater[i]*3600*24
        sedfwMTC = sedfwMTC[i]*24
        sedswMTC = sedswMTC[i]*24

        for a, b in environment:
            if a == 'soilpathlen':
                soilpathlen = float(b)

        ##########AEROSOL DEPOSITION RATE##########
        for a, b in environment:
            if a == 'aerDepR':
                aerDepR = float(b)
            if a == 'precipScavR':
                precipScavR = float(b)
            if a == 'leachR':
                leachR = float(b)
            if a == 'soilRunS':
                soilRunS = float(b)
            if a == 'soilRunW':
                soilRunW = float(b)
            if a == 'freshssDepR':
                freshssDepR = float(b)
            if a == 'seassDepR':
                seassDepR = float(b)
            if a == 'freshssSusR':
                freshssSusR = float(b)
            if a == 'seassSusR':
                seassSusR = float(b)
            if a == 'freshssBurR':
                freshssBurR = float(b)
            if a == 'seassBurR':
                seassBurR = float(b)

        ##########COMPARTMENT FLOWS##########
        airrestime = 20
        waterrestime = 4400
        sedrestime = 4400000

        for a, b in environment:
            if a == 'airrestime':
                airrestime = float(b)
            if a == 'waterrestime':
                waterrestime = float(b)
            if a == 'sedrestime':
                sedrestime = float(b)

        aerosolflow = np.true_divide(aerV,airrestime)

        SSedFWflow = np.true_divide(fwSSedV,waterrestime)
        SSedSWflow = np.true_divide(swSSedV,waterrestime)

        sedFWflow = np.true_divide(sedFWV,sedrestime)
        sedSWflow = np.true_divide(sedSWV,sedrestime)


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

        #ZBIOTAFRESHSUB#
        zBiotaFreshSub = np.multiply(biotaFWlc,zOctanolSub)

        #ZBIOTASEASUB#
        zBiotaSeaSub = np.multiply(biotaSWlc,zOctanolSub)

        #ZBIOTAFSEDSUB#
        zBiotaFSedSub = np.multiply(biotaFSedlc,zOctanolSub)

        #ZBIOTASSEDSUB#
        zBiotaSSedSub = np.multiply(biotaSSedlc,zOctanolSub)

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

        #ZSOILPARTICLESUB#
        factor = np.multiply(kOrganicWater,soilOC1)
        factor2 = np.multiply(factor,densitySolidSoil1)
        factor3 = np.true_divide(factor2,1000)
        zSoilParticleSub = np.multiply(factor3,zWaterSub)

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
        factor = np.multiply(fwSSedV,kDegredationInSSediment)
        dFreshSSedReact = np.multiply(factor,zSuspendedFreshSub)

        #DWATERSEAREACT#
        factor = np.multiply(seawV,kDegredationInWater)
        dWaterSeaReact = np.multiply(factor,zWaterSea)

        #DSEASSEDREACT#
        factor = np.multiply(swSSedV,kDegredationInSSediment)
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
        dAiradvection = np.multiply(airSpeed,zAir)

        #DAEROSOLADVECTION#
        dAerosoladvection = np.multiply(aerosolflow,zAerosolSub)

        #DFWADVECTION#
        dFWadvection = np.multiply(fwSpeed,zWaterFresh)

        #DSWADVECTION#
        dSWadvection = np.multiply(swSpeed,zWaterSea)

        #DFWSEDADVECTION#
        dFWSedadvection = np.multiply(sedFWflow,zSedimentFresh)

        #DFWSSEDADVECTION#
        dFWSSedadvection = np.multiply(SSedFWflow,zSuspendedFreshSub)

        #DSWSEDADVECTION#
        dSWSedadvection = np.multiply(sedSWflow,zSedimentSea)

        #DSWSSEDADVECTION#
        dSWSSedadvection = np.multiply(SSedSWflow,zSuspendedSeaSub)


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
        dSFWrunS1 = np.multiply(factor,zSoilParticleSub)

        #DSFWRUNS2#
        factor = np.multiply(soilA2,soilRunS)
        dSFWrunS2 = np.multiply(factor,zSoilParticleSub)

        #DSFWRUNS3#
        factor = np.multiply(soilA3,soilRunS)
        dSFWrunS3 = np.multiply(factor,zSoilParticleSub)

        #DSFWRUNW1#
        factor = np.multiply(soilA1,soilRunW)
        dSFWrunW1 = np.multiply(factor,zWaterSub)

        #DSFWRUNW2#
        factor = np.multiply(soilA2,soilRunW)
        dSFWrunW2 = np.multiply(factor,zWaterSub)

        #DSFWRUNW3#
        factor = np.multiply(soilA3,soilRunW)
        dSFWrunW3 = np.multiply(factor,zWaterSub)

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

        #DSEDFWDIFFUSION#
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

        #DFSEDTOA#
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
        dSSedtoFW = np.add(dSedSWdiffusion,dSedSWsus)

        #DSSEDTOSW#
        dSSedtoSW = np.zeros([1, len(new_datetime)])

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
        dAremoval = np.multiply(-1,factor10)

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
        dFWremoval = np.multiply(-1,factor10)

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
        dSWremoval = np.multiply(-1,factor10)

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
        dS1removal = np.multiply(-1,factor10)

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
        dS2removal = np.multiply(-1,factor10)

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
        dS3removal = np.multiply(-1,factor10)

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
        dFSedremoval = np.multiply(-1,factor10)

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
        dSSedremoval = np.multiply(-1,factor10)

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
        dDeepS1removal = np.multiply(-1,factor10)

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
        dDeepS2removal = np.multiply(-1,factor10)

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
        dDeepS3removal = np.multiply(-1,factor10)


        days = len(new_datetime)

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

        indices = np.array(indices)
        matrix_index = np.where(indices > 0)

        bg0 = bg0[matrix_index]


        fresults = []
        f_calcs = []
        fresults.append(bg0)
        for i in range(days):
            index = i

            dAremoval_val =  [x[index] for x in dAremoval]
            dFWtoA_val =  [dFWtoA[index]]
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


            dAtoFW_val = [dAtoFW[index]]
            dFWremoval_val = [x[index] for x in dFWremoval]
            dSWtoFW_val = [x[index] for x in dSWtoFW]
            dS1toFW_val = [dS1toFW[index]]
            dS2toFW_val = [dS2toFW[index]]
            dS3toFW_val = [dS3toFW[index]]
            dFSedtoFW_val = [dFSedtoFW[index]]
            dSSedtoFW_val = [dSSedtoFW[index]]
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

            dAtoSW_val = [dAtoSW[index]]
            dFWtoSW_val = [dFWtoSW[index]]
            dSWremoval_val = [x[index] for x in dSWremoval]
            dS1toSW_val = [x[index] for x in dS1toSW]
            dS2toSW_val = [x[index] for x in dS2toSW]
            dS3toSW_val = [x[index] for x in dS3toSW]
            dFSedtoSW_val = [x[index] for x in dFSedtoSW]
            dSSedtoSW_val = [x[index] for x in dSSedtoSW]
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

            dAtoS1_val = [dAtoS1[index]]
            dFWtoS1_val = [x[index] for x in dFWtoS1]
            dSWtoS1_val = [x[index] for x in dSWtoS1]
            dS1removal_val = [x[index] for x in dS1removal]
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


            dAtoS2_val = [dAtoS2[index]]
            dFWtoS2_val = [x[index] for x in dFWtoS2]
            dSWtoS2_val = [x[index] for x in dSWtoS2]
            dS1toS2_val = [x[index] for x in dS1toS2]
            dS2removal_val = [x[index] for x in dS2removal]
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


            dAtoS3_val = [dAtoS3[index]]
            dFWtoS3_val = [x[index] for x in dFWtoS3]
            dSWtoS3_val = [x[index] for x in dSWtoS3]
            dS1toS3_val = [x[index] for x in dS1toS3]
            dS2toS3_val = [x[index] for x in dS2toS3]
            dS3removal_val = [x[index] for x in dS3removal]
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


            dAtoFSed_val = [x[index] for x in dAtoFSed]
            dFWtoFSed_val =  [dFWtoFSed[index]]
            dSWtoFSed_val = [x[index] for x in dSWtoFSed]
            dS1toFSed_val = [x[index] for x in dS1toFSed]
            dS2toFSed_val = [x[index] for x in dS2toFSed]
            dS3toFSed_val = [x[index] for x in dS3toFSed]
            dFSedremoval_val = [x[index] for x in dFSedremoval]
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


            dAtoSSed_val = [x[index] for x in dAtoSSed]
            dFWtoSSed_val = [x[index] for x in dFWtoSSed]
            dSWtoSSed_val = [dSWtoSSed[index]]
            dS1toSSed_val = [x[index] for x in dS1toSSed]
            dS2toSSed_val = [x[index] for x in dS2toSSed]
            dS3toSSed_val = [x[index] for x in dS3toSSed]
            dFSedtoSSed_val = [x[index] for x in dFSedtoSSed]
            dSSedremoval_val = [x[index] for x in dSSedremoval]
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


            dAtoDeepS1_val = [x[index] for x in dAtoDeepS1]
            dFWtoDeepS1_val = [x[index] for x in dFWtoDeepS1]
            dSWtoDeepS1_val = [x[index] for x in dSWtoDeepS1]
            dS1toDeepS1_val = [dS1toDeepS1[index]]
            dS2toDeepS1_val = [x[index] for x in dS2toDeepS1]
            dS3toDeepS1_val = [x[index] for x in dS3toDeepS1]
            dFSedtoDeepS1_val = [x[index] for x in dFSedtoDeepS1]
            dSSedtoDeepS1_val = [x[index] for x in dSSedtoDeepS1]
            dDeepS1removal_val = [x[index] for x in dDeepS1removal]
            dDeepS2toDeepS1_val = [x[index] for x in dDeepS2toDeepS1]
            dDeepS3toDeepS1_val = [x[index] for x in dDeepS3toDeepS1]


            def d9_func(n):
                d9_matrix = [dAtoDeepS1_val, dFWtoDeepS1_val, dSWtoDeepS1_val, dS1toDeepS1_val, dS2toDeepS1_val, dS3toDeepS1_val, dFSedtoDeepS1_val, dSSedtoDeepS1_val, dDeepS1removal_val, dDeepS2toDeepS1_val, dDeepS3toDeepS1_val]
                for val in d9_matrix:
                    for i in val:
                        yield i
            dm9 = np.fromiter(d9_func(1), dtype=float)
            d9 = dm9[matrix_index]


            dAtoDeepS2_val = [x[index] for x in dAtoDeepS2]
            dFWtoDeepS2_val = [x[index] for x in dFWtoDeepS2]
            dSWtoDeepS2_val = [x[index] for x in dSWtoDeepS2]
            dS1toDeepS2_val = [x[index] for x in dS1toDeepS2]
            dS2toDeepS2_val = [dS2toDeepS2[index]]
            dS3toDeepS2_val = [x[index] for x in dS3toDeepS2]
            dFSedtoDeepS2_val = [x[index] for x in dFSedtoDeepS2]
            dSSedtoDeepS2_val = [x[index] for x in dSSedtoDeepS2]
            dDeepS1toDeepS2_val = [x[index] for x in dDeepS1toDeepS2]
            dDeepS2removal_val = [x[index] for x in dDeepS2removal]
            dDeepS3toDeepS2_val = [x[index] for x in dDeepS3toDeepS2]

            def d10_func(n):
                d10_matrix = [dAtoDeepS2_val, dFWtoDeepS2_val, dSWtoDeepS2_val, dS1toDeepS2_val, dS2toDeepS2_val, dS3toDeepS2_val, dFSedtoDeepS2_val, dSSedtoDeepS2_val, dDeepS1toDeepS2_val, dDeepS2removal_val, dDeepS3toDeepS2_val]
                for val in d10_matrix:
                    for i in val:
                        yield i
            dm10 = np.fromiter(d10_func(1), dtype=float)
            d10 = dm10[matrix_index]


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
            dDeepS3removal_val = [x[index] for x in dDeepS3removal]

            def d11_func(n):
                d11_matrix = [dAtoDeepS3_val, dFWtoDeepS3_val, dSWtoDeepS3_val, dS1toDeepS3_val, dS2toDeepS3_val, dS3toDeepS3_val, dFSedtoDeepS3_val, dSSedtoDeepS3_val, dDeepS1toDeepS3_val, dDeepS2toDeepS3_val, dDeepS3removal_val]
                for val in d11_matrix:
                    for i in val:
                        yield i
            dm11 = np.fromiter(d11_func(1), dtype=float)
            d11 = dm11[matrix_index]

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


        # rowtitles = ['new_datetime']
        # rowtitles2 = ['new_datetime']
        # rowtitles3 = ['new_datetime']
        # data_columns = [(new_datetime)]
        # data_columns2 = [(new_datetime)]
        # data_columns3 = [(new_datetime)]

        rowtitles = []
        rowtitles2 = []
        rowtitles3 = []
        data_columns = []
        data_columns2 = []
        data_columns3 = []

        if len(air_fugacity) !=0:
            air_conc_mole = np.multiply(air_fugacity,zAir)
            air_conc_mass = np.multiply(air_conc_mole,molecular_mass)
            air_mass = np.multiply(air_conc_mass,airV)
            rowtitles.append('air_fugacity')
            rowtitles2.append('air_conc_mole')
            rowtitles3.append('air_conc_mass')
            data_columns.append(air_fugacity)
            data_columns2.append(air_conc_mole)
            data_columns3.append(air_conc_mass)

            aerosol_fugacity = air_fugacity
            aerosol_conc_mole = np.multiply(aerosol_fugacity,zAerosolSub)
            aerosol_conc_mass = np.multiply(aerosol_conc_mole,molecular_mass)
            rowtitles.append('aerosol_fugacity')
            rowtitles2.append('aerosol_conc_mole')
            rowtitles3.append('aerosol_conc_mass')
            data_columns.append(aerosol_fugacity)
            data_columns2.append(aerosol_conc_mole)
            data_columns3.append(aerosol_conc_mass)


        if len(fw_fugacity) !=0:
            fw_conc_mole = np.multiply(fw_fugacity,zWaterFresh)
            fw_conc_mass = np.multiply(fw_conc_mole,molecular_mass)
            fw_mass = np.multiply(fw_conc_mass,freshwV)
            rowtitles.append('fw_fugacity')
            rowtitles2.append('fw_conc_mole')
            rowtitles3.append('fw_conc_mass')
            data_columns.append(fw_fugacity)
            data_columns2.append(fw_conc_mole)
            data_columns3.append(fw_conc_mass)

            fwSusSed_fugacity = fw_fugacity
            fwSusSed_conc_mole = np.multiply(fwSusSed_fugacity,zSuspendedFreshSub)
            fwSusSed_conc_mass = np.multiply(fwSusSed_conc_mole,molecular_mass)
            rowtitles.append('fwSusSed_fugacity')
            rowtitles2.append('fwSusSed_conc_mole')
            rowtitles3.append('fwSusSed_conc_mass')
            data_columns.append(fwSusSed_fugacity)
            data_columns2.append(fwSusSed_conc_mole)
            data_columns3.append(fwSusSed_conc_mass)

        if len(sw_fugacity) !=0:
            sw_conc_mole = np.multiply(sw_fugacity,zWaterSea)
            sw_conc_mass = np.multiply(sw_conc_mole,molecular_mass)
            sw_mass = np.multiply(sw_conc_mass,seawV)
            rowtitles.append('sw_fugacity')
            rowtitles2.append('sw_conc_mole')
            rowtitles3.append('sw_conc_mass')
            data_columns.append(sw_fugacity)
            data_columns2.append(sw_conc_mole)
            data_columns3.append(sw_conc_mass)

            swSusSed_fugacity = sw_fugacity
            swSusSed_conc_mole = np.multiply(swSusSed_fugacity,zSuspendedSeaSub)
            swSusSed_conc_mass = np.multiply(swSusSed_conc_mole,molecular_mass)
            rowtitles.append('swSusSed_fugacity')
            rowtitles2.append('swSusSed_conc_mole')
            rowtitles3.append('swSusSed_conc_mass')
            data_columns.append(swSusSed_fugacity)
            data_columns2.append(swSusSed_conc_mole)
            data_columns3.append(swSusSed_conc_mass)

        if len(soil1_fugacity) !=0:
            soil1_conc_mole = np.multiply(soil1_fugacity,zSoil1)
            soil1_conc_mass = np.multiply(soil1_conc_mole,molecular_mass)
            rowtitles.append('urban_fugacity')
            rowtitles2.append('urban_conc_mole')
            rowtitles3.append('urban_conc_mass')
            data_columns.append(soil1_fugacity)
            data_columns2.append(soil1_conc_mole)
            data_columns3.append(soil1_conc_mass)

            soil1_air_fugacity = soil1_fugacity
            soil1_air_conc_mole = np.multiply(soil1_air_fugacity,zSoilAirSub1)
            soil1_air_conc_mass = np.multiply(soil1_air_conc_mole,molecular_mass)
            rowtitles.append('urban_air_fugacity')
            rowtitles2.append('urban_air_conc_mole')
            rowtitles3.append('urban_air_conc_mass')
            data_columns.append(soil1_air_fugacity)
            data_columns2.append(soil1_air_conc_mole)
            data_columns3.append(soil1_air_conc_mass)

            soil1_water_fugacity = soil1_fugacity
            soil1_water_conc_mole = np.multiply(soil1_water_fugacity,zSoilWaterSub1)
            soil1_water_conc_mass = np.multiply(soil1_water_conc_mole,molecular_mass)
            rowtitles.append('urban_water_fugacity')
            rowtitles2.append('urban_water_conc_mole')
            rowtitles3.append('urban_water_conc_mass')
            data_columns.append(soil1_water_fugacity)
            data_columns2.append(soil1_water_conc_mole)
            data_columns3.append(soil1_water_conc_mass)


            #factor = np.multiply(soilV1,soilpercWater1)
            #soil1_water_mass = np.multiply(factor,soil1_water_conc_mass)

            soil1_solid_fugacity = soil1_fugacity
            soil1_solid_conc_mole = np.multiply(soil1_solid_fugacity,zSoilSubSolid1)
            soil1_solid_conc_mass = np.multiply(soil1_solid_conc_mole,molecular_mass)
            rowtitles.append('urban_solid_fugacity')
            rowtitles2.append('urban_solid_conc_mole')
            rowtitles3.append('urban_solid_conc_mass')
            data_columns.append(soil1_solid_fugacity)
            data_columns2.append(soil1_solid_conc_mole)
            data_columns3.append(soil1_solid_conc_mass)

        if len(soil2_fugacity) !=0:
            soil2_conc_mole = np.multiply(soil2_fugacity,zSoil2)
            soil2_conc_mass = np.multiply(soil2_conc_mole,molecular_mass)
            rowtitles.append('natural_fugacity')
            rowtitles2.append('natural_conc_mole')
            rowtitles3.append('natural_conc_mass')
            data_columns.append(soil2_fugacity)
            data_columns2.append(soil2_conc_mole)
            data_columns3.append(soil2_conc_mass)

            soil2_air_fugacity = soil2_fugacity
            soil2_air_conc_mole = np.multiply(soil2_air_fugacity,zSoilAirSub2)
            soil2_air_conc_mass = np.multiply(soil2_air_conc_mole,molecular_mass)
            rowtitles.append('natural_air_fugacity')
            rowtitles2.append('natural_air_conc_mole')
            rowtitles3.append('natural_air_conc_mass')
            data_columns.append(soil2_air_fugacity)
            data_columns2.append(soil2_air_conc_mole)
            data_columns3.append(soil2_air_conc_mass)

            soil2_water_fugacity = soil2_fugacity
            soil2_water_conc_mole = np.multiply(soil2_water_fugacity,zSoilWaterSub2)
            soil2_water_conc_mass = np.multiply(soil2_water_conc_mole,molecular_mass)
            rowtitles.append('natural_water_fugacity')
            rowtitles2.append('natural_water_conc_mole')
            rowtitles3.append('natural_water_conc_mass')
            data_columns.append(soil2_water_fugacity)
            data_columns2.append(soil2_water_conc_mole)
            data_columns3.append(soil2_water_conc_mass)



            #factor = np.multiply(soilV2,soilpercWater2)
            #soil2_water_mass = np.multiply(factor,soil2_water_conc_mass)

            soil2_solid_fugacity = soil2_fugacity
            soil2_solid_conc_mole = np.multiply(soil2_solid_fugacity,zSoilSubSolid2)
            soil2_solid_conc_mass = np.multiply(soil2_solid_conc_mole,molecular_mass)
            rowtitles.append('natural_solid_fugacity')
            rowtitles2.append('natural_solid_conc_mole')
            rowtitles3.append('natural_solid_conc_mass')
            data_columns.append(soil2_solid_fugacity)
            data_columns2.append(soil2_solid_conc_mole)
            data_columns3.append(soil2_solid_conc_mass)

        if len(soil3_fugacity) !=0:
            soil3_conc_mole = np.multiply(soil3_fugacity,zSoil3)
            soil3_conc_mass = np.multiply(soil3_conc_mole,molecular_mass)
            rowtitles.append('agricultural_fugacity')
            rowtitles2.append('agricultural_conc_mole')
            rowtitles3.append('agricultural_conc_mass')
            data_columns.append(soil3_fugacity)
            data_columns2.append(soil3_conc_mole)
            data_columns3.append(soil3_conc_mass)

            soil3_air_fugacity = soil3_fugacity
            soil3_air_conc_mole = np.multiply(soil3_air_fugacity,zSoilAirSub3)
            soil3_air_conc_mass = np.multiply(soil3_air_conc_mole,molecular_mass)
            rowtitles.append('agricultural_air_fugacity')
            rowtitles2.append('agricultural_air_conc_mole')
            rowtitles3.append('agricultural_air_conc_mass')
            data_columns.append(soil3_air_fugacity)
            data_columns2.append(soil3_air_conc_mole)
            data_columns3.append(soil3_air_conc_mass)

            soil3_water_fugacity = soil3_fugacity
            soil3_water_conc_mole = np.multiply(soil3_water_fugacity,zSoilWaterSub3)
            soil3_water_conc_mass = np.multiply(soil3_water_conc_mole,molecular_mass)
            rowtitles.append('agricultural_water_fugacity')
            rowtitles2.append('agricultural_water_conc_mole')
            rowtitles3.append('agricultural_water_conc_mass')
            data_columns.append(soil3_water_fugacity)
            data_columns2.append(soil3_water_conc_mole)
            data_columns3.append(soil3_water_conc_mass)


            #factor = np.multiply(soilV3,soilpercWater3)
            #soil3_water_mass = np.multiply(factor,soil3_water_conc_mass)

            soil3_solid_fugacity = soil3_fugacity
            soil3_solid_conc_mole = np.multiply(soil3_solid_fugacity,zSoilSubSolid3)
            soil3_solid_conc_mass = np.multiply(soil3_solid_conc_mole,molecular_mass)
            rowtitles.append('agricultural_solid_fugacity')
            rowtitles2.append('agricultural_solid_conc_mole')
            rowtitles3.append('agricultural_solid_conc_mass')
            data_columns.append(soil3_solid_fugacity)
            data_columns2.append(soil3_solid_conc_mole)
            data_columns3.append(soil3_solid_conc_mass)

        if len(fw_sed_fugacity) !=0:
            fw_sed_conc_mole = np.multiply(fw_sed_fugacity,zSedimentFresh)
            fw_sed_conc_mass = np.multiply(fw_sed_conc_mole,molecular_mass)
            rowtitles.append('fw_sed_fugacity')
            rowtitles2.append('fw_sed_conc_mole')
            rowtitles3.append('fw_sed_conc_mass')
            data_columns.append(fw_sed_fugacity)
            data_columns2.append(fw_sed_conc_mole)
            data_columns3.append(fw_sed_conc_mass)

            fw_sed_water_fugacity = fw_sed_fugacity
            fw_sed_water_conc_mole = np.multiply(fw_sed_water_fugacity,zSedimentFreshSubWater)
            fw_sed_water_conc_mass = np.multiply(fw_sed_water_conc_mole,molecular_mass)
            rowtitles.append('fw_sed_water_fugacity')
            rowtitles2.append('fw_sed_water_conc_mole')
            rowtitles3.append('fw_sed_water_conc_mass')
            data_columns.append(fw_sed_water_fugacity)
            data_columns2.append(fw_sed_water_conc_mole)
            data_columns3.append(fw_sed_water_conc_mass)

            fw_sed_solid_fugacity = fw_sed_fugacity
            fw_sed_solid_conc_mole = np.multiply(fw_sed_solid_fugacity,zSedimentFreshSubSolid)
            fw_sed_solid_conc_mass = np.multiply(fw_sed_solid_conc_mole,molecular_mass)
            rowtitles.append('fw_sed_solid_fugacity')
            rowtitles2.append('fw_sed_solid_conc_mole')
            rowtitles3.append('fw_sed_solid_conc_mass')
            data_columns.append(fw_sed_solid_fugacity)
            data_columns2.append(fw_sed_solid_conc_mole)
            data_columns3.append(fw_sed_solid_conc_mass)

        if len(sw_sed_fugacity) !=0:
            sw_sed_conc_mole = np.multiply(sw_sed_fugacity,zSedimentSea)
            sw_sed_conc_mass = np.multiply(sw_sed_conc_mole,molecular_mass)
            rowtitles.append('sw_sed_fugacity')
            rowtitles2.append('sw_sed_conc_mole')
            rowtitles3.append('sw_sed_conc_mass')
            data_columns.append(sw_sed_fugacity)
            data_columns2.append(sw_sed_conc_mole)
            data_columns3.append(sw_sed_conc_mass)

            sw_sed_water_fugacity = sw_sed_fugacity
            sw_sed_water_conc_mole = np.multiply(sw_sed_water_fugacity,zSedimentSeaSubWater)
            sw_sed_water_conc_mass = np.multiply(sw_sed_water_conc_mole,molecular_mass)
            rowtitles.append('sw_sed_water_fugacity')
            rowtitles2.append('sw_sed_water_conc_mole')
            rowtitles3.append('sw_sed_water_conc_mass')
            data_columns.append(sw_sed_water_fugacity)
            data_columns2.append(sw_sed_water_conc_mole)
            data_columns3.append(sw_sed_water_conc_mass)

            sw_sed_solid_fugacity = sw_sed_fugacity
            sw_sed_solid_conc_mole = np.multiply(sw_sed_solid_fugacity,zSedimentSeaSubSolid)
            sw_sed_solid_conc_mass = np.multiply(sw_sed_solid_conc_mole,molecular_mass)
            rowtitles.append('sw_sed_solid_fugacity')
            rowtitles2.append('sw_sed_solid_conc_mole')
            rowtitles3.append('sw_sed_solid_conc_mass')
            data_columns.append(sw_sed_solid_fugacity)
            data_columns2.append(sw_sed_solid_conc_mole)
            data_columns3.append(sw_sed_solid_conc_mass)

        if len(deep_soil1_fugacity) !=0:
            deep_soil1_conc_mole = np.multiply(deep_soil1_fugacity,zDeepSoil1)
            deep_soil1_conc_mass = np.multiply(deep_soil1_conc_mole,molecular_mass)
            rowtitles.append('deep_urban_fugacity')
            rowtitles2.append('deep_urban_conc_mole')
            rowtitles3.append('deep_urban_conc_mass')
            data_columns.append(deep_soil1_fugacity)
            data_columns2.append(deep_soil1_conc_mole)
            data_columns3.append(deep_soil1_conc_mass)

        if len(deep_soil2_fugacity) !=0:
            deep_soil2_conc_mole = np.multiply(deep_soil2_fugacity,zDeepSoil2)
            deep_soil2_conc_mass = np.multiply(deep_soil2_conc_mole,molecular_mass)
            rowtitles.append('deep_natural_fugacity')
            rowtitles2.append('deep_natural_conc_mole')
            rowtitles3.append('deep_natural_conc_mass')
            data_columns.append(deep_soil2_fugacity)
            data_columns2.append(deep_soil2_conc_mole)
            data_columns3.append(deep_soil2_conc_mass)

        if len(deep_soil3_fugacity) !=0:
            deep_soil3_conc_mole = np.multiply(deep_soil3_fugacity,zDeepSoil3)
            deep_soil3_conc_mass = np.multiply(deep_soil3_conc_mole,molecular_mass)
            rowtitles.append('deep_agricultural_fugacity')
            rowtitles2.append('deep_agricultural_conc_mole')
            rowtitles3.append('deep_agricultural_conc_mass')
            data_columns.append(deep_soil3_fugacity)
            data_columns2.append(deep_soil3_conc_mole)
            data_columns3.append(deep_soil3_conc_mass)


        fugacity_results = {}
        for ind, title in enumerate(rowtitles):
            fugacity_results[title] = list(data_columns[ind])
        #
        # T = Table(data_columns, names = rowtitles)
        #
        # T.write('new_fugacity_data.csv',format='csv')

        conc_mole_results = {}
        for ind, title in enumerate(rowtitles2):
            conc_mole_results[title] = list(data_columns2[ind])

        # T2 = Table(data_columns2, names = rowtitles2)
        #
        # T2.write('new_conc_mole_data.csv',format='csv')

        conc_mass_results = {}
        for ind, title in enumerate(rowtitles3):
            conc_mass_results[title] = list(data_columns3[ind])

        # T3 = Table(data_columns3, names = rowtitles3)
        #
        # T3.write('new_conc_mass_data.csv',format='csv')

        time2 = datetime.datetime.now()
        print time2, "2"
        total_time = time2 - time1
        print "Run time", total_time

        exposure_inputs = {
        # Concentrations - kg/m^3
            'c_air':	air_conc_mass,
            'c_aerosol':	aerosol_conc_mass,
            'c_freshwater':	fw_conc_mass,
            'c_seawater':	sw_conc_mass,
            'agricultural_soil':	soil3_conc_mass,
            'agricultural_soil_water':	soil3_water_conc_mass,
        # Densities - kg/m^3
            'densitySoil2':	densitySoil2,
            'densityAir':	None,
            'densityWater':	None,
        # Misc
            'T':	len(new_datetime),
            'p':	None,
            'kOctanolWater':	kOctanolWater,
            'kAirWater':	kAirWater,
            'kDegredationInSoil':	kDegredationInSoil,
        }

        result = {
            'exposure_inputs': exposure_inputs,
            'fat_outputs': {
                'fugacity_results':fugacity_results,
                'new_conc_mole_results': conc_mole_results,
                'new_conc_mass_results': conc_mass_results
            }
        }

        return result
