from chemspipy import ChemSpider

cs = ChemSpider('c48d4595-ead2-40e7-85c9-1e5d2a77754c')

def get_smiles(query):
    results = cs.search(query)
    if results:
        smiles = results[0].smiles
        return smiles
    else:
        return None

def generate_smiles(input_path, output_path):
    # generate a smiles txt
    lines = tuple(open(input_path, 'r'))
    smiles = []

    for line in lines:
        # avoid empty lines
        if line:
            # strip extra spaces
            line.strip(' ')
            chem = get_smiles(line)
            if chem:
                smiles.append(chem)

    smiles_text = '\n'.join(smiles)
    smile_file = open(output_path, 'w+')
    smile_file.write(smiles_text)
    smile_file.close
