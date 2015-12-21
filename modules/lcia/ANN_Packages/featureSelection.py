'''
Created on Aug 18, 2015
A group of functions that serve for feature selection using 'Filter method'
First, it delete those variables that has lower variance than threshold,
Second, it calcuate 'Pair-wise' correlation' between variables. If less than threshold,
delete the second variable.

 
@author: sourunsheng
'''
import numpy as np
from scipy import stats
import pandas as pd
from sklearn.feature_selection import VarianceThreshold

def calCorrMat():
    '''
    delete variable that has variance lower than threshold. 10 here
    '''
    df = pd.read_csv('183_descs_3763.csv',header=0,index_col=None)
    
    sel = VarianceThreshold(10)
    data = sel.fit_transform(df.values)
    aMask = sel.get_support(True)
    newDf = df.iloc[:,aMask]
    print newDf.shape
    raw_input()
    corrMat = newDf.corr(method='pearson')
    corrMat.to_csv('./data/corrNew.csv')
    newDf.to_csv('./data/reducedDescs.csv')  
    return corrMat

def calLowCorr():
    '''
    calculate 'Pair-Wise' variable correlation matrix.
    Delete the second one if it less than 0.7 here. 
    '''
    df = pd.read_csv('./data/corrNew.csv',header=0,index_col=0)
    totalRow, totalCol = df.shape    
    tracker = np.zeros([totalCol])
    for num_row in range(totalRow):
        print num_row
        if tracker[num_row] == 1:
            continue
        for num_col in range(num_row+1,totalCol):
            if tracker[num_col] == 1:
                continue
            if df.iloc[num_row,num_col]>=0.7:
                tracker[num_col] = 1      
    np.savetxt('./data/corrResultsNew.csv',tracker,delimiter=',')      

def newMat():
    '''
    Return selected variables.
    '''
    theMask = np.loadtxt('./data/corrResultsNew.csv',delimiter=',')
    theMask = theMask==0
    oldData = pd.read_csv('./data/reducedDescs.csv',header=0,index_col=0)
    newData = oldData.iloc[:,theMask]
    newData.to_csv('./data/reducedDescs2.csv')
    np.savetxt('./data/theMask.csv',theMask,delimiter=',')

