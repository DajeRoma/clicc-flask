'''
Created on Dec 15, 2015
Call python predict.py -n [NETWORK] -s [SMILEs] -o [OUTPUT FILE]
http://www.tutorialspoint.com/python/python_command_line_arguments.htm

@author: rsong_admin
'''

import sys, getopt
import pandas as pd
import numpy as np
from ANN_Packages.regression import predicting as Predictor

class NetPrediction:

    def __init__(self):
        self.networks = './modules/lcia/nets/CED_new.xml'

        self.trn = self.__readTrn('./modules/lcia/descriptors/trn_data_30.csv')
#         try:
#             opts, args = getopt.getopt(argv,"hn:d:t:",["net=","descs=","trn="])
#         except getopt.GetoptError:
#             print 'predict.py -n [Networks] -d [Descs] -t [TrnData]'
#             sys.exit(2)
#
# #         if len(args) == 0:
# #             print 'Please provide networks, descriptors and training data, use -h for help'
# #             sys.exit(2)
#
#         for opt, arg in opts:
#             if opt == '-h':
#                 print 'predict.py -n <network> -s <SMILEs>'
#                 sys.exit()
#             elif opt in ("-n", "--net"):
#                 self.networks = arg
#             elif opt in ("-d", "--descs"):
#                 self.descs = self._readDescs(arg)
#             elif opt in ("-t", "--trn"):
#                 self.trn = self._readTrn(arg)
#             else:
#                 print "Wrong arguments, use -h for helps."
#
#         try:
#             self.predictor = ann.predicting(network_name=self.networks,
#                                 predict_descs=self.descs,
#                                 training_descs=self.trn,
#                                 featureNorm=True)
#         except AttributeError:
#             print 'Worng input files, please provide networks, descriptors and training data, use -h for help'
#             sys.exit(2)

    def __readDescs(self,raw_file):
        '''
        clean up descs file use pandas
        remove header and col name

        Input: raw_file: raw descriptors file with header and two useless colnums
        return pure numpy arrary of descriptors values
        '''
        df = pd.read_csv(raw_file,delim_whitespace=True)
        df = df.fillna(df.mean())
        df = df.drop('No.', 1)
        self.smiles = df['NAME']
        df = df.drop('NAME',1)
        val = df.values
        return val

    def __readTrn(self,trn_data):
        '''
        read training data
        '''
#         trnData = np.loadtxt(trn_data,skiprows=1)
        df = pd.read_csv(trn_data)
        trnData = df.values
        return trnData

    def predict(self, descs=None, to_file=False):
        '''
        Call package functions to predict
        '''
        if descs == None:
            self.descs = self.__readDescs('./modules/lcia/descriptors/output.txt')
        else:
            self.descs = descs

        self.predictor = Predictor(network_name=self.networks,
                            predict_descs=self.descs,
                            training_descs=self.trn,
                            featureNorm=True)
        # feature Normalization
        normedDescs = self.predictor.featureNorm(self.predictor.descsForPred, self.predictor.X_scalar)
        prediction_results = self.predictor.predict(self.predictor.network, normedDescs)
        # Transform back
        self.prediction_results = np.exp(prediction_results)
        # if to_file:
        # # save to file
        #     np.savetxt('prediction_results.csv',self.prediction_results,delimiter=',')
        #     print "Prediction results saved [prediction_results]. Make a copy if you want to keep it."
        results_array = self.prediction_results.tolist()
        confidence = self.predict_conf()
        results = []

        for idx, smiles in enumerate(self.smiles):
            results.append([smiles, results_array[idx], confidence[idx]])

        return results

    def predict_conf(self):
        '''
        Prediction Confidence Level,
        Base on the distance to the centroid of training data
        '''
        assert self.prediction_results is not None
        assert self.trn is not None

        self.dist = self.predictor.calcDist(self.descs, self.trn)
        conf = []
        for eachDist in self.dist:
            if eachDist > 100:
                conf.append('Low')
            else:
                conf.append('High')

        self.prediction_conf = conf
#         print self.smiles,self.dist
        return conf

    def to_file(self):
        '''
        combine outputs to file
        '''
        assert self.prediction_results is not None

        outputs = pd.DataFrame(self.smiles)
        outputs['prediction results'] = self.prediction_results
        outputs['prediction confidence'] = self.prediction_conf
        outputs.to_csv('prediction_results.csv')
        print 'Prediction results output to "prediction_results.csv". Make a copy if you want to save the results'




# if __name__ == '__main__':
#     # set up object
#     thisPredict = net_prediction(sys.argv[1:])
#     # predict
#     thisPredict.predict()
#     # prediction confidence
#     thisPredict.prediction_conf()
#     # write to file
#     thisPredict.to_file()
