import re

# kDegAero and kDegSSed needed
wanted = {
    'smiles': None,
    'MW': None,
    'kOctWater': None,
    'kOrgWater': None,
    'kAirWater': None,
    'kAerAir': None,
    'vapor_pressure_at_25_C': None,
    'water_solubility_at_25_C': None,
    'kDegAir': None,
    'kDegWater': None,
    'kDegSoil': None,
    'kDegSed': None,
    'kDegSSed': None,
    'kDegAero': None,
    'bioconcentration_factor': None,
}
# BAF_fish

search_for = {
    'MOL WT' : 'MW',
    'Log Kow (E' : 'kOctWater',
    'Log Koc' : 'kOrgWater',
    'Log Kaw' : 'kAirWater',
    'Log Koa (K' : 'kAerAir',
    'VP (Pa' : 'vapor_pressure_at_25_C',
    'Water Solubility' : 'water_solubility_at_25_C',
    '(BCF' : 'bioconcentration_factor',
}

search_fugacity = {
    'Air    ' : 'kDegAir' ,
    'Water    ' : 'kDegWater',
    'Soil    ' : 'kDegSoil',
    'Sediment  ' : 'kDegSed'
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
    print type(input_path)
    if type(input_path) is str:
        print "file name string"
        lines = tuple(open(input_path, 'r'))
    elif type(input_path) is unicode:
        print "unicode"
        lines = tuple(input_path.splitlines())
    else:
        print "other"
        lines = tuple(input_path)



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


    for log_value in ['kOctWater','kOrgWater','kAirWater','kAerAir']:
        if current_chem[log_value]:
            current_chem[log_value] = 10.0**float(current_chem[log_value])

    chemicals.append(current_chem)

    return chemicals
