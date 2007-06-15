
import logging
import pUtils
from pAlarmOutput import pAlarmOutput


class pAlarmBaseAlgorithm:

    def __init__(self, limits, object, paramsDict):
        self.Limits = limits
        self.RootObject = object
        self.ParamsDict = paramsDict
        self.__RootObjectOK = True
        self.__ParametersOK = True
        self.checkObjectType()
        self.checkParameters()
        self.Output = pAlarmOutput(limits)

    def isValid(self):
        return self.__RootObjectOK and self.__ParametersOK

    def getName(self):
        return self.__class__.__name__.strip('alg__')

    def getObjectType(self):
        return self.RootObject.Class().GetName()

    def checkObjectType(self):
        if self.getObjectType() not in self.SUPPORTED_TYPES:
            self.__RootObjectOK = False
            logging.error('Invalid object type (%s) for %s. '    %\
                          (self.getObjectType(), self.getName()) +\
                          'The alarm will be ignored.')

    def checkParameters(self):
        for paramName in self.ParamsDict.keys():
            if paramName not in self.SUPPORTED_PARAMETERS:
                self.__ParametersOK = False
                logging.error('Invalid parameter (%s) for %s.' %\
                              (paramName, self.getName())      +\
                              'The alarm will be ignored.')

    def apply(self):
        if not self.__RootObjectOK:
            logging.warn('Invalid object, %s will not be applied.' %\
                         self.getName())
        elif not self.__ParametersOK:
            logging.warn('Invalid parameter(s), %s will not be applied.' %\
                         self.getName())
        else:
            self.run()

    def run(self):
        logging.warn('Method run() not implemented.')

    def adjustXRange(self):
        if self.getObjectType() not in ['TH1F']:
            logging.warn('Cannot use setRangeX() on a %s object.' %\
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

    def resetXRange(self):
        if self.getObjectType() not in ['TH1F']:
            logging.warn('Cannot use setRangeX() on a %s object.' %\
                         self.getObjectType())
            return None
        self.RootObject.GetXaxis().SetRange(1, 0)

    def getTextSummary(self):
        return '** Algorithm summary **\n' +\
               '%s: %s' % (pUtils.expandString('Algorithm type', 20),\
                           self.getName()) +\
               pUtils.expandString('') +\
               pUtils.expandString('')

    def __str__(self):
        pass
    
