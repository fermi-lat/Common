
from pSafeROOT import ROOT
from math      import sqrt

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm


## @brief Search for (statistically) empty bin(s) into a (1 or 2-d) histogram
## reporting detailed information.
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
#  <b>Valid parameters</b>:
#
#  @li <tt>num_neighbours</tt>: the number of bins on the left and on the right
#  (as well as those on top and bottom for the 2-dimensional histograms) of
#  the one under investigation that are considered in the average evaluation.
#  The bin under investigation is obviously excluded so that the total number
#  of bins considered (not taking into account possible cuts to remove
#  outliers) is <tt>2*num_neighbours - 1</tt> for 1-dimensional histograms and
#  <tt>(2*num_neighbours + 1)**2 - 1</tt> for 2-dimensional histograms---
#  this is not quite right, actually, for the bins on the edges, which should
#  be treated properly by @ref @ref pAlarmBaseAlgorithm.getNeighbourBinsList().
#  <br/>
#  @li <tt>out_low_cut</tt>: the <em>fraction</em> of bins with the
#  <em>lowest</em> content which are removed before the average evaluation
#  ---the list of bins is preliminary sorted based on the number of entries
#  per bin.
#  <br/>
#  @li <tt>out_high_cut</tt>:the <em>fraction</em> of bins with the
#  <em>highest</em> content which are removed before the average evaluation
#
#  <b>Output value</b>:
#
#  The statistical significance (number of standard deviations) of the
#  most significant empty bins---if any. If there are no empty bins, the
#  output value is zero.
#
#  <b>Output details</b>:
#
#  @li <tt>num_warning_bins</tt>: the number of empty bins whose statistical
#  significance produces a warning.
#  <br/>
#  @li <tt>num_error_bins</tt>: the number of empty bins whose statistical
#  significance produces an error.
#  <br/>
#  @li <tt>warning_bins</tt>: a list of all the bins producing a warning. Each
#  element of the list is a 3-elememts tuple of the form
#  (x-coordinate, y-coordinate, significance).
#  <br/>
#  @li <tt>error_bins</tt>: a list of all the bins producing a warning. Each
#  element of the list is a 3-elememts tuple of the form
#  (x-coordinate, y-coordinate, significance).
#  <br/>
#
#  @todo Add support for one dimensional histograms, which is still missing.


class alg__empty_bins(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH2F']
    SUPPORTED_PARAMETERS = ['num_neighbours', 'out_low_cut', 'out_high_cut']

    ## @brief Basic algorithm evaluation for 1-dimensional histograms.
    ## @param self
    #  The class instance.

    def __runTH1(self):
        print 'Not implemented, yet.'

    ## @brief Basic algorithm evaluation for 2-dimensional histograms.
    ## @param self
    #  The class instance.

    def __runTH2(self):
        try:
            numNeighbours = self.ParamsDict['num_neighbours']
        except KeyError:
            numNeighbours = 2
        try:
            outliersLowCut = self.ParamsDict['out_low_cut']
        except KeyError:
            outliersLowCut  = 0.0
        try:
            outliersHighCut = self.ParamsDict['out_high_cut']
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

    ## @brief Overloaded main function.
    ## @param self
    #  The class instance.
        
    def run(self):
        self.Output.setDictValue('num_warning_bins', 0)
        self.Output.setDictValue('num_error_bins'  , 0)
        self.Output.setDictValue('warning_bins', [])
        self.Output.setDictValue('error_bins'  , [])
        self.__runTH2()
