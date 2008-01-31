
from pSafeROOT import ROOT

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm


## @brief Position of the center of the first populated bin of
#  the histogram on the x axis.
#
#  <b>Output value</b>:
#
#  The center of the leftmost populated bin.

class alg__x_min_bin(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1F']
    SUPPORTED_PARAMETERS = []
    OUTPUT_DICTIONARY    = {}
    OUTPUT_LABEL         = 'Center of the righmost populated bin'

    def run(self):
        for bin in range(self.RootObject.GetXaxis().GetFirst(),\
                         self.RootObject.GetXaxis().GetLast() + 1):
            if self.RootObject.GetBinContent(bin) > 0:
                self.Output.setValue(self.RootObject.GetBinCenter(bin))
                return None


if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    limits = pAlarmLimits(-4, 4, -5, 5)
    canvas = ROOT.TCanvas('Test canvas', 'Test canvas', 400, 400)
    
    histogram = ROOT.TH1F('h', 'h', 100, -5, 5)
    histogram.FillRandom('gaus', 1000)
    histogram.Draw()
    canvas.Update()
    algorithm = alg__x_min_bin(limits, histogram, {})
    algorithm.apply()
    print algorithm.Output
