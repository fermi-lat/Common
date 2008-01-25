## @package pAlarmBaseAlgorithm
## @brief Base package for implementation of algorithms.

import pSafeLogger
logger = pSafeLogger.getLogger('pAlarmBaseAlgorithm')

import pUtils
from pAlarmOutput import pAlarmOutput


## @brief Base class for alarm algorithms. Look at the inheritance diagram for
#  the list of implemented algorithms.
#
#  Provides a general structure for the implementation of the algorithms,
#  along with some ROOT-related useful functions (like setting histogram
#  range etc...).

class pAlarmBaseAlgorithm:

    ## @var SUPPORTED_TYPES
    ## @brief The list of ROOT object types which are supported by a given
    #  algorithm.

    ## @var SUPPORTED_PARAMETERS
    ## @brief The list of (optional) parameters supported by a given
    #  algorithm.

    SUPPORTED_TYPES      = []
    SUPPORTED_PARAMETERS = []

    ## @brief Basic constructor
    ## @param self
    #  The class instance.
    ## @param limits
    #  The alarm limits.
    ## @param object
    #  The ROOT object the alarm is set on.
    ## @param paramsDict
    #  The dictionary of optional algorithm parameters.

    def __init__(self, limits, object, paramsDict):

        ## @var Limits
        ## @brief The alarm limits.

        ## @var RootObject
        ## @brief The ROOT object the alarm is set on.
        
        ## @var ParamsDict
        ## @brief The dictionary of optional algorithm parameters.

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
        self.__RootObjectOK = True
        self.__ParametersOK = True
        self.checkObjectType()
        self.checkParameters()
        self.Output = pAlarmOutput(limits)

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

    ## @brief Make sure the algorithm supports the ROOT object it has
    #  to operate on.
    ## @param self
    #  The class instance.

    def checkObjectType(self):
        if self.getObjectType() not in self.SUPPORTED_TYPES:
            self.__RootObjectOK = False
            logger.error('Invalid object type (%s) for %s. '    %\
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
                              (paramName, self.getName())      +\
                              'The alarm will be ignored.')

    ## @brief Apply the algorithm on the ROOT object.
    ## @param self
    #  The class instance.

    def apply(self):
        if not self.__RootObjectOK:
            logger.warn('Invalid object, %s will not be applied.' %\
                         self.getName())
        elif not self.__ParametersOK:
            logger.warn('Invalid parameter(s), %s will not be applied.' %\
                         self.getName())
        else:
            self.run()

    ## @brief Actual algorithm implementation ("virtual" function to be
    #  overridden by the derived classes).
    ## @param self
    #  The class instance.

    def run(self):
        logger.warn('Method run() not implemented.')

    ## @brief Adjust the range of the x axis of a ROOT object according
    #  to the dictionary of optional parameters.
    ## @param self
    #  The class instance.

    def adjustXRange(self):
        if self.getObjectType() not in ['TH1F']:
            logger.warn('Cannot use setRangeX() on a %s object.' %\
                         self.getObjectType())
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
    ## @param self
    #  The class instance.

    def resetXRange(self):
        if self.getObjectType() not in ['TH1F']:
            logger.warn('Cannot use setRangeX() on a %s object.' %\
                         self.getObjectType())
            return None
        self.RootObject.GetXaxis().SetRange(1, 0)

    def getAverage(self, list):
        return sum(list)/float(len(list))

    def __getNeighbourBinsList(self, bin, numNeighbours):
        binsList = []
        if len(bin) == 2:
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
            return binsList
        logger.error('Invalid bin identifier in getNeighbourBinsList().')
        logger.info('Returning an empty list.')
        return binsList

    def getNeighbourAverage(self, bin, numNeighbours = 2,\
                            lowCut = 0.0, highCut = 0.25):
        binsList = self.__getNeighbourBinsList(bin, numNeighbours)
        binsContent = []
        for (i, j) in binsList:
            binsContent.append(self.RootObject.GetBinContent(i, j))
        binsContent.sort()
        numBins = len(binsContent)
        numCutBinsLow = int(numBins*lowCut)
        numCutBinsHigh = int(numBins*highCut)
        binsContent =  binsContent[numCutBinsLow:-numCutBinsHigh]
        return self.getAverage(binsContent)
