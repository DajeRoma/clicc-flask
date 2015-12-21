'''
Created on Dec 17, 2015
Use ANN to predict chemical LCIA in command line interface
Inputs: -n : ANNs
        -d: The descriptors of the chemical that you want to predict on
        -t: The original training data (can be hard coded in the script actually)

Outputs: Prediction results in 'prediction_results.csv'
@author: rsong_admin
'''
import subprocess as sb

proc = sb.Popen(['python','predict.py','-n','./nets/CED_new.xml','-d', './descriptors/output.txt', '-t','./descriptors/trn_data_30.csv'])
# proc = sb.Popen(['python','predict.py','-n','./nets/CED_new.xml'])