
from chemspipy import ChemSpider

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
