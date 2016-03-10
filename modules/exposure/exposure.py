import math
from exposure_constants import *
import xlrd
import xlwt
import numpy as np
import datetime

# info for standalone use
stand_alone_input = "SF_glycerin_betaSF_glycerin_betaMar_10_16-10_25_18"

class Exposure:
    def __init__(self):
        self.arrays = {}
        inputs = {}

    def run_standalone(self, title):
        main_workbook = xlrd.open_workbook(title)
        ft_out_sheet = main_workbook.sheet_by_name('Raw_output')
        out_row1 = ft_out_sheet.row_values(0, start_colx=0, end_colx=None)
        out_cols = []
        for idx, name in enumerate(out_row1):
            out_cols.append(ft_out_sheet.col_values(idx, start_rowx=0,
                            end_rowx=None))
        ft_out = {}
        for col in out_cols:
            ft_out[col[0]] = col[1:]

        chem_sheet = main_workbook.sheet_by_name('Chem_Parameters')
        chem_col1 = chem_sheet.col_values(1, start_rowx=0, end_rowx=None)
        chem_col2 = chem_sheet.col_values(2, start_rowx=0, end_rowx=None)
        chem_props = {}
        for idx, name in enumerate(chem_col1):
            chem_props[name] = chem_col2[idx]

        ft_out = {
        # Concentrations - kg/m^3
            'results': {
                'air_conc': {'values': ft_out['air_conc']},
                'aerosol_conc': {'values': ft_out['aerosol_conc']},
                'fw_conc': {'values': ft_out['fw_conc']},
                'sw_conc': {'values': ft_out['sw_conc']},
                'agricultural_soil_solid': {'values': ft_out['agricultural_soil_solid']},
                'agricultural_soil_water': {'values': ft_out['agricultural_soil_water']}
            },
            'chem_props': {
            # Densities - kg/m^3
                'densitySoil2':	chem_props['soilP2'],
                'densityAir': None,
                'densityWater':	None,
            # Misc
                'T': len(ft_out['fw_conc']),
                'p': None,
                'kOctanolWater': chem_props['kOctWater'],
                'kAirWater': chem_props['kAirWater'],
                'kDegredationInSoil':	chem_props['kDegSoil'],
                'BCF': chem_props['BCF']
            },
            'env_props': {

            }
        }

        def attempt_float(value):
            try:
                return float(value)
            except:
                return value

        for key, val in inputs.iteritems():
            # try to convert members of an array of values(strings) to floats.
            # If it fails, probably because target isn't an array, it converts
            # target itself to float itself
            if isinstance(val, list):
                inputs[key] = map(attempt_float, val)
            else:
                inputs[key] = attempt_float(val)

        results = self.run(inputs)
        self.write_output(results)


    def run(self, ft_out={}):
        time1 = datetime.datetime.now()

        # Concentrations - kg/m^3 Big Arrays
        self.arrays = {
            'air': ft_out['results']['air_conc']['values'],
            'aerosol': ft_out['results']['aerosol_conc']['values'],
            'freshwater': ft_out['results']['fw_conc']['values'],
            'seawater': ft_out['results']['sw_conc']['values'],
            'agricultural_soil': ft_out['results']['agricultural_soil_solid']['values'],
            'agricultural_soil_water': ft_out['results']['agricultural_soil_water']['values']
        }

        # Densities - kg/m^3 Constants
        self.densitySoil2 = ft_out['env_props']['soilP2']
        self.densityAir = 1.29
        self.densityWater = 1000

        # Various Others
        self.kOctanolWater = ft_out['chem_props']['kOctWater']
        self.kAirWater = ft_out['chem_props']['kAirWater']
        self.kDegredationInSoil = ft_out['chem_props']['kDegSoil']
        self.BAF_fish = ft_out['chem_props']['BCF']

        # duration(days)
        self.T = len(self.arrays['air'])

        # population size(persons)
        if('p' in ft_out['env_props'] and ft_out['env_props']['p']):
            ft_out['env_props']['p']
        else:
            self.p = 1

        if self.T == 1:
            self.time_to_equilibrium = 0
        else:
            self.time_to_equilibrium = 365

        self.import_variables()

        # calculate intermediate values
        self.rDegradationInSoil = math.log(2)/(self.kDegredationInSoil)
        self.lambdat = 10*(self.rDegradationInSoil)
        self.RCF = min(200,0.82+0.0303*self.kOctanolWater**0.77)
        self.BAF_soil_exp =	self.densitySoil2/self.densityPlant*((0.784*math.exp(-(((math.log10(self.kOctanolWater))-1.78)**2.0)/2.44)*self.Qtrans)/((self.MTC*2*self.LAI)/(0.3+0.65/self.kAirWater+0.015*self.kOctanolWater/self.kAirWater)+self.Vplant*(self.lambdag+self.lambdat)))
        self.BAF_airp_exp =	self.densityAir/self.densityPlant*(self.Vd/((self.MTC*2*self.LAI)/(0.3+0.65/self.kAirWater+0.015*self.kOctanolWater/self.kAirWater)+self.Vplant*(self.lambdag+self.lambdat)))
        self.BAF_airg_exp =	self.densityAir/self.densityPlant*((self.MTC*2*self.LAI)/((self.MTC*2*self.LAI)/(0.3+0.65/self.kAirWater+0.015*self.kOctanolWater/self.kAirWater)+self.Vplant*(self.lambdag+self.lambdat)))
        self.BAF_soil_unexp = self.densitySoil2/self.densityPlant*(self.RCF*0.8)
        if math.log10(self.kOctanolWater)>6.5:
            dairy_intermediary = 6.5-8.1
        else:
            if math.log10(self.kOctanolWater)<3:
                dairy_intermediary = 3-8.1
            else:
                dairy_intermediary = math.log10(self.kOctanolWater)-8.1
        self.BTF_dairy = 10.0**(dairy_intermediary)
        if math.log10(self.kOctanolWater)>6.5:
            meat_intermediary = 6.5-5.6+math.log10(self.meat_fat/self.meat_veg)
        else:
            if math.log10(self.kOctanolWater)<3:
                meat_intermediary = 3-5.6+math.log10(
                                            self.meat_fat/self.meat_veg
                                          )
            else:
                meat_intermediary = (math.log10(self.kOctanolWater)
                    - 5.6+math.log10(self.meat_fat/self.meat_veg))
        self.BTF_meat =	10.0**(meat_intermediary)

        # run cycles over the course of T
        results = {}
        for i in range(self.time_to_equilibrium, self.T):
            cycle_values = {}
            for name, array in self.arrays.iteritems():
                cycle_values[name] = array[i-1]

            cycle_results = self.cycle(cycle_values)
            cycle_results['day'] = i

            for name, value in cycle_results.iteritems():
                if results.has_key(name):
                    results[name][i-self.time_to_equilibrium]=(value)
                else:
                    results[name] = [None]*(self.T-self.time_to_equilibrium)
                    results[name][i-self.time_to_equilibrium]=(value)

        time2 = datetime.datetime.now()
        total_time = time2 - time1
        print total_time
        return results


    def cycle(self, inputs):
        # this method runs once per day over the course of the module time
        results = {}
        results['In_inh'] = inputs['air']*self.inhal_air*self.T*self.p
        results['In_wat'] = inputs['freshwater']*self.ing_water*self.T*self.p
        results['In_ingffre'] = inputs['freshwater']*(self.BAF_fish/1000)*self.ing_fishfre*self.T*self.p
        results['In_ingfmar'] = inputs['seawater']*(self.BAF_fish/1000)*self.ing_fishmar*self.T*self.p
        results['In_ingexp'] = (inputs['aerosol']*(self.BAF_airp_exp/self.densityAir)+inputs['air']*(self.BAF_airg_exp/self.densityAir)+inputs['agricultural_soil_water']*(self.BAF_soil_exp/self.densitySoil2))*self.ing_exp*self.T*self.p
        results['In_ingunexp'] = inputs['agricultural_soil_water']*(self.BAF_soil_unexp/self.densitySoil2)*self.ing_unexp*self.T*self.p
        results['In_inmeat'] = ((inputs['air']*self.meat_air+(inputs['aerosol']*(self.BAF_airp_exp/self.densityAir)+inputs['air']*(self.BAF_airp_exp/self.densityAir))*self.meat_veg)+(inputs['freshwater']*(self.meat_water/self.densityWater))+(inputs['agricultural_soil']*(self.meat_soil/self.densitySoil2)+inputs['agricultural_soil_water']*(self.BAF_soil_exp/self.densitySoil2)*self.meat_veg))*self.BTF_meat*self.ing_meat*self.T*self.p
        results['In_milk'] =((inputs['air']*self.dairy_air+(inputs['aerosol']*(self.BAF_airp_exp/self.densityAir)+inputs['air']*(self.BAF_airp_exp/self.densityAir))*self.dairy_veg)+(inputs['freshwater']*(self.dairy_water/self.densityWater))+(inputs['agricultural_soil']*(self.dairy_soil/self.densitySoil2)+inputs['agricultural_soil_water']*(self.BAF_soil_exp/self.densitySoil2)*self.dairy_veg))*self.BTF_dairy*self.ing_dairy*self.T*self.p
        return results


    def import_variables(self):

        for table in [ingestion_food, ingestion_water, inhalation]:
            for key, value in table.items():
                setattr(self, key, value)

    def write_output(self, output):
        chem_book = xlwt.Workbook()
        output_name = ("exp_output_" +
            datetime.datetime.now().strftime("%b_%d_%y-%H_%M_%S") + ".xls")
        sheet = chem_book.add_sheet('output')

        i = 0
        for prop, vals in output.iteritems():
            sheet.write(0, i, prop)
            for idx, val_idx in enumerate(vals):
                sheet.write(idx + 1, i, val_idx)
            i += 1

        chem_book.save(output_name)

if __name__ == "__main__":
    g = ExposureMod()
    output = g.run_standalone(stand_alone_input)
    g.write_output(output)
