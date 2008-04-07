
from pSafeROOT import ROOT

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm
from pAlarmBaseAlgorithm import ROOT2NUMPYDICT

import pUtils
import numpy
import types
import math

## @brief Make sure all the entries of a branch are within limits.
#
#  The algorithm loops over the entries of the branch and makes sure that
#  all the values are within the limits.
#
#  The algorithm itself is quite complicated and deserves some comment.
#  At the beginning the (optional) <tt>exclude</tt> and <tt>only</tt>
#  parameters are processed and the list of indexes to loop on is created---by
#  default the loop is done, for each single event, over all the array
#  dimensions.
#
#  There's a relevant consideration to be made here; there are actually
#  two different "coordinate systems" identifying the position of an element
#  into an array: the natural array system and the one in which the array
#  itself is mapped onto a monodimensional space. A <tt>a[2][2]</tt> array,
#  for instance can be mapped into an <tt>a[4]</tt> monodimensional array.
#  In this context the natural representation is used in all the IO interfaces
#  to and from the outside (i.e. while passing <tt>exclude</tt> and
#  <tt>only</tt> parameters and while writing entries into the output details);
#  the monodimensional representation is used in the internal loop, instead
#  (all the arrays are flattened before processing each single event).
#
#  Three arrays are created at the beginning and initialized to 0: the array
#  for the timestamps, the array for the actual values and the array for
#  the errors. Given a branch name, the name of the branch containing the
#  errors is assumed to be called exactly like the main one, with a "_err"
#  prepended (and also assumed to be of the same type and shape).
#  The only exception is consitured by the "Counter_" variables, for which
#  the error is assumed to be the square root of the value.
#
#  The way the statistical errors are taken into account, here, is probably
#  not the optimal one (though perfectly correct) but changing it would
#  require too many modifications. Essentially for each single value, the
#  two values:
#  @f[
#  v_- = v - n_{\sigma} \cdot \Delta v
#  @f]
#  and
#  @f[
#  v_+ = v + n_{\sigma} \cdot \Delta v
#  @f]
#  (where the number of sigma is exactly the <tt>num_bound_sigma</tt> parameter
#  passed via the xml file and defaulting to 3) are calculated and the status
#  of the point is checked against the one with the lowest badness.
#  That implies that, in case an error or a warning has to be issued, the
#  number in the detailed dictionary is not the value in the tree corresponding
#  to the particular timestamp, but the value plus or minus a certain number
#  of error bars. As mentioned before, this might not be optimal; the whole
#  thing is mentioned explicitely in the values of the output detailed
#  dictionary to avoid confusion.
#
#  <b>Valid parameters</b>:
#
#  @li <tt>exclude</tt>: a list of array indexes to be excluded from the event
#  loop.
#  <br>
#  @li <tt>only</tt>: the list of indexes to loop on.
#  <br>
#  @li <tt>num_bound_sigma</tt>: the number of sigma a single point has to be
#  out of the limits before a warning or an error is issued.
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
    SUPPORTED_PARAMETERS = ['exclude', 'only', 'num_bound_sigma']
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
    ## @param timeBranchName
    #  The name of the branch identifying the timestamp (used in the output
    #  detailed dictionary).

    def __createArrays(self, timeBranchName = 'TimeStampFirstEvt'):
        self.RootTree = self.RootObject.GetTree()
        (branchName, branchType) = self.RootObject.GetTitle().split('/')
        if '[' not in branchName:
            shape = (1)
        else:
            shape = branchName.replace(self.RootObject.GetName(), '')
            shape = shape.replace('][', ',')
            shape = shape.replace('[', '(').replace(']', ')')
            shape = eval(shape)
        self.TimestampArray = numpy.zeros((1), 'd')
	self.BranchArray = numpy.zeros(shape, ROOT2NUMPYDICT[branchType])
        valueBranchName = self.RootObject.GetName()
        errorBranchName = '%s_err' % valueBranchName
        self.RootTree.SetBranchStatus('*', 0)
        self.RootTree.SetBranchStatus(timeBranchName, 1)
        self.RootTree.SetBranchAddress(timeBranchName, self.TimestampArray)
        self.RootTree.SetBranchStatus(valueBranchName, 1)
        self.RootTree.SetBranchAddress(valueBranchName, self.BranchArray)
        if branchName[:8] != 'Counter_':
            self.__branchIsCounter = False
            self.ErrorArray = numpy.zeros(shape, ROOT2NUMPYDICT[branchType])
            self.RootTree.SetBranchStatus(errorBranchName, 1)
            self.RootTree.SetBranchAddress(errorBranchName, self.ErrorArray)
        else:
            self.__branchIsCounter = True

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

    def run(self):
        numBoundSigma = self.getParameter('num_bound_sigma', 3.0)
        badnessDict = {}
        self.__createArrays()
        self.__setupIndexList()
        for i in range(self.RootObject.GetEntries()):
            self.RootTree.GetEntry(i)
            valueFlatArray = self.BranchArray.flatten()
            if not self.__branchIsCounter:
                errorFlatArray = self.ErrorArray.flatten()
            for j in self.IndexList:
                value = valueFlatArray[j]
                if not self.__branchIsCounter:
                    error = errorFlatArray[j]
                else:
                    error = math.sqrt(value)
                minusValue = value - numBoundSigma*error
                plusValue = value + numBoundSigma*error
                minusBadness = self.getBadness(minusValue)
                plusBadness = self.getBadness(plusValue)
                if minusBadness < plusBadness:
                    value = minusValue
                    badnessDict[minusBadness] = value
                    label = 'value - %.1f sigma' % numBoundSigma
                else:
                    value = plusValue
                    badnessDict[plusBadness] = value
                    label = 'value + %.1f sigma' % numBoundSigma
                self.checkStatus(j, value, label)
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
    valueBranchName = 'valueBranch'
    errorBranchName = '%s_err' % valueBranchName
    testFile = ROOT.TFile(testFilePath, 'RECREATE')
    testTree = ROOT.TTree(testTreeName, testTreeName)
    timeArray = array.array('d', [0.0])
    valueArray = array.array('d', [0.0])
    errorArray = array.array('d', [0.0])
    testTree.Branch(timeBranchName, timeArray, '%s/D' % timeBranchName)
    testTree.Branch(valueBranchName, valueArray, '%s/D' % valueBranchName)
    testTree.Branch(errorBranchName, errorArray, '%s/D' % errorBranchName)
    for i in range(20):
        timeArray[0] = i*10.0
        valueArray[0] = random.gauss(0, 1)
        errorArray[0] = 0.1*abs(valueArray[0])
        testTree.Fill()
    testFile.Write()
    testTree.Draw('(valueBranch+3*valueBranch_err):TimeStampFirstEvt', '', '*')
    testTree.Draw('(valueBranch-3*valueBranch_err):TimeStampFirstEvt', '',\
                      '*same')
    valueBranch = testTree.GetBranch(valueBranchName)
    pardict = {}
    algorithm = alg__values(limits, valueBranch, pardict)
    algorithm.apply()
    print algorithm.Output
    testFile.Close()
    import os
    os.system('rm -f %s' % testFilePath)
