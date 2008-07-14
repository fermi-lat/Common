
import pSafeLogger
logger = pSafeLogger.getLogger('alg__values')

from pSafeROOT import ROOT

import pUtils
import numpy
import types
import sys
import time

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm
from pAlarmBaseAlgorithm import ROOT2NUMPYDICT
from pAlarmBaseAlgorithm import MET_OFFSET
from pGlobals            import MINUS_INFINITY


VAR_LABELS_DICT = {'Tower': ['tower'],
                   'TowerPlane': ['tower', 'plane'],
                   'TowerPlaneGTFE': ['tower', 'plane', 'gtfe'],
                   'TowerCalLayer': ['tower', 'layer'],
                   'TowerCalLayerCalColumn': ['tower', 'layer', 'column'],
                   'TowerCalLayerCalColumnR': ['tower', 'layer', 'column',
                                               'face'],
                   'TowerCalLayerCalColumnFR': ['tower', 'layer', 'column',
                                                'face', 'range'],
                   'GARC': ['garc'],
                   'AcdTile': ['tile'],
                   'XYZ': ['xyz'],
                   'ReconNumTracks': ['num. tracks'],
                   'GammaFilterBit': ['filter bit'],
                   'TriggerEngine': ['trg. engine']
                   }

MIN_TRUE_TIME_INTERVAL = 5.0

## @brief Make sure all the entries of a branch are within limits.
#
#  The algorithm loops over the entries of the branch and makes sure that
#  all the values are within the limits.
#
#  <b>Output value</b>:
#
#  The value of the entry which is "more" out of the limits.
#
#  <b>Output details</b>:
#
#  @li <tt>num_warning_entries</tt>: the number of warning entries.
#  <br>
#  @li <tt>num_error_entries</tt>: the number of error entries.
#  <br>
#  @li <tt>warning_entries</tt>: the detailed list of warning entries. 
#  <br>
#  @li <tt>error_entries</tt>: the detailed list of error entries. 
#  <br>


