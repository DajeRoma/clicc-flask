'''
Created on Apr 28, 2015
Classes for regression, based on ANN
Take chemical descriptors as input,
predict chemical values as you trained.
@author: rsong_admin
'''

from sklearn import preprocessing
from sklearn.decomposition import PCA
from sklearn.feature_selection import VarianceThreshold

from pybrain.datasets            import SupervisedDataSet
from pybrain.tools.shortcuts     import buildNetwork
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.datasets            import SupervisedDataSet
from pybrain.tools.shortcuts     import buildNetwork
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.tools.validation import CrossValidator, Validator
from pybrain.tools.validation import ModuleValidator
from pybrain.tools.xml import NetworkWriter
from pybrain.tools.xml import NetworkReader
from pybrain.structure.modules.linearlayer import LinearLayer

from pybrain.structure.modules.sigmoidlayer import SigmoidLayer
from pybrain.tools.validation import CrossValidator
from numpy.random.mtrand import permutation

import csv
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from matplotlib import style
style.use('ggplot')


class training:
    network_name=None;
    network=None; '''a network instance'''

    '''input data'''
    descriptors=None
    target=None
    data_set=None
    data_setNormed = None
    tstdata = None
    trndata = None

    '''these for PCA'''
    scalar_X = None

    '''important outputs'''
    r_squared=None
    median_error=None
    predicted_value=None

    def __init__(self,X_filename,Y_filename=None):
        '''some important factors'''

        '''loading data'''
        self._load_training_data(X_filename, Y_filename)

    def _load_training_data(self,X_filename,Y_filename):
        '''
        X and Y values will be loaded here
        '''
        self.descriptors=X_filename
        print "Descriptors loaded!"
        if Y_filename is not None:
            self.target=Y_filename
            print "Target for training loaded!"

    def do_pca(self,user_input=0,threshold_input=0):
        '''PCA will be doen here'''

    def set_dataset(self,splitProtion = 0.15,featureNorm = True, Y_log = True):
        '''put training data into pybrain object'''

        '''Feature Selection doing here'''
#         self.descriptors = self.featureReduction(self.descriptors, threshold_input = 10)

        num_row=self.descriptors.shape[0]
        num_col=self.descriptors.shape[1]
        '''Pack data '''
        self.data_set = SupervisedDataSet(num_col , 1)
        for num_data in range(num_row):
            inputs=self.descriptors[num_data,:]
            outputs=self.target[num_data]
            self.data_set.addSample(inputs, outputs)
        print self.data_set.indim

        if featureNorm:
            '''split data'''
            self.tstdata, self.trndata = self.split_data(self.data_set,splitProtion)

            '''get the scalar for the trndata'''
            '''and normalize the tstdata with this scalar'''
            trn_scalar = self._getScalar(self.trndata['input'])

            self.trndata = self.featureNorm(self.trndata,trn_scalar,Y_log = True)
            self.tstdata = self.featureNorm(self.tstdata, trn_scalar, Y_log = True)
            self.data_setNormed = self.featureNorm(self.data_set, trn_scalar, Y_log = True)
            print 'Feature Normed'
        else:
            self.tstdata, self.trndata = self.split_data(self.data_set,splitProtion)
            print 'Feature not Normed'
        raw_input("Pybrain data object has been set up.")

    def featureReduction(self, data,threshold_input = 0.99):
        '''
        feature reduction that only keep variables that the variance
        is greater than threshold.
        '''
        selector = VarianceThreshold(threshold = threshold_input)
        data = selector.fit_transform(data)
        print 'Feature Selected with threshold ', threshold_input, data.shape
        return data

    def _getScalar(self, data):
        '''For Normalization '''
        '''get the scalar of the input data and return  '''
        thisScalar = preprocessing.StandardScaler().fit(data)
        return thisScalar

    def featureNorm(self,data,scalar,Y_log = True):
        '''
        feature Normalization, deal with self.data_set, return self.data_setNormed
        '''
        descs = data['input']
        target = data['target']
        num_col = descs.shape[1]
        data_setNormed = SupervisedDataSet(num_col,1)
        data_setNormed.setField('input', scalar.transform(descs))
        '''feature norm for Y'''
        if Y_log:
            print 'Using log value of target'
            data_setNormed.setField('target',np.log(target))
        else:
            print 'Using the original value of target'
            data_setNormed.setField('target',target)
        return data_setNormed

    def split_data(self,dataset,proportion = 0.15):
        '''
        split the data to self.tstdata and self.trndata.
        '''
        tstdata,trndata = dataset.splitWithProportion(proportion)
        return tstdata, trndata

    def train_net(self,training_times_input=100,num_neroun=200,learning_rate_input=0.1,weight_decay=0.1,momentum_in = 0,verbose_input=True):
        '''
        The main function to train the network
        '''
        print self.trndata['input'].shape
        raw_input()
        self.network=buildNetwork(self.trndata.indim,
                                  num_neroun,self.trndata.outdim,
                                  bias=True,
                                  hiddenclass=SigmoidLayer,
                                  outclass = LinearLayer)
        self.trainer=BackpropTrainer(self.network,
                                     dataset=self.trndata,
                                     learningrate=learning_rate_input,
                                     momentum=momentum_in,
                                     verbose=True,
                                     weightdecay=weight_decay )

        for iter in range(training_times_input):
            print "Training", iter+1,"times"
            self.trainer.trainEpochs(1)
            trn_error = self._net_performance(self.network, self.trndata)
            tst_error = self._net_performance(self.network, self.tstdata)
            print "the trn error is: ", trn_error
            print "the test error is: ",tst_error

        '''prediction on all data:'''
