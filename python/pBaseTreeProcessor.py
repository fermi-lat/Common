## @package pBaseTreeProcessor
## @brief Module providing functions for processing a ROOT tree and producing
#  a new ROOT file with histograms, plots, etc..

import pSafeLogger
logger = pSafeLogger.getLogger('pBaseTreeProcessor')

import os
import time
import sys

from pSafeROOT import ROOT


## @brief Implementation of the ROOT tree processor.

class pBaseTreeProcessor:

    ## @brief Constructor.
    ## @param self
    #  The class instance.
    ## @param xmlParser
    #  The xml parser containing the requested output lists.
    ## @param inputFilePath
    #  Path to the input ROOT file.
    ## @param outputFilePath
    #  Path to the output ROOT file.
    
    def __init__(self, xmlParser, inputFilePath, treeName,\
                 outputFilePath = None):

        ## @var XmlParser
        ## @brief The xml parser containing the requested output lists.

        ## @var InputFilePath
        ## @brief Path to the input ROOT TFile object.

        ## @var InputFile
        ## @brief The input ROOT TFile object.

        ## @var OutputFilePath
        ## @brief Path to the output ROOT file.

        ## @var OutputFile
        ## @brief The output ROOT TFile object.

        ## @var RootTree
        ## @brief The ROOT TTree object to be read from the input file.
        
        self.XmlParser     = xmlParser
        self.InputFile     = ROOT.TFile(inputFilePath)
        self.RootTree      = self.InputFile.Get(treeName)
        if self.RootTree is None:
            sys.exit('Could not find TTree %s in %s.' % (treeName,\
                                                         self.InputFilePath))
        if outputFilePath is None:
            outputFilePath = inputFilePath.replace('.root', '.processed.root')
        self.OutputFile    = ROOT.TFile(outputFilePath, 'recreate')

    ## @brief Close the output ROOT file.
    ## @param self
    #  The class instance.

    def closeOutputFile(self):
        self.OutputFile.Write()
        self.OutputFile.Close()

    ## @param self
    #  The class instance.

    def process(self):
        logger.info('Processing the root tree and writing histograms...')
        startTime = time.time()
        self.__createObjects()
        logger.info('Done in %.2f s.\n' % (time.time() - startTime))
        self.closeOutputFile()

    ## @brief Create the ROOT objects defined in the enabled output lists
    #  of the xml configuration file.
    ## @param self
    #  The class instance.

    def __createObjects(self):
        for rep in self.XmlParser.EnabledPlotRepsDict.values():
            rep.createRootObjects(self.RootTree)
