
import pUtils

from pSafeROOT           import ROOT
from math                import sqrt
from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm

from pAlarmOutput import STATUS_CLEAN, STATUS_WARNING, STATUS_ERROR

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
#  documentation of @ref pAlarmBaseAlgorithm.getNeighbouringBinsList() and
#  @ref pAlarmBaseAlgorithm.getNeighbouringAverage() for more details.
#
#  <b>Valid parameters</b>:
#
#  @li <tt>num_neighbours</tt>: the number of bins on the left and on the right
#  (as well as those on top and bottom for the 2-dimensional histograms) of
#  the one under investigation that are considered in the average evaluation.
#  The bin under investigation is obviously excluded so that the total number
#  of bins considered (not taking into account possible cuts to remove
#  outliers) is
#  @f[
#  2 \cdot {\tt num\_neighbours} - 1
#  @f]
#  for 1-dimensional histograms and
#  @f[
#  (2 \cdot {\tt num\_neighbours} + 1)^2 - 1
#  @f]
#  for 2-dimensional histograms---
#  this is not quite right, actually, for the bins on the edges, which are
#  treated properly by @ref pAlarmBaseAlgorithm.getNeighbouringBinsList().
#  <br>
#  @li <tt>out_low_cut</tt>: the <em>fraction</em> of bins with the
#  <em>lowest</em> content which are removed before the average evaluation
#  ---the list of bins is preliminary sorted based on the number of entries
#  per bin.
#  <br>
#  @li <tt>out_high_cut</tt>:the <em>fraction</em> of bins with the
#  <em>highest</em> content which are removed before the average evaluation.
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
#  <br>
#  @li <tt>num_error_bins</tt>: the number of empty bins whose statistical
#  significance produces an error.
#  <br>
#  @li <tt>warning_bins</tt>: a list of all the bins producing a warning. Each
#  element of the list is a string which should be self-explaining.
#  <br>
#  @li <tt>error_bins</tt>: a list of all the bins producing a warning. Each
#  element of the list is a string which should be self-explaining.
#  <br>



class alg__empty_bins(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1F', 'TH2F']
    SUPPORTED_PARAMETERS = ['num_neighbours', 'out_low_cut', 'out_high_cut']
    OUTPUT_DICTIONARY    = {'num_warning_bins': 0,
                            'num_error_bins'  : 0,
                            'warning_bins'    : [],
                            'error_bins'      : []
                            }
    OUTPUT_LABEL          = 'Significance for the worst bin'

    ## @brief Basic algorithm evaluation for 1-dimensional histograms.
    ## @param self
    #  The class instance.

    def runTH1F(self):
        numNeighbours = self.getParameter('num_neighbours', 3)
        outliersLowCut = self.getParameter('out_low_cut', 0.0)
        outliersHighCut = self.getParameter('out_high_cut', 0.25)
        values = [0.0]
        for i in range(1, self.RootObject.GetNbinsX() + 1):
            if self.RootObject.GetBinContent(i) == 0:
                averageCounts = self.getNeighbouringAverage(i, numNeighbours,\
                                     outliersLowCut, outliersHighCut)
                significance = sqrt(averageCounts)
                values.append(significance)
                if self.getStatus(significance) == STATUS_ERROR:
                    self.Output.incrementDictValue('num_error_bins')
                    self.Output.appendDictValue('error_bins',\
                        self.getDetailedLabel(i, significance, 'significance'))
                elif self.getStatus(significance) == STATUS_WARNING:
                    self.Output.incrementDictValue('num_warning_bins')
                    self.Output.appendDictValue('warning_bins',\
                        self.getDetailedLabel(i, significance, 'significance'))
        self.Output.setValue(max(values))
                

    ## @brief Basic algorithm evaluation for 2-dimensional histograms.
    ## @param self
    #  The class instance.

    def runTH2F(self):
        numNeighbours = self.getParameter('num_neighbours', 2)
        outliersLowCut = self.getParameter('out_low_cut', 0.0)
        outliersHighCut = self.getParameter('out_high_cut', 0.25)
        values = [0.0]
        for i in range(1, self.RootObject.GetNbinsX() + 1):
            for j in range(1, self.RootObject.GetNbinsY() + 1):
                position = (self.RootObject.GetBinCenter(i),\
                                self.RootObject.GetBinCenter(j))
                if self.RootObject.GetBinContent(i, j) != 0:
                    if position in self.ExceptionIds:
                        self.handleException((i, j), 0, 'significance')
                else:
                    averageCounts = self.getNeighbouringAverage((i, j),\
                                                        numNeighbours,\
                                                        outliersLowCut,\
                                                        outliersHighCut)
                    significance = sqrt(averageCounts)
                    if position in self.ExceptionIds:
                        self.handleException((i, j), significance,\
                                                 'significance')
                    else:
                        values.append(significance)
                        if self.getStatus(significance) == STATUS_ERROR:
                            self.Output.incrementDictValue('num_error_bins')
                            self.Output.appendDictValue('error_bins',\
                                 self.getDetailedLabel((i, j), significance,\
                                                           'significance'))
                        elif self.getStatus(significance) == STATUS_WARNING:
                            self.Output.incrementDictValue('num_warning_bins')
                            self.Output.appendDictValue('warning_bins',\
                                 self.getDetailedLabel((i, j), significance,\
                                                           'significance'))
        self.Output.setValue(max(values))



if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    canvas = ROOT.TCanvas('Test canvas', 'Test canvas', 600, 300)
    canvas.Divide(2, 1)
    limits = pAlarmLimits(-1, 3, -1, 6)

    print
    print 'Testing on a 1-dimensional histogram...'
    canvas.cd(1)
    histogram1d = ROOT.TH1F('h1d', 'h1d', 10, -5, 5)
    histogram1d.FillRandom('pol0', 1000)
    histogram1d.SetBinContent(3, 0)
    histogram1d.Draw()
    canvas.Update()
    pardict1d = {}
    algorithm1d = alg__empty_bins(limits, histogram1d, pardict1d)
    algorithm1d.apply()
    print 'Parameters: %s\n' % pardict1d
    print algorithm1d.Output

    print
    print 'Testing on a 2-dimensional histogram...'
    canvas.cd(2)
    histogram2d = ROOT.TH2F('h2d', 'h2d', 10, -5, 5, 10, -5, 5)
    function2d = ROOT.TF2('f2d', '1 + 0*x + 0*y', -5, 5, -5, 5)
    function2d.SetParameter(0, 1)
    histogram2d.FillRandom('f2d', 5000)
    histogram2d.SetBinContent(2, 2, 0)
    histogram2d.SetBinContent(4, 4, 0)
    histogram2d.Draw('colz')
    canvas.Update()
    pardict2d = {}
    algorithm2d = alg__empty_bins(limits, histogram2d, pardict2d)
    algorithm2d.apply()
    print 'Parameters: %s\n' % pardict2d
    print algorithm2d.Output