#         self.predicted_value = self.predict(self.network,self.data_setNormed['input'])

    def train_best_converge(self,training_times_input=5,num_neuron=120,learning_rate_input=0.1,weightdecay_input = 0.01,maxEpochs_input=1200,verbose_input=True):

        '''pass values'''
        self.training_time=training_times_input
        self.learning_rate=learning_rate_input
        self.maxEpo=maxEpochs_input
        self.verbose=verbose_input
        self.r_squared=np.empty([self.training_time])
        self.median_error=np.empty([self.training_time])
        test_data,training_data=self.data_set.splitWithProportion(0.15)

        #train the network 30 times
        for iter in range(self.training_time):
            print "Training", iter+1,"times"

            '''randomly split the dataset to have 20% to be test data'''
            valid_data_this,train_data_this=training_data.splitWithProportion(0.1)

            net=buildNetwork(self.data_set.indim,num_neuron,self.data_set.outdim,bias=True,outputbias=True,hiddenclass=SigmoidLayer)
            t=BackpropTrainer(net,train_data_this,learningrate=self.learning_rate,weightdecay=weightdecay_input,momentum=0.,verbose=self.verbose)
            t.trainUntilConvergence(train_data_this,maxEpochs=self.maxEpo, validationProportion=0.1,verbose=self.verbose)

            '''validate the model with validation dataset'''
            self.r_squared[iter],self.median_error[iter]=self.do_regression(net, valid_data_this.getField("input"),valid_data_this.getField("target")[:,0])

            locals()['net'+str(iter)]=net
            locals()['train_data' + str(iter)]=train_data_this
            locals()['valid_data' + str(iter)]=valid_data_this
            locals()['train' + str(iter)]=t

            print "Training",iter+1,"has done!"

        r_max = np.amax(self.r_squared)
        max_index=self.r_squared.argmax()

        print "Model ", max_index+1, "has been selected"
        self.network=locals()['net'+str(max_index)]
        self.train_best=locals()['train_data' + str(max_index)]
        self.valid_best=locals()['valid_data' + str(max_index)]

        '''run the best network on the test data'''
        print "The performance on test data........."
        descriptors_test=test_data.getField("input")
        Y_test=test_data.getField("target")[:,0]

        r2_all=self.do_regression(self.network, descriptors_test, Y_test)

        raw_input("Paused!")

        '''run the best network on the all data'''
        print "The performance on all data........."
        self.predicted_value=self.test_data(self.network, self.descriptors_pca)
        r2_test=self.do_regression(self.network, self.descriptors_pca, self.target)

    def train_CV(self,n_folds=5,num_neuron = 50,learning_rate_input=0.01,decay=0.01,maxEpochs_input=1200,verbose_input=True):
        '''call the class in model validators'''
        '''and do cross validation'''
        '''pass values'''
        dataset = self.data_set
        l = dataset.getLength()
        indim = dataset.indim
        outdim = dataset.outdim
        inp = dataset.getField("input")
        out = dataset.getField("target")
        perms = np.array_split(permutation(l), n_folds)
        perf = 0
        for i in range(n_folds):
            train_perms_idxs = list(range(n_folds))
            train_perms_idxs.pop(i)
            temp_list = []
            for train_perms_idx in train_perms_idxs:
                temp_list.append(perms[ train_perms_idx ])
            train_idxs = np.concatenate(temp_list)
            #this is the test set:
            test_idxs = perms[i]
            #train:
            print "Training on part: ", i
            train_ds = SupervisedDataSet(indim,outdim)
            train_ds.setField("input", inp[train_idxs])
            train_ds.setField("target",out[train_idxs])
            net_this = buildNetwork(indim,num_neuron,outdim,bias=True,hiddenclass = SigmoidLayer)
            t_this = BackpropTrainer(net_this,train_ds,learningrate = learning_rate_input,weightdecay=decay,
                                     momentum=0.,verbose=verbose_input)
            #train asked times:
            t_this.trainEpochs(maxEpochs_input)
            #test on testset.
            test_ds = SupervisedDataSet(indim,outdim)
            test_ds.setField("input", inp[test_idxs])
            test_ds.setField("target",out[test_idxs])
            perf_this = self._net_performance(net_this, test_ds)
            perf = perf + perf_this
        perf /=n_folds
        print perf
        return perf

    def do_CV(self,):
        '''
        call CV
        '''
        data_set_this = self.data_set
        perf_all=[]
        for num_neuron in np.arange(20,200,5):
            print "Training with number of neuron :", num_neuron
            perf_this = self.train_CV(n_folds=5, num_neuron=num_neuron, learning_rate_input=0.001, maxEpochs_input=50, verbose_input=False)
            perf_all.append(perf_this)
        print "All of the performance: ", perf_all
        output=open("CV_results_20to200.csv",'wb')
        filewriter=csv.writer(output)
        filewriter.writerow(perf_all)

    def _net_performance(self,net,test_data):
        """
        calculate the median relatively error (mre)
        """
        input = test_data.getField("input")
        target = test_data.getField("target")
        outputs = self.predict(net, input)
        abs_error = np.absolute(outputs - target)
        rel_error = np.divide(abs_error,np.absolute(target))
        mre = np.median(rel_error)
        return mre

    def predict(self,net,X):
        '''
        run the prediction of the given data (descriptors) on the given network.
        '''
        num_row=X.shape[0]
        num_col=X.shape[1]
        results=np.empty([num_row])
        for line in range(num_row):
            results[line]=net.activate(X[line])[0]
