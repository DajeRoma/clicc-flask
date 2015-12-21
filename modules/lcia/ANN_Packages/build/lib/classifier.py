'''
Created on Apr 28, 2015
A Classifier based on ANN
Take Chemical descriptors as input
Predict functional use of chemicals
@author: rsong_admin
'''

from pybrain.datasets            import ClassificationDataSet
from pybrain.tools.shortcuts     import buildNetwork
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.structure.modules.softmax import SoftmaxLayer
from sklearn import preprocessing
from numpy import array
from pybrain.utilities           import percentError
from pybrain.tools.customxml import NetworkWriter
from pybrain.tools.customxml import NetworkReader
import matplotlib.pyplot as plt
import numpy as np 

import csv
from scipy import dot, argmax
from pybrain.structure.modules.sigmoidlayer import SigmoidLayer
from pybrain.tools.validation import CrossValidator
from pybrain.tools.validation import ModuleValidator
from numpy.random.mtrand import permutation

class training:

    trainer=None
    network=None; '''a network instance'''
    
    '''input data'''
    descriptors=None
    target=None
    trn_pca = None
    tst_pca = None
    data_set=None
    trndata=None
    tstdata=None
    num_classes=None
    train_mu =None
    train_std =None

    '''important outputs'''
    r_squared=None
    median_error=None
    predicted_value=None
    
    
    
    def __init__(self,X_filename,Y_filename):
        '''some important factors'''
        
        '''loading data'''
        self._load_training_data(X_filename, Y_filename)
        
    def _load_training_data(self,X_filename,Y_filename):
        '''
        X and Y values wull be loaded here 
        '''
        self.descriptors=X_filename
        print "Descriptors loaded!"
        self.target=Y_filename
        self.num_classes = int(np.max(self.target))+1
        print "Target for training loaded!"
        print "Number of classes is: ", self.num_classes
    
    def _split_data(self,proportion = 0.15, featureNorm = True):
        self.tstdata,self.trndata = self.data_set.splitWithProportion(0.15)
        self.trndata._convertToOneOfMany()
        self.tstdata._convertToOneOfMany()
        print 'Data split with ', proportion
        '''feature Normalization done here'''
        if featureNorm:
            self.scalar = preprocessing.StandardScaler().fit(self.trndata['input'])
            self.trndata.setField('input',self.scalar.transform(self.trndata['input']))
            self.tstdata.setField('input',self.scalar.transform(self.tstdata['input']))
            print 'Feature Normalized'

    def set_dataset(self,prop = 0.15,featureNorm = True):
        '''put training data into pybrain object'''
        num_row = self.descriptors.shape[0]
        num_col = self.descriptors.shape[1]
      
        self.data_set = ClassificationDataSet(num_col,1,nb_classes=self.num_classes)
        for num_data in range(num_row):
            inputs=self.descriptors[num_data,:]
            outputs=self.target[num_data]
            self.data_set.addSample(inputs, [outputs])
        '''split data and do normorlization'''
        self._split_data(prop, featureNorm)
        print "Pybrain data have been set up" 
        
    def train_net(self,training_times_input=100,num_neroun=200,learning_rate_input=0.1,weight_decay=0.1,momentum_in = 0,verbose_input=True):
        self.network=buildNetwork(self.trndata.indim,num_neroun,self.trndata.outdim,bias=True,hiddenclass=SigmoidLayer,outclass=SoftmaxLayer)
        self.trainer=BackpropTrainer(self.network, dataset=self.trndata,learningrate=learning_rate_input, momentum=momentum_in, verbose=True, weightdecay=weight_decay )

        for iter in range(training_times_input):
            print "Training", iter+1,"times"
            self.trainer.trainEpochs( 1 )
            trnresult = percentError( self.trainer.testOnClassData(dataset= self.trndata ),
                                      self.trndata['class'] )
            tstresult = percentError( self.trainer.testOnClassData(dataset= self.tstdata ),  
                                      self.tstdata['class'] )

            print "epoch: %4d" % self.trainer.totalepochs, \
                "  train error: %5.2f%%" % trnresult, \
                "  test error: %5.2f%%" % tstresult
                
            
    def CrossValidation(self,n_fold=5,num_neuron=50):  
        data_set_this=self.data_set
        data_set_this._convertToOneOfMany()
        print "Training with number of neuron :",num_neuron
        network_this=buildNetwork(data_set_this.indim,num_neuron,data_set_this.outdim,bias=True,hiddenclass=SigmoidLayer)  
        trainer_this=BackpropTrainer(network_this,dataset=data_set_this,learningrate=0.001,momentum=0,verbose=True,weightdecay=0.1)
        CV=CrossValidator(trainer_this,data_set_this,num_neuron,n_folds=n_fold,max_epochs=3)
        perf_this=CV.validate()
        print "The performance of this network with CV is: ", perf_this
    

    def CV_best_struct(self,n_fold=5):  

        data_set_this = self.data_set
        
        perf=[]
        for num_neuron in np.arange(200,4000,500):
            print "Training with number of neuron :",num_neuron
            
            network_this=buildNetwork(data_set_this.indim,num_neuron,data_set_this.outdim,bias=True,hiddenclass=SigmoidLayer,outclass=SoftmaxLayer)  
            trainer_this=BackpropTrainer(network_this,dataset=data_set_this,learningrate=0.001,momentum=0,verbose=False,weightdecay=0.1)
        
            '''here, the data set should be raw data instead of pca data'''
            '''do pca after data spliting '''
            CV=CrossValidator(trainer_this,data_set_this,num_neuron,n_folds=n_fold,max_epochs=3)
            perf_this=CV.validate()
            
            perf.append(perf_this)
            print "The performance of this network with CV is: ", perf_this
        
        print "All performance: ", perf
        output=open("CV_results_200to4000.csv",'wb')
        filewriter=csv.writer(output)
        filewriter.writerow(perf)
       
        
    def predict(self,net,X_pca):
        '''
        run the prediction of the given data (descriptors) on the given network.
        '''
        out = []
        targ = []
        
        for input in X_pca:
            res = net.activate(input)
            out.append(argmax(res))
