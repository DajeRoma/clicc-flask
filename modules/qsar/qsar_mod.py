import json
from subprocess import Popen, PIPE, STDOUT
import os.path
import subprocess
from chem_spider_api import ChemSpiderAPI
from parse_epi import ParseEpi
import inspect

class_directory = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

class QSARmod:
    def __init__(self):
        # open config file and create dict from contents
        self.directory = class_directory
        self.logging_file = os.path.join(self.directory, 'logging', 'logging.txt')
        self.cmd_logging_file = os.path.join(self.directory, 'logging', 'cmd_logging.txt')
        self.smiles_path = os.path.join(self.directory, 'smiles.txt')
        self.batch_folder = os.path.join(self.directory, 'batch_files')
        self.results_folder = os.path.join(self.directory, 'results')
        self.default_inputs = os.path.join(self.directory, 'inputs.txt')
        config_file = open(os.path.join(self.directory, 'configuration.txt'), 'r')
        self.config = json.loads(config_file.read())
        config_file.close()

        # construct epi suite batch file based on paths from config.txt
        epi_batch_string = ("@echo off\ncall " + self.config['sikuli_cmd'] + " -r " + self.directory + '\\epi_script.sikuli --args %%*% >> log.txt\nexit')
    	try:
    		epi_batch_file = open(os.path.join(self.batch_folder, 'run_epiweb_sikuli.cmd'),'w+')
    		epi_batch_file.write(epi_batch_string)
                epi_batch_file.close()

        except IOError as (errno,strerror):
    		print "I/O error({0}): {1}".format(errno, strerror)

            # construct TEST batch file based on paths from config.txt
        # test_batch_string = ("@echo off\ncall " + self.config['sikuli_cmd'] + " -r "
        #                     + self.batch_folder + '/test_script.sikuli --args %%*%\nexit')
        # test_batch_file = open(os.path.join(self.batch_folder, 'run_test_sikuli.cmd'), 'w+')
        # test_batch_file.write(test_batch_string)
        # test_batch_file.close()
        #
        # # construct VEGA batch file
        # vega_batch_string = ("@echo off\ncall " + self.config['sikuli_cmd'] + " -r "
        #                     + self.batch_folder + '/vega_script.sikuli --args %%*%\nexit')
        # vega_batch_file = open(os.path.join(self.batch_folder, 'run_vega_sikuli.cmd'), 'w+')
        # vega_batch_file.write(vega_batch_string)
        # vega_batch_file.close()

    def run(self, file_in=None):
        smiles_path = os.path.join(self.directory, 'smiles.txt')

        if self.config['query_chemspider']:
            # generate smiles from inputs. can be smiles, casrn, or common names
            ChemSpiderAPI.generate_smiles_with_chemspider(self.default_inputs, smiles_path)
        # else:
        #     ChemSpiderAPI.update_smiles_with_input_directly(self.default_inputs, smiles_path)

        # execute batch file to run epi suite
        if self.config['run_epi']:
            epi_batch_path = os.path.join(self.batch_folder, 'run_epiweb_sikuli.cmd')
            try:
                e = Popen([epi_batch_path , smiles_path, self.results_folder, self.logging_file], cwd=self.batch_folder, shell=True)
                stdout = e.communicate()[0]
                return({'path': epi_batch_path, 'batch folder': self.batch_folder, 'stdout': stdout})
            except IOError as (errno,strerror):
        		print "I/O error({0}): {1}".format(errno, strerror)

        # execute batch file to run TEST
        if self.config['run_test']:
            test_batch_path = self.batch_folder + '/run_test_sikuli.cmd'
            t = Popen([test_batch_path, smiles_path, self.results_folder], cwd=self.batch_folder)
            stdout, stderr = t.communicate()

        # execute batch file to run VEGA
        if self.config['run_vega']:
            vega_batch_path = self.batch_folder + '/run_vega_sikuli.cmd'
            v = Popen([vega_batch_path, smiles_path, self.results_folder], cwd=self.batch_folder)
            stdout, stderr = v.communicate()

        # not finished
        if self.config['parse_results']:
            if file_in:
                epi_output = file_in
            else:
                epi_output = self.results_folder + '/EPI_results.txt'
            chems = ParseEpi.parse(epi_output)
            return chems
