import json
import os.path
# import subprocess
from subprocess import Popen
from chem_spider_api import ChemSpiderAPI
from parse_epi import epi_parse
import inspect

class_directory = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe()))
)

class QSARmod:
    def __init__(self):
        # define paths
        self.directory = class_directory
        self.logging_file = os.path.join(self.directory, 'logging', 'logging.txt')
        self.smiles_path = os.path.join(self.directory, 'smiles.txt')
        self.batch_folder = os.path.join(self.directory, 'batch_files')
        self.results_folder = os.path.join(self.directory, 'results')
        self.sikuli_scripts = os.path.join(self.directory, 'sikuli_scripts')
        self.default_inputs = os.path.join(self.directory, 'inputs.txt')

        # open config file and create dict from contents
        config_file = open(os.path.join(self.directory, 'configuration.txt'),
                           'r')
        self.config = json.loads(config_file.read())
        config_file.close()

        # construct batch files
        script_list = ["epi_script", "test_script", "vega_script"]
        strings = {}
        for string in (script_list):
            strings[string] = ("@echo off\ncall {0} -r {1} --args %%*%>>log.txt\nexit"
                .format(self.config['sikuli_cmd'],os.path.join(
                                                    self.sikuli_scripts,
                                                    string + '.sikuli'
                                                  )))
        for name, value  in strings.iteritems():
            try:
        		batch_file = open(os.path.join(self.batch_folder,
                                               'run_{0}.cmd'.format(name)),
                                               'w+')
        		batch_file.write(value)
                        batch_file.close()
            except IOError as (errno,strerror):
        		print "I/O error({0}): {1}".format(errno, strerror)

    def run(self, input_hash={}):
        #allow varying input types for testing purposes by using an options hash
        if not input_hash:
            # no arguments = run with seed files
            smiles_path = os.path.join(self.directory, 'test_seeds',
                                       'smiles.txt')
            results_folder = os.path.join(self.directory, 'test_seeds')
        elif 'smiles_in' in input_hash:
            smiles_path = os.path.join(self.directory, 'smiles.txt')
            results_folder = self.results_folder

            # EPI Suite is run in batch mode using a txt file as input, so
            # create a text file of smiles
            smiles_file = open(smiles_path, 'w+')
            smiles_file.write(smiles_in)
            smiles_file.close()

        #Chemspider queries disabled pending SMILES generation issues resolved.
        # if self.config['query_chemspider']:
            # generate smiles from inputs. can be smiles, casrn, or common names
            # ChemSpiderAPI.generate_smiles_with_chemspider(self.default_inputs,
            #                                               smiles_path)
        # else:
        #     ChemSpiderAPI.update_smiles(self.default_inputs, smiles_path)

        # execute batch file to run epi suite, but not if parsing results directly
        if 'smiles_in' in input_hash:
            if self.config['run_epi']:
                epi_batch_path = os.path.join(self.batch_folder,
                                              'run_epiweb_sikuli.cmd')
                try:
                    e = Popen(
                        [epi_batch_path, smiles_path, self.results_folder,
                            self.logging_file],
                        cwd=self.batch_folder,
                        shell=True
                    )
                    stdout, stderr = e.communicate()
                except IOError as (errno,strerror):
            		print "I/O error({0}): {1}".format(errno, strerror)

            # execute batch file to run TEST
            if self.config['run_test']:
                test_batch_path = os.path.join(self.batch_folder,
                                               'run_test_sikuli.cmd')
                try:
                    t = Popen([test_batch_path, smiles_path, self.results_folder],
                              cwd=self.batch_folder)
                    stdout, stderr = t.communicate()
                except IOError as (errno,strerror):
            		print "I/O error({0}): {1}".format(errno, strerror)

            # execute batch file to run VEGA
            if self.config['run_vega']:
                vega_batch_path = os.path.join(self.batch_folder,
                                               'run_vega_sikuli.cmd')
                try:
                    v = Popen([vega_batch_path, smiles_path, self.results_folder],
                              cwd=self.batch_folder)
                    stdout, stderr = v.communicate()
                except IOError as (errno,strerror):
            		print "I/O error({0}): {1}".format(errno, strerror)

        # parse results from EPI Suite
        if self.config['parse_results']:
            if 'file_in' in input_hash:
                epi_output = input_hash['file_in']
            else:
                epi_output = os.path.join(results_folder, 'EPI_results.txt')
            chems = epi_parse(epi_output)
            return chems
