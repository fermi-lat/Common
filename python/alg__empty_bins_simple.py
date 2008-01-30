
from pSafeROOT import ROOT
from math      import sqrt

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm


## @brief Search for (statistically) empty bin(s) into a (1 or 2-d) histogram
## reporting detailed information.
#
#  This is a trivial extension of the alg__num_empty_bins base algorithm.
#  In the output the complete list of the empty bins is embedded in the
#  detailed dictionary.
#
#  <b>Output value</b>:
#
#  The number of empty bins.
#
#  <b>Output details</b>:
#
#  @li <tt>empty_bins</tt>: the list of empty bins.
#
#  @todo Add support for one dimensional histograms, which is still missing.


class alg__empty_bins_simple(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH2F']
    SUPPORTED_PARAMETERS = []
    OUTPUT_DICTIONARY    = {'empty_bins': []}

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
                    binString = 'bin = (%d, %d)' % (i - 1, j - 1)
                    self.Output.appendDictValue('empty_bins', binString)
        self.Output.setValue(numEmptyBins)

    ## @brief Overloaded main function.
    ## @param self
    #  The class instance.
        
    def run(self):
        self.__runTH2()
