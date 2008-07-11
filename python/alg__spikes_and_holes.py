
import pUtils

from pSafeROOT           import ROOT
from math                import sqrt
from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm


## @brief Find spikes and/or holes in (1-dimensional or 2-dimensional)
#  histograms.
#
#  The algorithm works pretty much like @ref alg__empty_bins.alg__empty_bins
#  except for the fact that there's no check on whether the bin is empty or
#  not and the significance s is evaluated as:
#  @f[
#  s = \frac{o - e}{\sqrt{e}}
#  @f]
#  where o is the number of observed counts in the bin and e is the number
#  of expected counts (i.e. the average value of the neighbouring bins).
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
#  The statistical significance of the most pronounced spike or hole.
#
#  <b>Output details</b>:
#
#  @li <tt>num_warning_entries</tt>: the number spikes/holes whose statistical
#  significance produces a warning.
#  <br>
#  @li <tt>num_error_entries</tt>: the number of spikes/holes whose statistical
#  significance produces an error.
#  <br>
#  @li <tt>warning_entries</tt>: a list of all the spikes/holes producing a
#  warning.
#  Each element of the list is a string which should be self-explaining.
#  <br>
#  @li <tt>error_entries</tt>: a list of all the spikes/holes producing a
#  warning.
#  Each element of the list is a string which should be self-explaining.
#  <br>



class alg__spikes_and_holes(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1F', 'TH2F']
    SUPPORTED_PARAMETERS = ['num_neighbours', 'out_low_cut', 'out_high_cut']
    OUTPUT_LABEL          = 'Significance of the worst spike/hole'

    ## @brief Basic algorithm evaluation for 1-dimensional histograms.
    ## @param self
    #  The class instance.

    def runTH1F(self):
        numNeigh = self.getParameter('num_neighbours', 4)
        outLoCut = self.getParameter('out_low_cut', 0.3)
        outHiCut = self.getParameter('out_high_cut', 0.3)
        maxSignificance = -1
        for i in range(1, self.RootObject.GetNbinsX() + 1):
            obs = self.RootObject.GetBinContent(i)
            exp = self.getNeighbouringAverage(i, numNeigh, outLoCut, outHiCut)
            if exp > 0:
                significance = abs(obs - exp)/sqrt(exp)
            else:
                significance = 0.0
            if significance > maxSignificance:
                maxSignificance = significance
            badness = self.checkStatus(i, significance, 'significance')
        self.Output.setValue(maxSignificance)  

    ## @brief Basic algorithm evaluation for 2-dimensional histograms.
    ## @param self
    #  The class instance.

    def runTH2F(self):
        numNeigh = self.getParameter('num_neighbours', 2)
        outLoCut = self.getParameter('out_low_cut', 0.25)
        outHiCut = self.getParameter('out_high_cut', 0.25)
        maxSignificance = -1
        for i in range(1, self.RootObject.GetNbinsX() + 1):
            for j in range(1, self.RootObject.GetNbinsY() + 1):
                obs = self.RootObject.GetBinContent(i, j)
                exp = self.getNeighbouringAverage((i, j), numNeigh, outLoCut,\
                                                      outHiCut)
                if exp > 0:
                    significance = abs(obs - exp)/sqrt(exp)
                else:
                    significance = 0.0
                if significance > maxSignificance:
                    maxSignificance = significance
                badness = self.checkStatus((i, j), significance, 'significance')
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
    histogram1d.GetXaxis().SetTitle('Pulse height (ADC)')
    histogram1d.FillRandom('pol0', 1000)
    histogram1d.SetBinContent(3, 10)
    histogram1d.SetBinContent(9, 250)
    histogram1d.Draw()
    canvas.Update()
    pardict1d = {}
    algorithm1d = alg__spikes_and_holes(limits, histogram1d, pardict1d)
    algorithm1d.apply()
    print 'Parameters: %s\n' % pardict1d
    print algorithm1d.Output

    print
    print 'Testing on a 2-dimensional histogram...'
    canvas.cd(2)
    histogram2d = ROOT.TH2F('h2d', 'h2d', 10, -5, 5, 10, -5, 5)
    histogram2d.GetXaxis().SetTitle('GTFE')
    histogram2d.GetYaxis().SetTitle('Tower number')
    function2d = ROOT.TF2('f2d', '1 + 0*x + 0*y', -5, 5, -5, 5)
    function2d.SetParameter(0, 1)
    histogram2d.FillRandom('f2d', 5000)
    histogram2d.SetBinContent(5, 5, 5)
    histogram2d.SetBinContent(8, 8, 100)
    histogram2d.Draw('colz')
    canvas.Update()
    pardict2d = {}
    algorithm2d = alg__spikes_and_holes(limits, histogram2d, pardict2d)
    algorithm2d.apply()
    print 'Parameters: %s\n' % pardict2d
    print algorithm2d.Output
