
from pSafeROOT import ROOT
from math      import sqrt

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm


## @brief Search for (statistically) empty bin(s) into a (1 or 2-d) histogram
## reportnig detailed information.
#
#  This is an attempt to extend the alg__num_empty_bins base algorithm
#  to handle a more general variety of cases taking into account the
#  statistics of the histogram.
#
#  This is a rough step-by-step description of the algorithm:
#  @li Loop over all the the bins of an existing histogram (<em>not</em>
#  including overflow and underflow bins)
#  @li Whenever an empty bin (if any) is found the average content of the
#  neighbour bins is evaluated and the significance of the <em>emptiness</em>
#  is then calculated as the square root of average content itself---poisson
#  statistics is assumed, here.
#  To tell the whole story, there are some knobs that can be turned to
#  make the algorithm more roboust in the real life. First of all the number
#  of bins on the left and on the right (and on top/bottom also for the
#  2-dimensional histograms) that are considered <em>neighbour</em> can be
#  set by the user. The other thing is that the outliers can be automatically
#  removed in the evaluation of the average via parameters. See the
#  documentation of @ref pAlarmBaseAlgorithm.getNeighbourBinsList() and
#  @ref pAlarmBaseAlgorithm.getNeighbourAverage() for more details.  
#
#  @todo Add support for one dimensional histograms, which is still missing.


class alg__empty_bins(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH2F']
    SUPPORTED_PARAMETERS = ['num_neighbours', 'outliers_low_cut',\
                            'outliers_high_cut']
    
    def __init__(self, limits, object, paramsDict = {}):
        pAlarmBaseAlgorithm.__init__(self, limits, object, paramsDict)

    def __runTH1(self):
        print 'Not implemented, yet.'

    def __runTH2(self):
        try:
            numNeighbours = self.ParamsDict['num_neighbours']
        except KeyError:
            numNeighbours = 2
        try:
            outliersLowCut = self.ParamsDict['outliers_low_cut']
        except KeyError:
            outliersLowCut  = 0.0
        try:
            outliersHighCut = self.ParamsDict['outliers_high_cut']
        except KeyError:
            outliersHighCut = 0.25
        values = [0.0]
        for i in range(1, self.RootObject.GetNbinsX() + 1):
            for j in range(1, self.RootObject.GetNbinsY() + 1):
                if self.RootObject.GetBinContent(i, j) == 0:
                    averageNeighbourContent = self.getNeighbourAverage((i, j),\
                        numNeighbours, outliersLowCut, outliersHighCut)
                    significance = sqrt(averageNeighbourContent)
                    values.append(significance)
                    if significance > self.Limits.ErrorMax:
                        self.Output.incrementDictValue('num_error_bins')
                        self.Output.appendDictValue('error_bins',\
                                                    (i-1, j-1, significance))
                    elif significance > self.Limits.WarningMax:
                        self.Output.incrementDictValue('num_warning_bins')
                        self.Output.appendDictValue('warning_bins',\
                                                    (i-1, j-1, significance))
        self.Output.setValue(max(values))
        
    def run(self):
        self.Output.setDictValue('num_warning_bins', 0)
        self.Output.setDictValue('num_error_bins'  , 0)
        self.Output.setDictValue('warning_bins', [])
        self.Output.setDictValue('error_bins'  , [])
        self.__runTH2()
