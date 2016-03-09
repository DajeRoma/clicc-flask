import math
from exposure_constants import *
import xlrd
import xlwt
import numpy as np
import datetime

class ExposureMod:
    def __init__(self):
        self.arrays = {}
        inputs = {}

    def run_standalone(self, title):
        main_workbook = xlrd.open_workbook(title + ".xls")
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
        chem_col1 = chem_sheet.col_values(0, start_rowx=0, end_rowx=None)
        chem_col2 = chem_sheet.col_values(1, start_rowx=0, end_rowx=None)
        chem_props = {}
        for idx, name in enumerate(chem_col1):
            chem_props[name] = chem_col2[idx]

        inputs = {
        # Concentrations - kg/m^3
            'air':	    ft_out['air_conc'],
            'aerosol':	ft_out['aerosol_conc'],
            'freshwater':	ft_out['fw_conc'],
            'seawater':	ft_out['sw_conc'],
            'agricultural_soil':	ft_out['agricultural_soil_solid'],
            'agricultural_soil_water':	ft_out['agricultural_soil_water'],
        # Densities - kg/m^3
            'densitySoil2':	chem_props['soilP2'],
            'densityAir':	None,
            'densityWater':	None,
        # Misc
            'T': len(ft_out['fw_conc']),
            'p': None,
            'kOctanolWater':chem_props['kOctWater'],
            'kAirWater':	chem_props['kAirWater'],
            'kDegredationInSoil':	chem_props['kDegSoil'],
            'BCF': chem_props['BCF']
        }

        def attempt_float(value):
            try:
                return float(value)
            except:
                return value

        for key, val in inputs.iteritems():
            if isinstance(val, list):
                inputs[key] = map(attempt_float, val)
            else:
                inputs[key] = attempt_float(val)

        results = self.run(inputs)
        self.write_output(results)

    def run(self, inputs={}):
        time1 = datetime.datetime.now()
        if not inputs:
            # running without input will use seed data for testing.
            for key, value in default_inputs.items():
                inputs[key] = value

        inputs['densityAir'] = 1.29
        inputs['densityWater'] = 1000
        inputs['BAF_fish'] = inputs['BCF']
        self.inputs = inputs

        # duration(days)
        if(inputs['T']):
            self.T = int(inputs['T'])
        else:
            self.T = 3653

        # population size(persons)
        if(inputs['p']):
            self.p = int(inputs['p'])
        else:
            self.p = 1

        if self.T == 1:
            self.time_to_equilibrium = 0
        else:
            if 'time_to_equilibrium' in inputs:
                self.time_to_equilibrium = inputs['time_to_equilibrium']
            else:
                self.time_to_equilibrium = 365

        self.import_constants()

        # calculate intermediate values
        itrmd = {}
        itrmd['rDegradationInSoil'] = math.log(2)/(inputs['kDegredationInSoil'])
        itrmd['lambdat'] = 10*(itrmd['rDegradationInSoil'])
        itrmd['RCF'] = min(200, 0.82+0.0303 * inputs['kOctanolWater'] ** 0.77)
        itrmd['BAF_soil_exp'] = inputs['densitySoil2']/self.densityPlant*((0.784*math.exp(-(((math.log10(inputs['kOctanolWater']))-1.78)**2.0)/2.44)*self.Qtrans)/((self.MTC*2*self.LAI)/(0.3+0.65/inputs['kAirWater']+0.015*inputs['kOctanolWater']/inputs['kAirWater'])+self.Vplant*(self.lambdag+itrmd['lambdat'])))
        itrmd['BAF_airp_exp'] = inputs['densityAir']/self.densityPlant*(self.Vd/((self.MTC*2*self.LAI)/(0.3+0.65/inputs['kAirWater']+0.015*inputs['kOctanolWater']/inputs['kAirWater'])+self.Vplant*(self.lambdag+itrmd['lambdat'])))
        itrmd['BAF_airg_exp'] = inputs['densityAir']/self.densityPlant*((self.MTC*2*self.LAI)/((self.MTC*2*self.LAI)/(0.3+0.65/inputs['kAirWater']+0.015*inputs['kOctanolWater']/inputs['kAirWater'])+self.Vplant*(self.lambdag+itrmd['lambdat'])))
        itrmd['BAF_soil_unexp'] = inputs['densitySoil2']/self.densityPlant*(itrmd['RCF']*0.8)

        if math.log10(inputs['kOctanolWater'])>6.5:
            dairy_intermediary = 6.5-8.1
        else:
            if math.log10(inputs['kOctanolWater'])<3:
                dairy_intermediary = 3-8.1
            else:
                dairy_intermediary = math.log10(inputs['kOctanolWater'])-8.1
        itrmd['BTF_dairy'] = 10.0**(dairy_intermediary)
        if math.log10(inputs['kOctanolWater'])>6.5:
            meat_intermediary = 6.5-5.6+math.log10(self.meat_fat/self.meat_veg)
        else:
            if math.log10(inputs['kOctanolWater'])<3:
                meat_intermediary = 3-5.6+math.log10(
                                            self.meat_fat/self.meat_veg
                                          )
            else:
                meat_intermediary = (math.log10(inputs['kOctanolWater'])
                    - 5.6+math.log10(self.meat_fat/self.meat_veg))
        itrmd['BTF_meat'] =	10.0**(meat_intermediary)

        self.intermediates = itrmd

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
                    # create a result field if none exists
                    results[name] = [None]*(self.T-self.time_to_equilibrium)
                    results[name][i-self.time_to_equilibrium]=(value)

        time2 = datetime.datetime.now()
        total_time = time2 - time1
        print total_time
        return results


    def cycle(self, inputs):
        # this method runs once per day over the course of the module time
        inputs = self.inputs
        itrmd = self.intermediates
        results = {}
        results['In_inh'] = np.asarray(inputs['air'])*self.inhal_air*self.T*self.p
        results['In_wat'] = np.asarray(inputs['freshwater'])*self.ing_water*self.T*self.p
        results['In_ingffre'] = np.asarray(inputs['freshwater'])*(inputs['BAF_fish']/1000)*self.ing_fishfre*self.T*self.p
        results['In_ingfmar'] = np.asarray(inputs['seawater'])*(inputs['BAF_fish']/1000)*self.ing_fishmar*self.T*self.p
        results['In_ingexp'] = (np.asarray(inputs['aerosol'])*(itrmd['BAF_airp_exp']/inputs['densityAir'])+np.asarray(inputs['air'])*(itrmd['BAF_airg_exp']/inputs['densityAir'])+np.asarray(inputs['agricultural_soil_water'])*(itrmd['BAF_soil_exp']/inputs['densitySoil2']))*self.ing_exp*self.T*self.p
        results['In_ingunexp'] = np.asarray(inputs['agricultural_soil_water'])*(itrmd['BAF_soil_unexp']/inputs['densitySoil2'])*self.ing_unexp*self.T*self.p
        results['In_inmeat'] = ((np.asarray(inputs['air'])*self.meat_air+(np.asarray(inputs['aerosol'])*(itrmd['BAF_airp_exp']/inputs['densityAir'])+np.asarray(inputs['air'])*(itrmd['BAF_airp_exp']/inputs['densityAir']))*self.meat_veg)+(np.asarray(inputs['freshwater'])*(self.meat_water/inputs['densityWater']))+(np.asarray(inputs['agricultural_soil'])*(self.meat_soil/inputs['densitySoil2'])+np.asarray(inputs['agricultural_soil_water'])*(itrmd['BAF_soil_exp']/inputs['densitySoil2'])*self.meat_veg))*itrmd['BTF_meat']*self.ing_meat*self.T*self.p
        results['In_milk'] =((np.asarray(inputs['air'])*self.dairy_air+(np.asarray(inputs['aerosol'])*(itrmd['BAF_airp_exp']/inputs['densityAir'])+np.asarray(inputs['air'])*(itrmd['BAF_airp_exp']/inputs['densityAir']))*self.dairy_veg)+(np.asarray(inputs['freshwater'])*(self.dairy_water/inputs['densityWater']))+(np.asarray(inputs['agricultural_soil'])*(self.dairy_soil/inputs['densitySoil2'])+np.asarray(inputs['agricultural_soil_water'])*(itrmd['BAF_soil_exp']/inputs['densitySoil2'])*self.dairy_veg))*itrmd['BTF_dairy']*self.ing_dairy*self.T*self.p
        return results


    def import_constants(self):
        # import objects from exposure constants file
        for table in [ingestion_food, ingestion_water, inhalation]:
            for key, value in table.items():
                setattr(self, key, value)

    def write_output(self, output):
        chem_book = xlwt.Workbook()
        output_name = ("output_" +
            datetime.datetime.now().strftime("%b_%d_%y-%H_%M_%S") + ".xls")
        sheet = chem_book.add_sheet('output')

        i = 0
        for prop, vals in output.iteritems():
            sheet.write(0, i, prop)
            print prop, vals[0]
            for idx, val_idx in enumerate(vals['values']):
                sheet.write(idx + 1, i, val_idx)
            i += 1

        chem_book.save(output_name)

if __name__ == "__main__":
    g = ExposureMod()
    output = g.run_standalone("SF_glycerin_beta_output")
