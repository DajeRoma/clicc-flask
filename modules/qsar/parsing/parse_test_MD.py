import re

def parse(input_path):
    lines = tuple(open(input_path, 'r'))
    chemicals = [None] * (len(lines) - 2)

    for i, line in enumerate(lines):
        if i not in [0, 1]:
            parts = line.split()
            id_num = int(parts[0])
            values = []
            md_max = None
            md_min = None
            md_avg = None
            for value in parts[2:]:
                if value != 'N/A' and value:
                    val = float(value)
                    if (not md_max) or (val > md_max):
                        md_max = val
                    if (not md_min) or (val < md_min):
                        md_min = val
                    values.append(val)
            try:
                md_avg = sum(values)/float(len(values))
            except:
                if len(values) > 0:
                    md_avg = 'Error'
            chemicals[id_num - 1] = {
                'md_max': md_max,
                'md_min': md_min,
                'md_avg': md_avg
            }

    return chemicals