#         if self.scalar_Y is not None:
#             results = self.scalar_Y.inverse_transform(results)
        return results

    def do_regression(self,net,X_pca,Y):
        '''
        run the network prediction on descriptor X
        do regression on Y
        return R_squred value
        '''
        test_result=self.test_data(net, X_pca)
        slope,intercept,r_value,p_value,std_err =stats.linregress(Y, test_result)
        median_error_this=self.calc_Diff(Y, test_result)
        print "The R squared of this time is: ",r_value**2
        print "The median relatively error of this time is:", median_error_this
        return r_value**2,median_error_this

    def calc_Diff(self,real_value,predicted_value):
        '''
        this function calculate the median and average absolute error and relatively error
        between the real_value and the predicted value
        '''
        diff_between_abs=np.absolute(predicted_value-real_value)
        diff_between_abs_relatively=diff_between_abs/real_value
        mean_rel_error=np.mean(diff_between_abs_relatively)
        median_rel_error=np.median(diff_between_abs_relatively)
        mean_abs_error=np.mean(diff_between_abs)
        median_abs_error=np.median(diff_between_abs)

        return median_rel_error

    def plot_diff(self,real_value,predicted_value,xlab,ylab,title):
        '''
        plot the line of real value and estimated value and plot the difference bar on the same graph
        '''
        num_row=real_value.shape[0] #this is the length of x axis
        data_all=np.array((real_value,predicted_value))
        data_all=np.transpose(data_all)
        data_all_sorted=data_all[data_all[:,0].argsort()]
        diff=data_all_sorted[:,1]-data_all_sorted[:,0]
        y_value=np.arange(num_row)

        fig=plt.figure()
        ax=fig.gca()
        ax.plot(y_value,data_all_sorted[:,1],label="Estimated Values")
        ax.plot(y_value,data_all_sorted[:,0],label="Reported Values")
        plt.xlabel(xlab, fontsize = 16)
        plt.ylabel(ylab, fontsize = 16)
        plt.title(title)
        ax.legend(loc = 2)

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

    def load_network(self,name_of_the_net):
        print "load existing trained network"
        self.network=NetworkReader.readFrom(name_of_the_net)
        print "Succeed!"


