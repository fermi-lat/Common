
from pSafeROOT import ROOT

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm



## @brief Position of the center of the last populated bin of
#  the histogram on the x axis.
#
#  <b>Output value</b>:
#
#  The center of the righmost populated bin.



class alg__x_max_bin(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1F', 'TH1D']
    SUPPORTED_PARAMETERS = []
    OUTPUT_LABEL         = 'Center of the righmost populated bin'

    def run(self):
        for bin in range(self.RootObject.GetXaxis().GetLast(),\
                         self.RootObject.GetXaxis().GetFirst() - 1, -1):
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
    algorithm = alg__x_max_bin(limits, histogram, {})
    algorithm.apply()
    print 'Parameters: %s\n' % algorithm.ParamsDict
    print algorithm.Output
