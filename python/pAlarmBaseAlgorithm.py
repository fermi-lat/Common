## @package pAlarmBaseAlgorithm
## @brief Base package for implementation of algorithms.

import pSafeLogger
logger = pSafeLogger.getLogger('pAlarmBaseAlgorithm')

import pUtils
import types
import numpy

from pAlarmOutput import pAlarmOutput
from pAlarmOutput import STATUS_CLEAN, STATUS_WARNING, STATUS_ERROR
from copy         import copy, deepcopy

ROOT2NUMPYDICT = {'C' : 'c',      #a character string terminated by the 0 char
                  'B' : 'int8',   #an 8 bit signed integer (Char_t)
                  'b' : 'uint8',  #an 8 bit unsigned integer (UChar_t)
                  'S' : 'int16',  #a 16 bit signed integer (Short_t)
                  's' : 'uint16', #a 16 bit unsigned integer (UShort_t)
                  'I' : 'int32',  #a 32 bit signed integer (Int_t)
                  'i' : 'uint32', #a 32 bit unsigned integer (UInt_t)
                  'F' : 'float32',#a 32 bit floating point (Float_t)
                  'D' : 'float64',#a 64 bit floating point (Double_t)
                  'L' : 'int64',  #a 64 bit signed integer (Long64_t)
                  'l' : 'uint64'  #a 64 bit unsigned integer (ULong64_t)
		  }

ERROR_BADNESS_FACTOR   = 1.0e6
WARNING_BADNESS_FACTOR = 1.0e3
CLEAN_BADNESS_FACTOR   = 1.0
	    
## @brief Base class for alarm algorithms. Look at the inheritance diagram for
#  the list of implemented algorithms.
#
#  Provides a general structure for the implementation of the algorithms,
#  along with some ROOT-related useful functions (like setting histogram
#  range etc...).
#
#  The derived classes inheriting from pAlarmBaseAlgorithm have the following
#  responsibilities:
#  
#  @li Define the base variables @ref SUPPORTED_TYPES,
#  @ref SUPPORTED_PARAMETERS, @ref OUTPUT_DICTIONARY and @ref OUTPUT_LABEL.
#
#  @li Implement the core of the actual algorithm in such a way it gets
#  executed when the base function apply() is called. Depending on the
#  algorithm itself it may be embedded into an overloaded run() method or
#  (if different ROOT objects must be treated in diffent ways) runROOTTYPE()
#  method (i. e. runTH1F(), runTH2F() etc.)
#  The implementation of apply() first check whether a function of this last
#  form exists for execution and, if that's not the case, just call the run()
#  method.


