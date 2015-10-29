import random

def run(smiles):
    print 'running modules'
    # LCI: Lifecycle Inventory
    # PRD: Production
    # FAT: Fate and Transport
    # TXC: Toxicity
    # SCR: Scarcity
    lci = LCIrun(smiles)
    print 'completed LCI'
    prd = PRDrun(smiles)
    print 'completed PRD'
    rls = RLSrun(smiles)
    print 'completed RLS'
    fat = FATrun(prd)
    print 'completed FAT'
    txc = TXCrun(fat)
    print 'completed TXC'
    scr = SCRrun(smiles)
    print 'completed SCR'

    results = {
        'SMILES': str(smiles),
        'results': [lci, prd, rls, fat, txc, scr]
    }

    print 'results compiled'
    return results

def LCIrun(smiles):
    print 'running LCI'
    #smiles -> final
    lci = random.randint(0,1000)
    results = {
        'property': 'Life Cycle Inventory Result',
        'result': lci
    }
    return results

def PRDrun(smiles):
    #smiles -> F&T
    results = {
        'property': 'Production Result',
        'result': random.randint(0,1000),
    }
    return results

def FATrun(smiles):
    #PRD -> TXC
    results = {
        'property': 'Fate and Transport Result',
        'result': random.randint(0,1000),
    }
    return results

def RLSrun(smiles):
    #smiles -> final
    results = {
        'property': 'Release Result',
        'result': random.randint(0,1000),
    }
    return results

def TXCrun(smiles):
    #FAT -> final
    results = {
        'property': 'Toxicity Result',
        'result': random.randint(0,1000),
    }
    return results

def SCRrun(smiles):
    #smiles -> final
    results = {
        'property': 'Scarcity Result',
        'result': random.randint(0,1000),
    }
    return results
