import os
import inspect

script_dir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe()))
)

def get_locations():
    path_array = script_dir.split(os.sep)
    del path_array[-1]
    qsar_dir = (os.sep).join(path_array)

    smiles_location = os.path.join(qsar_dir, 'smiles.txt')
    results_dir = os.path.join(qsar_dir, 'results')
    log_file = os.path.join(qsar_dir, 'logging', 'logging.txt')

    return {
        'smiles': smiles_location,
        'results': results_dir,
        'log': log_file
    }
