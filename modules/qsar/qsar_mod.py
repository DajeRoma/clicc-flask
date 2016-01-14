import json
from subprocess import Popen
import os.path
import subprocess
from chem_spider_api import ChemSpiderAPI
from parse_epi import ParseEpi
import inspect

filename = inspect.getfile(inspect.currentframe())
if '.py' in filename:
    class_directory = filename.split('/')
    if len(class_directory) == 1:
        class_directory = class_directory[0].split('\\')
        class_directory.remove('qsar_mod.py')
        class_directory = '\\'.join(class_directory)
    else:
        class_directory.remove('qsar_mod.py')
        class_directory = '/'.join(class_directory)

class QSARmod:

    def __init__(self):
        # open config file and create dict from contents
        self.directory = class_directory
        self.smiles_path = self.directory + '/smiles.txt'
        self.script_folder = self.directory + '/batch_files'
        self.results_folder = self.directory + '/results'
        self.default_inputs = self.directory + '/inputs.txt'
        config_file = open(self.directory + '/configuration.txt', 'r')
        self.config = json.loads(config_file.read())
        config_file.close()

        # construct epi suite batch file based on paths from config.txt
        epi_batch_string = ("@echo off\ncall " + self.config['sikuli_cmd'] + " -r "
                            + self.script_folder + '/epi_script.sikuli --args %%*%\nexit')
        epi_batch_file = open(os.path.join(self.script_folder, 'run_epiweb_sikuli.cmd'), 'w+')
        epi_batch_file.write(epi_batch_string)
        epi_batch_file.close()

        # construct TEST batch file based on paths from config.txt
        test_batch_string = ("@echo off\ncall " + self.config['sikuli_cmd'] + " -r "
                            + self.script_folder + '/test_script.sikuli --args %%*%\nexit')
        test_batch_file = open(os.path.join(self.script_folder, '/run_test_sikuli.cmd'), 'w+')
        test_batch_file.write(test_batch_string)
        test_batch_file.close()

        # construct VEGA batch file
        vega_batch_string = ("@echo off\ncall " + self.config['sikuli_cmd'] + " -r "
                            + self.script_folder + '/vega_script.sikuli --args %%*%\nexit')
        vega_batch_file = open(os.path.join(self.script_folder, '/run_vega_sikuli.cmd'), 'w+')
        vega_batch_file.write(vega_batch_string)
        vega_batch_file.close()

    def run(self, file_in=None):
        smiles_path = self.class_directory + '/inputs.txt'

        if self.config['query_chemspider']:
            # generate smiles from inputs. can be smiles, casrn, or common names
            ChemSpiderAPI.generate_smiles_with_chemspider(self.default_inputs, smiles_path)
        # else:
        #     ChemSpiderAPI.update_smiles_with_input_directly(self.default_inputs, smiles_path)

        # execute batch file to run epi suite
        if self.config['run_epi']:
            epi_batch_path = self.script_folder + 'batch_files/run_epiweb_sikuli.cmd'
            e = Popen([epi_batch_path , smiles_path, self.results_folder], cwd=self.script_folder)
            stdout, stderr = e.communicate()

        # execute batch file to run TEST
        if self.config['run_test']:
            test_batch_path = self.script_folder + 'batch_files/run_test_sikuli.cmd'
            t = Popen([test_batch_path, smiles_path, self.results_folder], cwd=self.script_folder)
            stdout, stderr = t.communicate()

        # execute batch file to run VEGA
        if self.config['run_vega']:
            vega_batch_path = self.script_folder + 'batch_files/run_vega_sikuli.cmd'
            v = Popen([vega_batch_path, smiles_path, self.results_folder], cwd=self.script_folder)
            stdout, stderr = v.communicate()

        # not finished
        if self.config['parse_results']:
            if file_in:
                epi_output = file_in
            else:
                epi_output = self.results_folder + '/EPI_results.txt'
            chems = ParseEpi.parse(epi_output)
            return chems
