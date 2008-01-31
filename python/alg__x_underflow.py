
from pSafeROOT import ROOT

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm



## @brief Number of entries in the underflow bin.
#
#  <b>Output value</b>:
#
#  Content of the underflow bin.



class alg__x_underflow(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1F']
    SUPPORTED_PARAMETERS = []
    OUTPUT_DICTIONARY    = {}
    OUTPUT_LABEL         = 'Number of underflows'

    def run(self):
        self.Output.setValue(self.RootObject.GetBinContent(0))


if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    limits = pAlarmLimits(-1, 2, -1, 3)
    canvas = ROOT.TCanvas('Test canvas', 'Test canvas', 400, 400)
    
    histogram = ROOT.TH1F('h', 'h', 100, -5, 5)
    histogram.FillRandom('gaus', 1000)
    for i in range(25):
        histogram.Fill(-10)
    histogram.Draw()
    canvas.Update()
    algorithm = alg__x_underflow(limits, histogram, {})
    algorithm.apply()
    print algorithm.Output
