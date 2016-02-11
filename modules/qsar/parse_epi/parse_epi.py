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
    'BCF': None,
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
    '(BCF' : 'BCF',
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
    # Super ugly as EPI Suite results are a txt file amalgamation of many indoividual
    # application outputs, all formatted differently
    lines = tuple(open(input_path, 'r'))

    chemicals = []
    current_chem = dict.copy(wanted)
    for line in lines:
        if 'SMILES' in line:
        #separates by chemical in case of batched input
            if current_chem['smiles'] != None:
                chemicals.append(current_chem)
                current_chem = dict.copy(wanted)
            current_chem['smiles'] = find_value(line)
        if any(x in line for x in ['=',':']):
            for key in dict.keys(search_for):
                if key in line:
                    if key == "BCF":
                        current_chem[search_for[key]] = float(find_value(line.split('(')[1]))
                    else:
                        try:
                            current_chem[search_for[key]] = float(find_value(line))
                        except:
                            current_chem[search_for[key]] = find_value(line)
        else:
            for key in dict.keys(search_fugacity):
                if key in line:
                    current_chem[search_fugacity[key]] = float(find_fugacity_value(line))


    for log_value in ['kOctWater','kOrgWater','kAirWater','kAerAir']:
        if current_chem[log_value]:
            current_chem[log_value] = 10.0**float(current_chem[log_value])

    chemicals.append(current_chem)

    return chemicals
