import json
from subprocess import Popen
import os.path
import subprocess
from chem_spider_api import ChemSpiderAPI
from parse_epi import ParseEpi

class QSARmod:

    def __init__(self):
        # open config file and create dict from contents
        config_file = open('configuration.txt', 'r')
        self.config = json.loads(config_file.read())
        config_file.close()

        # # construct epi suite batch file based on paths from config.txt
        # epi_batch_string = ("@echo off\ncall " + self.config['sikuli_cmd'] + " -r "
        #                     + self.config['script_path'] + 'epi_script.sikuli --args %%*%\nexit')
        # epi_batch_file = open('./batch_files/run_epiweb_sikuli.cmd', 'w+')
        # epi_batch_file.write(epi_batch_string)
        # epi_batch_file.close()
        #
        # # construct TEST batch file based on paths from config.txt
        # test_batch_string = ("@echo off\ncall " + self.config['sikuli_cmd'] + " -r "
        #                     + self.config['script_path'] + 'test_script.sikuli --args %%*%\nexit')
        # test_batch_file = open(os.path.join('./batch_files/', 'run_test_sikuli.cmd'), 'w+')
        # test_batch_file.write(test_batch_string)
        # test_batch_file.close()
        #
        # # construct VEGA batch file
        # vega_batch_string = ("@echo off\ncall " + self.config['sikuli_cmd'] + " -r "
        #                     + self.config['script_path'] + 'vega_script.sikuli --args %%*%\nexit')
        # vega_batch_file = open(os.path.join('./batch_files/', 'run_vega_sikuli.cmd'), 'w+')
        # vega_batch_file.write(vega_batch_string)
        # vega_batch_file.close()

    def run(self, file_in=None):
        smiles_path = self.config['script_path'] + 'smiles.txt'
        if self.config['query_chemspider']:
            # generate smiles from inputs. can be smiles, casrn, or common names
            ChemSpiderAPI.generate_smiles_with_chemspider(self.config['inputs_text'], smiles_path)
        # else:
        #     ChemSpiderAPI.update_smiles_with_input_directly(self.config['inputs_text'], smiles_path)

        # execute batch file to run epi suite
        if self.config['run_epi']:
            epi_batch_path = self.config['script_path'] + 'batch_files/run_epiweb_sikuli.cmd'
            e = Popen([epi_batch_path , smiles_path, self.config['results_folder']], cwd=self.config['script_path'])
            stdout, stderr = e.communicate()

        # execute batch file to run TEST
        if self.config['run_test']:
            test_batch_path = self.config['script_path'] + 'batch_files/run_test_sikuli.cmd'
            t = Popen([test_batch_path, smiles_path, self.config['results_folder']], cwd=self.config['script_path'])
            stdout, stderr = t.communicate()

        # execute batch file to run VEGA
        if self.config['run_vega']:
            vega_batch_path = self.config['script_path'] + 'batch_files/run_vega_sikuli.cmd'
            v = Popen([vega_batch_path, smiles_path, self.config['results_folder']], cwd=self.config['script_path'])
            stdout, stderr = v.communicate()

        # not finished
        if self.config['parse_results']:
            if file_in:
                epi_output = file_in
            else:
                epi_output = self.config['results_folder'] + '\\EPI_results.txt'
            chems = ParseEpi.parse(epi_output)
            return chems
