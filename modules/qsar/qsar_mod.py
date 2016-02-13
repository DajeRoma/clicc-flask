import json
import os
import sys
from subprocess import Popen
from chem_spider_api import ChemSpiderAPI
from parse_epi import epi_parse
import inspect
import csv
import datetime
class_directory = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe()))
)
# import custom exceptions from utils
path_array = class_directory.split(os.sep)
del path_array[-1]
del path_array[-1]
path_array.append("utils")
util_dir = (os.sep).join(path_array)
sys.path.insert(0, util_dir)
from utils import ModuleError
sys.path.pop(0)

class QSARmod:
    def __init__(self):
        # define paths
        self.directory = class_directory
        self.logging_file = os.path.join(self.directory, 'logging', 'logging.txt')
        self.smiles_path = os.path.join(self.directory, 'smiles.txt')
        self.batch_folder = os.path.join(self.directory, 'batch_files')
        self.results_folder = os.path.join(self.directory, 'results')
        self.sikuli_scripts = os.path.join(self.directory, 'sikuli_scripts')
        self.seed_folder = os.path.join(self.directory, 'test_seeds')

        # open config file and create dict from contents
        config_file = open(os.path.join(self.directory, 'configuration.txt'), 'r')
        self.config = json.loads(config_file.read())
        config_file.close()

        # construct batch files
        self.script_list = ["epi_script", "test_script", "test_MD_script", "vega_script"]
        script_strings = {}
        for name in self.script_list:
            script_strings[name] = ("@echo off\ncall {0} -r {1} --args %%*%>>log.txt\nexit"
                .format(self.config['sikuli_cmd'],os.path.join(
                                                    self.sikuli_scripts,
                                                    name + '.sikuli'
                                                  )))
        for name, value  in script_strings.iteritems():
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
        #take {'smiles_in': smiles_value} or {'file_in': results_text_file}
        if not input_hash:
            # no arguments = run with seed files
            smiles_path = os.path.join(self.seed_folder, 'smiles.txt')
            results_folder = self.seed_folder
        elif 'smiles_in' in input_hash:
            smiles_path = os.path.join(self.directory, 'smiles.txt')
            results_folder = self.results_folder
            # EPI Suite is run in batch mode using a txt file as input, so
            # create a text file of smiles
            smiles_file = open(smiles_path, 'w+')
            smiles_file.write(input_hash['smiles_in'])
            smiles_file.close()

        #Chemspider queries disabled pending SMILES generation issues resolved.
        # if self.config['query_chemspider']:
            # generate smiles from inputs. can be smiles, casrn, or common names
            # ChemSpiderAPI.generate_smiles_with_chemspider(self.default_inputs,
            #                                               smiles_path)
        # else:
        #     ChemSpiderAPI.update_smiles(self.default_inputs, smiles_path)

        # execute batch file to run epi suite, but not if parsing results file
        # directly.

        if 'smiles_in' in input_hash:
            for script in self.script_list:
                if self.config['run_{0}'.format(script)]:
                    batch_path = os.path.join(self.batch_folder,
                                              'run_{0}.cmd'.format(script))
                    try:
                        print batch_path
                        e = Popen(
                            [batch_path],
                            cwd=self.batch_folder,
                            shell=True
                        )
                        stdout, stderr = e.communicate()
                    except IOError as (errno,strerror):
                		print "I/O error({0}): {1}".format(errno, strerror)

        # parse results from EPI Suite
        if self.config['parse_results']:
            if 'file_in' in input_hash:
                epi_output = input_hash['file_in']
            else:
                epi_output = os.path.join(results_folder, 'EPI_results.txt')
            chems = epi_parse(epi_output)
            if self.config['log_results']:
                lines = []
                for chem in chems:
                    for key, value in chem.iteritems():
                        lines.append("{0}: {1}".format(key, value))
                lines = "\n".join(lines)
                with open(os.path.join(self.directory, 'logging',
                        datetime.datetime.now().strftime("%b_%d_%y-%H_%M_%S") + '.txt'),
                        "w+") as f:
                        f.write(lines)
            return chems
