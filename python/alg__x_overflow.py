
from pSafeROOT import ROOT

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm


## @brief Number of entries in the overflow bin.
#
#  <b>Output value</b>:
#
#  Content of the overflow bin.



class alg__x_overflow(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1F', 'TH1D']
    SUPPORTED_PARAMETERS = []
    OUTPUT_LABEL         = 'Number of overflows'

    def run(self):
        lastBin = self.RootObject.GetNbinsX() + 1
        self.Output.setValue(self.RootObject.GetBinContent(lastBin))


if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    limits = pAlarmLimits(-1, 2, -1, 3)
    canvas = ROOT.TCanvas('Test canvas', 'Test canvas', 400, 400)
    
    histogram = ROOT.TH1F('h', 'h', 100, -2, 2)
    histogram.FillRandom('gaus', 1000)
    for i in range(10):
        histogram.Fill(3)
    histogram.Draw()
    canvas.Update()
    algorithm = alg__x_overflow(limits, histogram, {})
    algorithm.apply()
    print 'Parameters: %s\n' % algorithm.ParamsDict
    print algorithm.Output
