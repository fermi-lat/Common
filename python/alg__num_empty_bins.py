
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

    SUPPORTED_TYPES      = ['TH2F']
    SUPPORTED_PARAMETERS = []

    ## @brief Basic algorithm evaluation for 1-dimensional histograms.
    ## @param self
    #  The class instance.

    def __runTH1(self):
        print 'Not implemented, yet.'

    ## @brief Basic algorithm evaluation for 2-dimensional histograms.
    ## @param self
    #  The class instance.

    def __runTH2(self):
        numEmptyBins = 0
        for i in range(1, self.RootObject.GetNbinsX() + 1):
            for j in range(1, self.RootObject.GetNbinsY() + 1):
                if self.RootObject.GetBinContent(i, j) == 0:
                    numEmptyBins += 1
        self.Output.setValue(numEmptyBins)

    ## @brief Overloaded main function.
    ## @param self
    #  The class instance.
                    
    def run(self):
        self.__runTH2()
