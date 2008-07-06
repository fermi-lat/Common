
from pSafeROOT import ROOT

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm
from pAlarmBaseAlgorithm import ROOT2NUMPYDICT

import pUtils
import numpy
import types

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
    OUTPUT_DICTIONARY    = {'num_warning_entries': 0,
                            'num_error_entries'  : 0,
                            'warning_entries'    : [],
                            'error_entries'      : []
                            }
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
        self.RootTree.SetBranchStatus('*', 0)
        self.RootTree.SetBranchStatus(self.RootObject.GetName(), 1)
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
            shape = branchName.replace(self.RootObject.GetName(), '')
            shape = shape.replace('][', ',')
            shape = shape.replace('[', '(').replace(']', ')')
            shape = eval(shape)
            if type(shape) == types.IntType:
                shape = eval('(%d,)' % shape)
            self.IndexLabels = ['index %d' % i for (i, dim) in enumerate(shape)]
            variableType = branchName.split('_')[-1].split('[')[0]
            if variableType == 'TowerPlane':
                self.IndexLabels = ['tower', 'plane']
            elif variableType == 'Tower':
                self.IndexLabels = ['tower']
            elif variableType == 'GARC':
                self.IndexLabels = ['garc']
            elif variableType == 'AcdTile':
                self.IndexLabels = ['tile']
	self.BranchArray = numpy.zeros(shape, ROOT2NUMPYDICT[branchType])
        self.RootTree.SetBranchAddress(self.RootObject.GetName(),\
                                       self.BranchArray)

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

    def run(self):
        badnessDict = {}
        self.__createArrays()
        self.__setupIndexList()
        for i in range(self.NumTreeEntries):
            self.getEntry(i)
            flatArray = self.BranchArray.flatten()
            for j in self.IndexList:
                value = flatArray[j]
                badnessDict[self.getBadness(value)] = value
                self.checkStatus(j, value, 'value')
        badnessList = badnessDict.keys()
        badnessList.sort()
        maxBadness = badnessList[-1]
        self.Output.setValue(badnessDict[maxBadness])
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
