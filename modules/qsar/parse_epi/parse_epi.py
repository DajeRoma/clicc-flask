import re

wanted = {
    'smiles': None,
    'molecular_weight': None,
    'kOctanolWater': None,
    'organic_carbon_water_partition_coefficient': None,
    'kAirWater': None,
    'aerosol_air_partition_coefficient': None,
    'vapor_pressure_at_25_C': None,
    'water_solubility_at_25_C': None,
    'degradation_rate_in_air': None,
    'degradation_rate_in_water': None,
    'kDegredationInSoil': None,
    'degradation_rate_in_sediment': None,
    'bioconcentration_factor': None,
}
# BAF_fish

search_for = {
    'MOL WT' : 'molecular_weight',
    'Log Kow (E' : 'kOctanolWater',
    'LogKoc' : 'organic_carbon_water_partition_coefficient',
    'Log Kaw' : 'kAirWater',
    'Log Koa (K' : 'aerosol_air_partition_coefficient',
    'VP (Pa' : 'vapor_pressure_at_25_C',
    'Water Solubility' : 'water_solubility_at_25_C',
    '(BCF' : 'bioconcentration_factor',
}

search_fugacity = {
    'Air    ' : 'degradation_rate_in_air' ,
    'Water    ' : 'degradation_rate_in_water',
    'Soil    ' : 'kDegredationInSoil',
    'Sediment  ' : 'degradation_rate_in_sediment'
}

def find_value(stringly):
    # get a value coming after = or : anywhere in a line with unknown whitespaces
    # regex-starting after a colon get substring that has 1-6 whitespaces and then any number of non-whitespaces.
    value1 = re.search('(?<=:)\s{1,6}(\S*)', stringly)
    # regex- after an = this time. No group function for this :/
    value2 = re.search('(?<==)\s{1,6}(\S*)', stringly)

    valid_search = value1 or value2
    if valid_search:
        return valid_search.group(0).strip()

def find_fugacity_value(stringly):
    return stringly.split()[2]

def parse(input_path):
    if type(input_path) is str:
        print "string"
        lines = tuple(open(input_path, 'r'))
    else:
        lines = tuple(input_path)
        print "file"

    chemicals = []
    current_chem = dict.copy(wanted)
    for line in lines:
        if 'SMILES' in line:
            if current_chem['smiles'] != None:
                chemicals.append(current_chem)
                current_chem = dict.copy(wanted)
            current_chem['smiles'] = find_value(line)
        if any(x in line for x in ['=',':']):
            for key in dict.keys(search_for):
                if key in line:
                    current_chem[search_for[key]] = find_value(line)
        else:
            for key in dict.keys(search_fugacity):
                if key in line:
                    current_chem[search_fugacity[key]] = find_fugacity_value(line)
    chemicals.append(current_chem)
    return chemicals
