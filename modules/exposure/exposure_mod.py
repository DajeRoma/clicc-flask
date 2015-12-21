import math
from exposure_constants import *

class ExposureMod:
    def run(self, inputs={}):
        if inputs:
            self.properties = {}
            # Concentrations - kg/m^3
            self.properties['air'] = inputs['c_air']
            self.properties['aerosol'] = inputs['c_aerosol']
            self.properties['freshwater'] = inputs['c_freshwater']
            self.properties['seawater'] = inputs['c_seawater']
            self.properties['agricultural_soil'] = inputs['agricultural_soil']
            self.properties['agricultural_soil_water'] = inputs['agricultural_soil_water']
            # Densities - kg/m^3
            self.properties['densitySoil2'] = inputs['densitySoil2']
            self.properties['densityAir'] = 1.29
            self.properties['densityWater'] = 1000
            # duration(days)
            if(inputs[ft_duration]):
                self.properties['T'] = inputs[ft_duration]
            else:
                self.properties['T'] = 3653
            # population size(persons)
            if(inputs[ft_population]):
                self.properties[p] = inputs[ft_population]
            else:
                self.properties[p] = 1
        else:
            # for testing purposes
            self.properties = default_inputs

        self.expand_variables()

        self.lambdat = 10*(self.kDegredationInSoil*3600)*(60*60*24)
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
                meat_intermediary = 3-5.6+math.log10(self.meat_fat/self.meat_veg)
            else:
                meat_intermediary = math.log10(self.kOctanolWater)-5.6+math.log10(self.meat_fat/self.meat_veg)

        self.BTF_meat =	10.0**(meat_intermediary)

        results = {}
        results['In_inh'] = self.air*self.inhal_air*self.T*self.p
        results['In_wat'] = self.freshwater*self.ing_water*self.T*self.p
        results['In_ingffre'] = self.freshwater*(self.BAF_fish/1000)*self.ing_fishfre*self.T*self.p
        results['In_ingfmar'] = self.seawater*(self.BAF_fish/1000)*self.ing_fishmar*self.T*self.p
        results['In_ingexp'] = (self.aerosol*(self.BAF_airp_exp/self.densityAir)+self.air*(self.BAF_airg_exp/self.densityAir)+self.agricultural_soil_water*(self.BAF_soil_exp/self.densitySoil2))*self.ing_exp*self.T*self.p
        results['In_ingunexp'] = self.agricultural_soil_water*(self.BAF_soil_unexp/self.densitySoil2)*self.ing_unexp*self.T*self.p
        results['In_inmeat'] = ((self.air*self.meat_air+(self.aerosol*(self.BAF_airp_exp/self.densityAir)+self.air*(self.BAF_airp_exp/self.densityAir))*self.meat_veg)+(self.freshwater*(self.meat_water/self.densityWater))+(self.agricultural_soil*(self.meat_soil/self.densitySoil2)+self.agricultural_soil_water*(self.BAF_soil_exp/self.densitySoil2)*self.meat_veg))*self.BTF_meat*self.ing_meat*self.T*self.p
        results['In_milk'] =((self.air*self.dairy_air+(self.aerosol*(self.BAF_airp_exp/self.densityAir)+self.air*(self.BAF_airp_exp/self.densityAir))*self.dairy_veg)+(self.freshwater*(self.dairy_water/self.densityWater))+(self.agricultural_soil*(self.dairy_soil/self.densitySoil2)+self.agricultural_soil_water*(self.BAF_soil_exp/self.densitySoil2)*self.dairy_veg))*self.BTF_dairy*self.ing_dairy*self.T*self.p
        
        return results

    def expand_variables(self):
        # expand variables from excel defined dicts to individual object attributes.
        # the only purpose of this is to be able to copy in the excel formulas
        # and references tables easily. does require appending self to each formula value.
        for table in [self.properties, ingestion_food, ingestion_water, inhalation]:
            for key, value in table.items():
                setattr(self, key, value)