class alg__values(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TBranch']
    SUPPORTED_PARAMETERS = ['exclude', 'only']
    OUTPUT_LABEL          = 'The worst entry of the branch'

    ## @brief Create all the necessary arrays for the loop over the
    #  TBranch entries.
    ## @param self
    #  The class instance.
    ## @param timestampBranchName
    #  The name of the branch identifying the timestamp (used in the output
    #  detailed dictionary).

    def __createArrays(self):
        self.RootTree = self.RootObject.GetTree()
        self.NumTreeEntries = self.RootObject.GetEntries()
        valueBranchName = self.RootObject.GetName()
        errorBranchName = '%s_err' % valueBranchName
        self.RootTree.SetBranchStatus('*', 0)
        self.RootTree.SetBranchStatus(valueBranchName, 1)
        self.RootTree.SetBranchStatus('Bin_Start', 1)
        self.RootTree.SetBranchStatus('Bin_End', 1)
        self.RootTree.SetBranchStatus('TrueTimeInterval', 1)
        self.BinStartArray = numpy.zeros((1), 'l')
        self.BinEndArray = numpy.zeros((1), 'l')
        self.TimeIntervalArray = numpy.zeros((1), 'd')
        self.RootTree.SetBranchAddress('Bin_Start', self.BinStartArray)
        self.RootTree.SetBranchAddress('Bin_End', self.BinEndArray)
        self.RootTree.SetBranchAddress('TrueTimeInterval',
                                       self.TimeIntervalArray)
        (branchName, branchType) = self.RootObject.GetTitle().split('/')
        if '[' not in branchName:
            shape = (1)
        else:
            shape = branchName.replace(valueBranchName, '')
            shape = shape.replace('][', ',')
            shape = shape.replace('[', '(').replace(']', ')')
            shape = eval(shape)
            if type(shape) == types.IntType:
                shape = eval('(%d,)' % shape)
            variableType = branchName.split('_')[-1].split('[')[0]
            try:
                self.IndexLabels = VAR_LABELS_DICT[variableType]
            except KeyError:
                self.IndexLabels =\
                    ['index %d' % i for (i, dim) in enumerate(shape)]
	self.BranchArray = numpy.zeros(shape, ROOT2NUMPYDICT[branchType])
        self.RootTree.SetBranchAddress(self.RootObject.GetName(),\
                                       self.BranchArray)
        self.ErrorArray = numpy.zeros(shape, ROOT2NUMPYDICT[branchType])
        if self.RootTree.GetBranch(errorBranchName) is not None:
            self.RootTree.SetBranchStatus(errorBranchName, 1)
            self.RootTree.SetBranchAddress(errorBranchName, self.ErrorArray)
        else:
            logger.debug('%s has no associated errors.' % branchName)

    ## @brief Setup the list of indexes to loop over, taking into account
    #  the optional "exclude" and "only" parameters.
    ## @param self
    #  The class instance.

    def __setupIndexList(self):
        if 'only' in self.ParamsDict.keys():
            self.IndexList = []
            for position in self.ParamsDict['only']:
                index = self.tuple2Index(position, self.BranchArray.shape)
                self.IndexList.append(index)
        else:
            self.IndexList = range(self.BranchArray.size)
            try:
                for position in self.ParamsDict['exclude']:
                    index = self.tuple2Index(position, self.BranchArray.shape)
                    self.IndexList.remove(index)
            except KeyError:
                pass
            
    ## @brief Get a given entry of the ROOT tree and set the timestamp.

    def getEntry(self, index):
        self.RootTree.GetEntry(index)
        if index == 0:
            binStart = self.BinEndArray[0] - self.TimeIntervalArray[0]
            binEnd = self.BinEndArray[0]
        elif index == self.NumTreeEntries - 1:
            binStart = self.BinStartArray[0]
            binEnd = self.BinStartArray[0] + self.TimeIntervalArray[0]
        else:
            binStart = self.BinStartArray[0]
            binEnd = self.BinEndArray[0]
        self.TimeStamp = (binStart + binEnd)/2.0

    ## @brief Convert the indexes of the alarm exception (if any) from tuple
    #  to flat numbers, in asuch a way that the opposite conversion does not
    #  have to be done for each event while checking the status.
        
    def setupException(self):
        if self.Exception is None:
            return 
        for (i, detail) in enumerate(self.Exception.FlippedDetails):
            self.Exception.FlippedDetails[i] =\
                self.tuple2Index(detail, self.BranchArray.shape)

    def run(self):
        maxBadness = MINUS_INFINITY
        self.__createArrays()
        self.__setupIndexList()
        self.setupException()
        for i in range(self.NumTreeEntries):
            self.getEntry(i)
            if self.TimeIntervalArray[0] > MIN_TRUE_TIME_INTERVAL:
                valueFlatArray = self.BranchArray.flatten()
                errorFlatArray = self.ErrorArray.flatten()
                for j in self.IndexList:
                    value = valueFlatArray[j]
                    error = errorFlatArray[j]
                    badness = self.checkStatus(j, value, 'value', error)
                    if badness > maxBadness:
                        maxBadness = badness
                        (outputEntry, outputIndex, outputValue, outputError) =\
                            (i, j, value, error)
            else:
                logger.info('Skipping entry %d (TrueTimeInterval = %f)...' %\
                                (i, self.TimeIntervalArray[0]))
        self.Output.setValue(outputValue, outputError, maxBadness)
        self.getEntry(outputEntry)
        try:
            label = self.getDetailedLabel(outputIndex, outputValue, 'value',\
                                              outputError)
            label = '%s, badness = %s' % (label,\
                                              pUtils.formatNumber(maxBadness)) 
            self.Output.setDictValue('output_point', label)
        except:
            pass
        self.RootTree.SetBranchStatus('*', 1)

            

if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    limits = pAlarmLimits(-2, 2, -2.5, 2.5)   
    import array
    import numpy
    import random
    testFilePath = './test.root'
    testTreeName = 'testTree'
    timeBranchName = 'TimeStampFirstEvt'
    testBranchName = 'testBranch'
    testFile = ROOT.TFile(testFilePath, 'RECREATE')
    testTree = ROOT.TTree(testTreeName, testTreeName)
    timeArray = array.array('d', [0.0])
    testArray = array.array('d', [0.0])
    testTree.Branch(timeBranchName, timeArray, '%s/D' % timeBranchName)
    testTree.Branch(testBranchName, testArray, '%s/D' % testBranchName)
    for i in range(100):
        timeArray[0] = i
        testArray[0] = random.gauss(0, 1)
        testTree.Fill()
    testFile.Write()
    testTree.Draw('testBranch:TimeStampFirstEvt', '', '*')
    testBranch = testTree.GetBranch(testBranchName)
    pardict = {}
    algorithm = alg__values(limits, testBranch, pardict)
    algorithm.apply()
    print algorithm.Output
    testFile.Close()
    import os
    os.system('rm -f %s' % testFilePath)
