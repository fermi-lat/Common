
from pSafeROOT import ROOT

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm

import pUtils
import numpy

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
    SUPPORTED_PARAMETERS = []
    OUTPUT_DICTIONARY    = {'num_warning_entries': 0,
                            'num_error_entries'  : 0,
                            'warning_entries'    : [],
                            'error_entries'      : []
                            }
    OUTPUT_LABEL          = 'The most "out of range" entry of the branch'

    ## @brief Create all the necessary arrays for the loop over the
    #  TBranch entries.
    ## @param self
    #  The class instance.
    ## @param timestampBranchName
    #  The name of the branch identifying the timestamp (used in the output
    #  detailed dictionary).

    def __createArrays(self, timestampBranchName = 'TimeStampFirstEvt'):
        self.RootTree = self.RootObject.GetTree()
        self.RootLeaf = self.RootTree.GetLeaf(self.RootObject.GetName())
        self.TimestampArray = numpy.zeros((1), 'd')
        self.RootTree.SetBranchAddress(timestampBranchName,\
                                       self.TimestampArray)
        (name, type) = self.RootObject.GetTitle().split('/')
        if '[' not in name:
            shape = (1)
        else:
            shape = name.replace(self.RootObject.GetName(), '')
            shape = shape.replace('][', ',')
            shape = shape.replace('[', '(').replace(']', ')')
            shape = eval(shape)
        self.BranchArray = numpy.zeros(shape, type.lower())
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
        position = self.getArrayPosition(index)
        return 'Time bin starting @ %f, array index = %s,  value = %s'  %\
               (self.TimestampArray[0], position, value)

    ## @brief Go back from the index of the flattened array to the position
    #  in the original multidimensional array.
    ## @param self
    #  The class instance.
    ## @param index
    #  The index of the flattened numpy array.

    def getArrayPosition(self, index):
        position = []
        for i in range(self.BranchArray.ndim):
            fact = 1
            for j in range(i + 1, self.BranchArray.ndim):
                fact *= int(self.BranchArray.shape[j])
            position.append(index/fact)
            index -= index/fact*fact
        return position

    def run(self):
        deltaDict = {}
        self.__createArrays()
        for i in range(self.RootObject.GetEntries()):
            self.RootTree.GetEntry(i)
            j = 0
            for value in self.BranchArray.flat:
                if value < self.Limits.ErrorMin:
                    label = self.getOutputDictLabel(value, j)
                    self.Output.incrementDictValue('num_error_entries')
                    self.Output.appendDictValue('error_entries', label)
                    delta = (self.Limits.ErrorMin - value)*10000
                elif value > self.Limits.ErrorMax:
                    label = self.getOutputDictLabel(value, j)
                    self.Output.incrementDictValue('num_error_entries')
                    self.Output.appendDictValue('error_entries', label)
                    delta = (value - self.Limits.ErrorMax)*10000
                elif value < self.Limits.WarningMin:
                    label = self.getOutputDictLabel(value, j)
                    self.Output.incrementDictValue('num_warning_entries')
                    self.Output.appendDictValue('warning_entries', label)
                    delta = (self.Limits.WarningMin - value)*100
                elif value > self.Limits.WarningMax:
                    label = self.getOutputDictLabel(value, j)
                    self.Output.incrementDictValue('num_warning_entries')
                    self.Output.appendDictValue('warning_entries', label)
                    delta = (value - self.Limits.WarningMax)*100
                else:
                    delta = max((self.Limits.WarningMax - value),\
                                (value - self.Limits.WarningMin))
                deltaDict[delta] = value
                j += 1
        deltas = deltaDict.keys()
        deltas.sort()
        self.Output.setValue(deltaDict[deltas[-1]])
        
            

if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    limits = pAlarmLimits(-2, 2, -3, 3)   
    import array
    import numpy
    import random
    testFilePath = './test.root'
    testTreeName = 'testTree'
    timeBranchName = 'TimeStampFirstEvt'
    testBranchName = 'testBranch'
    testFile = ROOT.TFile(testFilePath, 'RECREATE')
    testTree = ROOT.TTree(testTreeName, testTreeName)
    timeArray = array.array('f', [0.0])
    testArray = array.array('f', [0.0])
    testTree.Branch(timeBranchName, timeArray, '%s/F' % timeBranchName)
    testTree.Branch(testBranchName, testArray, '%s/F' % testBranchName)
    for i in range(100):
        timeArray[0] = i
        testArray[0] = random.gauss(0, 1)
        testTree.Fill()
    testFile.Write()
    testBranch = testTree.GetBranch(testBranchName)
    pardict = {}
    algorithm = alg__values(limits, testBranch, pardict)
    algorithm.apply()
    print algorithm.Output
    testFile.Close()
    import os
    os.system('rm -f %s' % testFilePath)
