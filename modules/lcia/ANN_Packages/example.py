'''
Created on Aug 12, 2015
A example of using the regression model
@author: rsong_admin
'''
import regression as ann
import numpy as np

'''
A example of using the module to do regression
X is the chemical descriptors and y is the cumulative energy demand when manufacturing this chemical

if the program stop at somewhere just press any key to continue
'''
# load data
X = np.loadtxt('183_descs_21.csv',skiprows=1,delimiter=',')
y = np.loadtxt('CED_Y_183.csv',skiprows=1,delimiter=',')

# set up training class
aTrainer = ann.training(X,y)
aTrainer.set_dataset(splitProtion=.15, featureNorm=True, Y_log=True)
aTrainer.train_net(training_times_input=200, 
                   num_neroun=60, 
                   learning_rate_input=0.01,
                   weight_decay=0, 
                   momentum_in=0, 
                   verbose_input=True)

prediction_tst = aTrainer.predict(aTrainer.network, aTrainer.tstdata['input'])
prediction_tst = np.exp(prediction_tst) #since the data were logged during training, here must be transformed back
real_tst = aTrainer.tstdata['target'][:,0]
real_tst = np.exp(real_tst)

# plot the prediction error
aTrainer.plot_diff(real_tst, prediction_tst, 
                   xlab='chemical number', 
                   ylab='CED values', 
                   title='predicted CED value vs real value on test dataset')

# calculate median relative error
theError = aTrainer.calc_Diff(real_tst, prediction_tst)

#save network to xml file
raw_input('Save the network?')
aTrainer.save_network('testNetwork.xml')

raw_input('Going to the part of using exsisting network to do prediction, press anykey to continue')

# here set up the predictor class, must load your original X value for corresponding network to do feature Normalization
aPredictor = ann.predicting(network_name='testNetwork.xml',
                            predict_descs=X,
                            training_descs=X,
                            featureNorm=True)
# do feature normalization
normedDescs = aPredictor.featureNorm(aPredictor.descsForPred, aPredictor.X_scalar)

# prediction here
prediction_results = aPredictor.predict(aPredictor.network, normedDescs)
# still, transform back 
prediction_results = np.exp(prediction_results)
raw_input('Going to save the prediction results')
np.savetxt('prediction_results.csv',prediction_results,delimiter=',')

