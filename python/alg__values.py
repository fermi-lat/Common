
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
from pAlarmLimits        import WARNING_BADNESS


VAR_LABELS_DICT = {
    'Tower': ['tower'],
    'TowerPlane': ['tower', 'plane'],
    'TowerPlaneGTFE': ['tower', 'plane', 'gtfe'],
    'TowerCalLayer': ['tower', 'layer'],
    'TowerCalLayerCalColumn': ['tower', 'layer', 'column'],
    'TowerCalLayerCalColumnR': ['tower', 'layer', 'column', 'face'],
    'TowerCalLayerCalColumnFR': ['tower', 'layer', 'column', 'face', 'range'],
    'GARC': ['garc'],
    'AcdTile': ['tile'],
    'XYZ': ['xyz'],
    'ReconNumTracks': ['number of tracks'],
    'GammaFilterBit': ['filter bit'],
    'TriggerEngine': ['trigger engine']
    }

LINK_LABELS_DICT = {
    'Tower': ['tower'],
    'TowerPlane': ['tower', 'plane'],
    'TowerPlaneGTFE': ['tower', 'plane', 'gtfe'],
    'TowerCalLayer': ['tower', 'callayer'],
    'TowerCalLayerCalColumn': ['tower', 'callayer', 'calcolumn'],
    'TowerCalLayerCalColumnR': ['tower', 'callayer', 'calcolumn', 'calxface'],
    'TowerCalLayerCalColumnFR': ['tower', 'callayer', 'calcolumn', 'calxface',\
                                 'range'],
    'GARC': ['garc'],
    'AcdTile': ['acdtile'],
    'XYZ': ['xyz'],
    'ReconNumTracks': ['reconnumtracks'],
    'GammaFilterBit': ['gammafilterbit'],
    'TriggerEngine': ['triggerengine']
    }

MIN_TRUE_TIME_INTERVAL = 10.0

## @brief Make sure all the entries of a branch are within limits.
#
#  The algorithm loops over the entries of the branch and makes sure that
#  all the values are within the limits.
#
#  <b>Valid parameters</b>:
#
#  @li <tt>exclude</tt>: a list of indexes of the branch array to be excluded.
#  <br>
#  @li <tt>only</tt>: the list of indexes the alarm has to run on.
#  <br>
#  @li <tt>num_sigma</tt>: multiplicative factor for the error bars.
#  <br>
#  @li <tt>min_n<tt>: the minimum value of branch_name_n, below which the alarm
#  is disengaged.
#  <br>
#  @li <tt>max_rel_err<tt>: the maximum relative error Delta v/v on the single
#  data point, above which the alarm is disengaged.
#  <br>
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


MIN_N_MESSAGE = 'Entry %d, index %d ignored (n = %d less than %d)'
MAX_REL_ERR_MESSAGE =\
    'Entry %d, index %d ignored (rel. err. = %.4f larger than %.4f)'


