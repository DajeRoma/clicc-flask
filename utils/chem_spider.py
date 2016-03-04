
from chemspipy import ChemSpider

cs = ChemSpider('c48d4595-ead2-40e7-85c9-1e5d2a77754c')

def get_chem(query):

    # from chem_spider import get_chem
    # g = get_chem('c52c3c4c(cc5ccc1c2c(cc3)ccc1)cccc4')
    chem = None
    results = cs.search(query)
    if results:
        name = results[0].common_name
        smiles = results[0].smiles
        chem = {
            'name': name,
            'smiles': smiles
        }

    return results[0]
