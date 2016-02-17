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
    'Log Kow (K' : 'kOctWater',
    'Log Koc' : 'kOrgWater',
    'Log Kaw' : 'kAirWater',
    'Log Koa' : 'kAerAir',
    'VP (Pa' : 'vapor_pressure_at_25_C',
    'VP  (exp': 'vapor_pressure_at_25_C',
    'Water Solubility' : 'water_solubility_at_25_C',
    '(BCF ' : 'BCF',
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
    else:
        return None

def find_fugacity_value(stringly):
    return stringly.split()[2]

def parse(input_path):
    # Super ugly as EPI Suite results are a txt file amalgamation of many individual
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
                    if search_for[key] == "BCF":
                        val = float(find_value(line.split('(')[1]))
                        if current_chem[search_for[key]]:
                            print "second val: {0}".format(val)
                            current_chem[search_for[key]] = (current_chem[search_for[key]]
                                    + val)/2.0
                            print "avg: {0}".format(current_chem[search_for[key]])
                        else:
                            print "first val: {0}".format(val)
                            current_chem[search_for[key]] = val
                    else:
                        parsed_value = find_value(line)
                        try:
                            # experimental values come last and will overwrite
                            # if they exist

                            value = float(parsed_value)
                            if value:
                                if search_for[key] == 'Log Koc':
                                    print 'Doing Log Koc stuff'
                                    print current_chem[search_for[key]]
                                    if current_chem[search_for[key]]:
                                        current_chem[search_for[key]] = (current_chem[search_for[key]] + value)/2.0
                                else:
                                    current_chem[search_for[key]] = value
                        except:
                            # catches not integer/float values
                            current_chem[search_for[key]] = 'Error'
        else:
            for key in dict.keys(search_fugacity):
                if key in line:
                    current_chem[search_fugacity[key]] = float(find_fugacity_value(line))

    # append final chemical as it wont reach first loop
    chemicals.append(current_chem)

    # deloggify values
    for chem in chemicals:
        for log_value in ['kOctWater','kOrgWater','kAirWater','kAerAir']:
            if log_value != None:
                try:
                    print "{0} {1}: {2}".format(chem['smiles'],
                        log_value, chem[log_value])
                    chem[log_value] = 10.0**chem[log_value]
                    print "{0} {1}: {2}".format(chem['smiles'],
                        log_value, chem[log_value])
                except:
                    chem[log_value] = "Error"
    return chemicals
