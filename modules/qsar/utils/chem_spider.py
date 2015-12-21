
from chemspipy import ChemSpider

# this should be set to environment variable rather than included in the code
# cs = os.environ.get('CHEM_SPIDER_KEY')
cs = ChemSpider('c48d4595-ead2-40e7-85c9-1e5d2a77754c')

def get_chem(query):
    chem = None
    results = cs.search(query)
    if results:
        name = results[0].common_name
        smiles = results[0].smiles
        chem = {
            'name': name,
            'smiles': smiles
        }

    return chem

def get_smiles(query):
    results = cs.search(query)
    if results:
        smiles = results[0].smiles
        return smiles
    else:
        return None

def generate_smiles_with_chemspider(filename):
    # generate a smiles txt
    lines = tuple(open(filename, 'r'))

    smiles = []

    for line in lines:
        # avoid empty lines
        if line:
            # strip extra spaces
            line.strip(' ')
            chem = chem_spider.get_smiles(line)
            if chem:
                smiles.append(chem)

    smiles_text = '\n'.join(smiles)
    smile_file = open('SMILES.txt', 'w')
    smile_file.write(smiles_text)
    lines.close()
    smile_file.close()

def update_smiles_with_input_directly(filename):
    # generate a smiles txt
    txt = open(filename, 'r').read()

    smile_file = open('SMILES.txt', 'w')
    smile_file.write(txt)
    txt.close()
    smile_file.close()
