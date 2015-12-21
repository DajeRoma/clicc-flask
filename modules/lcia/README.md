# Stremlined Predictive LCIA Module

These modules serve the purpose of estimating chemical LCIA using Artificial Neural Networks in command line

Necessary Packages:
Pybrain:http://pybrain.org/

Pybrain Wrapper for CLiCC Project: 
https://github.com/RunshengSong/CLiCC_Packages
And Numpy, Scikit-learn and Pandas



make_descs.py:  Calculate predefined chemical descriptors via Dragon 6, must have license
                Call >python make_descs.py [CAS_FILE]   (example: ./cas/cas_inputs.csv)

predict.py: Estimate chemical LCIA taking descriptors, ANNs as input
            Call > predict.py -n [Networks] -d [Descs] -t [TrnData]

caller.py: An example about how to use predict.py

