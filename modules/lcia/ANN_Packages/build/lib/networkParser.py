'''
Created on Aug 17, 2015
A Artificial Network Parameters Parser
This will output the parameters between each layers.
Only works for 3 layers networks (i.e input layers + hidden layer 1 + output layer)
@author: rsong_admin
'''
from pybrain.tools.customxml import NetworkReader
import numpy as np

class networkParser():
    def __init__(self,networkName):
        self.network = NetworkReader.readFrom(networkName)
        self.indim = self.network.indim
        self.outdim = self.network.outdim
    
    def getParam(self):
        '''
        get the parameters values from the network for input-hidden layer
        and for hidden-output layer
        
        the instance that store parameters is a dict
        this function only applicable to one hidden layer models.
        '''
        theConnections = self.network.connections
        theKeys = theConnections.keys()
        
        for eachKey in theKeys:
            if 'bias' in eachKey.name: #ignore bias unit
                continue 
            if 'out' in eachKey.name: #ignore output unit, it has not parameters actually
                continue
            if 'in' in eachKey.name:
                #this is the parameters from input layer to hidden layer
                in_to_hidden_raw = theConnections[eachKey][0].params
                self.num_hidden = theConnections[eachKey][0].outdim
                self.in_to_hidden = in_to_hidden_raw.reshape((self.num_hidden,self.indim))
            if 'hidden' in eachKey.name:
                self.hidden_to_out = theConnections[eachKey][0].params
    
    def calcuateWeight(self, rowIdx, colIdx):
        '''
        A helper function that calucate Wij * WjH for current network,
        return the result
        '''
        first_layer_value = self.in_to_hidden[colIdx,rowIdx] #get the weight for 'colIdx' neuron to 'rowIdx' input
        second_layer_value = self.hidden_to_out[colIdx]
        
        return first_layer_value * second_layer_value
        
    def orderNeuron(self):
        '''
        Calculate SCV value for each neuron
        return a list of index for neuron, order them by SCV value
        from high  to low
        '''
        CV = (np.sum(self.in_to_hidden,axis=1) * self.hidden_to_out)/self.indim 
        CV_sq = np.square(CV)
        CV_sq_sum = np.sum(CV_sq)
        self.SCV = CV_sq / CV_sq_sum
        neuronOrder = np.argsort(self.SCV)
        neuronOrder = neuronOrder[::-1] #reverse to from high to low
        return neuronOrder
    
    def weightTable(self):
        '''
        Create and return the effective weight table 
        for ordered neuron from high SCV to low
        '''
        self.getParam()
        neuronOrder = self.orderNeuron()
        self.weightTable = np.empty([self.indim, self.num_hidden])
        for eachRow in range(self.indim):
            for eachCol in range(self.num_hidden):
                thisNeuron = neuronOrder[eachCol] #get the index from the order list
                self.weightTable[eachRow,eachCol] = self.calcuateWeight(eachRow, thisNeuron)
    
    def outputTable(self):
        '''
        A getter function
        '''
        self.weightTable()
        return self.weightTable
            
    def saveToFile(self,fileName):
        '''
        save the two interested parameters array to csv file
        the matrix shape is: number of neuron times the number of input
        '''
        theArray = np.array(self.hidden_to_out)
        np.savetxt(fileName+'.csv',theArray,delimiter=',')
    
    def pesos_conexiones(self,n):
        '''
        print out the parameters for each layer, 
        marked by the actual connection pathway in the model.
        '''
        for mod in n.modules:
            for conn in n.connections[mod]:
                print conn
                for cc in range(len(conn.params)):
                    print conn.whichBuffers(cc), conn.params[cc]
                    
if __name__ == '__main__':
    '''
    example
    '''
    aParser = networkParser('CED_July23.xml')
    test = aParser.outputTable()
#     aParser.pesos_conexiones(aParser.network)
    np.savetxt('CEDJuly23_weightTable.csv',test,delimiter=',')
#     aParser.getParam()
#     test = aParser.hidden_to_out
#     print test[np.nonzero(test)].shape
    
    
    