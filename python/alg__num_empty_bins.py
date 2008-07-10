
from pSafeROOT import ROOT
from math      import sqrt

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm


## @brief Count the number of empty bin(s) into a (1 or 2-d) histogram.
#
#  This is a very stupid algorithm looping over all the bins of an existing
#  histogram (<em>not</em> including overflow and underflow bins) and counts
#  the number of empty bins.
#  Depending on the particular application, the result may depend---for obvious
#  reasons---on the histogram statistics, so pay attention to the use you do
#  of the algorithm.
#
#  <b>Output value</b>:
#
#  The number of empty bins in the histogram.  
#
#  @todo Add support for one dimensional histograms, which is still missing.


class alg__num_empty_bins(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1F', 'TH2F']
    SUPPORTED_PARAMETERS = []
    OUTPUT_LABEL         = 'Number of empty bins'

    ## @brief Basic algorithm evaluation for 1-dimensional histograms.
    ## @param self
    #  The class instance.

    def runTH1F(self):
        numEmptyBins = 0
        for i in range(1, self.RootObject.GetNbinsX() + 1):
            if self.RootObject.GetBinContent(i) == 0:
                numEmptyBins += 1
        self.Output.setValue(numEmptyBins)

    ## @brief Basic algorithm evaluation for 2-dimensional histograms.
    ## @param self
    #  The class instance.

    def runTH2F(self):
        numEmptyBins = 0
        for i in range(1, self.RootObject.GetNbinsX() + 1):
            for j in range(1, self.RootObject.GetNbinsY() + 1):
                if self.RootObject.GetBinContent(i, j) == 0:
                    numEmptyBins += 1
        self.Output.setValue(numEmptyBins)



if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    canvas = ROOT.TCanvas('Test canvas', 'Test canvas', 600, 300)
    canvas.Divide(2, 1)
    limits = pAlarmLimits(-1, 1, -1, 1)

    print
    print 'Testing on a 1-dimensional histogram...'
    canvas.cd(1)
    histogram1d = ROOT.TH1F('h1d', 'h1d', 10, -5, 5)
    histogram1d.FillRandom('pol0', 1000)
    histogram1d.SetBinContent(3, 0)
    histogram1d.Draw()
    canvas.Update()
    algorithm1d = alg__num_empty_bins(limits, histogram1d, {})
    algorithm1d.apply()
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
    algorithm2d = alg__num_empty_bins(limits, histogram2d, {})
    algorithm2d.apply()
    print algorithm2d.Output