#             out.append(res)
        self.predicted_value=out
        return out

    def calc_accuracy(self,real_value,predicted_value):
        '''
        this function calculate the median and average absolute error and relatively error 
        between the real_value and the predicted value
        '''
        true_right=np.empty(len(real_value))
        for iter in range(len(real_value)):
            if real_value[iter]==predicted_value[iter]:
                true_right[iter]=1
            else:
                true_right[iter]=0
        tot_right=sum(true_right)
        acc=tot_right/len(real_value)
        
        return acc
    
    def SectionalAcc(self,realValue,predictedValue):
        '''
        Return accuracy for each section of class
        '''
        accDict = {}
        numDict = {}
        for i in range(len(predictedValue)-1):
            thisClass = realValue[i][0]
            numDict[thisClass] = numDict.get(thisClass,0) + 1 #total number of each class
            accDict[thisClass] = 0
        for i in range(len(predictedValue)-1):
            thisClass = realValue[i][0]
            if thisClass == predictedValue[i]:
                #right prediction of each class
                accDict[thisClass] += 1
        sectionalAcc = {k: float(accDict[k])/numDict[k] for k in numDict}
        
        return sectionalAcc
        
    def plot_class_results(self,target_in):
        '''
        
        '''
        descs = self.descriptors
        target =  target_in
        predicted = self.predicted_value
        assert len(target) == len(predicted)
        
        error_pair = np.empty([len(target)])
        for i in range(len(target)):
            if target[i]!=predicted[i]:
                error_pair[i] = 4
            else:
                error_pair[i] = 5
  
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.scatter(descs[:,1],descs[:,2],15*array(error_pair),15*array(error_pair))
        plt.show()      
        
    
    def plot_diff(self,real_value,predicted_value):
        '''
        plot the line of real value and estimated value and plot the difference bar on the same graph
        for continues value, supervised leanring problem
        '''
        num_row=real_value.shape[0] #this is the length of x axis
        
        data_all=np.array((real_value,predicted_value))
        data_all=np.transpose(data_all)
        
        data_all_sorted=data_all[data_all[:,0].argsort()]
        
        diff=data_all_sorted[:,1]-data_all_sorted[:,0]
        
        y_value=np.arange(num_row)
        
        fig=plt.figure()
        ax=fig.gca()
    #     print len(diff)
    #     print y_value.shape
        ax.plot(y_value,data_all_sorted[:,1],label="Estimated Values")
        ax.plot(y_value,data_all_sorted[:,0],label="Reported Values")
        ax.legend()
        ax.bar(y_value,diff)
        plt.show()
    
    
    def save_toFile(self,filename,pred):
        '''this function save the Numpy object array of prediction results to csv file'''
        np.savetxt('filename', pred, delimiter=',')

    def save_network(self,name_of_the_net):
        print "Saving the trained network to file"
        
        if self.network is None:
            print "Network has not been trained!!"
        else:
            NetworkWriter.writeToFile(self.network, name_of_the_net)
            print "Saving Finished"
           
class predicting:
    def __init__(self,network_name,predict_descs,training_descs,featureNorm=True):
        self.network = self.load_network(network_name)
        self.descsForPred_raw = predict_descs
        self.trainingData = training_descs
        if featureNorm:
            '''do feature normalization '''
            '''get training scalar first '''
            self.scalar_X = self._getScalar(training_descs)
            self.descsForPred_normed = self.featureNorm(self.descsForPred_raw, self.scalar_X)
            
    def load_network(self,name_of_the_net):
        print "load existing trained network"
        network=NetworkReader.readFrom(name_of_the_net)
        print "Networking Succeed!"
        return network
          
    def featureNorm(self,descs,scalar):
        assert scalar is not None
        normed_data = scalar.transform(descs)
        print 'Descriptors for prediction have been normalized!'
        return normed_data
        
    def _getScalar(self, data):
        thisScalar = preprocessing.StandardScaler().fit(data)
        return thisScalar       
    
    def predict(self,net,descs):
        '''
        run prediction of the given data (descriptors) on the given network.
        '''
        out = []
        targ = []
        print 'Predicting...'
        for input in descs:
            res = net.activate(input)
            out.append(argmax(res)) #one to many method
#             out.append(res) #output all  
        return out
    
    @staticmethod
    def calc_accuracy(real_value,predicted_value):
        '''
        for CLASSIFICATION
        calculate the right classification rate
        '''
        true_right=np.empty(len(real_value))
        for iter in range(len(real_value)):
            if real_value[iter]==predicted_value[iter]:
                true_right[iter]=1
            else:
                true_right[iter]=0
        tot_right=sum(true_right)
        acc=tot_right/len(real_value)
        
        return acc 
    
    @staticmethod
    def SectionalAcc(realValue,predictedValue):
        accDict = {}
        numDict = {}
        for i in range(len(predictedValue)):
            thisClass = realValue[i]
            numDict[thisClass] = numDict.get(thisClass,0) + 1 #total number of each class
            accDict[thisClass] = 0
        for i in range(len(predictedValue)):
            thisClass = realValue[i]
            if thisClass == predictedValue[i]:
                #right prediction of each class
                accDict[thisClass] += 1
        sectionalAcc = {k: float(accDict[k])/numDict[k] for k in numDict}
        return sectionalAcc
    
    