class pAlarmBaseAlgorithm:

    ## @var SUPPORTED_TYPES
    ## @brief The list of ROOT object types which are supported by a given
    #  algorithm.

    ## @var SUPPORTED_PARAMETERS
    ## @brief The list of (optional) parameters supported by a given
    #  algorithm.

    ## @var OUTPUT_DICTIONARY
    ## @brief The initial value of the output dictionary containing the
    #  details for the alarms.

    ## @var OUTPUT_LABEL
    ## @brief A brief string representing what the output value actually
    #  represents.

    SUPPORTED_TYPES      = []
    SUPPORTED_PARAMETERS = []
    OUTPUT_DICTIONARY    = {}
    OUTPUT_LABEL         = 'N/A'

    ## @brief Basic constructor
    ## @param self
    #  The class instance.
    ## @param limits
    #  The alarm limits.
    ## @param object
    #  The ROOT object the alarm is set on.
    ## @param paramsDict
    #  The dictionary of optional algorithm parameters.
    ## @param conditionsDict
    #  The dictionary of algorithm conditions.

    def __init__(self, limits, object, paramsDict, conditionsDict = {}):

        ## @var Limits
        ## @brief The alarm limits.

        ## @var RootObject
        ## @brief The ROOT object the alarm is set on.
        
        ## @var ParamsDict
        ## @brief The dictionary of optional algorithm parameters.

        ## @var ConditionsDict
        ## @brief The dictionary of optional conditions which the application
        ## of the alarm is subjected to.

        ## @var __RootObjectOK
        ## @brief Flag.

        ## @var __ParametersOK
        ## @brief Flag.
        
        ## @var Output
        ## @brief The alarm output (initialized to an undefined pAlarmOutput
        #  object in the constructor).
     
        self.Limits = limits
        self.RootObject = object
        self.ParamsDict = paramsDict
        self.ConditionsDict = conditionsDict
        self.__RootObjectOK = True
        self.__ParametersOK = True
        self.Output = pAlarmOutput(limits, self)
        self.Output.Label = copy(self.OUTPUT_LABEL)
        self.Output.DetailedDict = deepcopy(self.OUTPUT_DICTIONARY)
        self.Exception = None
        self.checkObjectType()
        self.checkParameters()

    def hasDetails(self):
        return self.Output.DetailedDict != self.OUTPUT_DICTIONARY

    ## @brief Return True if the algorithm is valid (i.e. both the ROOT
    #  object type and the parameters type are supported).
    ## @param self
    #  The class instance.

    def isValid(self):
        return self.__RootObjectOK and self.__ParametersOK

    ## @brief Return the algorithm name.
    ## @param self
    #  The class instance.

    def getName(self):
        return self.__class__.__name__.strip('alg__')

    ## @brief Return the ROOT object type (the name of the class the
    #  object belongs to).
    ## @param self
    #  The class instance.

    def getObjectType(self):
        return self.RootObject.Class().GetName()

    ## @brief Return the name of the underlying ROOT object the alarm is
    #  set on.
    ## @param self
    #  The class instance.

    def getObjectName(self):
        return self.RootObject.GetName()

    ## @brief Return the value of an algorithm parameter.
    ## @param self
    #  The class instance.    
    ## @param paramName
    #  The name of the parameter, i.e. the corresponding key in the parameters
    #  dictionary.
    ## @param defaultValue
    #  The default value in case the parameter is not explicitely defined.

    def getParameter(self, paramName, defaultValue):
        try:
            return self.ParamsDict[paramName]
        except KeyError:
            return defaultValue

    ## @brief Make sure the algorithm supports the ROOT object it has
    #  to operate on.
    ## @param self
    #  The class instance.

    def checkObjectType(self):
        if self.RootObject is None:
            self.__RootObjectOK = False
            logger.error('None ROOT object for algorithm "%s".' %\
                             self.getName())
            self.Output.setDictValue('UNDEFINED status reason',
                                     'Could not find ROOT object.')
        elif self.getObjectType() not in self.SUPPORTED_TYPES:
            self.__RootObjectOK = False
            logger.error('Invalid object type (%s) for %s. '        %\
                             (self.getObjectType(), self.getName()) +\
                             'The alarm will be ignored.')

    ## @brief Make sure all the optional parameters are supported.
    ## @param self
    #  The class instance.

    def checkParameters(self):
        for paramName in self.ParamsDict.keys():
            if paramName not in self.SUPPORTED_PARAMETERS:
                self.__ParametersOK = False
                logger.error('Invalid parameter (%s) for %s.' %\
                                 (paramName, self.getName())  +\
                                 'The alarm will be ignored.')

    ## @brief Make sure the ROOT object has more then the minimum number
    #  of entries required.
    ## @param self
    #  The class instance.
    ## @param requiredEntries
    #  The minimum number of entries required.

    def min_entries(self, requiredEntries):
        numEntries = self.RootObject.GetEntries()
        if numEntries < requiredEntries:
            self.Output.setDictValue('UNDEFINED status reason',\
                 'Not enough entries (%d, %d required)' %\
                                         (numEntries, requiredEntries))
            return False
        return True

    ## @brief Make sure the condition for running the alarm algorithm on
    #  the ROOT objects are satisfied (return False if not).
    ## @param self
    #  The class instance.

    def checkConditions(self):
        for (condition, value) in self.ConditionsDict.items():
            if not eval('self.%s(%s)' % (condition, value)):
                logger.info('Condition %s not satisfied for %s on %s.' %\
                                (condition, self.getName(),\
                                     self.getObjectName()))
                return False
        return True

    ## @brief Apply the algorithm on the ROOT object.
    ## @param self
    #  The class instance.

    def apply(self):
        if not self.__RootObjectOK:
            logger.warn('Invalid object, "%s" will not be applied.' %\
                         self.getName())
        elif not self.__ParametersOK:
            logger.warn('Invalid parameter(s), "%s" will not be applied.' %\
                         self.getName())
        else:
            if self.checkConditions():
                try:
                    exec('self.run%s()' % self.getObjectType())
                except AttributeError:
                    self.run()

    ## @brief Actual algorithm implementation ("virtual" function to be
    #  overridden by the derived classes).
    ## @param self
    #  The class instance.

    def run(self):
        logger.error('Method run() not implemented for %s.' % self.getName())

    ## @brief Return the "badness" of a given value.
    #
    #  The badness is a measure of the distance of a given points from the
    #  alarm bounds, weighted with the status (CLEAN, WARNING, ERROR) of the
    #  point itself---according to fixed weight factors.
    ## @param self
    #  The class instance.
    ## @param value
    #  The value.
    
    def getBadness(self, value):
        if value < self.Limits.ErrorMin:
            badness = (self.Limits.ErrorMin - value)*ERROR_BADNESS_FACTOR
        elif value > self.Limits.ErrorMax:
            badness = (value - self.Limits.ErrorMax)*ERROR_BADNESS_FACTOR
        elif value < self.Limits.WarningMin:
            badness = (self.Limits.WarningMin - value)*WARNING_BADNESS_FACTOR
        elif value > self.Limits.WarningMax:
            badness = (value - self.Limits.WarningMax)*WARNING_BADNESS_FACTOR
        else:
            highBadness = (self.Limits.WarningMax - value)*CLEAN_BADNESS_FACTOR
            lowBadness  = (value - self.Limits.WarningMin)*CLEAN_BADNESS_FACTOR
            badness = max(lowBadness, highBadness)
        return badness

    ## @brief Return the bin center for a given bin index on the x axis.
    ## @param self
    #  The class instance.
    ## @param bin
    #  The bin index.
    
    def getX(self, bin):
        return self.RootObject.GetXaxis().GetBinCenter(bin)

    ## @brief Return the (formatted) bin center for a given bin index on the
    #  x axis.
    ## @param self
    #  The class instance.
    ## @param bin
    #  The bin index.

    def getFormattedX(self, bin):
        return pUtils.formatNumber(self.getX(bin))

    ## @brief Return the bin center for a given bin index on the y axis.
    ## @param self
    #  The class instance.
    ## @param bin
    #  The bin index.

    def getY(self, bin):
        return self.RootObject.GetYaxis().GetBinCenter(bin)

    ## @brief Return the (formatted) bin center for a given bin index on the
    #  y axis.
    ## @param self
    #  The class instance.
    ## @param bin
    #  The bin index.

    def getFormattedY(self, bin):
        return pUtils.formatNumber(self.getY(bin))

    ## @brief Return the position (in physical coordinates)
    #  corresponding to a given bin index(es).
    ## @param self
    #  The class instance.
    ## @param bins
    #  The bin (i) or the bins tuple (i, j).

    def getPosition(self, index):
        objectType = self.getObjectType()        
        if 'TH1' in objectType:
            return self.getX(index)
        elif 'TH2' in objectType:
            return (self.getX(index[0]), self.getY(index[1]))
        else:
            return index

    ## @brief Return the formatted position (in physical coordinates)
    #  corresponding to a given bin index(es).
    ## @param self
    #  The class instance.
    ## @param bins
    #  The bin (i) or the bins tuple (i, j).

    def getFormattedPosition(self, index):
        objectType = self.getObjectType()        
        if 'TH1' in objectType:
            return self.getFormattedX(index)
        elif 'TH2' in objectType:
            return (self.getFormattedX(index[0]), self.getFormattedY(index[1]))
        else:
            return index

    ## @brief Return the axis title, if any, stripped of the units, to be
    #  used in the label for the detailed dictionary.
    ## @param self
    #  The class instance.
    ## @param axis
    #  The axis (i.e. 'x' or 'y')

    def getAxisLabel(self, axis = 'x'):
        try:
            if axis == 'x':
                label = self.RootObject.GetXaxis().GetTitle()
            elif axis == 'y':
                label = self.RootObject.GetYaxis().GetTitle()
        except:
            return axis
        if '(' in label:
            label = label.split('(')[0].strip()
        if label == '':
            label = axis
        return label

    ## @brief Return a suitable label to be put into the output detailed
    #  dictionary of an alarm when a given value exceeds the limits.
    ## @param self
    #  The class instance.
    ## @param position
    #  The position in the ROOT object (i.e. tree branch or histogram).
    ## @param value
    #  The value.
    
    def getDetailedLabel(self, index, value, valueLabel = 'value'):
        objectType = self.getObjectType()
        value = pUtils.formatNumber(value)
        position = self.getFormattedPosition(index)
        if objectType == 'TBranch':
            label = 'time = %f, ' % self.TimestampArray[0]
            if self.BranchArray.size > 1:
                index = self.index2Tuple(index, self.BranchArray.shape)
                if len(index) == 1:
                    index = '[%d]' % index[0]
                else:
                    index = str(index)
                    index = index.replace('(', '[').replace(')', ']')
                label += 'array index = %s, ' % index
            label += '%s = %s' % (valueLabel, value)
        elif 'TH1' in objectType:
            label = '%s = %s, %s = %s' % (self.getAxisLabel('x'), position,\
                                              valueLabel, value)
        elif 'TH2' in objectType:
            label = '%s = %s, %s = %s, %s = %s' %\
                (self.getAxisLabel('x'), position[0], self.getAxisLabel('y'),\
                     position[1], valueLabel, value)
        else:
            label = 'index = %s, value = %s' % (index, value)
        return label

    ## @brief Return the "status" (i.e. CLEAN, WARNING, ERROR) of a given
    #  value, when checked against the alarm limits.
    ## @param self
    #  The class instance.
    ## @param value
    #  The value.

    def getStatus(self, value):
        if value < self.Limits.ErrorMin or value > self.Limits.ErrorMax:
            return STATUS_ERROR
        elif value < self.Limits.WarningMin or value > self.Limits.WarningMax:
            return STATUS_WARNING
        return STATUS_CLEAN

    ## @brief Check the status for a given step (bin index or array index)
    #  in the execution of a given algorithm and fill the output detailed
    #  dictionaries if needed.
    #  
    #  This is a quite complicated function that might deserve some more
    #  explanation.
    #  At the beginning we check whether the particulat histogram bin or
    #  array index is in the list of exception, in which case the logic
    #  of the whole thing must be flipped. At this point there are actually
    #  three different possible cases (with relative sub-cases) in the
    #  "decision tree":
    #
    #  @li Case 1: ERROR.
    #  <br>
    #  In case of exception fill the list of known issues, otherwise the
    #  list of errors.
    #
    #  @li Case 2: WARNING.
    #  <br>
    #  In case of exception fill the list of known issues, otherwise the
    #  list of warning.
    #
    #  @li Case 3: CLEAN.
    #  <br>
    #  In case of exception fill the list of exception violations, otherwise
    #  just pass by.
    #
    #  There's a basic design issue, here, on whether it's better to use
    #  histogram bin indexes of physical locations on the histogram (i.e. bin
    #  centers) as function parameters. The first approach has the advantage
    #  that you put physical quantities (i.e. GTFE number or ACD tile number)
    #  in the exception file, but not sure how we can handle the case
    #  in which the bin center is not integer, since the algorithm involves
    #  a comparison between numbers. We stick to this first implementation,
    #  for the moment.
    #
    #  Also note that the function returns a boolean telling whether the
    #  particular index is in the list of exceptions (meaning whether the logic
    #  has been flipped or not). This value may be used in the calling function
    #  to differenciate its behaviour.
    #  
    ## @param self
    #  The class instance

    def checkStatus(self, index, value, valueLabel):
        position = self.getPosition(index)
        if self.Exception is None:
            flip = False
        else:
            flip = (position in self.Exception.FlippedDetails)
        if value < self.Limits.ErrorMin or value > self.Limits.ErrorMax:
            label = self.getDetailedLabel(index, value, valueLabel)
            if flip:
                self.Output.appendDictValue('known_issues', label)
            else:
                self.Output.incrementDictValue('num_error_entries')
                self.Output.appendDictValue('error_entries', label)
        elif value < self.Limits.WarningMin or value > self.Limits.WarningMax:
            label = self.getDetailedLabel(index, value, valueLabel)
            if flip:
                self.Output.appendDictValue('known_issues', label)
            else:
                self.Output.incrementDictValue('num_warning_entries')
                self.Output.appendDictValue('warning_entries', label)
        else:
            if flip:
                label = self.getDetailedLabel(index, value, valueLabel)
                self.Output.appendDictValue('exception violations', label)
        return flip

    ## @brief Convert a flat index to a multi-dimensional array position.
    ## @param self
    #  The class instance.
    ## @param index
    #  The flat index.
    ## @param shape
    #  The array shape---in the numpy sense.
    
    def index2Tuple(self, index, shape):
        return numpy.unravel_index(index, shape)

    ## @brief Convert a multi-dimensional array position to a flat index.
    ## @param self
    #  The class instance.
    ## @param tuple
    #  The flat the position in the arary.
    ## @param shape
    #  The array shape---in the numpy sense.

    def tuple2Index(self, tuple, shape):
        if type(tuple) == types.IntType:
            return tuple
        index = 0
        for i in range(len(shape)):
            factor = 1
            for j in shape[(i+1):]:
                factor *= j
            index += factor*tuple[i]
        return index

    ## @brief Adjust the range of the x axis of a ROOT object according
    #  to the dictionary of optional parameters.
    #
    #  If the self.ParamsDict variable does not contain neither 'min' nor
    #  'max' key, then there's nothing to do. Otherwise the range on the
    #  x-axis is set properly, using the SetRangeUser() ROOT function.
    #  Note that the minimum and maximum values can be specified separately
    #  (there's no need to specify both). If one of the two is not set,
    #  the function behaves as expected (namely it leaves that end of the range
    #  untouched).
    #
    #  @todo Extend the implementation to ROOT objects other than TH1
    #  (the only supported type at the moment).
    #
    ## @param self
    #  The class instance.

    def adjustXRange(self):
        if self.getObjectType() not in ['TH1F']:
            logger.warn('Cannot use setRangeX() on a %s object.' %\
                         self.getObjectType())
            return None
        if ('min' not in self.ParamsDict.keys())\
                and ('max' not in self.ParamsDict.keys()):
            return None
        try:
            min = self.ParamsDict['min']
        except KeyError:
            min = self.RootObject.GetXaxis().GetXmin()
        try:
            max = self.ParamsDict['max']
        except KeyError:
            max = self.RootObject.GetXaxis().GetXmax()
        self.RootObject.GetXaxis().SetRangeUser(min, max)

    ## @brief Restore the original x axis range for a ROOT object.
    #
    #  This is done via a call to the SetRange(1, 0) ROOT function.
    #
    ## @param self
    #  The class instance.

    def resetXRange(self):
        if self.getObjectType() not in ['TH1F']:
            logger.warn('Cannot use setRangeX() on a %s object.' %\
                         self.getObjectType())
            return None
        self.RootObject.GetXaxis().SetRange(1, 0)

    ## @brief Perform a fit with a user defined function and return
    #  a given fit parameter.
    #
    #  Note that the fit execution is embedded in the body the method so that
    #  in case more than one fit parameters are required this may not be the
    #  optimal approach.
    #
    ## @param self
    #  The class instance.
    ## @param fitFunction
    #  The fitting function (a ROOT TF1 object).
    ## @param paramNumber
    #  The index identifying the required parameter.

    def getFitParameter(self, fitFunction, paramNumber, fitOptions = 'QN'):
        self.adjustXRange()
        self.RootObject.Fit(fitFunction, fitOptions)
        self.resetXRange()
        return fitFunction.GetParameter(paramNumber)

    ## @brief Perform a fit with a user defined function and return
    #  the list of fit parameters.
    #
    ## @param self
    #  The class instance.
    ## @param fitFunction
    #  The fitting function (a ROOT TF1 object).

    def getFitParameters(self, fitFunction, fitOptions = 'QN'):
        self.adjustXRange()
        self.RootObject.Fit(fitFunction, fitOptions)
        self.resetXRange()
        params = []
        for i in range(fitFunction.GetNpar()):
            params.append(fitFunction.GetParameter(i))
        return params

    ## @brief Return the average value of a list of number.
    ## @param self
    #  The class instance.
    ## @param list
    #  The list to be averaged.
    ## @param default
    #  The default value to be returned in case something goes wrong during the
    #  average evaluation.

    def getAverage(self, list, default = 0):
        try:
            return sum(list)/float(len(list))
        except:
            logger.error('Could not evaluate the average of %s.' % list)
            logger.info('Returning %s.' % default)
            return default

    ## @brief Return a list of bins close to a given bin.
    ## @param self
    #  The class instance.
    ## @param bin
    #  The bin we're interested into.
    #  If the bin is a simple integer, then is it interpreted as the bin
    #  ID of a 1-dimensional histogram; a list of integers is returned in this
    #  case. If it's a list or a tuple of length 2 it is interpreted as the
    #  (i, j) bin ID of a 2-dimensional histogram and a list of tuples of
    #  length 2 is returned.
    ## @param numNeighbours
    #  The number of bins on the left and right---as well as top and bottom,
    #  for the 2-dimensional histograms---which are considered neighbours.

    def getNeighbouringBinsList(self, bin, numNeighbours):
        binsList = []
        if type(bin) == types.IntType:
            numBins = self.RootObject.GetNbinsX()
            minBin = max(1, bin - numNeighbours)
            maxBin = min(numBins, bin + numNeighbours)
            for i in range(minBin, maxBin + 1):
                if i != bin:
                    binsList.append(i)
        elif len(bin) == 2:
            (binX, binY) = bin
            numBinsX = self.RootObject.GetNbinsX()
            numBinsY = self.RootObject.GetNbinsY()
            minBinX  = max(1, binX - numNeighbours)
            maxBinX  = min(numBinsX, binX + numNeighbours)
            minBinY  = max(1, binY - numNeighbours)
            maxBinY  = min(numBinsY, binY + numNeighbours)
            for i in range(minBinX, maxBinX + 1):
                for j in range(minBinY, maxBinY + 1):
                    if (i, j) != (binX, binY):
                        binsList.append((i, j))
        else:
            logger.error('Invalid bin identifier in getNeighbouringBinsList.')
            logger.info('Returning an empty list.')
        return binsList

    ## @brief Return the average content of the histogram bins located close
    #  to a given bin.
    ## @param self
    #  The class instance.
    ## @param bin
    #  The bin we're interested into.
    #  If the bin is a simple integer, then is it interpreted as the bin
    #  ID of a 1-dimensional histogram. If it's a list or a tuple of length 2
    #  it is interpreted as the (i, j) bin ID of a 2-dimensional histogram.
    ## @param numNeighbours
    #  The number of bins on the left and right---as well as top and bottom,
    #  for the 2-dimensional histograms---which are considered neighbours.
    ## @param lowCut
    #  The <em>fraction</em> of bins with the lowest content to be excluded in
    #  the average evaluation.
    ## @param highCut
    #  The <em>fraction</em> of bins with the highest content to be excluded in
    #  the average evaluation.

    def getNeighbouringAverage(self, bin, numNeighbours, lowCut, highCut):
        binsContent = []
        binsList = self.getNeighbouringBinsList(bin, numNeighbours)
        firstBin = binsList[0]
        if type(firstBin) == types.IntType:
            for i in binsList:
                binsContent.append(self.RootObject.GetBinContent(i))
        elif len(firstBin) == 2:
            for (i, j) in binsList:
                binsContent.append(self.RootObject.GetBinContent(i, j))
        binsContent.sort()
        numBins = len(binsContent)
        numCutBinsLow = int(numBins*lowCut)
        numCutBinsHigh = int(numBins*highCut)
        binsContent =  binsContent[numCutBinsLow:-(numCutBinsHigh + 1)]
        return self.getAverage(binsContent)



if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    from pSafeROOT    import ROOT
    limits = pAlarmLimits(-1, 3, -1, 6)

    print
    print 'Testing on a 1-dimensional histogram...'
    histogram1d = ROOT.TH1F('h1d', 'h1d', 10, -5, 5)
    algorithm1d = pAlarmBaseAlgorithm(limits, histogram1d, {})
    print algorithm1d.getNeighbouringBinsList(3, 1)
    print algorithm1d.getNeighbouringBinsList(3, 2)
    print algorithm1d.getNeighbouringBinsList(3, 3)
    print algorithm1d.getNeighbouringBinsList(3, 10)
    
    print
    print 'Testing on a 2-dimensional histogram...'
    histogram2d = ROOT.TH2F('h2d', 'h2d', 10, -5, 5, 10, -5, 5)
    algorithm2d = pAlarmBaseAlgorithm(limits, histogram2d, {})
    print algorithm2d.getNeighbouringBinsList((3, 3), 1)
    print algorithm2d.getNeighbouringBinsList((3, 3), 2)
