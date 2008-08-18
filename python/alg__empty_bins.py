
import pUtils

from pSafeROOT           import ROOT
from math                import sqrt
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
#  @li <tt>num_warning_entries</tt>: the number of empty bins whose statistical
#  significance produces a warning.
#  <br>
#  @li <tt>num_error_entries</tt>: the number of empty bins whose statistical
#  significance produces an error.
#  <br>
#  @li <tt>warning_entries</tt>: a list of all the bins producing a warning.
#  Each element of the list is a string which should be self-explaining.
#  <br>
#  @li <tt>error_entries</tt>: a list of all the bins producing a warning. Each
#  element of the list is a string which should be self-explaining.
#  <br>



class alg__empty_bins(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1F', 'TH2F', 'TH1D', 'TH2D']
    SUPPORTED_PARAMETERS = ['num_neighbours', 'out_low_cut', 'out_high_cut']
    OUTPUT_LABEL          = 'Significance for the worst bin'

    ## @brief Basic algorithm evaluation for 1-dimensional histograms.
    ## @param self
    #  The class instance.

    def runTH1F(self):
        numNeigh = self.getParameter('num_neighbours', 3)
        outLoCut = self.getParameter('out_low_cut', 0.0)
        outHiCut = self.getParameter('out_high_cut', 0.25)
        maxSignificance = -1
        for i in range(1, self.RootObject.GetNbinsX() + 1):
            if self.RootObject.GetBinContent(i) != 0:
                significance = 0
            else:
                exp = self.getNeighbouringAverage(i, numNeigh,\
                                                      outLoCut, outHiCut)
                significance = sqrt(exp)
            if significance > maxSignificance:
                maxSignificance = significance
            badness = self.checkStatus(i, significance, 'significance')
        self.Output.setValue(maxSignificance)
                
    ## @brief Basic algorithm evaluation for 2-dimensional histograms.
    ## @param self
    #  The class instance.

    def runTH2F(self):
        numNeigh = self.getParameter('num_neighbours', 2)
        outLoCut = self.getParameter('out_low_cut', 0.0)
        outHiCut = self.getParameter('out_high_cut', 0.25)
        maxSignificance = -1
        for i in range(1, self.RootObject.GetNbinsX() + 1):
            for j in range(1, self.RootObject.GetNbinsY() + 1):
                if self.RootObject.GetBinContent(i, j) != 0:
                    significance = 0
                else:
                    exp = self.getNeighbouringAverage((i, j), numNeigh,\
                                                          outLoCut, outHiCut)
                    significance = sqrt(exp)
                if significance > maxSignificance:
                    maxSignificance = significance
                badness = self.checkStatus((i, j), significance,\
                                               'significance')
        self.Output.setValue(maxSignificance)



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
    print 'Parameters: %s\n' % algorithm1d.ParamsDict
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
    print 'Parameters: %s\n' % algorithm2d.ParamsDict
    print algorithm2d.Output
