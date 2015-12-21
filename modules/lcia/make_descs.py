'''
Created on Dec 15, 2015
read in CAS file and output smiles 
by querying chemspider

Call >python make_descs.py [CAS_FILE]

@author: rsong_admin
'''
from chemspipy import ChemSpider
import csv
import sys
import subprocess as sb

class make_descs:
    def __init__(self,argv):
        ''' load input arguments'''
        self.CAS_file = argv[1]
        ''' my chemsphder token '''
        self.cs=ChemSpider('d1778a9f-c41f-41f6-920e-fc6d9ff739ca')

    def querySMILEs(self):
        '''
        Read CAS file as input
        To calculate SMILEs through querying chemspider
        '''
        index_num=-1
        self.CAS = []
        self.SMILEs=[]
        self.missing = []
        with open (self.CAS_file,'rb') as csvfile:
            csv_read=csv.reader(csvfile,delimiter=',')
            for row in csv_read:
                index_num += 1
                row = row[0]
                row = row.split('//')
                row = row[0]
                chem_this=self.cs.search(row)
                try:
                    print "Working on chemical ", index_num, row
        #             raw_input(chem_this[0].smiles)
                    self.CAS.append(row)
                    self.SMILEs.append(chem_this[0].smiles)
                except IndexError:
                    print "Can't find index: ", index_num, row
                    self.SMILEs.append(row)
                    self.missing.append(index_num)
                    continue
        
        # delete missing rows        
        for index in sorted(self.missing,reverse=True):
            del self.CAS[index]
            del self.SMILEs[index]
        
        # Clean up SMILEs
        self._cleanSMILEs()
        
        # Write SMILEs
        self._writeSEMILs()
       
        return self.SMILEs
    
    def _writeSEMILs(self):
           
        resultsfile=open('./cas/SMILEs.csv','wb')
        wr=csv.writer(resultsfile,dialect='excel')
        for eachSMILEs in self.SMILEs:
            wr.writerow([eachSMILEs])
    
    def _cleanSMILEs(self):
        ''' 
        Clean up SMILEs
        Make sure there is not '+', "-", and "."
        '''
        assert self.SMILEs is not None
        for indx, eachSMILEs in enumerate(self.SMILEs):
            eachSMILEs = eachSMILEs.replace("+","")
            eachSMILEs = eachSMILEs.replace("-","")
            eachSMILEs = eachSMILEs.replace(".","")
            self.SMILEs[indx] = eachSMILEs
        print "SMILEs have been cleaned up!"
        
    def calculateDescs(self):
        '''
        Use subprocess to call Dragon command line shell
        And calculate predefined descriptors.
        
        These descriptors are suited for the LCIA module at this time
        '''
        dragonShellCall = "./Dragon/dragon6shell.exe"
        dragonScriptCall = "./Dragon/test_script.drs"
        proc = sb.Popen([dragonShellCall,"-s" ,dragonScriptCall])
        
    
if __name__ == '__main__':
    try: 
        thisLook = make_descs(sys.argv)
        smilesOut = thisLook.querySMILEs()
        thisLook.calculateDescs()
    except IndexError:
        print "Please provide a CAS file"