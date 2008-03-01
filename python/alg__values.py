
from pSafeROOT import ROOT

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm, ROOT2NUMPYDICT

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

    def __createArrays(self, timestampBranchName = 'TimeStampFirstEvt'):
        self.RootTree = self.RootObject.GetTree()
        self.TimestampArray = numpy.zeros((1), 'd')
        self.RootTree.SetBranchAddress(timestampBranchName,\
                                       self.TimestampArray)
        (branchName, branchType) = self.RootObject.GetTitle().split('/')
        if '[' not in branchName:
            shape = (1)
        else:
            shape = branchName.replace(self.RootObject.GetName(), '')
            shape = shape.replace('][', ',')
            shape = shape.replace('[', '(').replace(']', ')')
            shape = eval(shape)
	self.BranchArray = numpy.zeros(shape, ROOT2NUMPYDICT[branchType])
        self.RootTree.SetBranchAddress(self.RootObject.GetName(),\
                                       self.BranchArray)

    ## @brief Get the label for the output detailed dictionary when an entry
    #  causes a warning or an error.
    ## @param self
    #  The class instance.
    ## @param value
    #  The value which is out of range.
    ## @param index
    #  The index of the flattened numpy array corresponding to the bad value.

    def getOutputDictLabel(self, value, index):
        value = pUtils.formatNumber(value)
        if self.BranchArray.size == 1:
            return 'Time bin starting @ %f, value = %s'  %\
	        (self.TimestampArray[0], value)
        position = self.flat2tuple(index)
        if len(position) == 1:
            position = '[%d]' % position[0]
        else:
            position = str(position).replace('(', '[').replace(')', ']')
        return 'Time bin starting @ %f, array index = %s,  value = %s'  %\
            (self.TimestampArray[0], position, value)

    def flat2tuple(self, flatIndex):
        return numpy.unravel_index(flatIndex, self.BranchArray.shape)
         

    def tuple2flat(self, tupleIndex):
        if type(tupleIndex) == types.IntType:
            tupleIndex = (tupleIndex,)
        index = 0
        shape = self.BranchArray.shape
        numDimensions = len(shape)
        for i in range(numDimensions):
            factor = 1
            for j in shape[(i+1):]:
                factor *= j
            index += factor*tupleIndex[i]
        return index
            
    ## @brief Check that a particular branch values lies within limits and
    #  take the necessary actions if not (i.e. fill the output detailed
    #  dictionary).
    ## @param self
    #  The class instance.
    ## @param value
    #  The branch value.
    ## @param index
    #  The index of the flattened numpy array.

    def checkValue(self, value, index):
	if value < self.Limits.ErrorMin:
            label = self.getOutputDictLabel(value, index)
            self.Output.incrementDictValue('num_error_entries')
            self.Output.appendDictValue('error_entries', label)
            delta = (self.Limits.ErrorMin - value)*10000
        elif value > self.Limits.ErrorMax:
            label = self.getOutputDictLabel(value, index)
            self.Output.incrementDictValue('num_error_entries')
            self.Output.appendDictValue('error_entries', label)
            delta = (value - self.Limits.ErrorMax)*10000
        elif value < self.Limits.WarningMin:
            label = self.getOutputDictLabel(value, index)
            self.Output.incrementDictValue('num_warning_entries')
            self.Output.appendDictValue('warning_entries', label)
            delta = (self.Limits.WarningMin - value)*100
        elif value > self.Limits.WarningMax:
            label = self.getOutputDictLabel(value, index)
            self.Output.incrementDictValue('num_warning_entries')
            self.Output.appendDictValue('warning_entries', label)
            delta = (value - self.Limits.WarningMax)*100
        else:
            delta = max((self.Limits.WarningMax - value),\
                        (value - self.Limits.WarningMin))
        self.DeltaDict[delta] = value        

    def run(self):
        self.DeltaDict = {}
        self.__createArrays()
	try:
            indexList = []
            for tupleIndex in self.ParamsDict['only']:
                indexList.append(self.tuple2flat(tupleIndex))
        except KeyError:
            indexList = range(self.BranchArray.size)
            try:
                for tupleIndex in self.ParamsDict['exclude']:
                    indexList.remove(self.tuple2flat(tupleIndex))
            except KeyError:
                pass
        for i in range(self.RootObject.GetEntries()):
            self.RootTree.GetEntry(i)
            flatArray = self.BranchArray.flatten()
            for j in indexList:
                self.checkValue(flatArray[j], j)
        deltas = self.DeltaDict.keys()
        deltas.sort()
        self.Output.setValue(self.DeltaDict[deltas[-1]])
        
            

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
