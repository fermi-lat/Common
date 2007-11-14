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
    
    def __init__(self, xmlParser, inputFilePath, rootTreeName, outputFilePath):
        self.XmlParser      = xmlParser
        self.InputFilePath  = inputFilePath
        self.RootTreeName   = rootTreeName
        if outputFilePath is None:
            outputFilePath = inputFilePath.replace('.root', '.processed.root')
        self.OutputFilePath = os.path.abspath(outputFilePath)

        outputFileDir = os.path.split(self.OutputFilePath)[0]
        if not os.path.exists(outputFileDir):
            os.makedirs(outputFileDir)
            logger.debug('Creating new directory to store output files: %s' %\
                         outputFileDir )

    def open(self):
        self.InputFile  = ROOT.TFile(self.InputFilePath)
        self.RootTree   = self.InputFile.Get(self.RootTreeName)
        if self.RootTree is None:
            sys.exit('Could not find TTree %s in %s.' % (self.RootTreeName,\
                                                         self.InputFilePath))
        self.OutputFile = ROOT.TFile(self.OutputFilePath, 'recreate')

    ## @brief Close the output ROOT file.
    ## @param self
    #  The class instance.

    def close(self):
        self.OutputFile.Write()
        self.OutputFile.Close()
        self.InputFile.Close()

    ## @param self
    #  The class instance.

    def run(self, numEntries):
        logger.info('Processing the root tree and writing histograms...')
        startTime = time.time()
        self.open()
        self.createObjects(numEntries)
        logger.info('Done in %.2f s.\n' % (time.time() - startTime))
        self.close()

    ## @brief Create the ROOT objects defined in the enabled output lists
    #  of the xml configuration file.
    ## @param self
    #  The class instance.

    def createObjects(self, numEntries):
        for rep in self.XmlParser.EnabledPlotRepsDict.values():
            try:
                rep.createRootObject(self.RootTree, numEntries)
            except:
                logger.error('Could not create %s.' % rep.Name)
