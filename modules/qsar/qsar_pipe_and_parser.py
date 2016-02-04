import os.path
from chem_spider_api import ChemSpiderAPI
from parse_epi import ParseEpi
from pipes.pipe_send import PipeOut
from pipes.pipe_receive import PipeIn
import inspect

class_directory = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

class QSARpipe:
    def __init__(self):
        self.pipe_client = PipeOut("to_qsar")
        self.directory = class_directory
        # self.pipe_server = PipeIn("to_parser")
        # self.pipe_server.set_callback(self.parse)
        self.results_folder = os.path.join(self.directory, 'results')
        self.smiles_path = os.path.join(self.directory, 'smiles.txt')

    def run(self, smiles=False):
        if smiles:
            # implicitly move cursor to 0 position and truncate
            open(self.smiles_path,"w").close()

            smiles_file = open(self.smiles_path, 'w+')
            smiles_file.write(smiles)
            smiles_file.close()

        self.pipe_client.send("True")

    def parse():
        epi_output = self.results_folder + '/EPI_results.txt'
        chems = ParseEpi.parse(epi_output)
        return chems
