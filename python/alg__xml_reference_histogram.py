
import pUtils

from pSafeROOT                import ROOT
from alg__reference_histogram import alg__reference_histogram
from pAlarmBaseAlgorithm      import pAlarmBaseAlgorithm
from math                     import sqrt

## @brief Comparison against a reference histogram.
#


class alg__xml_reference_histogram(alg__reference_histogram):
    
    SUPPORTED_PARAMETERS = ['bin_values', 'reference_name']

    def __init__(self, limits, object, paramsDict, conditionsDict = {}):
        pAlarmBaseAlgorithm.__init__(self, limits, object, paramsDict,\
                                         conditionsDict)
        self.__createReference()

    def __createReference(self):
        binValues = self.ParamsDict['bin_values']
        xMin = self.RootObject.GetXaxis().GetXmin()
        xMax = self.RootObject.GetXaxis().GetXmax()
        numBins = len(binValues) 
        self.ReferenceObject = ROOT.TH1F('reference', 'reference', numBins,\
                                            xMin, xMax)
        for (bin, value) in enumerate(binValues):
            self.ReferenceObject.SetBinContent(bin + 1, value)
        self.ReferenceObject.SetEntries(sum(binValues))          



if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    canvas = ROOT.TCanvas('Test canvas', 'Test canvas', 400, 300)
    limits = pAlarmLimits(-1, 3, -1, 6)

    histogram = ROOT.TH1F('h', 'h', 10, -5, 5)
    histogram.FillRandom('pol1', 10000)
    histogram.SetMinimum(0)
    histogram.SetLineColor(ROOT.kRed)
    histogram.Draw()

    pardict = {'bin_values': [1, 3, 5, 5, 5, 3, 4, 2, 5, 2]}
    algorithm = alg__xml_reference_histogram(limits, histogram, pardict)
    algorithm.ReferenceObject.DrawNormalized('same',\
                                                 histogram.GetSumOfWeights())
    canvas.Update()
    algorithm.apply()
    print 'Parameters: %s\n' % algorithm.ParamsDict
    print algorithm.Output