class predicting:
    '''some paramaters to be keeping track of'''
    network = None
    descsForPred = None
    normed_descsForPred = None
    X_scalar = None

    def __init__(self,network_name,predict_descs,training_descs,featureNorm = True):
        self.network = self.load_network(network_name)
        self.descsForPred = predict_descs
        self.TrainingData = training_descs
        if featureNorm:
            print 'Normalization using the training data.....'
            self.X_scalar = self._getScalar(self.TrainingData)
            self.normed_descsForPred = self.featureNorm(self.descsForPred,self.X_scalar)

    def load_file(self,fileName):
        data = np.loadtxt(fileName,delimiter = ',')
        return data

    def featureNorm(self,descs,scalar):
        assert scalar is not None
        normed_data = scalar.transform(descs)
        print 'Descriptors for prediction have been normalized!'
        return normed_data

    def predict(self,net,descs):
        '''
        run prediction of the given data (descriptors) on the given network.
        '''
        num_row=descs.shape[0]
        num_col=descs.shape[1]
        results=np.empty([num_row])
        print 'Predicting...'
        for line in range(num_row):
            results[line]=net.activate(descs[line])[0]
#         if self.scalar_Y is not None:
#             results = self.scalar_Y.inverse_transform(results)
        return results

    @staticmethod
    def calcDist(data,training_data):
        '''calculate the distance from the predicting dataset
        to the centroid of the training dataset
        '''
        num_row = data.shape[0]
        dist = np.empty([num_row])
        cent = np.mean(training_data,0)
        for i in range(num_row):
            dist[i] = np.linalg.norm(cent - data[i,:])
        return dist

    def plot_diff(self,real_value,predicted_value,xlab,ylab,title):
        '''
        plot the line of real value and estimated value and plot the difference bar on the same graph
        '''
        num_row=real_value.shape[0] #this is the length of x axis
        data_all=np.array((real_value,predicted_value))
        data_all=np.transpose(data_all)
        data_all_sorted=data_all[data_all[:,0].argsort()]
        diff=data_all_sorted[:,1]-data_all_sorted[:,0]
        y_value=np.arange(num_row)

        fig=plt.figure()
        ax=fig.gca()
        ax.plot(y_value,data_all_sorted[:,1],label="Estimated Values")
        ax.plot(y_value,data_all_sorted[:,0],label="Reported Values")
        plt.xlabel(xlab, fontsize = 16)
        plt.ylabel(ylab, fontsize = 16)
        plt.title(title)
        ax.legend(loc = 2)

        ax.bar(y_value,diff)
        plt.show()

    def calc_Diff(self,real_value,predicted_value):
        '''
        this function calculate the median and average absolute error and relatively error
        between the real_value and the predicted value
        '''
        diff_between_abs=np.absolute(predicted_value-real_value)
        diff_between_abs_relatively=diff_between_abs/real_value
        mean_rel_error=np.mean(diff_between_abs_relatively)
        median_rel_error=np.median(diff_between_abs_relatively)
        mean_abs_error=np.mean(diff_between_abs)
        median_abs_error=np.median(diff_between_abs)

        return median_rel_error

    def load_network(self,name_of_the_net):
        print "load existing trained network"
        network=NetworkReader.readFrom(name_of_the_net)
        print "Succeed!"
        return network

    def _getScalar(self, data):
        thisScalar = preprocessing.StandardScaler().fit(data)
        return thisScalar

    def save_toFile(self,filename,pred):
        '''this function save the Numpy object array of prediction results to csv file'''
        np.savetxt('filename', pred, delimiter=',')
        print 'File Saved'