class alg__values(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TBranch']
    SUPPORTED_PARAMETERS = ['exclude', 'only', 'num_sigma',
                            'min_n', 'max_rel_err']
    OUTPUT_LABEL          = 'The worst entry of the branch'

    def __init__(self, limits, object, paramsDict, conditionsDict = {}):
        pAlarmBaseAlgorithm.__init__(self, limits, object, paramsDict,
                                     conditionsDict)
        self.LinksDict = {}

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
            self.VariableType = branchName.split('_')[-1].split('[')[0]
            # This is a brute force fix (see Jira GDQMQ-342)
            if self.VariableType in ['NormRateMeritTriggerEngine',
                                     'NormRateGAMMAFilterAndTriggerEngine',
                                     'NormRateFswGAMMAFilterAndTriggerEngine']:
                self.VariableType = 'TriggerEngine'
            # End of fix (Luca Baldini, March 10, 2010).
            try:
                self.IndexLabels = VAR_LABELS_DICT[self.VariableType]
            except KeyError:
                self.IndexLabels =\
                    ['index %d' % i for (i, dim) in enumerate(shape)]
	self.BranchArray = numpy.zeros(shape, ROOT2NUMPYDICT[branchType])
        self.RootTree.SetBranchAddress(self.RootObject.GetName(),\
                                       self.BranchArray)
        if self.RootTree.GetBranch(errorBranchName) is not None:
            self.ErrorArray = numpy.zeros(shape, ROOT2NUMPYDICT[branchType])
            self.RootTree.SetBranchStatus(errorBranchName, 1)
            self.RootTree.SetBranchAddress(errorBranchName, self.ErrorArray)
            self.__HasErrors = True
        else:
            logger.debug('%s has no associated errors.' % branchName)
            self.__HasErrors = False
        self.__MinEntries = self.getParameter('min_n', None)
        if self.__MinEntries is not None:
            self.__MinEntries = int(self.__MinEntries)
            numEntriesBranchName = '%s_n' % valueBranchName
            if self.RootTree.GetBranch(numEntriesBranchName) is not None:
                self.NumEntriesArray = numpy.zeros(shape, ROOT2NUMPYDICT['I'])
                self.RootTree.SetBranchStatus(numEntriesBranchName, 1)
                self.RootTree.SetBranchAddress(numEntriesBranchName,
                                               self.NumEntriesArray)
                logger.debug('Condition on min_n found, array(s) identified.')
            else:
                logger.error('Could not locate branch %s.' %\
                             numEntriesBranchName)
                self.__MinEntries = None
        self.__MaxRelError = self.getParameter('max_rel_err', None)

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
    #  to flat numbers, in such a way that the opposite conversion does not
    #  have to be done for each event while checking the status.
        
    def setupException(self):
        if self.Exception is not None:
            exceptionsDict = self.Exception.ExceptionsDict
            self.Exception.ExceptionsDict = {}
            for (key, value) in exceptionsDict.items():
                if key != 'status':
                    key = self.tuple2Index(key, self.BranchArray.shape)
                    self.Exception.ExceptionsDict[key] = value

    def run(self):
        linkIndexes = []
        self.setNumSigma()
        maxBadness = MINUS_INFINITY
        self.__createArrays()
        self.__setupIndexList()
        self.setupException()
        for i in range(self.NumTreeEntries):
            self.getEntry(i)
            if self.TimeIntervalArray[0] > MIN_TRUE_TIME_INTERVAL:
                valueFlatArray = self.BranchArray.flatten()
                if self.__HasErrors:
                    errorFlatArray = self.ErrorArray.flatten()
                if self.__MinEntries is not None:
                    numEntriesFlatArray = self.NumEntriesArray.flatten()
                for j in self.IndexList:
                    value = valueFlatArray[j]
                    if self.__HasErrors:
                        error = errorFlatArray[j]*self.NumSigma
                        if value != 0:
                            relError = error/abs(value)
                        else:
                            relError = None
                    else:
                        error = None
                        relError = None
                    if self.__MinEntries is not None:
                        entries = numEntriesFlatArray[j]
                    else:
                        entries = None
                    # Check the condition on the number of entries.
                    if self.__MinEntries is not None and\
                            entries is not None and\
                            entries < self.__MinEntries:
                        message = MIN_N_MESSAGE %\
                            (i, j, entries, self.__MinEntries)
                        logger.info(message)
                        self.Output.appendDictValue('messages', message)
                    # Check the condition on the relative error.
                    elif self.__MaxRelError is not None and\
                            relError is not None and\
                            relError > self.__MaxRelError:
                        message = MAX_REL_ERR_MESSAGE %\
                            (i, j, relError, self.__MaxRelError)
                        logger.info(message)
                        self.Output.appendDictValue('messages', message)
                    # Go ahead and check the limits.
                    else:
                        badness = self.checkStatus(j, value, 'value', error)
                        if badness > WARNING_BADNESS:
                            if j not in linkIndexes:
                                linkIndexes.append(j)
                        if badness > maxBadness:
                            maxBadness = badness
                            (outputEntry, outputIndex,
                             outputValue, outputError) =\
                             (i, j, value, error)
            else:
                logger.info('Skipping entry %d (TrueTimeInterval = %f)...' %\
                                (i, self.TimeIntervalArray[0]))
        try:
            self.Output.setValue(outputValue, outputError, maxBadness)
            self.getEntry(outputEntry)
            label = self.getDetailedLabel(outputIndex, outputValue, 'value',\
                                              outputError)
            label = '%s, badness = %s' % (label,\
                                              pUtils.formatNumber(maxBadness)) 
            self.Output.setDictValue('output_point', label)
            if self.BranchArray.shape != (1, ) and len(linkIndexes):
                labels = LINK_LABELS_DICT[self.VariableType]
                for label in labels:
                    self.LinksDict[label] = []
                for index in linkIndexes:
                    indexTuple = self.index2Tuple(index,self.BranchArray.shape)
                    for (i, value) in enumerate(indexTuple):
                        label = labels[i]
                        if value not in self.LinksDict[label]:
                            self.LinksDict[label].append(value)
                for label in labels:
                    self.LinksDict[label].sort()
        except:
            pass
        self.RootTree.SetBranchStatus('*', 1)

            

if __name__ == '__main__':
    print 'Too difficult to implement a test function, run on a file instead.'
